#!/usr/bin/env python3

import logging
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeTable, NodeVector, NodeVTable, NodeField


class FlatbuffersParsingState(object):
    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        raise NotImplementedError()


class FlatbuffersParsingTableFields(FlatbuffersParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):

        table = parser.current

        # Assuming ctx.field_idx is 0 at start
        # (Optionally?) Parsing the fields
        while ctx.field_idx < len(ctx.fields_desc):

            breakpoint()
            field_name = ctx.fields_desc[ctx.field_idx]['name']
            field = table.value[field_name]
            field.parse_value(self, parser, ctx)

        # If we're here, we pop the table back up to previous node.
        #print(f"Finished table @ {table.abs_offset()}")
        # if ctx.parent().type_name() == 'rknn.root_f2':
        breakpoint()
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


class FlatbuffersParsingVTable(FlatbuffersParsingState):

    def parse_data(self, parser: "Parser", ctx: "NodeContext"):
        # ! Bias breadth first:
        # ! - All field offsets and field objects parsed first, then optionally decend.

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

        # Create stubs for all the fields
        while ctx.field_idx < len(ctx.fields_desc):

            '''
            if value is a scalar, tbl.value['field_name'].value = scalar
            if value is a string, tbl.value['field_name'].value = string
            if value is a vector, tbl.value['field_name'].value = [values]
            if value is a table, tbl.value['field_name'].value = table
            if value is a union, tbl.value['field_name'].value = tbl/scalar/string??
            '''

            field_type_desc = ctx.fields_desc[ctx.field_idx]

            # Get the field ID (which determines position in vtable)
            # Fields are indexed by their 'id' if present, otherwise by order
            field_id = field_type_desc.get('id', 0)
            if field_id >= len(table.vtable.field_offsets): # Field not present
                ctx.field_idx += 1
                continue

            field_offset_in_table = table.vtable.field_offsets[field_id]
            if field_offset_in_table == 0: # Field not present
                ctx.field_idx += 1
                continue

            # Calculate absolute offset of field
            field_pos = table.abs_offset() + field_offset_in_table

            # Note: No parsing is done at this point.
            field = NodeField(table, ctx.reader(), field_pos, field_type_desc)
            table.value[field.name()] = field
            ctx.field_idx += 1
            continue

        ctx.field_idx = 0
        parser.current.ctx()._next_state(FlatbuffersParsingTableFields)
        return


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

            # if 'f2_graph' in vector.ctx().parent().value:
            #     breakpoint()

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
                elem_desc = parser.schema.objects_by_index[type_index]

                # Store elem_desc for printing. Consider reusing as cached value.
                ctx.node().elem_desc = elem_desc

                
                # Create a new table and start processing
                element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
                ctx.seek(element_pos)
                table_offset = element_pos + parser.peek_u32(ctx)
                new_table = NodeTable(ctx.node(), ctx.reader(), table_offset, elem_desc)
                vector.value.append(new_table)
                ctx.element_idx += 1

                ## ! Note: Observing an unintentional decision to parse depth first.
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
        # Assuming that the parser has been advanced to the start of flatbuffers stream.
        table_offset = parser.read_u32(ctx, peek=True)
        type_desc = parser.schema.objects[parser.schema.root_table_name]

        # Advance cursor to table.
        ctx.seek(table_offset)

        ctx.node().value = NodeTable(ctx.node(), ctx.reader(), table_offset, type_desc)
        ctx.node().value.is_root = True
        raise pparse.EndOfNodeException("end of node in FlatbuffersParsingRootTableOffset")

        #parser.current = ctx.node().value
        #parser.current.ctx()._next_state(FlatbuffersParsingVTable)