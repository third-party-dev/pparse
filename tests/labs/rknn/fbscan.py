#!/usr/bin/env python3

import struct
import sys
from pprint import pprint

'''
Next steps:

I've now determined a few techniques that can be used to flesh out an understanding
of a flatbuffers file without a schema. Additionally, I've fleshed out a few nuggets
about the rknn file format, namely the header, and beginning of flatbuffers plus
the table that defines the start of each section of the file (outside of the
flatbuffers stream).

With that knowledge, I am thinking I need to take a step back and work on my pparse
implementation of flatbuffers. In general, I'd like to have a workflow whereby I can
compile a flatbuffers schema into JSON. The pparse flatbuffers would then have the
ability to parse the parts of the schema it can identify (deterministically) and perhaps
also be hinted to do unlinked (i.e. dynamically discovered) parts.

Until we base the parsing on a schema, it gets very ugly very quit with regards to
boiler plate code or code that locks into a specific format for simple things like
"get the u64 from this table in this vector". `import flatbuffers` is utterly useless
and amounts to a wrapper for `import struct` without a schema and assumption that
you aren't doing partial parsing!
'''



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

def str_table_scan(buf):
    str_tbl = {}
    min_str_len = 3
    for off in range(0, len(buf), 4):
        if off % 0x1000 == 0:
            print(f"{off} offsets processed, {len(str_tbl)} strings found.")

        try:
            pot_len = struct.unpack_from("<I", buf, off)[0]
        except:
            continue

        if pot_len > (0x1000 * 256) or pot_len == 0:
            continue

        try:
            pot = buf[off+4:off+4+pot_len].decode('ascii')
        except:
            continue

        if len(pot) < 3:
            continue

        bad_chars = set(\
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'\
            '\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'\
        )
        if bad_chars.intersection(pot):
            continue

        str_tbl[off] = pot
    return str_tbl

class FB_Field():
    def __init__(self, tbl=None, abs_off=None):
        # The table this field is associated with.
        self.tbl = tbl
        # Offset of field from start of buffer.
        self.abs_off = abs_off

        # Raw field value before cast or deref.
        # Note: We want to always grab 8 bytes for the slot, but if we're up
        #       against the end of the buffer, we must only grab whats left.
        self.slot = self._read_slot()
        
        # Record that this field is a valid string.
        self.likely_str = False
        self.likely_value = False
        self.unlikely_float = False
        self.likely_vec = False
        self.likely_tbl = False
        # When set, is the abs_off of first elem of vector
        self.likely_vec_of_tbl = None

        self._do_heuristics()

    def _read_slot(self):
        slot_len = 8
        if self.abs_off + 8 >= len(buf):
            slot_len = len(buf) - abs_off
        return self.tbl.buf[self.abs_off:self.abs_off+slot_len]

    def _do_heuristics(self):
        if self.cast_u32() < self.tbl.abs_off:
            self.likely_value = True
        
        try:
            self.deref_str()
            self.likely_str = True
        except:
            pass

        # TODO: We can try to detect float:
        # TODO: - ((u32 >> 23) & 0xFF) == 0xFF -> NaN/Inf
        # TODO: - range check: abs(f) < 1e10 and abs(f) > 1e-38
        # TODO: - adjacent similarity via array of range checks

        try:
            if int(self.slot[3]) & 0x7F == 0x7F:
                self.unlikely_float = True
        except:
            pass

        # TODO: We can try to detect:
        # TODO: - vectors of strings - maybe assisted with a whole buffer string scan?
        # TODO: - vectors of tables - maybe assisted with a whole buffer table scan?
        # TODO: - vectors of scalars - we'd guess based on buffer mask

        if not self.likely_str:
            try:
                MAX_VECTOR_LEN = 0x800 # (2048)
                val = self.deref_u32()
                if val > 0 and val < MAX_VECTOR_LEN:
                    self.likely_vec = True
            except:
                pass


    def cast_bool(self):
        return struct.unpack_from("<?", self.slot, 0)[0]

    def cast_i8(self):
        return struct.unpack_from("<b", self.slot, 0)[0]
    
    def cast_u8(self):
        return struct.unpack_from("<B", self.slot, 0)[0]
    
    def cast_i16(self):
        return struct.unpack_from("<h", self.slot, 0)[0]
    
    def cast_u16(self):
        return struct.unpack_from("<H", self.slot, 0)[0]
    
    def cast_i32(self):
        return struct.unpack_from("<i", self.slot, 0)[0]
    
    def cast_u32(self):
        return struct.unpack_from("<I", self.slot, 0)[0]
    
    def cast_i64(self):
        return struct.unpack_from("<q", self.slot, 0)[0]

    def cast_u64(self):
        return struct.unpack_from("<Q", self.slot, 0)[0]
    
    def cast_f32(self):
        return struct.unpack_from("<f", self.slot, 0)[0]
    
    def cast_f64(self):
        return struct.unpack_from("<d", self.slot, 0)[0]

    # cast field value as absolute offset
    def as_offset(self):
        return self.cast_u32() + self.abs_off

    def deref_u32(self):
        # Note: For vector length extraction.
        return struct.unpack_from("<I", self.tbl.buf, self.as_offset())[0]

    def deref_bytes(self, byte_cnt):
        val_addr = self.as_offset()
        return self.tbl.buf[val_addr:val_addr+byte_cnt]

    def deref_str(self):
        str_len_addr = self.abs_off + self.cast_u32()
        str_len = struct.unpack_from("<I", self.tbl.buf, str_len_addr)[0]
        if str_len == 0:
            raise ValueError('string to short')
        str_addr = str_len_addr + 4

        str_val = self.tbl.buf[str_addr:str_addr+str_len].decode('ascii')
        bad_chars = set(\
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'\
            '\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'\
        )
        if bad_chars.intersection(str_val):
            raise ValueError('string has bad characters')

        return str_val

    '''
        Can we use a flatbuffers schema to only grab the bits we know?

        table SectionOffset {
            value:uint64;
        }

        table Root {
            sections:[SectionOffset] (id: 20);
        }

        root_type Root;
    '''

    # tbl_tbl[0x88].field[20].dump_u32_vector_offs()
    def dump_u32_vector_offs(self):
        vec_cnt = self.deref_u32()
        vec_bytes = self.deref_bytes(4+(vec_cnt * 4))[4:]
        vec_off = self.as_offset()

        for i in range(vec_cnt):
            vec_en_addr_off = vec_off + 4 + (i * 4)
            vec_en_bytes_off = i * 4
            vec_en = struct.unpack("<I", vec_bytes[vec_en_bytes_off:vec_en_bytes_off+4])[0]
            vec_en_addr_abs = vec_en_addr_off + vec_en
            print(f"vec[{i}] = {vec_en_addr_abs:08x}    ({vec_en_addr_off:08x} + {vec_en:08x})")

            # The above vec entry is a table
            offset_table_abs = vec_en_addr_abs
            # Cheat, skip table size and grab u64
            val = struct.unpack("<Q", self.tbl.buf[offset_table_abs+4:offset_table_abs+12])[0]
            real_offset = (offset_table_abs + 4) + val
            print(f"real_offset: {real_offset:08x}   ({offset_table_abs:08x} + 4 + {val:08x})")


    # TODO: enums?, structs?, tables?, unions? fixed-length arrays (struct only)?

    # TODO: Consider a generator for vector
    # TODO: - vectors can be scalars, enums, structs, tables, strings, and unions

    def __repr__(self):
        lines = []
        parts = []
        parts.append(f"off {self.as_offset():08x}")
        parts.append(f"as-u32 {self.cast_u32():08x}")
        parts.append(\
            f'{"S" if self.likely_str else "-"}'\
            f'{"V" if self.likely_vec else "-"}'\
            f'{"N" if self.likely_value else "-"}'\
            f'{"T" if self.likely_tbl else "-"}'\
            f'{"!f" if self.unlikely_float else "--"}'\
        )
        if self.slot:
            parts.append(f"slot {''.join(f'\\x{b:02x}' for b in self.slot)}")
        lines.append(' '.join(parts))
        
        if self.likely_str:
            lines.append(f"  str: {self.deref_str()[:60]}")
        if self.likely_vec:
            seen = ''.join(f'\\x{b:02x}' for b in self.deref_bytes(18)[4:])
            if self.likely_vec_of_tbl:
                lines.append(f"  vec-len: {self.deref_u32()} tbl: {self.likely_vec_of_tbl:08x}")
            else:
                lines.append(f"  vec-len: {self.deref_u32()} peek: {seen}")
        if self.likely_tbl:
            lines.append(f"  tbl abs_off: {self.as_offset():08x}")
        return '\n'.join(lines)


class FB_VTable():
    def __init__(self, tbl=None, abs_off=None, vtbl_sz=None, tbl_sz=None, cnt=None):
        # Reference to associated table
        self.tbl = tbl
        # Absolute buffer offset of vtable
        self.abs_off = abs_off
        # Size of vtable in bytes
        self.vtbl_sz = vtbl_sz
        # Size of table in bytes
        self.tbl_sz = tbl_sz
        # Number of fields in vtable
        self.cnt = cnt
        # Each offset by index
        self.entry = self._read_field_offsets()


    def _read_field_offsets(self):
        entry = []
        # Note: We expect exceptions from struct.unpack_from.
        tbl_end = self.tbl.abs_off + self.tbl_sz
        for idx in range(self.cnt):
            # Every field in vtable is 2 bytes.
            U16_SZ = 2
            entry_off = self.abs_off + U16_SZ + U16_SZ + (idx * U16_SZ)
            entry_val = struct.unpack_from("<H", self.tbl.buf, entry_off)[0]
            if self.tbl.abs_off + entry_val >= tbl_end:
                raise ValueError("vtable entry goes past end of table")
            entry.append(entry_val)
        return entry


class FB_Table():
    def __init__(self, buf=None, abs_off=None):
        # The buffer this table is associated with.abs
        self.buf = buf
        # The absolute table offset
        self.abs_off = abs_off
        # Attempt to parse vtable from buffer
        self.vtbl = self._try_vtable_read()
        # Field dictionary
        self.field = self._read_fields()


    def _try_vtable_read(self):
        # Try to unpack the i32 vtable offset from the table offset
        try:
            vtbl_off = struct.unpack_from("<I", self.buf, self.abs_off)[0]
        except:
            raise

        # Calculate the absolute vtable address
        vtbl_abs = self.abs_off - vtbl_off
        if vtbl_abs < 0 or vtbl_abs >= len(buf):
            # Vtable outside of buffer bounds is bad.
            raise ValueError("vtable offset out of buffer bounds")

        # Try to unpack the u16 vtbl size and u16 table size.
        try:
            vtbl_sz = struct.unpack_from("<H", buf, vtbl_abs)[0]
            tbl_sz = struct.unpack_from("<H", buf, vtbl_abs+2)[0]
        except:
            raise

        # vtable size should always even and >= 4 bytes
        if vtbl_sz % 2 != 0 or vtbl_sz < 4:
            # note: a vtable is empty if a table has zero fields
            raise ValueError("vtable size to small or vtable size not even")

        # The vtbl size and tbl size must always be in buffer bounds
        # TODO: We could be more forgiving for truncation cases.
        if self.abs_off + tbl_sz >= len(buf) or vtbl_abs + vtbl_sz >= len(buf):
            #tables and vtables can not go past end of file
            raise ValueError("table or vtable size exceed buffer bounds")

        vtbl_cnt = (vtbl_sz - 4) // 2
        # assuming all fields are only 1 byte, does count exceed tbl size
        if vtbl_cnt > (tbl_sz - 4):
            raise ValueError("vtable count (worse case) exceeds table size")

        return FB_VTable(tbl=self, abs_off=vtbl_abs, vtbl_sz=vtbl_sz, tbl_sz=tbl_sz, cnt=vtbl_cnt)


    def _read_fields(self):

        field = {}

        for idx in range(self.vtbl.cnt):
            if self.vtbl.entry[idx] == 0:
                # This field is empty
                continue

            field_abs_off = self.abs_off + self.vtbl.entry[idx]
            field[idx] = FB_Field(tbl=self, abs_off=self.abs_off + self.vtbl.entry[idx])
        
        return field


    def __repr__(self):
        lines = [f"FB_Table (abs_off {self.abs_off:08x})"]
        lines.append("-"*78)
        for idx in self.field:
            lines.append(f"{idx:02}: {self.field[idx]}")
            lines.append("- "*38)
        return '\n'.join(lines)

def fb_table_scan(buf):
    tbl_tbl = {}

    # For each absolute table offset (on a 4 byte alignment).
    for tbl_abs in range(0, len(buf), 4):
        if tbl_abs % 0x1000 == 0:
            print(f"{tbl_abs} offsets processed, {len(tbl_tbl)} tables found.")

        try:
            # Generate the table and vtable objects.
            tbl = FB_Table(buf=buf, abs_off=tbl_abs)
        except Exception as e:
            #if not str(e).startswith('vtable') and not str(e).startswith('table'):
            #    print(e)
            continue

        tbl_tbl[tbl_abs] = tbl
    
    return tbl_tbl


# Example usage:
with open(sys.argv[1], "rb") as f:
    buf = f.read()

#str_tbl = str_table_scan(buf)
tbl_tbl = fb_table_scan(buf)


# Scan table fields for fields that point to existing tables and mark likely table.
for tbl_idx in tbl_tbl:
    tbl = tbl_tbl[tbl_idx]
    for idx in tbl.field:
        if tbl.field[idx].as_offset() in tbl_tbl:
            tbl.field[idx].likely_tbl = True

# Scan all "likely vectors" and check first "offset" if its a valid table.
for tbl in tbl_tbl.values():
    for field in tbl.field.values():
        if field.likely_vec:
            v_elem_ref_abs_off = field.as_offset() + 4
            v_elem_val_rel_off = struct.unpack("<I", field.deref_bytes(8)[4:])[0]
            v_elem_val_abs_off = v_elem_ref_abs_off + v_elem_val_rel_off
            if v_elem_val_abs_off in tbl_tbl:
                field.likely_vec_of_tbl = v_elem_val_abs_off


# # Print all tables with a field that is likely_str
# for tbl_idx in tbl_tbl:
#     tbl = tbl_tbl[tbl_idx]
#     for idx in tbl.field:
#         if tbl.field[idx].likely_tbl:
#             print(tbl)
#             break


# # Print all tables with a field that is likely_str
# for tbl_idx in tbl_tbl:
#     has_str = False
#     tbl = tbl_tbl[tbl_idx]
#     for idx in tbl.field:
#         if tbl.field[idx].likely_str:
#             print(tbl)
#             break





# Scan for highest flatbuffers tbl offset
highest_tbl_off = 0
for tbl_off in tbl_tbl:
    if tbl_off > highest_tbl_off:
        highest_tbl_off = tbl_off
print(f"Highest tbl offset: {highest_tbl_off}")

# Scan for highest flatbuffers field offset
highest_field_off = 0
for tbl in tbl_tbl.values():
    for field in tbl.field.values():
        if field.likely_str:
            if field.as_offset() > highest_field_off:
                highest_field_off = field.as_offset()
print(f"Highest field offset: {highest_field_off}")

# Print root table
print(tbl_tbl[0x88])

# # Print all tables
# for tbl in tbl_tbl.values():
#     print(tbl)



breakpoint()



'''
assume every offset is a table with an offset to vtable, if the vtable 
'''