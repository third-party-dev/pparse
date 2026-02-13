#!/usr/bin/env python3

import logging
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeTable, NodeVector, NodeVTable

# Example flatbuffer of yolo
"""
    0: 1c 00 00 00 <- root table offset (28)
    54 46 4c 33 <- magic bytes (TFL3)
    VTABLE:
    14 00 <- vtable size
    20 00 <- table size
    FIELD_OFFSETS (from start of table):
        1c 00 version (idx: 0, 1ch+h1c=38h)
        18 00 operator_codes (idx: 1, 1ch+18h=34h)
        14 00 subgraphs (idx: 2, 1ch+14h=30h)
        10 00 description (idx: 3, 1ch+10h=2ch)
        0c 00 buffers (idx: 4, 1ch+0ch=28h)
        00 00 (absent)
        08 00 metadata (idx: 6, 1ch+08h=24h)
        04 00 signature_defs (idx: 7, 1ch+0x4h=20h)

    TABLE (0x1c):
    14 00 00 00 <- (i32)vtable_off (bytes before this table/offset)
    20:
    1c 00 00 00 +20=3Ch signature_defs (vec<Obj>)
    1c 00 00 00 +24=40h metadata (vec<Obj>)
    6c 00 00 00 +28=94h buffers (vec<Obj>)
    70 2c 31 02 +2c=2312C9Ch description (String)
    30:
    80 2c 31 02 +30=2312CB0h subgraphs (vec<Obj>)
    94 ff 31 02 +34=231FFC8h operator_codes (vec<Obj>)

    TABLE VALUES (38h):
    VERSION
    03 00 00 00 version (u32)
    SIG_DEFS (0x3c):
    00 00 00 00 cnt=0?
    METADATA (0x40):
    02 00 00 00 cnt=2?
    2c 00 00 00 +44h=70h metadata table offset
    04 00 00 00 +48h=4Ch metadata table offset

    ---
    METADATA vtable (0x023132b8): 
        08 00 vtable_size
        0c 00 table_size
        08 00 name (idx: 0)
        04 00 buffer (idx: 1)
    ---

    METADATA TABLE (4Ch):
        94 cd ce fd vtable (0x4Ch-(-36778604) => addr: 023132B8h)
        c2 01 00 00  450d = buffer (UInt)
        04 00 00 00  +54h=58h name (offset)
    58h:
        13 00 00 00  19d (string length)
    5ch:
        43 4f 4e 56 45 52 53 49 4f 4e 5f 4d 45 54 41 44 41 54 41 00 ("CONVERSION_METADATA" len: 19+1)

    METADATA TABLE (70h):
        b8 cd ce fd
        c1 01 00 00 449d
        04 00 00 00
        13 00 00 00 19d
    80h:
        6d 69 6e 5f 72 75 6e 74 69 6d 65 5f 76 65 72 73 69 6f 6e 00 ()"min_runtime_version" len: 19+1)


    BUFFERS (94h):
    c3 01 00 00 cnt 451d
    98h: 00 2c 31 02 [0]
    9ch: f8 2b 31 02 [1]
    000000a0: d8 2b 31 02 88 2a 31 02 78 28 31 02 68 26 31 02  .+1..*1.x(1.h&1.
    ...
    00000790: ac 00 00 00 a4 00 00 00 9c 00 00 00 
    79Ch:
    7c 00 00 00 +79Ch=818h  buffers[449]

    7a0:
    04 00 00 00 +7A0h=7A4h  buffers[450]
    ^^^ END OF BUFFERS ARRAY

    7A4h:
    92 a8 ce fd --- vtable: 06 00 vtable_size 08 00 table_size 04 00 data (vec<UByte>)
    7A8h:
    04 00 00 00 data offset
    7ACh:
    68 00 00 00 data length (104d)
    7B0: 10 00 00 00 00 00 00 00 08 00 0e 00 08 00 04 00
    7c0: 08 00 00 00 14 00 00 00 2c 00 00 00 00 00 0a 00
    7d0: 0c 00 08 00 00 00 07 00 0a 00 00 00 00 00 00 01
    7e0: 04 00 00 00 00 00 00 00 0c 00 18 00 14 00 10 00
    7f0: 0c 00 04 00 0c 00 00 00 3f fb 44 11 fb 3d 73 3c
    800: 03 00 00 00 02 00 00 00 04 00 00 00 06 00 00 00
    810: 32 2e 31 39 2e 30 00 00

    818h: 
    06 a9 ce fd vtable_offset
    04 00 00 00 data offset

    820h:
    10 00 00 00 length
    32 2e 33 2e 30 00 00 00 00 00 00 00 00 00 00 00 

    834h: .... and on it goes
    c4 07 ce fd c8 07 ce fd cc 07 ce fd
    00000840: d0 07 ce fd d4 07 ce fd d8 07 ce fd dc 07 ce fd  ................
    00000850: e0 07 ce fd e4 07 ce fd e8 07 ce fd ec 07 ce fd  ................
    00000860: f0 07 ce fd f4 07 ce fd f8 07 ce fd fc 07 ce fd  ................
    00000870: 00 08 ce fd 04 08 ce fd 08 08 ce fd 0c 08 ce fd  ................
    00000880: 10 08 ce fd 14 08 ce fd 18 08 ce fd 1c 08 ce fd  ................
    00000890: 20 08 ce fd 24 08 ce fd 28 08 ce fd 2c 08 ce fd   ...$...(...,...
    000008a0: 30 08 ce fd 34 08 ce fd 38 08 ce fd 3c 08 ce fd  0...4...8...<...
    000008b0: 40 08 ce fd 44 08 ce fd 48 08 ce fd 4c 08 ce fd  @...D...H...L...
    000008c0: 50 08 ce fd 54 08 ce fd 58 08 ce fd 5c 08 ce fd  P...T...X...\...
    000008d0: 60 08 ce fd 64 08 ce fd 68 08 ce fd 6c 08 ce fd  `...d...h...l...
    000008e0: 70 08 ce fd 74 08 ce fd 78 08 ce fd 7c 08 ce fd  p...t...x...|...
"""

class FlatbuffersParsingState(object):
    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        raise NotImplementedError()

'''
Consider a table's offset as the table's vtable offset since the vtable is always
the first entry in the table. Then the state machine can sequentially parse the
vTable and then parse the table.

- FlatbuffersParsingVTable
- FlatbuffersParsingUnion
- FlatbuffersParsingTable
- FlatbuffersParsingVector
- FlatbuffersParsingScalar

In practice, we probably need to create the NodeTable as part of the NodeVTable,
process the NodeVTable data and then switch to a state to finish the NodeTable
that assumes the Node already exists.
'''

# class FlatbuffersParsingUnion(FlatbuffersParsingState):

#     def parse_data(self, parser: "Parser", ctx: "NodeContext"):


class FlatbuffersParsingTable(FlatbuffersParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        # Assuming ctx.tell() is at beginning of table.
        table = parser.current
        ctx.seek(table.abs_offset())

        # Try parsing vtable if not done.
        if table.vtable is None:
            # Get the vtable offset
            vtable_offset = parser.peek_i32(ctx)
            vtable_pos = table.abs_offset() - vtable_offset

            # Get the vTable values
            ctx.seek(vtable_pos)
            vtable = NodeVTable(table, ctx.reader(), vtable_pos, table.type_desc())
            vtable.vtable_size = parser.read_u16(ctx)
            vtable.table_size = parser.read_u16(ctx)
            vtable.field_offsets = []
            for i in range(4, vtable.vtable_size, 2):
                ctx.seek(vtable_pos + i)
                vtable.field_offsets.append(parser.peek_u16(ctx))
            
            # Finalize it.
            table.vtable = vtable
            return

        # Try initializing loop ctx members
        if not hasattr(ctx, "fields_desc"):
            table_name = table.type_desc()['name']
            ctx.fields_desc = parser.schema.objects[table_name].get('fields', [])
            ctx.field_idx = 0
            return

        while ctx.field_idx < len(ctx.fields_desc):

            ctx.field = ctx.fields_desc[ctx.field_idx]

            field_name = ctx.field['name']
            field_type = ctx.field['type']
            
            # Get the field ID (which determines position in vtable)
            # Fields are indexed by their 'id' if present, otherwise by order
            field_id = ctx.field.get('id', 0)

            # vtable entries correspond to field IDs
            # The vtable has entries for field 0, 1, 2, etc.
            if field_id >= len(table.vtable.field_offsets):
                # Field not present (using default value)
                ctx.field_idx += 1
                continue

            field_offset_in_table = table.vtable.field_offsets[field_id]
            if field_offset_in_table == 0:
                # Field not present in this instance
                ctx.field_idx += 1
                continue

            field_pos = table.abs_offset() + field_offset_in_table
            base_type = field_type.get('base_type')

            # Scalars are inplace, do those first.
            if base_type in parser.schema.TYPE_SIZES:
                # Scalar value stored inline
                ctx.seek(field_pos)
                table.value[field_name] = parser.read_scalar(ctx, base_type)
                ctx.field_idx += 1
                continue

            # Strings are nice an simple.
            if base_type == 'String':
                # Seek to string offset
                ctx.seek(field_pos)
                ctx.seek(field_pos + parser.peek_u32(ctx))
                # TODO: Do we create a NodeString? Pythonic str for now.
                table.value[field_name] = parser.read_string(ctx)
                ctx.field_idx += 1
                continue

            # Vectors are common and require a new node.
            if base_type == 'Vector':
                # Seek to vector offset
                ctx.seek(field_pos)
                vector_pos = field_pos + parser.peek_u32(ctx)

                table.value[field_name] = NodeVector(ctx.node(), ctx.reader(), vector_pos, field_type)
                parser.current = table.value[field_name]
                parser.current.ctx()._next_state(FlatbuffersParsingVector)
                ctx.field_idx += 1
                return

            if base_type == 'Union':
                # Skip and let the UType base_type drive both Union and UType parsing.
                ctx.field_idx += 1
                continue

            if base_type == 'UType':
                
                # Get the UType index
                utype_idx = field_type.get('index', 0)

                # # Check if the union has content.
                # if utype_idx == 0:
                #     # Nothing
                #     table.value[field_name] = None
                #     ctx.field_idx += 1
                #     return

                # Locate the paired Union field
                union_desc = None
                for field_entry in ctx.fields_desc:
                    if 'type' in field_entry and 'index' in field_entry['type'] and \
                        field_entry['type']['index'] == utype_idx:
                        union_desc = field_entry
                        break
                if union_desc is None:
                    raise ValueError(f"Union index {utype_idx} not found for {field_name}.")

                union_name = union_desc['name']

                # Get the enum type associated with utype_idx
                enum_type = parser.schema.enums_by_index[utype_idx]
                
                # Get the enum value (utype). (enum_value == 0 means no content.)
                # NOTE: Defined by underlying_type, but assuming 1 byte with 3 padded zeros.
                ctx.seek(field_pos)
                # TODO: Check for return.
                enum_value = struct.unpack('B', ctx.peek(1))[0]
                #enum_value = parser.peek_u32(ctx)
                
                forward_align = lambda value: value + (4 - value % 4) if value % 4 != 0 else value
                union_offset_pos = forward_align(field_pos + 1)

                # Get the union table offset (union)
                ctx.seek(union_offset_pos)
                union_pos = union_offset_pos + parser.peek_u32(ctx)

                # Get the entry from enum_type who has the enum_value as value
                enum_desc = None
                for enum_entry in enum_type['values']:
                    if enum_entry['value'] == enum_value:
                        enum_desc = enum_entry
                        break
                if enum_desc is None:
                    raise ValueError(f"Enum {utype_idx} desc for value {enum_value} not found.")
                
                union_base_type = enum_desc['union_type']['base_type']

                if union_base_type == 'Obj':
                    table_pos = union_pos
                    type_index = enum_desc['union_type']['index']
                    type_desc = parser.schema.objects_by_index[type_index]
                    table.value[union_name] = NodeTable(ctx.node(), ctx.reader(), union_pos, type_desc)

                    parser.current = table.value[union_name]
                    parser.current.ctx()._next_state(FlatbuffersParsingTable)
                    ctx.field_idx += 1
                    return

                # Catch all for unsupported union_base_type
                msg = f"Unsupported base type while parsing union {union_name} at {table.abs_offset()}"
                print(msg)
                breakpoint()
                raise ValueError(msg)
                

            if base_type == 'Obj':
                # Seek to vector offset
                ctx.seek(field_pos)
                table_pos = field_pos + parser.peek_u32(ctx)

                # Get the table schema stuff

                type_index = field_type.get('index')
                if type_index is None:
                    raise ValueError("Vector of objects missing 'index' field")
                if type_index not in parser.schema.objects_by_index:
                    raise ValueError(f"Unknown object index: {type_index}")

                type_desc = parser.schema.objects_by_index[type_index]
                table.value[field_name] = NodeTable(ctx.node(), ctx.reader(), table_pos, type_desc)

                parser.current = table.value[field_name]
                parser.current.ctx()._next_state(FlatbuffersParsingTable)
                ctx.field_idx += 1
                return


            # Catch all for unsupported element_types
            print(f"Unsupported byte type while parsing table: {base_type}")
            breakpoint()
            raise ValueError(f"Unsupported byte type while parsing table: {base_type}")

        # If we're here, we pop the table back up to previous node.
        #print(f"Finished table @ {table.abs_offset()}")
        parser.current = ctx.parent()
        if isinstance(parser.current, NodeTable):
            parser.current.ctx()._next_state(FlatbuffersParsingTable)
            return
        if isinstance(parser.current, NodeVector):
            parser.current.ctx()._next_state(FlatbuffersParsingVector)
            return
        # Catch all?
        if isinstance(parser.current, Node):
            raise pparse.EndOfDataException("No more data to process in flatbuffers.")
        
        # Catch all for unsupported element_types
        msg = f"Couldn't tell what parent node is at end of table."
        print(msg)
        breakpoint()
        raise ValueError(msg)

'''
Union Notes

023162d8: 
  0e enum?
  00 00 00 padding?
  1c 00 00 00 
  00 00 00 01 
  20 00 00 00
023162e8: 24 00 00 00 00 00 0a 00 0c 00 00 00 08 00 04 00
023162f8: 0a 00 00 00 02 00 00 00 02 00 00 00 01 00 00 00
02316308: ae 00 00 00 03 00 00 00 00 00 00 00 9c 00 00 00
02316318: ad 00 00 00 01 00 00 00 bf 01 00 00 01 00 00 00
02316328: 00 00 00 00 c0 01 00 00 5c 9c 00 00 04 9c 00 00
02316338: b0 9b 00 00 74 9b 00 00 38 9b 00 00 fc 9a 00 00
02316348: c0 9a 00 00 84 9a 00 00 48 9a 00 00 0c 9a 00 00
'''




class FlatbuffersParsingVector(FlatbuffersParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        # Assuming ctx.tell() is at beginning of table.
        vector = parser.current

        if not hasattr(vector, "element_count"):
            ctx.seek(vector.abs_offset())
            vector.element_count = parser.read_u32(ctx)
            return

        element_type = vector.type_desc().get('element')
        element_size = vector.type_desc().get('element_size')

        # NOTE: We can heuristically determine if we want to skip the vector
        # based on (element_size * vector.length).
        
        # Anything other than a scalar or string is an array of offsets that
        # we push down into their own nodes.

        if element_type in parser.schema.TYPE_SIZES and \
            element_size != parser.schema.TYPE_SIZES[element_type]:
            raise ValueError("Mismatch between schema element size and parser size.")

        if not hasattr(ctx, "element_idx"):
            ctx.element_idx = 0

        while ctx.element_idx < vector.element_count:

            # Scalars are inplace, do those first.
            if element_type in parser.schema.TYPE_SIZES:

                element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
                ctx.seek(element_pos)
                vector.value.append(parser.read_scalar(ctx, element_type))
                ctx.element_idx += 1

                continue

            # Strings are nice an simple.
            if element_type == 'String':

                # Seek to string offset
                element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
                ctx.seek(element_pos)
                ctx.seek(element_pos + parser.peek_u32(ctx))
                # TODO: Do we create a NodeString? Pythonic str for now.
                vector.value.append(parser.read_string(ctx))
                ctx.element_idx += 1

                continue

            # Tables
            if element_type == 'Obj':

                # Get the table schema stuff
                type_index = vector.type_desc().get('index')
                if type_index is None:
                    raise ValueError("Vector of objects missing 'index' field")
                if type_index not in parser.schema.objects_by_index:
                    raise ValueError(f"Unknown object index: {type_index}")
                type_desc = parser.schema.objects_by_index[type_index]
                
                # Create a new table and start processing
                element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
                ctx.seek(element_pos)
                table_offset = element_pos + parser.peek_u32(ctx)
                new_table = NodeTable(ctx.node(), ctx.reader(), table_offset, type_desc)
                vector.value.append(new_table)
                ctx.element_idx += 1

                parser.current = new_table
                parser.current.ctx()._next_state(FlatbuffersParsingTable)

                return

            # Catch all for unsupported element_types
            raise ValueError(f"Unsupported vector element type: {element_type}")

        # If we're here, we pop the table back up to previous node.
        #print(f"Finished vector @ {vector.abs_offset()}")
        parser.current = ctx.parent()
        if isinstance(parser.current, NodeTable):
            parser.current.ctx()._next_state(FlatbuffersParsingTable)
            return
        if isinstance(parser.current, NodeVector):
            parser.current.ctx()._next_state(FlatbuffersParsingVector)
            return
        
        # Catch all for unsupported element_types
        raise ValueError(f"Couldn't tell what parent node is at end of vector.")


class FlatbuffersParsingRootTableOffset(FlatbuffersParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        # Assuming we're at offset 0
        table_offset = parser.read_u32(ctx, peek=True)
        type_desc = parser.schema.objects[parser.schema.root_table_name]

        # Advance cursor to table.
        ctx.seek(table_offset)

        ctx.node().value = NodeTable(ctx.node(), ctx.reader(), table_offset, type_desc)
        ctx.node().value.is_root = True
        parser.current = ctx.node().value
        parser.current.ctx()._next_state(FlatbuffersParsingTable)