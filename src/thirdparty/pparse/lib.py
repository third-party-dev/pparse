#!/usr/bin/env python3

import io
import logging
import os
import sys
import stat
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
    def read(self, length, mode=None):
        length = self._adjust_length(length)
        return self._cursor.read(length, mode=mode)


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
        data = self._data.read(self, length, mode=mode)
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

    def load(self, recursive=False):
        '''
            RULE: load() should handle the recursive behavior, not the parser state.

            json is weird because you have to recurse every time. Since I implemented
            JSON first, I believe its driving some of the anti-patterns in pparse. If
            we want to save on memory for JSON, we could theoretically parse and allocate
            nodes and as we complete branches of a depth first parse we deallocated.
            I naturally want to do this for recursive=False, but since recursive=False
            is default, it makes it feel like unnecessary thrashing of the CPU. 
            
            PLAN: After we get an initial parse of JSON, we can re-eval a callback param
            for this function that is responsible for determining the deallocation policy.
        '''

        # Maybe a naughty pattern, but for now we retry until 
        # Retry until state returns UnsupportedFormatException or EndOfNodeException
        # ! When EndOfDataException raised, we need a way to retry. For now, fail.
        try:
            # RULE: AGAIN is a Parser return. Not a Node is complete status!
            res = AGAIN
            while res == AGAIN:
                
                #breakpoint()
                res = self.ctx().state().parse_data(self)

                # if res == COMPLETE:
                #     breakpoint()
                #     #return self.ctx().parent()

                '''
                    - The parser is responsible for populating _decendents.
                    - Whenever Node.load() sees elements in _decendents, it immediately
                    calls the load() method on those elements.
                '''
                while self.ctx()._descendants:
                    #breakpoint()self
                    # ! Here, we're making Node responsible for _descendants cleanup.
                    child = self.ctx()._descendants.pop()

                    # TODO: use try/except to push forward, even on failure.
                    # TODO: we should be able to track failures for retry later.
                    child.load(recursive=recursive)

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

        #breakpoint()
        # TODO: if recursive, for node in value: node.ctx().state().parse_data(node)

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
    MODE_READ = 1
    MODE_MMAP = 2

    def _load_length(self):
        raise NotImplementedError()

    def open(self, offset=0):
        raise NotImplementedError()

    def peek(self, cursor, length, mode=None):
        raise NotImplementedError()

    def seek(self, cursor):
        raise NotImplementedError()

    def read(self, cursor, length, mode=None):
        raise NotImplementedError()


# Data manages mmap and fobj. Cursor does not manage mmap or fobj.
class FileData(Data):
    MODE_READ = 1
    MODE_MMAP = 2

    def __init__(self, path=None, mode=None):
        if not path or not os.path.exists(path):
            raise ValueError("path must be a string that points to a valid file path")
        self._path = path

        if mode is None:
            self._mode = Data.MODE_READ
        else:
            self._mode = mode

        # TODO: Only allow setting MODE_MMAP if has_mmap()

        self.length = None
        self._fobj = open(path, "rb")
        self._load_length()

        # Mmap, if available.
        if has_mmap():
            self._mmap = mmap.mmap(self._fobj.fileno(), 0, access=mmap.ACCESS_READ)
            self._mem = memoryview(self._mmap)

    def _load_length(self):
        # TODO: This size is only relevant if the size doesn't change.
        fd = self._fobj.fileno()
        st = os.fstat(fd)

        if stat.S_ISREG(st.st_mode):
            self.length = st.st_size

    def mode(self):
        return self._mode

    # Create a cursor, like a logical file descriptor.
    def open(self, offset=0):
        return Cursor(self, offset)

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length, mode=None):
        # TODO: Only allow setting MODE_MMAP if has_mmap()
        # Allow each read to optionally override mode.
        active_mode = self.mode()
        if mode:
            active_mode = mode

        if active_mode == Data.MODE_READ:
            self._fobj.seek(cursor.tell(), os.SEEK_SET)
            return self._fobj.read(length)

        if active_mode == Data.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off : off + length]

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        if self.mode() == Data.MODE_READ:
            self._fobj.seek(cursor.tell(), os.SEEK_SET)
        # Noop for mmap.
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length, mode=None):
        # TODO: Only allow setting MODE_MMAP if has_mmap()
        # Allow each read to optionally override mode.
        active_mode = self.mode()
        if mode:
            active_mode = mode

        if active_mode == Data.MODE_READ:
            self.seek(cursor)
            return self._fobj.read(length)

        if active_mode == Data.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off : off + length]


# When working with data that is already (reasonably) in memory, we may want to use it as a
# data source. Having that use case in its own class permits us to handle that without extra
# conditions. Mostly the same as FileData, but understood to be in memory.
#
# Real World Use Case: File-format is a ZIP and the header is a file in the ZIP.
#
class BytesIoData(Data):
    def __init__(self, bytes_io: io.BytesIO = None, mode=None):
        if not bytes_io or not isinstance(bytes_io, io.BytesIO):
            raise ValueError("bytes_io must be io.BytesIO and not be None")

        # TODO: Validate mode value.
        if mode is None or mode == Data.MODE_READ:
            self._mode = Data.MODE_READ
        elif mode == Data.MODE_MMAP:
            self._mode = DAta.MODE_MMAP
        else:
            raise ValueError("mode must be MODE_READ or MODE_MMAP")

        self._bytes_io = bytes_io
        self._mem = bytes_io.getbuffer()

        self.length = None
        self._load_length()

    def _load_length(self):
        if hasattr(self._bytes_io, "getbuffer"):
            self.length = len(self._mem)
            return
        raise Exception("Expected getbuffer(). Did you forget to use FileData?")

    def mode(self):
        return self._mode

    # Create a cursor, like a logical file descriptor.
    def open(self, offset=0):
        return Cursor(self, offset)

    # Read data ahead without progressing cursor.
    def peek(self, cursor, length, mode=None):
        # Allow each read to optionally override mode.
        active_mode = self.mode()
        if mode:
            active_mode = mode

        if active_mode == Data.MODE_READ:
            self._bytes_io.seek(cursor.tell(), os.SEEK_SET)
            return self._bytes_io.read(length)

        if active_mode == Data.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off : off + length]

    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        if self.mode() == Data.MODE_READ:
            self._bytes_io.seek(cursor.tell(), os.SEEK_SET)
        # Noop for mmap.
        return cursor.tell()

    # Read the data.
    def read(self, cursor, length, mode=None):
        # TODO: Only allow setting MODE_MMAP if has_mmap()
        # Allow each read to optionally override mode.
        active_mode = self.mode()
        if mode:
            active_mode = mode

        if active_mode == Data.MODE_READ:
            self.seek(cursor)
            return self._bytes_io.read(length)

        if active_mode == Data.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off : off + length]


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
