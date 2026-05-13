#!/usr/bin/env python3

import io
import logging
import os
import sys
import stat
import requests
from pprint import pprint
from typing import Optional

import numpy

log = logging.getLogger(__name__)

from thirdparty.pparse.utils import has_mmap, hexdump, mmap
from thirdparty.pparse.dump import Dumper

PARSERS = {}

# Generally, rerun the parser on same node.
AGAIN = 1
# Generally, run the parser on parent node.
ASCEND = 2
COMPLETE = 3


# Job's only purpose is to facilitate kick off of XML import.
class Job:
    # Assuming root node in XML is <job />
    @classmethod
    def from_xml(cls, source):
        from thirdparty.pparse._xml import XmlNode
        job = XmlNode(source)
        if job.get_el().tag != 'job':
            raise ValueError("root node is not <job /> in Job class.")

        # TODO: Verify schema.

        # Kick off parsing by instantiating the root extraction.
        # Note: job is only a root node holder (and is thrown away)
        extraction_cls = globals()[job.extraction['type']]
        return extraction_cls.from_xml(job.extraction)

    # extraction.to_xml() -> "<job />"
    def to_xml(self, extraction) -> str:

        # TODO: Verify schema.

        return '\n'.join(['<job>', extraction.to_xml(), '</job>'])


# OBE ?
# # Generally, run the parser on child node.
# DESCEND = 2
# # Generally, run the parser across all child nodes.
# DESCEND_ALL = 4


class EndOfDataException(Exception):
    pass


class EndOfNodeException(Exception):
    pass


class UnsupportedFormatException(Exception):
    pass


class BufferFullException(Exception):
    pass


class UnloadedValue:
    def __repr__(self):
        return "<UNLOADED_VALUE />"


UNLOADED_VALUE = UnloadedValue()


# Api for Reader-like objects (Cursor, Range)
class Reader:
    def dup(self):
        raise NotImplementedError()

    def tell(self):
        raise NotImplementedError()

    def seek(self):
        raise NotImplementedError()

    def skip(self):
        raise NotImplementedError()

    def peek(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()


# Range manages length and boundaries.
# Range start cursor and length are assumed correct.
# - Range has no insight into data.
# - Length must not be < 0
# Cursor does not manage length.
# Data does not manage offset.
class Range(Reader):
    # Given Cursor object is the start offset
    def __init__(self, cursor, length: int, offset: int = -1):
        self._start_cursor = cursor.dup()
        self._init(cursor.tell(), length, offset)

    def _init(self, start_offset, length, current_offset=-1):
        self._start_cursor.seek(start_offset)
        self._start = self._start_cursor.tell()
        self._cursor = self._start_cursor.dup()

        if current_offset >= 0:
            self._cursor.seek(current_offset)
        if length < 0:
            raise ValueError("Length must not be < 0")
        # Consider: Check for length beyond data?
        self._length = length
        self._end = self._start + length

    def cursor(self):
        return self._cursor.dup()

    def dup(self):
        return Range(self._start_cursor, self._length, self._cursor.tell())

    def truncate(self, new_length):
        if new_length > self._length:
            raise Exception("Truncation of Range must be <= Range length")
        if self._cursor.tell() > self._start + new_length:
            raise Exception("Range cursor must not be in truncated space.")

        self._length = new_length
        self._end = self._start + self._length

        return self

    def length(self):
        return self._length

    def left(self):
        return self._end - self.tell()

    def valid_offset(self, offset):
        return offset >= self._start and offset <= self._end

    def tell(self):
        return self._cursor.tell()

    # Set cursor to absolute location in Data (within bounds).
    def seek(self, offset):
        if not self.valid_offset(offset):
            if offset < self._start:
                offset = self._start
            elif offset > self._end:
                offset = self._end
        self._cursor.seek(offset)
        return offset

    # Ensure length (relative to cursor) is inbounds.
    def _adjust_length(self, length):
        if length < 0:
            return 0
        offset = self.tell() + length
        if not self.valid_offset(offset):
            length = self._end - self.tell()
        return length

    # Progress data without reading.
    def skip(self, length):
        length = self._adjust_length(length)
        return self._cursor.skip(length)

    # Read data ahead without progressing cursor.
    def peek(self, length):
        length = self._adjust_length(length)
        return self._cursor.peek(length)

    # Read data and progress data.
    def read(self, length):
        length = self._adjust_length(length)
        return self._cursor.read(length)


# Cursor manages offset. (Data does not manage offset.)
# Cursor does not manage boundaries.
class Cursor(Reader):
    def __init__(self, data, offset=0):
        self._data = data
        self._offset = offset

    def cursor(self):
        return self

    def dup(self):
        return self._data.open(self._offset)

    # Where in the Data are we
    def tell(self):
        return self._offset

    # Set cursor to specific location.
    def seek(self, offset):
        self._offset = offset
        return self._data.seek(self)

    def skip(self, length):
        self._offset += length
        return self._data.seek(self)

    # Read data ahead without progressing cursor.
    def peek(self, length):
        return self._data.peek(self, length)

    # Copy and progress data.
    def read(self, length, mode=None):
        data = self._data.read(self, length)
        self._offset += len(data)
        return data


class NodeContext:
    def __init__(self, parent: "Node", reader: Reader, parser: "Parser"):
        self._reader = reader.dup()
        self._reader.seek(reader.tell())
        self._state = None
        self._parent = parent  # Parent Node (None for root)
        self._start = self.tell()
        self._end = None
        self._parser = parser
        # When doing a recursive parse, list of descendent references.
        self._descendants = []

    def parent(self):
        return self._parent

    def parent_ctx(self):
        if self._parent:
            return self._parent.ctx()
        return None

    def reader(self):
        return self._reader.dup()

    def state(self):
        return self._state

    def parser(self):
        return self._parser

    def _next_state(self, state):
        self._state = state()

    def set_remaining(self, length):
        self._end = self.tell() + length

    def mark_end(self, node):
        self._end = self.tell()
        node.set_length(self._end - self._start)

    def mark_field_start(self):
        self._field_start = self.tell()

    def field_start(self):
        return self._field_start

    def dup(self):
        return self._reader.dup()

    def tell(self):
        return self._reader.tell()

    def seek(self, *args, **kwargs):
        return self._reader.seek(*args, **kwargs)

    def skip(self, *args, **kwargs):
        return self._reader.skip(*args, **kwargs)

    def peek(self, *args, **kwargs):
        return self._reader.peek(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self._reader.read(*args, **kwargs)

    def left(self):
        if not isinstance(self._reader, Range):
            raise Exception("Reader must be range to use left()")
        return self._reader.left()


class RecursionControl:
    MAX_DEPTH = 9223372036854775807
    def __init__(self, min_depth=0, max_depth=MAX_DEPTH, callback=None):
        self.cur_depth = 0

        self.max_seen_depth = 0

        self.min_depth = min_depth
        self.max_depth = max_depth
        self.cb = callback

    def stopped(self, node) -> bool:
        if self.cur_depth < self.min_depth:
            return False
        if self.cur_depth > self.max_depth:
            return True
        
        if self.cb is not None:
            return self.cb(node)
    
    def increase_depth(self, amount=1):
        self.cur_depth += amount
        if self.cur_depth > self.max_seen_depth:
            self.max_seen_depth = self.cur_depth
    
    def decrease_depth(self, amount=1):
        self.cur_depth -= amount
    
    def current_depth(self):
        return self.cur_depth

    def deepest_depth(self):
        return self.max_seen_depth

'''
    NEW PLAN:
    - phase 1: ctx is always loaded and node always UNLOADED until parent says otherwise
    - phase 2: ctx can be archived and unloaded (optionally cleared archive)
               root node always has ctx
    - phase 3: ability to replay from root to re-acquire ctx

    Things To Work Out:
    - we can prefer to not parse until referenced by using .value, but if we want to 
      intentionally pre-parse everything, we need a load(recursive=True) or something.
    - with new plan, we should have generic node for 99% of cases. NodeContext is the parser
      specific class going forward. (maybe a generic self._attrs:dict required at node level)
'''
class Node:
    def __init__(self, reader: Reader, parser: "Parser", default_value = UNLOADED_VALUE, parent: "Node" = None, ctx_class: NodeContext = None, ctx_args={}):

        # Reference to the start of data for parsing node.
        self._reader = reader.dup()

        '''
            weird situation here where I don't want to double bind Node and 
            NodeContext, but they are indirectly double bound by NodeContext
            knowing parent of node. This is intentional so that we can throw
            away unnecessary references to parents later.
        '''

        # Reference to the parser in context of node.
        if not ctx_class:
            self._ctx = NodeContext(parent, reader.dup(), parser)
        else:
            self._ctx = ctx_class(parent, reader.dup(), parser, **ctx_args)

        # Reference to the value(s) of node (e.g. dict, list, scalars, or Node)
        self._value = default_value

    @property
    def value(self):
        if self._value == UNLOADED_VALUE:
            #breakpoint()
            self.load()
        return self._value

    def ctx(self):
        return self._ctx

    def clear_ctx(self):
        # TODO: Archive context here. Archive in parser?
        self._ctx = None
        return self

    def tell(self):
        return self._reader.tell()

    def set_length(self, length):
        self._reader = Range(self._reader.dup(), length)
        return self

    def length(self):
        # TODO: Check for range?
        return self._reader.length()

    def load(self, recursion: Optional[RecursionControl] = None):
        '''
            load() manages RecursionControl lifetime, enabling load() to have different
            behaviors per call and manage recursion relative to current node.

            CAUTION: Recursion control is a mechanism that allows parsers to delegate recursion
            decisions to the caller or user of the API. It does not enforce or provide 
            tightly controlled governance over the parts of the Node tree that get processed.

            RULE: load() should handle the recursive behavior, not the parser state.

            RULE: Leaky abstraction when recursion policy stored in Node or NodeContext!

            NOTE: json is weird because you have to recurse every time. Since I implemented
            JSON first, I believe its driving some of the anti-patterns in pparse. If
            we want to save on memory for JSON, we could theoretically parse and allocate
            nodes and as we complete branches of a depth first parse we deallocated.
            I naturally want to do this for recursive=False, but since recursive=False
            is default, it makes it feel like unnecessary thrashing of the CPU. 
        '''

        # Increment the depth on entrance to load().
        # NOTE: Checking for recursion here because we don't want to mess with reentrant
        #       states and we don't want to wipe or confuse _descendants todo lists. 
        # CAUTION:
        # - states can add multiple branches at once.
        # - states can iterate multiple times in a single "depth level"
        if recursion is not None:
            if recursion.stopped(self):
                return
            recursion.increase_depth()
            #print(f"INCREASE {recursion.cur_depth}")

        # Maybe a naughty pattern, but for now we retry until 
        # Retry until state returns UnsupportedFormatException or EndOfNodeException
        # ! When EndOfDataException raised, we need a way to retry. For now, fail.
        try:
            # RULE: AGAIN is a Parser return. Not a Node is complete status!
            res = AGAIN
            while res == AGAIN:
                
                #breakpoint()
                res = self.ctx().state().parse_data(self)

                '''
                    - The parser is responsible for populating _decendents.
                    - Whenever Node.load() sees elements in _decendents, it immediately
                    calls the load() method on those elements.
                '''
                while self.ctx()._descendants:
                    #breakpoint()self
                    # ! Here, we're making Node responsible for _descendants cleanup.
                    child = self.ctx()._descendants.pop(0)

                    # TODO: use try/except to push forward, even on failure.
                    # TODO: we should be able to track failures for retry later.
                    child.load(recursion=recursion)

                    

                # if len(self.ctx()._descendants) > 0:
                #     breakpoint()
                #     for child in node.ctx()._descendants:
                #         child.load(recursive)

            #breakpoint()

        except EndOfNodeException as e:
            pass
        except EndOfDataException as e:
            raise
        except UnsupportedFormatException:
            raise

        finally:
            # Decrement the depth on exit from load() (exceptions included).
            if recursion is not None:
                recursion.decrease_depth()
                #print(f"DECREASE {recursion.cur_depth}")

        return self

    def unload(self):
        # TODO: Do we have context?
        self.value = pparse.UNLOADED_VALUE


    def dump(self, depth=0, step=2, dumper=None):
        node_attrs =  [f'off="{self.tell()}"']

        if not dumper:
            dumper = Dumper.default()
        dumper.dump("Node", self._value, ' '.join(node_attrs), depth=depth, step=step)


# Data Considerations:
# - DiskData exists in its entirety on disk (even if truncated).
# - TapeData is constantly incoming and recorded (yes to Random Access).
#   - Need to re-mmap when data is appended.
# - StreamData is constantly incoming and only seen once (no to Random Access).

# StreamData may require entire stream to exist in memory, depending on parser
# references. A StreamData buffer can only deallocate data when all parsers
# have indicated they have no more need for the data range.


# Data interface.
class Data:
    def open(self, offset=0) -> Reader:
        return Cursor(self, offset)

    def peek(self, cursor, length):
        raise NotImplementedError()

    def seek(self, cursor) -> int:
        return cursor.tell()

    def read(self, cursor, length):
        # Dumb implementation.
        data = self.peek(cursor, length)
        self.seek(cursor)
        return data







'''
  HttpRangedData is very dumb and slow. If we add caching, we can potentially bump the performance 
  by more than double. The below metrics are misleading when comparing against each other. You need
  to understand the relationship between Range supported/not-supported, between deque based cache and
  linked list based cache, and the relationship between the application and the target kernels' page
  cache, and finally the fact that I tested all of these on the same system across the local network.

  Takeaways:
    - None of these tests include normal network latency.
    - All of the data from these tests lived in kernels page cache.
    - There were no other users on the system this was tested on.
    - FileData is a bit slower because it keeps file on disk, where HttpCacheData pulls
      most of the relevant data into memory. We could probably cache FileData in a similar
      way for a bit of speedup, especially in non-Linux environments (e.g. Windows).
    - The only meaningful numbers to compare are the Range supported cases where the
      whole file could not fit into memory at once. This shows that we've halved HttpRangedData
      behavior when using a cache.
    - Different formats jump around more so they'll produce different results. To mitigate this,
      there is a deliberate grab of chunks around the request for efficiency. This is similar to
      a CPU "read ahead" behavior (except with include "read behind" too.)

  Test results against `yolov5su_float32.tflite` (36832425 bytes / ~36MB)

    --- Control ---

    FileData with local file IO:
      real    0m0.714s
      user    0m1.006s
      sys     0m2.591s

    --- Naive Implementation ---

    HttpRangedData with Range header (i.e. test-server.py):
      real    0m15.338s
      user    0m9.357s
      sys     0m3.129s
    
    HttpRangedData without Range header (i.e. python -m http.server):
      * Not tested. (VERY LONG)

   --- Cached _without_ Range ---

    HttpCachedData with chunk_size 4096*1024, chunks 256, without Range header (i.e. python -m http.server):
      Note: 1,073,741,824B / 1GB cache using deque
      Note: Test case only valid when entire target fits in memory.

      real  0m0.573s
      user  0m0.951s
      sys   0m2.645s

    
    HttpCachedData with chunk_size 4096*256, chunks 1024, without Range header (i.e. python -m http.server):
      Note: 1,073,741,824B / 1GB cache using linked list
      Note: Test case only valid when entire target fits in memory.

      real  0m0.574s
      user  0m0.953s
      sys   0m2.421s


    HttpCachedData with chunk_size 4096, chunks 1024*256, without Range header (i.e. python -m http.server):
      Note: 1,073,741,824B / 1GB cache using linked list
      Note: Test case only valid when entire target fits in memory.
      Note: Bumped chunk count to see if there was a noticeable difference.

      real  0m0.616s
      user  0m1.003s
      sys   0m2.651s

    --- Cached _with_ Range ---

    HttpCachedData with chunk_size 4096, chunks 256, supported Range header (i.e. test-server.py):
      Note: 1,048,576B / 1MB cache using deque

      real  0m8.478s
      user  0m5.617s
      sys   0m2.892s


    HttpCachedData with chunk_size 256, chunks 4096, supported Range header (i.e. test-server.py):
      Note: 1,048,576B / 1MB cache using linked list

      real  0m8.478s
      user  0m5.617s
      sys   0m2.892s


    HttpCachedData with chunk_size 4096*1024, chunks 256, supported Range header (i.e. test-server.py):
      Note: 1,073,741,824B / 1GB cache using deque

      real  0m0.759s
      user  0m1.124s
      sys   0m2.502s


    HttpCachedData with chunk_size 4096*256, chunks 1024, supported Range header (i.e. test-server.py):
      Note: 1,073,741,824B / 1GB cache using linked list

      real  0m0.825s
      user  0m1.200s
      sys   0m2.620s

  Note: AWS has a minimal billable request size of 4K (i.e. 1 byte request is worth 4K in cash.)
'''

from thirdparty.pparse._httpdata import _HttpCachedData

class HttpCachedData(Data):
    # ~ 4MiB
    CHUNK_SIZE = 4096*256
    # Max Chunks
    MAX_CHUNKS = 1024

    def __init__(self, url: str, chunk_size: int = CHUNK_SIZE, chunk_max_count: int = MAX_CHUNKS, session=None):

        # ** If we're in a situation where we're requesting a file from a    **
        # ** remote resource that does not support Range, we might as well   **
        # ** download the whole thing and operate on it as a file. Any       **
        # ** realistic situation where the file is too big for memory, we'll **
        # ** not want to continually download the file when we don't have    **
        # ** the space we need in cache!                                     **

        # Detect the above scenario by fetching length and first chunk.
        self._session = session or requests.Session()
        response = self._session.head(url)
        response.raise_for_status()
        self.length = int(response.headers["Content-Length"])
        self._supports_ranges = response.headers.get("Accept-Ranges", "none").lower() == "bytes"

        if not self._supports_ranges and self.length > chunk_size * chunk_max_count:
            raise Exception("CAUTION: No ranged queries on server and target to large for cache.")

        self.httpdata = _HttpCachedData(url, chunk_size=chunk_size, chunk_max_count=chunk_max_count, session=self._session)


    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        return self.httpdata._read(cursor.tell(), length)



class HttpRangeData(Data):
    def __init__(self, url: str=None):
        if not url:
            raise ValueError("url must be a string that points to a valid url")
        self._url = url
        self._session = requests.Session()
        #self._session.verify = "/path/to/ca-bundle.crt"
        #self._session.verify = False
        #self._session.cert = ("/path/to/client.crt", "/path/to/client.key")
        #self._session.headers["Authorization"] = "Bearer <token>"

        self.length = self._load_length()


    def _load_length(self) -> int:
        response = self._session.head(self._url)
        # TODO: Determine how to handle exceptions.
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length is None:
            raise ValueError("Server did not return a Content-Length header.")

        return int(content_length)

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        if length <= 0:
            return b""

        start = cursor.tell()
        end = start + length - 1
        headers = {"Range": f"bytes={start}-{end}"}

        response = self._session.get(self._url, headers=headers)
        response.raise_for_status()
            
        if response.status_code == 206:
            return response.content

        if response.status_code == 200:
            # TODO: Cache our content.
            # ! Being dumb and throwing away content.
            return response.content[start:start+length]
        raise IOError(f"Range request failed with status {response.status_code}")

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length):
        return self.peek(cursor, length)



# Data manages mmap and fobj. Cursor does not manage mmap or fobj.
class FileData(Data):

    def __init__(self, path=None):
        if not path or not os.path.exists(path):
            raise ValueError("path must be a string that points to a valid file path")
        self._path = path

        self.length = None
        self._fobj = open(path, "rb")

        fd = self._fobj.fileno()
        st = os.fstat(fd)
        if stat.S_ISREG(st.st_mode):
            self.length = st.st_size

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        self._fobj.seek(cursor.tell(), os.SEEK_SET)
        return self._fobj.read(length)

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        self._fobj.seek(cursor.tell(), os.SEEK_SET)
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length):
        self.seek(cursor)
        return self._fobj.read(length)

    # extraction = Extraction.from_xml("<job />")
    @classmethod
    def from_xml(cls, source): # -> cls:
        from thirdparty.pparse._xml import XmlNode, XmlEntry
        xml = XmlNode.as_node(source)

        # Do we have the correct node?
        if xml.get_el().tag != "datasource":
            raise Exception(f"Expected datasource node. Got: {xml.get_el().tag}")

        extra = XmlEntry.using(xml.extra)
        # TODO: Handle non-posix paths
        path = extra['posix_path']

        data = cls(path)
        if data.length != extra['length']:
            raise Exception(f"Mismatch of length on import of {path}: xml length {extra['length']} real length {data.length}.")

        # Let the XML tree hold the reference
        xml.set_obj_inst(data)

        return data

    # extraction.to_xml() -> "<job />"
    def to_xml(self) -> str:
        raise NotImplementedError("to_xml not implemented")


# Data manages mmap and fobj. Cursor does not manage mmap or fobj.
class FileMmapData(Data):
    def __init__(self, path=None):
        if not path or not os.path.exists(path):
            raise ValueError("path must be a string that points to a valid file path")
        self._path = path

        self.length = None
        self._fobj = open(path, "rb")
        self._load_length()

        # Mmap, if available.
        if not has_mmap():
            raise Exception("No mmap available.")

        self._mmap = mmap.mmap(self._fobj.fileno(), 0, access=mmap.ACCESS_READ)
        self._mem = memoryview(self._mmap)

    def _load_length(self):
        # TODO: This size is only relevant if the size doesn't change.
        fd = self._fobj.fileno()
        st = os.fstat(fd)

        if stat.S_ISREG(st.st_mode):
            self.length = st.st_size

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        off = cursor.tell()
        return self._mem[off : off + length]

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        # Noop for mmap.
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length, mode=None):
        off = cursor.tell()
        return self._mem[off : off + length]


# When working with data that is already (reasonably) in memory, we may want to use it as a
# data source. Having that use case in its own class permits us to handle that without extra
# conditions. Mostly the same as FileData, but understood to be in memory.
#
# Real World Use Case: File-format is a ZIP and the header is a file in the ZIP.
#
class BytesIoData(Data):
    def __init__(self, bytes_io: io.BytesIO = None):
        if not bytes_io or not isinstance(bytes_io, io.BytesIO):
            raise ValueError("bytes_io must be io.BytesIO and not be None")

        self._bytes_io = bytes_io
        self.length = len(self._bytes_io.getbuffer())

    def _load_length(self):
        pass

    # Create a cursor, like a logical file descriptor.
    def open(self, offset=0):
        return Cursor(self, offset)

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        self._bytes_io.seek(cursor.tell(), os.SEEK_SET)
        return self._bytes_io.read(length)

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        self._bytes_io.seek(cursor.tell(), os.SEEK_SET)
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length):
        self.seek(cursor)
        return self._bytes_io.read(length)


# Generic artifact that ties parsers to cursor-ed data.
class Extraction:
    def __init__(self, name: str = None, source: Optional["Extraction"] = None):
        # The extraction we came from. Detect parser via source.
        self._source: Optional["Extraction"] = source
        self._name: Optional[str] = name
        self._parser = {}  # parsers by id
        self._result = {}  # results by id
        self._extractions = []

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        return self

    def add_parser(self, id, parser: Optional["Parser"]):
        self._parser[id] = parser

    def has_parser(self, parser_id):
        return parser_id in self._parser

    def discover_parsers(self, parser_registry):
        for pname, parser in parser_registry.items():
            if not self.has_parser(pname):
                if parser.match_extension(self.name()):
                    self.add_parser(pname, parser(self, pname))
                    continue
                if parser.match_magic(self.open()):
                    self.add_parser(pname, parser(self, pname))
                    continue

        return self

    def open(self):
        raise NotImplementedError()

    # Process all data at once.
    # TODO: Parse data lazily.
    # TODO: What is the interface that only parses what we need to?
    def scan_data(self):
        for parser in self._parser.values():
            parser.scan_data()
        return self

    # extraction = Extraction.from_xml("<job />")
    @classmethod
    def from_xml(cls, source):
        raise NotImplementedError("from_xml not implemented")

    # extraction.to_xml() -> "<job />"
    def to_xml(self) -> str:
        raise NotImplementedError("to_xml not implemented")


# Generic artifact that ties parsers to cursor-ed data.
class BytesExtraction(Extraction):
    def __init__(
        self,
        name: str = None,
        source: Optional["Extraction"] = None,
        reader: Reader = None,
    ):
        super().__init__(name, source)

        if (source is None and reader is None) or (source and reader):
            raise ValueError("Only one of source or data reader can be non-None.")
        if not source:
            # 'self' is the root Extraction.
            self._reader = reader.dup()
        if not reader:
            self._reader = source.open()

        # self._reader cursor is only used for dup() and tell()
        self._reader = reader

    def open(self):
        return self._reader.dup()

    def tell(self):
        return self._reader.tell()

    # extraction = Extraction.from_xml("<job />")
    @classmethod
    def from_xml(cls, source):
        from thirdparty.pparse._xml import XmlNode, XmlEntry
        xml = XmlNode.as_node(source)

        name = xml['name']

        # XmlNode stores instances for parent<->child relationships.
        if xml.get_parent().get_el().tag != "child_extractions":
            source = None
        else:
            print("IMPLEMENT PARENT")
            breakpoint()
            # Assuming this gets us to source
            source = xml.get_parent().get_parent()

        # ** Assuming extraction has datasource and datasource has type attribute.
        data_source = globals()[xml.datasource['type']].from_xml(xml.datasource)

        reader = Range(data_source.open(), data_source.length)

        extraction = cls(name=name, source=source, reader=reader)
        xml.set_obj_inst(extraction)

        # TODO: parsers
        # ! This gets nasty. We need another "registry" of parsers to indicate
        # ! what exists and what is allowed.
        import thirdparty.pparse.lazy.zip.Parser as LazyZipParser
        parser_registry = {
            "zip": LazyZipParser
        }
        for parser_xml in xml.parsers:
            extraction._parser[parser_xml['name']] = parser_registry["zip"].from_xml(parser_xml)
            if len(parser_xml.result) > 0:
                extraction._result[parser_xml['name']] = Node.from_xml(parser_xml.result.Node)
            breakpoint()

        # TODO: child_extractions

        breakpoint()

    # extraction.to_xml() -> "<job />"
    def to_xml(self) -> str:
        raise NotImplementedError("to_xml not implemented")


# class FolderExtraction(Extraction):
#     def __init__(self, name: str = None, source: Optional['Extraction'] = None, path=None):

#         super().__init__(name, source)

#         if (source is None and reader is None) or (source and reader):
#             raise ValueError("Only one of source or data reader can be non-None.")
#         if not source:
#             # 'self' is the root Extraction.
#             self._reader = reader.dup()
#         if not reader:
#             self._reader = source.open()

#         # self._reader cursor is only used for dup() and tell()
#         self._reader = reader


"""
    Parser Considerations:

    It is the parser's responsibility to be lazy. The framework will allow a parser to
    attempt to scan over the data within its scope. The parser can choose to do all of
    the parsing in this phase, or ramain willfully ignorant of the data until the user
    references the data.

    It is difficult to anticipate the types of references that all interfaces would
    require. Therefore its also the parser's responsibility to implement the lookup
    API for the data within its scope. Parsers must use the framework's children member
    to advertise data that it is not willing or able to parse (e.g. another file within
    a zip container).

    It may be possible to implement an 80% solution API for referencing data in a generic
    way. The idea is that all data should be representable in a graph and you'd string
    together references to create a generic path to access any given information in the
    graph. In the generic data graph we'd have nodes that have children nodes and attributes.
    An API might resemble:

    - Node.parents() -> [Node] -> Return array of parents (strong refs).
    - Node.children() -> [weakref(Node)] -> Return array of childen (weak refs).
    - Triggers parse/load
    - Node.attributes() -> {} - Return dictionary of attributes.
    - Triggers parse/load
    - Node.child(index=-1) -> Node - Return strong ref child.
    - Triggers parse/load
    - Node.as_{bytes,i64,u64,str}() - Cast raw data as type.
    - Triggers parse/load
    - Node.loaded() - Is the data loaded and parsed?
    - Node.range() - A range of data this node covers.
    - Note: There could be situations where a conceptual "Node" is a non-continguous
            set of ranges in the data. Joining non-continguous sections of data into
            a cohesive object is not the responsibility of the parser or framework.
            That responsibility should fall to a higher level framework or code base.
    - Note: There should be nothing preventing nodes from overlapping. Its is the parsers
            responsibility to manage that situation and be aware that readahead
            optimizations will break when moving backward in memory.

    If all the child references were weakref. As long as there is a strong reference to
    the child, its path will remain.

    All nodes should be either in a loaded state or unloaded state. In the loaded state
    they are fully cached and dereference-able. In the unloaded state, the node is only
    a cursor into the data to be parsed.

    Note: When processing a large JSON object or array, all of the data needs to be
    read and parsed to know where the end of the object is and all of its immediate
    children.

    When scanning a file or Artifact, parse entire file to tracking size of:
    - What are the sizes of strings and serialized arrays of primatives?
    - What is the memory footprint of the data structure up to leaf nodes?
"""


# Base Parser for Extraction parsers.
class Parser:
    
    def __init__(self, source: Extraction, id: str):
        if not isinstance(source, Extraction):
            raise TypeError("source must be an Extraction")

        # parser id
        # TODO: Shouldn't this be self known?
        self._id: str = id

        # parent source
        self._source = source

        # TODO: Store root node.
        # Current "Default" Node
        self.current = None

    def source(self):
        return self._source

    # This processes all data at once.
    # TODO: What is the interface that only parses what we need to?
    def scan_data(self):
        raise NotImplementedError()

    @staticmethod
    def match_extension(fname):
        return False

    @staticmethod
    def match_magic(cursor):
        return False


class Tensor:
    STTYPE_STRUCT = {
        "I8": "b",
        "U8": "B",
        "I16": "h",
        "U16": "H",
        "I32": "i",
        "U32": "I",
        "I64": "q",
        "U64": "Q",
        "F32": "f",
        "F64": "d",
    }

    STTYPE_SIZE = {
        "I8": 1,
        "U8": 1,
        "I16": 2,
        "U16": 2,
        "I32": 4,
        "U32": 4,
        "I64": 8,
        "U64": 8,
        "F32": 4,
        "F64": 8,
    }

    STTYPE_NP_MAP = {
        "F32": numpy.float32,
        "F64": numpy.float64,
        "F16": numpy.float16,
        # ! TypeError: data type 'bfloat16' not understood
        #'BF16': numpy.dtype("bfloat16"),
        "I8": numpy.int8,
        "I16": numpy.int16,
        "I32": numpy.int32,
        "I64": numpy.int64,
        "U8": numpy.uint8,
        "BOOL": numpy.bool_,
    }

    # Return (safetensors equivalent) type
    def get_type(self):
        raise NotImplementedError()

    # Return (safetensors equivalent) shape
    def get_shape(self):
        raise NotImplementedError()

    # Return raw data as extracted from source
    def get_data_bytes(self):
        raise NotImplementedError()

    # Return raw data as python array of dtype
    def as_array(self):
        raise NotImplementedError()

    # Return raw data as numpy array of dtype
    def as_numpy(self):
        raise NotImplementedError()
