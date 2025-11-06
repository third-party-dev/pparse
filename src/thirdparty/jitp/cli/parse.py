#!/usr/bin/env python3

def has_mmap():
    global mmap
    import sys
    try:
        import mmap
    except:
        return False

    try:
        with mmap.mmap(-1, 1) as m:
            m[0] = b"x"[0]
        return True
    except:
        return False
        
import os
from pprint import pprint

#PARSERS['json'] = JsonParser

PARSERS = {}

class EndOfDataException(Exception): pass
class UnsupportedFormatException(Exception): pass
class BufferFullException(Exception): pass


def hexdump(data, length=None):
    if isinstance(data, io.BytesIO):
        data = data.getvalue()

    if length is None:
        length = len(data)
    data = data[:length]

    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{byte:02x}' for byte in chunk)
        ascii_part = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        print(f'{i:08x}: {hex_part:<47}  {ascii_part}')


# Cursor manages offset. Data does not manage offset.
class Cursor():
    def __init__(self, data, offset=0):
        self._data = data
        self._offset = offset


    def dup(self):
        return self._data.open(self._offset)


    # Where in the Data are we
    def tell(self):
        return self._offset


    # Set cursor to specific location.
    def seek(self, offset):
        self._offset = offset
        self._data.seek(self)


    def skip(self, length):
        self._offset += length
        self._data.seek(self)


    # Read data ahead without progressing cursor.
    def peek(self, length):
        return self._data.peek(self, length)


    # Copy and progress data.
    def read(self, length, mode=None):
        data = self._data.read(self, length, mode=mode)
        self._offset += len(data)
        return data
        

# Data Considerations:
# - DiskData exists in its entirety on disk (even if truncated).
# - TapeData is constantly incoming and recorded (yes to Random Access).
#   - Need to re-mmap when data is appended.
# - StreamData is constantly incoming and only seen once (no to Random Access).

# StreamData may require entire stream to exist in memory, depending on parser
# references. A StreamData buffer can only deallocate data when all parsers
# have indicated they have no more need for the data range.


# Data manages mmap and fobj. Cursor does not manage mmap or fobj.
class Data():

    MODE_READ = 1
    MODE_MMAP = 2

    def __init__(self, path=None, mode=Data.MODE_READ):
        if not path or not os.path.exists(path):
            raise ValueError("path must be a string that points to a valid file path")

        # TODO: Only allow setting MODE_MMAP if has_mmap()

        self._path = path
        self._mode = mode

        # One descriptor to rule them all.
        self._fobj = open(path, "rb")

        # Mmap, if available.
        if has_mmap():
            self._mmap = mmap.mmap(self._fobj.fileno(), 0, access=mmap.ACCESS_READ)
            self._mem = memoryview(self._mmap)
            

    # Create a cursor, like a logical file descriptor.
    def open(self, offset=0):
        return Cursor(self, offset)


    # Read data ahead without progressing cursor.
    def peek(self, cursor, length):
        if mode == Data.MODE_READ:
            self._fobj.seek(os.SEEK_SET, cursor.tell())
            return self._fobj.read(length)

        if mode == Data.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off:off+length]


    # Progress cursor without reading (no copy).
    def seek(self, cursor) -> None:
        if mode == JitData.MODE_READ:
            self._fobj.seek(os.SEEK_SET, cursor.tell())

        # Noop for mmap.


    # Read the data.
    def read(self, cursor, length, mode=None):
        # TODO: Only allow setting MODE_MMAP if has_mmap()
        # Allow each read to optionally override mode.
        active_mode = self.mode
        if mode:
            active_mode = mode
    
        if active_mode == JitData.MODE_READ:
            self.seek(cursor)
            return self._fobj.read(length)

        if active_mode == JitData.MODE_MMAP and has_mmap():
            off = cursor.tell()
            return self._mem[off:off+length]


'''
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

'''

# Base Parser for Artifact parsers.
class Parser(dict):

    def __init__(self, artifact, id: str):
        if not isinstance(parent, 'Artifact'):
            raise TypeError("Parent must be an Artifact")
        
        # parser id
        self._id: str = id

        # parent artifact
        self._artifact = artifact

        # cursor to read data
        self._cursor = artifact.dup_cursor()

        # child artifacts
        self._meta: dict = { 'children': [] }
        self.children: list = self._meta['children']

        # Setup as dict for easy repr
        dict.__init__(self, meta=self._meta)


    # This processes all data at once.
    # TODO: What is the interface that only parses what we need to?   
    def process_data(self):
        raise NotImplementedError()
    

    @staticmethod
    def match_extension(fname):
        return False
    

    @staticmethod
    def match_magic(cursor):
        return False


# Generic artifact that ties parsers to cursor-ed data.
class Artifact(dict):
    def __init__(self, cursor, parser: Optional['Parser'] = None):
        self._parser: Optional['Parser'] = parser
        # This cursor is only used for dup() and tell()
        self._cursor = cursor

        self._meta = {
            'fname': None,
            'candidates': {},
        }

        # Candidate parsers.
        self.candidates: dict = self._meta['candidates']
        # Setup as dict for easy repr
        dict.__init__(self, meta=self._meta)
    

    def get_fname(self):
        return self._meta['fname']


    def set_fname(self, name):
        self._meta['fname'] = name
        return self

    
    def dup_cursor(self):
        self._cursor.dup()


    # This processes all data at once.
    # TODO: What is the interface that only parses what we need to?    
    def process_data(self):
        global PARSERS

        for (pname, parser) in PARSERS.items():
            if pname not in self.candidates:
                if parser.match_extension(self.get_fname()):
                    self.candidates[pname] = parser(self, pname)
                    continue
                if parser.match_magic(self.dup_cursor()):
                    self.candidates[pname] = parser(self, pname)
                    continue
            
        for (cname, candidate) in self.candidates.items():
            candidate.process_data()

        return self


# Data is independent of Artifact/Parser tree.
data = Data(path='test.json')

# Top Artifact has not parent parser.
root = Artifact(data.open()).set_fname('test.json').process_data()

# Dump output for examination.
print("Dumping root to output.txt")
with open("output.txt", "w") as fobj:
    pprint(root, stream=fobj, indent=2)
print("Dump complete.")
    

