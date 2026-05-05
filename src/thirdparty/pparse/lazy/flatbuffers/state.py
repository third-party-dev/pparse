#!/usr/bin/env python3

import logging
import struct
from collections import OrderedDict

log = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers.node import NodeContext
#from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeTable, NodeVector, NodeVTable, NodeField


class FlatbuffersParsingState(object):
    def parse_data(self, node: pparse.Node):
        raise NotImplementedError()


# class FlatbuffersParsingTableFields(FlatbuffersParsingState):

#     def parse_data(self, node: pparse.Node):
#         ctx = node.ctx()
#         parser = ctx.parser()

#         table = parser.current

#         # Assuming ctx.field_idx is 0 at start
#         # (Optionally?) Parsing the fields
#         while ctx.field_idx < len(ctx.fields_desc):

#             breakpoint()
#             field_name = ctx.fields_desc[ctx.field_idx]['name']
#             field = table.value[field_name]
#             field.parse_value(self, parser, ctx)

#         # If we're here, we pop the table back up to previous node.
#         #print(f"Finished table @ {table.abs_offset()}")
#         # if ctx.parent().type_name() == 'rknn.root_f2':
#         breakpoint()
#         parser.current = ctx.parent()
#         if isinstance(parser.current, NodeTable):
#             parser.current.ctx()._next_state(FlatbuffersParsingTable)
#             return
#         if isinstance(parser.current, NodeVector):
#             parser.current.ctx()._next_state(FlatbuffersParsingVector)
#             return
#         # Catch all?
#         if isinstance(parser.current, Node):
#             raise pparse.EndOfDataException("No more data to process in flatbuffers.")
        
#         # Catch all for unsupported element_types
#         msg = f"Couldn't tell what parent node is at end of table."
#         print(msg)
#         breakpoint()
#         raise ValueError(msg)


class FlatBuffersParsingComplete(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        return pparse.ASCEND


class FlatbuffersParsingVectorOfTables(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        type_desc = ctx.type_desc()
        elem_desc = parser.schema.objects_by_index[type_desc['type']['index']]

        # Generate nodes for each table and append to descendants in Post

        elem_count = parser.read_u32(ctx)

        node._value = []
        for elem_idx in range(elem_count):
            # Advance to vector elem (offset to table)
            ctx.seek(node.tell() + ((elem_idx + 1) * 4))
            ctx.skip(parser.peek_u32(ctx))
            # We're now at the target table.

            node._value.append(parser.new_node_table(node, elem_desc['name']))

        # Not until the loop is done do we try to submit descendants.

        # Note: With flatbuffers, we can easily not worry about descendants now.
        # TODO: Detect if Node.load(recursive=True)?
        for field in node._value:
            ctx._descendants.append(field)

        # We're done.
        ctx._next_state(FlatBuffersParsingComplete)
        return pparse.ASCEND


class FlatbuffersParsingVectorOfScalars(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        type_desc = ctx.type_desc()
        elem_count = parser.read_u32(ctx)
        elem_size = type_desc['type']['element_size']


        if type_desc['type']['element'].lower() == 'ubyte':
            node._value = ctx.read(elem_size * elem_count)
            ctx._next_state(FlatBuffersParsingComplete)
            return pparse.ASCEND
        
        if type_desc['type']['element'].lower() == 'byte':
            node._value = ctx.read(elem_size * elem_count)
            ctx._next_state(FlatBuffersParsingComplete)
            return pparse.ASCEND

        if type_desc['type']['element'].lower() == 'int':
            # TODO: Consider more efficient handler (esp with array is large)
            node._value = struct.unpack(f'<{elem_count}i', ctx.read(elem_size * elem_count))
            ctx._next_state(FlatBuffersParsingComplete)
            return pparse.ASCEND
        
        if type_desc['type']['element'].lower() == 'float':
            # TODO: Consider more efficient handler (esp with array is large)
            node._value = struct.unpack(f'<{elem_count}f', ctx.read(elem_size * elem_count))
            ctx._next_state(FlatBuffersParsingComplete)
            return pparse.ASCEND

        breakpoint()


class FlatbuffersParsingString(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        node._value = parser.read_string(ctx)
        ctx._next_state(FlatBuffersParsingComplete)
        return pparse.ASCEND


class FlatbuffersParsingVectorOfStrings(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        type_desc = ctx.type_desc()

        # Generate nodes for each string and append to descendants in Post
        elem_count = parser.read_u32(ctx)

        node._value = []
        for elem_idx in range(elem_count):
            # Advance to vector elem (offset to table)
            ctx.seek(node.tell() + ((elem_idx + 1) * 4))
            ctx.skip(parser.peek_u32(ctx))
            # We're now at the target string.
            node._value.append(parser.new_node_string(node))

        

        # Not until the loop is done do we try to submit descendants.

        # Note: With flatbuffers, we can easily not worry about descendants now.
        # TODO: Detect if Node.load(recursive=True)?
        for node_str in node._value:
            ctx._descendants.append(node_str)

        # We're done.
        ctx._next_state(FlatBuffersParsingComplete)
        return pparse.ASCEND


class FlatbuffersParsingUnion(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()
        type_desc = ctx.type_desc()

        ctx._enum = parser.schema.enums[type_desc['type']['index']]
        ctx._utype = struct.unpack('<B', ctx.read(1))[0]
        ctx._enum_desc = ctx._enum['values'][ctx._utype]

        if ctx._enum_desc['union_type']['base_type'].lower() == 'obj':
            breakpoint()
            # Convert node to a table node.
            ctx.skip(parser.peek_u32(ctx))
            ctx._utype_desc = type_desc
            ctx._type_desc = parser.schema.objects_by_index[ctx._enum_desc['union_type']['index']]
            ctx._next_state(FlatbuffersParsingVTable)
            return pparse.AGAIN

        breakpoint()


class FlatbuffersParsingTableField(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        # TODO: Is this field a table, enum, vector of tables, vector of simples?
        # TODO: Route the field to the appropriate state.

        type_desc = ctx.type_desc()

        if type_desc['type']['base_type'].lower() == 'obj':
            node._value = parser.new_node_table_idx(node, type_desc['type']['index'])
            # TODO: Optionally ignore until dereferenced.
            ctx._descendants.append(node._value)
            return pparse.ASCEND


        if type_desc['type']['base_type'].lower() == 'vector':
            # TODO: All of these are good candidates for deferral.
            if type_desc['type']['element'].lower() == 'obj':
                ctx._next_state(FlatbuffersParsingVectorOfTables)
                return pparse.AGAIN
            # TODO: Difference in ubyte and byte?
            if type_desc['type']['element'].lower() == 'ubyte':
                ctx._next_state(FlatbuffersParsingVectorOfScalars)
                return pparse.AGAIN
            # TODO: Difference in ubyte and byte?
            if type_desc['type']['element'].lower() == 'byte':
                ctx._next_state(FlatbuffersParsingVectorOfScalars)
                return pparse.AGAIN
            if type_desc['type']['element'].lower() == 'int':
                ctx._next_state(FlatbuffersParsingVectorOfScalars)
                return pparse.AGAIN
            if type_desc['type']['element'].lower() == 'float':
                ctx._next_state(FlatbuffersParsingVectorOfScalars)
                return pparse.AGAIN
            if type_desc['type']['element'].lower() == 'string':
                ctx._next_state(FlatbuffersParsingVectorOfStrings)
                return pparse.AGAIN
            

        if type_desc['type']['base_type'].lower() == 'union':
            raise ValueError("A union should never reach FlatbuffersParsingTableField")
        if type_desc['type']['base_type'].lower() == 'utype':
            ctx._next_state(FlatbuffersParsingUnion)
            return pparse.AGAIN

        breakpoint()


class FlatbuffersParsingTable(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        # By design, for better or worse, we retry the whole state on retry after error.
        # Note: This could be incomplete.

        field_descs = {}
        for field in parser.schema.objects[ctx.type_desc()['name']].get('fields', []):
            if 'id' in field:
                field_descs[field['id']] = field
            else:
                # ! Weirdness here.
                # Field 0 has no id. Not sure if this is normal or expected.
                if 0 in field_descs:
                    breakpoint()
                field_descs[0] = field

        # We store all fields here, and only schema defined ones in node._value
        ctx._fields = OrderedDict()
        fields_by_name = OrderedDict()
        # Note: By design, for better or worse, we redo the whole loop if anything goes wrong and retry.
        for field_idx in ctx._field_offsets:
            # Go to start of table (for load order independence).
            ctx.seek(node.tell())

            if ctx._field_offsets[field_idx] == 0:
                continue

            ctx.skip(ctx._field_offsets[field_idx])

            if len(field_descs) <= field_idx:
                # Field not in schema. We'll generate node and forget for now.
                # TODO: Consider generating a name and decoding as a number of value types for discovery?
                ctx._fields[field_idx] = pparse.Node(ctx.reader(), parser, parent=node, ctx_class=NodeContext)
                ctx._fields[field_idx].ctx()._next_state(FlatbuffersParsingTableField)
                continue

            log.debug(f"{ctx.type_desc()['name']}.{field_descs[field_idx]['name']} field at {ctx.tell():x}")

            if parser.is_simple(field_descs[field_idx]):
                ctx._fields[field_idx] = pparse.Node(ctx.reader(), parser, parent=node, ctx_class=NodeContext)
                ctx._fields[field_idx].ctx()._type_desc = field_descs[field_idx]
                ctx._fields[field_idx].ctx()._next_state(FlatbuffersParsingTableField)
                fields_by_name[field_descs[field_idx]['name']] = parser.peek_simple(ctx._fields[field_idx].ctx())
                continue

            if field_descs[field_idx]['type']['base_type'].lower() == 'utype':
                # utype field_idx is followed by union field_idx, we'll handle both here.
                # Note: This is complex, but we don't want to "jump to reference".

                # Get utype value from current offset, reset, jump to union offset.
                utype = struct.unpack('<B', ctx.peek(1))[0]
                ctx.seek(node.tell())
                ctx.skip(ctx._field_offsets[field_idx+1])

                utype_desc = field_descs[field_idx]
                enum = parser.schema.enums[utype_desc['type']['index']]
                enum_desc = enum['values'][utype]

                if enum_desc['union_type']['base_type'].lower() == 'obj':
                    ctx.skip(parser.peek_u32(ctx))
                    ctx._fields[field_idx] = pparse.Node(ctx.reader(), parser, parent=node, ctx_class=NodeContext)
                    fctx = ctx._fields[field_idx].ctx()
                    fctx._type_desc = parser.schema.objects_by_index[enum_desc['union_type']['index']]
                    fctx._next_state(FlatbuffersParsingVTable)
                    fields_by_name[field_descs[field_idx]['name']] = ctx._fields[field_idx]
                    continue
                else:
                    breakpoint()

                continue

            if field_descs[field_idx]['type']['base_type'].lower() == 'union':
                # Skipping union in favor of handling from utype
                continue


            ctx.skip(parser.peek_u32(ctx))
            ctx._fields[field_idx] = pparse.Node(ctx.reader(), parser, parent=node, ctx_class=NodeContext)
            ctx._fields[field_idx].ctx()._type_desc = field_descs[field_idx]
            ctx._fields[field_idx].ctx()._next_state(FlatbuffersParsingTableField)
            fields_by_name[field_descs[field_idx]['name']] = ctx._fields[field_idx]

        node._value = fields_by_name

        # Not until the loop is done do we try to submit descendants.

        # Note: With flatbuffers, we can easily not worry about descendants now.
        # TODO: Detect if Node.load(recursive=True)?
        for field in node._value.values():
            if isinstance(field, pparse.Node):
                ctx._descendants.append(field)

        # We're done.
        ctx._next_state(FlatBuffersParsingComplete)
        return pparse.ASCEND



class FlatbuffersParsingVTable(FlatbuffersParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        # Assuming ctx.tell() is at beginning of table.
        # By design, for better or worse, we retry the whole state on retry after error.

        ctx._vtable_offset = parser.read_i32(ctx)
        # Go to vtable
        ctx.seek(node.tell() - ctx._vtable_offset)

        ctx._vtable_size = parser.read_u16(ctx)
        if ctx._vtable_size % 2 != 0:
            raise pparse.UnsupportedFormatException("Invalid vtable: Not evenly sized.")
        if ctx.left() < ctx._vtable_size:
            msg = f"Not enough data to parse vtable at {(ctx.abs_off() - ctx._vtable_offset):x}"
            raise pparse.EndOfDataException(msg)

        ctx._table_size = parser.read_u16(ctx)
        ctx._field_count = (ctx._vtable_size // 2) - 2
        ctx._field_offsets = OrderedDict()
        for i in range(ctx._field_count):
            ctx._field_offsets[i] = parser.read_u16(ctx)

        ctx._next_state(FlatbuffersParsingTable)
        return pparse.AGAIN







        # # Try initializing loop ctx members
        # if not hasattr(ctx, "fields_desc"):
        #     table_name = table.type_desc()['name']
        #     ctx.fields_desc = parser.schema.objects[table_name].get('fields', [])
        #     ctx.field_idx = 0
        #     return

        # # Create stubs for all the fields
        # while ctx.field_idx < len(ctx.fields_desc):

        #     '''
        #     if value is a scalar, tbl.value['field_name'].value = scalar
        #     if value is a string, tbl.value['field_name'].value = string
        #     if value is a vector, tbl.value['field_name'].value = [values]
        #     if value is a table, tbl.value['field_name'].value = table
        #     if value is a union, tbl.value['field_name'].value = tbl/scalar/string??
        #     '''

        #     field_type_desc = ctx.fields_desc[ctx.field_idx]

        #     # Get the field ID (which determines position in vtable)
        #     # Fields are indexed by their 'id' if present, otherwise by order
        #     field_id = field_type_desc.get('id', 0)
        #     if field_id >= len(table.vtable.field_offsets): # Field not present
        #         ctx.field_idx += 1
        #         continue

        #     field_offset_in_table = table.vtable.field_offsets[field_id]
        #     if field_offset_in_table == 0: # Field not present
        #         ctx.field_idx += 1
        #         continue

        #     # Calculate absolute offset of field
        #     field_pos = table.abs_offset() + field_offset_in_table

        #     # Note: No parsing is done at this point.
        #     field = NodeField(table, ctx.reader(), field_pos, field_type_desc)
        #     table.value[field.name()] = field
        #     ctx.field_idx += 1
        #     continue

        # ctx.field_idx = 0
        # parser.current.ctx()._next_state(FlatbuffersParsingTableFields)
        # return


# class FlatbuffersParsingVector(FlatbuffersParsingState):

#     def parse_data(self, node: pparse.Node):
#         ctx = node.ctx()
#         parser = ctx.parser()

#         # Assuming ctx.tell() is at beginning of table.
#         vector = parser.current

#         if not hasattr(vector, "element_count"):
#             ctx.seek(vector.abs_offset())
#             vector.element_count = parser.read_u32(ctx)
#             return

#         element_type = vector.type_desc().get('element')
#         element_size = vector.type_desc().get('element_size')

#         # NOTE: We can heuristically determine if we want to skip the vector
#         # based on (element_size * vector.length).
        
#         # Anything other than a scalar or string is an array of offsets that
#         # we push down into their own nodes.

#         if element_type in parser.schema.TYPE_SIZES and \
#             element_size != parser.schema.TYPE_SIZES[element_type]:
#             raise ValueError("Mismatch between schema element size and parser size.")

#         if not hasattr(ctx, "element_idx"):
#             ctx.element_idx = 0

#         while ctx.element_idx < vector.element_count:

#             # if 'f2_graph' in vector.ctx().parent().value:
#             #     breakpoint()

#             # Scalars are inplace, do those first.
#             if element_type in parser.schema.TYPE_SIZES:

#                 element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
#                 ctx.seek(element_pos)
#                 vector.value.append(parser.read_scalar(ctx, element_type))
#                 ctx.element_idx += 1

#                 continue

#             # Strings are nice an simple.
#             if element_type == 'String':

#                 # Seek to string offset
#                 element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
#                 ctx.seek(element_pos)
#                 ctx.seek(element_pos + parser.peek_u32(ctx))
#                 # TODO: Do we create a NodeString? Pythonic str for now.
#                 vector.value.append(parser.read_string(ctx))
#                 ctx.element_idx += 1

#                 continue

#             # Tables
#             if element_type == 'Obj':

#                 # Get the table schema stuff
#                 type_index = vector.type_desc().get('index')
#                 if type_index is None:
#                     raise ValueError("Vector of objects missing 'index' field")
#                 if type_index not in parser.schema.objects_by_index:
#                     raise ValueError(f"Unknown object index: {type_index}")
#                 elem_desc = parser.schema.objects_by_index[type_index]

#                 # Store elem_desc for printing. Consider reusing as cached value.
#                 ctx.node().elem_desc = elem_desc

                
#                 # Create a new table and start processing
#                 element_pos = vector.abs_offset() + (ctx.element_idx * element_size) + 4
#                 ctx.seek(element_pos)
#                 table_offset = element_pos + parser.peek_u32(ctx)
#                 new_table = NodeTable(ctx.node(), ctx.reader(), table_offset, elem_desc)
#                 vector.value.append(new_table)
#                 ctx.element_idx += 1

#                 ## ! Note: Observing an unintentional decision to parse depth first.
#                 parser.current = new_table
#                 parser.current.ctx()._next_state(FlatbuffersParsingTable)

#                 return

#             # Catch all for unsupported element_types
#             raise ValueError(f"Unsupported vector element type: {element_type}")

#         # If we're here, we pop the table back up to previous node.
#         #print(f"Finished vector @ {vector.abs_offset()}")
#         parser.current = ctx.parent()
#         if isinstance(parser.current, NodeTable):
#             parser.current.ctx()._next_state(FlatbuffersParsingTable)
#             return
#         if isinstance(parser.current, NodeVector):
#             parser.current.ctx()._next_state(FlatbuffersParsingVector)
#             return
        
#         # Catch all for unsupported element_types
#         raise ValueError(f"Couldn't tell what parent node is at end of vector.")


class FlatbuffersParsingRootTableOffset(FlatbuffersParsingState):

    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        # Assuming that the parser has been advanced to the start of flatbuffers stream.
        table_offset = parser.read_u32(ctx, peek=True)
        node._value['root_abs_off'] = table_offset + ctx.tell()

        # Advance cursor to table.
        ctx.skip(table_offset)

        # Seed root table node
        root = parser.new_node_table(node, parser.schema.root_table_name)
        node._value['root_table'] = root
        ctx._descendants.append(root)

        # We're done.
        ctx._next_state(FlatBuffersParsingComplete)
        return pparse.ASCEND

        #raise pparse.EndOfNodeException("end of node in FlatbuffersParsingRootTableOffset")
        #parser.current = ctx.node().value
        #parser.current.ctx()._next_state(FlatbuffersParsingVTable)