#!/usr/bin/env python3

import struct
import sys
from pprint import pprint

'''Idea:

- scan entire file for any strings length >= 3.
- its only a valid string if the preceding 4 bytes match the length of a valid string
- record the offset of the string length field
- scan all offsets as a offset from itself and match against any string entries
- build table and measure coverage of the file.

- Note: strings in vectors may not map
- Note: we may capture tensor descriptor tables via name.
  - Once table field known, need to discover field index via vtable discovery?
    - probably requires brute force walking from field backwards looking for pointer to start of field
    - if we walked to the start of the file, need to walk from the end of the field to end of the file.

'''

'''
0: ?
1: string
2: string
3: string
4: UNSET
5: UNSET
6: u32
7: string
8: string
9: string
10: ? value (or vector)
11: value
12: string
13: string
14: string (or vector)
15: ?
16: string
17: ?
18: ?
19: ?
20: ?
21: ?
'''

class Field():
    def __init__(self, buf, tbloff, index, reloff):
        self.buf = buf
        self.tbloff = tbloff
        self.index = index
        self.reloff = reloff
        self.absoff = self.tbloff + self.reloff
        self.value = None
        self.dst_as_u32 = None
        self.dst_str = None
        self.data = None

        if self.reloff != 0:
            self.value = struct.unpack_from("<I", self.buf, self.absoff)[0]
            self.data = self.buf[self.absoff + self.value:self.absoff + self.value+16]
            self.dst_as_u32 = struct.unpack_from("<I", self.data, 0)[0]
            try:
                self.dst_str = self.buf[self.absoff + self.value+4:self.absoff + self.value+4+self.dst_as_u32].decode('utf-8')
            except:
                pass
        else:
            self.value = "--UNSET--"
        
    def __repr__(self):
        if isinstance(self.value, str):
            return f"index {self.index} value {self.value}"

        lines = [f"{self.index}: abs {self.absoff:x} value {self.value:08x} ({self.value})"]

        if self.dst_str:
            lines.append(f"  str(0x{(self.absoff + self.value + 0x40):x}): {self.dst_str}")
        else:
            lines.append(f"  (0x{self.dst_as_u32:08x}) [data {self.data}]")

        return '\n'.join(lines)

def read_table(buffer: bytes, table_offset: int):
    vtable_offset_rel = struct.unpack_from("<i", buffer, table_offset)[0]
    vtable_offset = table_offset - vtable_offset_rel

    # Read vtable header
    vtable_len, object_size = struct.unpack_from("<HH", buffer, vtable_offset)
    num_fields = (vtable_len - 4) // 2
    # vtable_len - size of vtable in bytes (vtable_len[u16] + object_size[u16] + fields)
    # object_size - size of the table instance (vtable offset + fields)
    print(f"vtable_len 0x{vtable_len:x} ({vtable_len}) table_size 0x{object_size:x} ({object_size}) num_fields {num_fields}")
    

    fields = {}
    for i in range(num_fields):
        reloff = struct.unpack_from("<H", buffer, vtable_offset + 4 + i*2)[0]
        fields[i] = Field(buf, table_offset, i, reloff)

    return fields

# Example usage:
with open(sys.argv[1], "rb") as f:
    f.seek(0x40)
    buf = f.read()

table_start = 0x48  # e.g., offset in buffer
fields = read_table(buf, table_start)
for idx in fields:
    print(fields[idx])
breakpoint()
