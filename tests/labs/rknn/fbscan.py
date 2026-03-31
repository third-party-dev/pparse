#!/usr/bin/env python3

import struct
import sys
import hashlib
import json
from collections import OrderedDict
from pprint import pprint


def str_table_scan(buf):
    str_tbl = {}
    min_str_len = 3
    for off in range(0, len(buf), 4):
        #if off % 0x1000 == 0:
        #    print(f"{off} offsets processed, {len(str_tbl)} strings found.")

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


class FB_Vector():
    def __init__(self, field=None, abs_off=None):
        self.field = field
        self.abs_off = abs_off

        self.likely_tbls = False
        self.likely_strs = False

        self._tbls = None
        self._tbls_list = None
        self._strs = None
        self._strs_list = None
    
    def get_count(self):
        return struct.unpack_from("<I", self.field.tbl.buf, self.abs_off)[0]

    def _idx_off(self, idx):
        return 4 + (idx * 4)

    def deref_u32(self, idx):
        return struct.unpack_from("<I", self.field.tbl.buf, self.abs_off + self._idx_off(idx))[0]
    
    def deref_off(self, idx):
        return self.abs_off + self._idx_off(idx) + self.deref_u32(idx)

    # Common Pattern For "Normal" Vectors
    def always_decreasing(self) -> bool:
        last_val = 0xFFFFFFFF
        for idx in range(self.get_count()):
            val = self.deref_u32(idx)
            if val < last_val:
                last_val = val
            else:
                return False
        return True
    
    def all_tables(self, tbl_tbl) -> bool:
        tbls = {}
        tbls_list = []
        for idx in range(self.get_count()):
            tbl_off = self.deref_off(idx)
            if tbl_off not in tbl_tbl:
                return False
            tbls_list.append(tbl_off)
            tbls[tbl_off] = tbl_tbl[tbl_off]
        self._tbls = tbls
        self._tbls_list = tbls_list
        return True
    
    def all_strings(self, str_tbl) -> bool:
        strs = {}
        strs_list = []
        for idx in range(self.get_count()):
            str_off = self.deref_off(idx)
            if str_off not in str_tbl:
                return False
            strs_list.append(str_off)
            strs[str_off] = str_tbl[str_off]
        self._strs = strs
        self._strs_list = strs_list
        return True

    def dump(self, d=0, spacer="  "):
        print(f'{spacer*(d)}<FB_Vector abs_off="{self.abs_off:08x}" count="{self.get_count()}">')

        if self.likely_strs:
            print(f'{spacer*(d+1)}<asStrings>')
            for s in self._strs_list:
                print(f'{spacer*(d+2)}<String abs_off="{s:x}">{self._strs[s]}</String>')
            print(f'{spacer*(d+1)}</asStrings>')

        if self.likely_tbls:
            print(f'{spacer*(d+1)}<asTables>')
            for t in self._tbls_list:
                self._tbls[t].dump(d+2, spacer)
            print(f'{spacer*(d+1)}</asTables>')

        print(f'{spacer*(d)}</FB_Vector>')


class FB_Field():
    def __init__(self, tbl=None, abs_off=None, idx=None):
        # The table this field is associated with (think up).
        self.tbl = tbl
        self.idx = idx
        # This field as a table
        self._tbl = None
        # This field as a string
        self._str = None
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
        self.likely_vec_of_str = None

        self._vec = None

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
            self._str = self.deref_str()
            self.likely_str = True
        except:
            self._str = None
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
                # MAX_VECTOR_LEN = 0x800 # (2048)
                # val = self.deref_u32()
                # if val > 0 and val < MAX_VECTOR_LEN:
                #     self.likely_vec = True
                if self.deref_u32() == 0:
                    self.likely_vec = True
                    # We can't detect vector_of here.
                else:
                    vec = FB_Vector(self, self.as_offset())
                    if vec.always_decreasing():
                        self._vec = vec
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
        # ! fixme
        # lines = []
        # parts = []
        # parts.append(f"off {self.as_offset():08x}")
        # parts.append(f"as-u32 {self.cast_u32():08x}")
        # parts.append(\
        #     f'{"S" if self.likely_str else "-"}'\
        #     f'{"V" if self.likely_vec else "-"}'\
        #     f'{"N" if self.likely_value else "-"}'\
        #     f'{"T" if self.likely_tbl else "-"}'\
        #     f'{"!f" if self.unlikely_float else "--"}'\
        # )
        # if self.slot:
        #     parts.append(f"slot {''.join(f'\\x{b:02x}' for b in self.slot)}")
        # lines.append(' '.join(parts))
        
        # if self.likely_str:
        #     lines.append(f"  str: {self.deref_str()[:60]}")
        # if self.likely_vec:
        #     seen = ''.join(f'\\x{b:02x}' for b in self.deref_bytes(18)[4:])
        #     # # !fix me
        #     # if self._vec.likely_tbls:
        #     #     lines.append(f"  vec-len: {self.deref_u32()} tbl: {self.likely_vec_of_tbl:08x}")
        #     # else:
        #     #     lines.append(f"  vec-len: {self.deref_u32()} peek: {seen}")
        # if self.likely_tbl:
        #     lines.append(f"  tbl abs_off: {self.as_offset():08x}")
        # return '\n'.join(lines)
        return ''
    
    def dump(self, d=0, spacer="  "):
        v_flag = '--'
        if self.likely_vec:
            v_flag = 'V-'
            if self._vec and self._vec.likely_tbls:
                v_flag = 'Vt'
            if self._vec and self._vec.likely_strs:
                v_flag = 'Vs'
        flags = ''.join([
            f'{"S" if self.likely_str else "-"}',
            f'{"T" if self.likely_tbl else "-"}',
            f'{v_flag}',
        ])

        tbl_hdr = [f'{spacer*(d)}<FB_Field abs_off="{self.as_offset():08x}" idx="{self.idx}" flags="{flags}"']
        if self.likely_vec:
            tbl_hdr.append(f'vcnt="{self._vec.get_count()}"' if self._vec else f'vcnt="0"')
        tbl_hdr.append(">")
        print(' '.join(tbl_hdr))

        if self.likely_str:
            print(f'{spacer*(d+1)}<asString>{self._str}</asString>')
        if self.likely_tbl:
            #print(f'{spacer*(d+1)}<asTable>')
            self._tbl.dump(d+2, spacer)
            #print(f'{spacer*(d+1)}</asTable>')
        if self.likely_vec:
            if self._vec:
                self._vec.dump(d+1, spacer)
        if not self.likely_str and not self.likely_tbl and not self.likely_vec:
            print(f'{spacer*(d+1)}<asUint32 dec="{self.cast_u32()}" hex="0x{self.cast_u32():x}" />')
            print(f'{spacer*(d+1)}<asFloat f32="{self.cast_f32()}" f64="{self.cast_f64()}" />')
            print(f'{spacer*(d+1)}<asOffset addr="0x{self.as_offset():08x}" />')
            sample = ''.join(f'\\x{b:02x}' for b in self.slot)
            print(f"{spacer*(d+1)}<asU8Sample>{sample}</asU8Sample>")
            
        print(f'{spacer*(d)}</FB_Field>')


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
            field[idx] = FB_Field(tbl=self, abs_off=self.abs_off + self.vtbl.entry[idx], idx=idx)
        
        return field


    def make_sig(self):
        FLAG_LIKELY_STR = 1 << 0
        FLAG_LIKELY_TBL = 1 << 1
        FLAG_LIKELY_VEC = 1 << 2
        FLAG_LIKELY_TBLVEC = 1 << 3
        FLAG_LIKELY_STRVEC = 1 << 4

        field_meta = OrderedDict()
        field_meta['total'] = self.vtbl.cnt
        field_meta['fields'] = []

        for i in range(self.vtbl.cnt):
            flags = 0
            if i in self.field:
                field = self.field[i]
                flags |= FLAG_LIKELY_STR if field.likely_str else 0
                flags |= FLAG_LIKELY_TBL if field.likely_tbl else 0
                flags |= FLAG_LIKELY_VEC if field.likely_vec else 0
                if field._vec:
                    flags |= FLAG_LIKELY_TBLVEC if field._vec.likely_tbls else 0
                    flags |= FLAG_LIKELY_STRVEC if field._vec.likely_strs else 0
            field_meta['fields'].append(flags)
        
        sane_json = json.dumps(field_meta, indent=None, separators=(",", ":"))
        return hashlib.sha256(sane_json.encode("utf-8")).hexdigest()


    def __repr__(self):
        # lines = [f"FB_Table (abs_off {self.abs_off:08x})"]
        # lines.append("-"*78)
        # for idx in self.field:
        #     lines.append(f"{idx:02}: {self.field[idx]}")
        #     lines.append("- "*38)
        # return '\n'.join(lines)
        return f'<FB_Table abs_off="0x{self.abs_off:x}" set="{len(self.field)}" tot="{self.vtbl.cnt}" sig="{self.make_sig()[:4]}"/>'


    def dump(self, d=0, spacer="  "):
        print(f'{spacer*(d)}<FB_Table abs_off="{self.abs_off:08x}" set="{len(self.field)}" tot="{self.vtbl.cnt}" sig="{self.make_sig()[:4]}">')
        for idx in self.field:
            self.field[idx].dump(d+1)
        print(f'{spacer*(d)}</FB_Table>')


def fb_table_scan(buf):
    tbl_tbl = {}

    # For each absolute table offset (on a 4 byte alignment).
    for tbl_abs in range(0, len(buf), 4):
        #if tbl_abs % 0x1000 == 0:
        #    print(f"{tbl_abs} offsets processed, {len(tbl_tbl)} tables found.")

        try:
            # Generate the table and vtable objects.
            tbl = FB_Table(buf=buf, abs_off=tbl_abs)
        except Exception as e:
            #if not str(e).startswith('vtable') and not str(e).startswith('table'):
            #    print(e)
            continue

        tbl_tbl[tbl_abs] = tbl
    
    return tbl_tbl


def process_fbdata(buf):

    str_tbl = str_table_scan(buf)
    tbl_tbl = fb_table_scan(buf)
    typ_tbl = {}

    # Post process relationships after we know all tables
    for tbl in tbl_tbl.values():
        for field in tbl.field.values():
            if field.as_offset() in tbl_tbl:
                field._tbl = tbl_tbl[field.as_offset()]
                field.likely_tbl = True
            if field.likely_vec and field._vec:
                if field._vec.all_tables(tbl_tbl):
                    field._vec.likely_tbls = True
                    #field.likely_vec_of_tbl = True
                elif field._vec.all_strings(str_tbl):
                    field._vec.likely_strs = True
                    #field.likely_vec_of_str = True
        
        # Organize tables by signature
        sig = tbl.make_sig()
        if sig not in typ_tbl:
            typ_tbl[sig] = []
        typ_tbl[sig].append(tbl)

    return tbl_tbl, str_tbl, typ_tbl



with open(sys.argv[1], "rb") as f:
    buf = f.read()

tbl_tbl, str_tbl, typ_tbl = process_fbdata(buf)
tbl_tbl[0x88].dump()
#breakpoint()


'''
(SIMPLE) if vtable is all_ascending, we can guess field size
(COMPLEX) if table u32's are _mostly_ decending with outliers, the decending line are pointers, outliers are values.
'''