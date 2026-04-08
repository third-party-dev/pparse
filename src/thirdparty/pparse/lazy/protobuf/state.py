#!/usr/bin/env python3

import logging
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf.meta import Field, Protobuf
# from thirdparty.pparse.lazy.protobuf.node import Node, NodeArray, NodeContext, NodeMap
from thirdparty.pparse.lazy.protobuf.node import NodeContext

def unzigzag(v):
    return (v >> 1) ^ -(v & 1)


def zigzag_i32(n):
    return (n << 1) ^ (n >> 31)


def zigzag_i64(n):
    return (n << 1) ^ (n >> 63)


class ProtobufParsingState(object):
    def parse_data(self, node: pparse.Node):
        raise NotImplementedError()


class ProtobufParsingComplete(object):
    def parse_data(self, node: pparse.Node):
        return pparse.ASCEND


'''
Each field is tagged: `tag = (field_number << 3) | wire_type`
The wire type VARINT, I64, and I32 are "simple" inline values.
The wire type LEN includes strings, bytes, messages, packed repeated fields.
- These are where new nodes should come from.
SGROUP/EGROUP are theoretically unused, but likely would trigger additional nodes as well.

VARINT: [tag varint (VARINT)] [value varint]
LEN: [tag varint (LEN)] [byte_length varint] [bytes]
Packed: [tag varint (LEN)] [byte_length varint] [varint0] [varint1] [varintN]

parser._root._value['graph']._value['node'][0]._value['attribute'][0]._value['t']
'''

class ProtobufParsingSimplePacked(ProtobufParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        breakpoint()

        while ctx.tell() < ctx._length:
            node._value.append(parser.parse_varint(ctx))
        
        # We're done.
        ctx._next_state(ProtobufParsingComplete)
        return pparse.ASCEND


class ProtobufParsingWireTypeLen(ProtobufParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        if ctx._field.type == Field.TYPE_MESSAGE:
            
            ctx._next_state(ProtobufParsingTag)
            return pparse.AGAIN

        if field.type in Protobuf.inline_types:
            breakpoint()
            length = parser.parse_varint(ctx)
            pkd_node = pparse.Node(ctx.reader(), parser, default_value=[], parent=node, ctx_class=NodeContext)
            pkd_node.ctx()._type_desc = field
            # TODO: With the length, we could parse fields out breadth first.
            pkd_node.ctx()._length = length
            pkd_node.ctx()._next_state(ProtobufParsingSimplePacked)

            if field.is_repeated():
                breakpoint()

            node._value[field.name] = pkd_node
            node.ctx()._descendants.append(pkd_node)
            return pparse.AGAIN


class ProtobufParsingBytes(ProtobufParsingState):
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        node._value = ctx.read(ctx.left())
        # We're done.
        ctx._next_state(ProtobufParsingComplete)
        return pparse.ASCEND


class ProtobufParsingWireTypeI32(ProtobufParsingState):
    # TODO: Split based on wire_type
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()
        breakpoint()


class ProtobufParsingTag(ProtobufParsingState):
    # TODO: Split based on wire_type
    def parse_data(self, node: pparse.Node):
        ctx = node.ctx()
        parser = ctx.parser()

        # TODO: While going through fields, we must not go past parent's length.
        # TODO: Ideally we'd construct ranges for each LEN and check ctx.left()
        # TODO: For the root table, we'd use the extraction data source length.

        if ctx.left() == 0:
            # We're done.
            ctx._next_state(ProtobufParsingComplete)
            return pparse.ASCEND

        # Get the tag data.
        wire_type, field_num = parser.parse_varint_key(ctx)
        field = ctx.type_desc().by_id(field_num)

        # if field.name == 'attribute':
        #     breakpoint()
        log.debug(f"ProtobufParsingKey: parsing {ctx.type_desc().type_name()} {field}")

        if wire_type == Protobuf.I32:
            data = ctx.read(4)
            if field.type == Field.TYPE_FLOAT:
                value = struct.unpack('<f', data)[0]
                if field.is_repeated():
                    log.debug(f"Appending value {value} to {field.name}")
                    node._value.setdefault(field.name, []).append(value)
                else:
                    log.debug(f"Setting value {value} to {field.name}")
                    node._value[field.name] = value
                return pparse.AGAIN

        if wire_type == Protobuf.VARINT:
            if field.type in Protobuf.inline_types:
                value = parser.parse_varint(ctx)
                if field.is_repeated():
                    log.debug(f"Appending value {value} to {field.name}")
                    node._value.setdefault(field.name, []).append(value)
                else:
                    log.debug(f"Setting value {value} to {field.name}")
                    node._value[field.name] = value
                return pparse.AGAIN

            # TODO: Add support for sint32/sint64 with zigzag here.
            breakpoint()
            return pparse.AGAIN

        if wire_type == Protobuf.LEN:
            length = parser.parse_varint(ctx)

            # At this point, cursor should be at start of LEN payload. Build a new range
            # that only encompasses the LEN data so we can use ctx.left().
            reader = pparse.Range(ctx.reader().cursor(), length)
            # node's reader must skip what sub-nodes will handle.
            ctx.skip(length)
            len_node = pparse.Node(reader, parser, parent=node, ctx_class=NodeContext)
            lctx = len_node.ctx()
            lctx._field = field

            if field.type == Field.TYPE_STRING:
                # Special case for strings
                value = lctx.read(lctx.left()).decode('utf-8')
                if field.is_repeated():
                    log.debug(f"Appending string to {field.name}, bytes left {lctx.left()}")
                    node._value.setdefault(field.name, []).append(value)
                else:
                    log.debug(f"Setting string to {field.name}, bytes left {lctx.left()}")
                    node._value[field.name] = value
                # Note: len_node is thrown away at this point.
                return pparse.AGAIN

            if field.type == Field.TYPE_MESSAGE:
                lctx._type_desc = parser.schema.by_type_name(field.type_name)
                # ! TODO: This doesn't feel right.
                len_node._value = {}
                lctx._next_state(ProtobufParsingTag)
            elif field.type == Field.TYPE_BYTES:
                # TODO: This could be deferred!
                lctx._next_state(ProtobufParsingBytes)
            else:
                breakpoint()
                lctx._next_state(ProtobufParsingWireTypeLen)

            if field.is_repeated():
                log.debug(f"Appending unloaded len node to {field.name}, bytes left {lctx.left()}")
                node._value.setdefault(field.name, []).append(len_node)
            else:
                log.debug(f"Setting unloaded len node to {field.name}, bytes left {lctx.left()}")
                node._value[field.name] = len_node

            # TODO: Optional, detect recursive=True?
            ctx._descendants.append(len_node)

            return pparse.AGAIN

        breakpoint()

        

        # If its a simple varint value, grab it and move on.
        
        # if wire_type == Protobuf.VARINT and field.type in simple_types:
        #     value = parser.parse_varint(ctx)

        #     if field.is_repeated():
        #         if field.name not in node._value:
        #             node._value[field.name] = []
        #         node._value[field.name].append(value)
        #         return pparse.AGAIN

        #     # not repeated
        #     node._value[field.name] = value
        #     return pparse.AGAIN
        





        # if wire_type == Protobuf.LEN and field.type == Field.TYPE_STRING:
        #     length = parser.parse_varint(ctx)
        #     value = ctx.read(length).decode('utf-8')

        #     if field.is_repeated():
        #         if field.name not in node._value:
        #             node._value[field.name] = []
        #         node._value[field.name].append(value)
        #         return pparse.AGAIN

        #     # if not repeated.
        #     node._value[field.name] = value
        #     return pparse.AGAIN

        # if wire_type == Protobuf.I32 and field.type == Field.TYPE_FLOAT:
        #     value = ctx.read(4)

        #     if field.is_repeated():
        #         breakpoint()

        #     node._value[field.name] = struct.unpack("<f", value)[0]
        #     return pparse.AGAIN
        
        # if wire_type == Protobuf.LEN and field.type == Field.TYPE_MESSAGE:
        #     length = parser.parse_varint(ctx)

        #     msg_node = pparse.Node(ctx.reader(), parser, default_value={}, parent=node, ctx_class=NodeContext)
        #     msg_node.ctx()._type_desc = parser.schema.by_type_name(field.type_name)
        #     # TODO: With the length, we could parse fields out breadth first.
        #     msg_node.ctx()._length = length
        #     msg_node.ctx()._next_state(ProtobufParsingTag)
        #     node.ctx()._descendants.append(msg_node)

        #     if field.is_repeated():
        #         if field.name not in node._value:
        #             node._value[field.name] = []
        #         node._value[field.name].append(msg_node)
        #         return pparse.AGAIN

        #     # Not repeated.
        #     node._value[field.name] = msg_node
        #     return pparse.AGAIN

        # if wire_type == Protobuf.LEN and field.type in simple_types:
        #     breakpoint()
        #     length = parser.parse_varint(ctx)
        #     pkd_node = pparse.Node(ctx.reader(), parser, default_value=[], parent=node, ctx_class=NodeContext)
        #     pkd_node.ctx()._type_desc = field
        #     # TODO: With the length, we could parse fields out breadth first.
        #     pkd_node.ctx()._length = length
        #     pkd_node.ctx()._next_state(ProtobufParsingSimplePacked)

        #     if field.is_repeated():
        #         breakpoint()

        #     node._value[field.name] = pkd_node
        #     node.ctx()._descendants.append(pkd_node)
        #     return pparse.AGAIN

        # breakpoint()

        








        # field = None
        # if isinstance(ctx.node(), NodeMap):
        #     field = ctx.node().field_by_id(field_num)
        # elif isinstance(ctx.node(), NodeArray):
        #     try:
        #         field = ctx._parent.field_by_id(field_num)
        #     except KeyError as e:
        #         breakpoint()
        # else:  # UNLIKELY
        #     breakpoint()

        # log.debug(
        #     f"\nPROCESSING FIELD (off: {ctx.tell()} left: {ctx.left()}): {field.name}   {field.type_name}\n"
        # )

        # if (
        #     isinstance(parser.current, NodeArray)
        #     and ctx.key()
        #     and field.name != ctx.key().name
        # ):
        #     # Pop NodeArray if complete, but not done with parent NodeMap.
        #     log.debug(f"Ending NodeArray for repeated field {ctx.key().name}")
        #     parser._end_container_node(ctx)
        #     return

        # # The following things are in an array, set that up first.
        # # Note: Assuming you can not do NodeArray.value = [NodeArray]
        # if field.label == Field.LABEL_REPEATED and not isinstance(
        #     parser.current, NodeArray
        # ):
        #     log.debug(f"Creating NodeArray for repeated field {field.name}")

        #     ctx.mark_field_start()
        #     parent = parser.current
        #     # Note: ctx.reader() returns duplicate.
        #     # 'field' is more universal than 'msgtype' for array nodes
        #     newarr = NodeArray(parent, ctx.reader(), field)

        #     # Assuming array parent is always a map.
        #     parser.current.value[field.name] = newarr
        #     parser.current = parser.current.value[field.name]

        #     # We're in a new _repeated_ _numeric_ field with wire_type == 2,
        #     # we're likely packed. Lets peek the length and verify it matches
        #     # value_length.
        #     # if value_length == 6:
        #     #     if wire_type == Protobuf.LEN and field.type in [
        #     #         Field.TYPE_INT64, Field.TYPE_UINT64,
        #     #     ]:
        #     #         # TODO: Should be new state.
        #     #         # Read varints until value_length bytes consumed.
        #     #         while (ctx.left() - meta_length) > 0:
        #     #             print(parser.parse_varint(ctx))
        #     #         parser._end_container_node(ctx)
        #     #         breakpoint()
        #     #         return
        #     # else:
        #     ctx._next_state(ProtobufParsingKey)

        #     return

        # # Progress past the key.
        # ctx.set_key(field)
        # ctx.skip(meta_length)

        # # if field.type in [Field.TYPE_INT64, Field.TYPE_UINT64] and wire_type == Protobuf.LEN:
        # #     breakpoint()
        # #     return

        # if field.type == Field.TYPE_MESSAGE and value_length:
        #     log.debug(
        #         f"  LENGTH: {value_length} (meta_length: {meta_length}) range: {ctx.tell()} - {ctx.tell() + value_length}"
        #     )

        #     # Create the new node and make it active.
        #     parser._start_map_node(ctx, field)

        #     # Save the length of the message in the new node.
        #     parser.current.ctx().reinit(ctx.tell(), value_length)
        #     return

        # # if field.type == Field.TYPE_BOOL:
        # #     value = parser.parse_varint(ctx)
        # #     parser._apply_value(ctx, field, value)
        # #     ctx._next_state(ProtobufParsingKey)
        # #     return

        # if field.type == Field.TYPE_INT64 or field.type == Field.TYPE_INT32 or \
        #     field.type == Field.TYPE_UINT64 or field.type == Field.TYPE_UINT32 or \
        #     field.type == Field.TYPE_BOOL:

        #     if wire_type == Protobuf.LEN and isinstance(parser.current, NodeArray):
        #         #breakpoint()
        #         # Handle repeated-packed numerical things
        #         while ctx.left() > 0:
        #             val = parser.parse_varint(ctx)
        #             #print(val)
        #             parser._apply_value(ctx, field, val)

        #         ctx._next_state(ProtobufParsingKey)
        #         return

        #     # TODO: Should this handle 2's compliment?
        #     value = parser.parse_varint(ctx)
        #     parser._apply_value(ctx, field, value)
        #     ctx._next_state(ProtobufParsingKey)
        #     return

        # if field.type == Field.TYPE_ENUM and wire_type == Protobuf.VARINT:
        #     # Get the length of the sub-message.
        #     enum = parser.parse_varint(ctx)
        #     parser._apply_value(ctx, field, enum)

        #     ctx._next_state(ProtobufParsingKey)
        #     return

        # if field.type == Field.TYPE_FLOAT and wire_type == Protobuf.I32:
        #     # Get the length of the sub-message.
        #     value = ctx.read(4)
        #     float_value = struct.unpack("<f", value)[0]
        #     parser._apply_value(ctx, field, float_value)

        #     ctx._next_state(ProtobufParsingKey)
        #     return

        # if field.type == Field.TYPE_STRING and wire_type == Protobuf.LEN:
        #     data = ctx.read(value_length)
        #     if len(data) <= 40:
        #         log.debug(f"Whole String: {data}")
        #     else:
        #         log.debug(
        #             f"Part of String (length {len(data)}): {data.decode('utf-8')[:40]}"
        #         )

        #     log.debug(f"String: {data}")
        #     if (value_length > 0 and not data) or len(data) < value_length:
        #         msg = (
        #             "Not enough data to parse Protobuf LEN data. "
        #             f"Offset: {ctx.tell()} Read: {len(data)} of {value_length}"
        #         )
        #         raise pparse.EndOfDataException(msg)
        #     parser._apply_value(ctx, field, data.decode("utf-8"))

        #     ctx._next_state(ProtobufParsingKey)
        #     return

        # if field.type == Field.TYPE_BYTES:
        #     data = ctx.read(value_length)
        #     if len(data) <= 40:
        #         log.debug(f"All Bytes: {data}")
        #     else:
        #         log.debug(f"First Bytes (length {len(data)}): {data[:40]}")

        #     if (value_length > 0 and not data) or len(data) < value_length:
        #         msg = (
        #             "Not enough data to parse Protobuf LEN data. "
        #             f"Offset: {ctx.tell()} Read: {len(data)} of {value_length}"
        #         )
        #         raise pparse.EndOfDataException(msg)

        #     parser._apply_value(ctx, field, data)

        #     ctx._next_state(ProtobufParsingKey)
        #     return

        # log.debug(f"UNKNOWN FIELD OR WIRE TYPE {wire_type} {field.type}")
        # breakpoint()

        # msg = f"Not a valid Protobuf wire type. Type: {wire_type} ({Protobuf.wire_type_str[wire_type]})"
        # raise pparse.UnsupportedFormatException(msg)





























# Example protobuf/onnx parse of GPT2.onnx
"""
        ModelProto
        08 07   ir_version = 7
        12 07   producer_name LEN: 7
            70 79 74 6f 72 63 68   = 'pytorch'
        1a 05   producer_version LEN: 5
            32 2e 30 2e 31   = '2.0.1'
    18: 3a 96 cc d8 b7 02 = GraphProto graph LEN: 653665814
    24:   0a 43 node[0] LEN: 67
    26:     0a 09 input LEN: 9
                69 6e 70 75 74 5f 69 64 73 input_ids
            12 1b output LEN: 27
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 53 68 61 70 65 5f 6f 75 74 70 75 74 5f 30
                /transformer/Shape_output
            1a 12 name LEN: 18
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 53 68 61 70 65 /transformer/Shape
            22 05 op_type LEN: 5
                53 68 61 70 65 = Shape
            0a 5b node[1] LEN: 91
            12 1e output LEN: 30
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 43 6f  /transformer/Constant_output_0
                6e 73 74 61 6e 74 5f 6f 75 74 70 75 74 5f 30
            1a 15 name LEN: 21
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 43 6f 6e 73 74 61 6e 74 ./transformer/Constant
            22 08 optype LEN: 8
                43 6f 6e 73 74 61 6e 74  Constant
            2a 18 AttributeProto attribute LEN: 24
                0a 05 name LEN: 5
                76 61 6c 75 65 'value'
                2a 0c TensorProto t LEN: 12
                10 - int32 data_type
                    07 - 7
                4a 08 raw_data LEN: 8
                    00 00 00 00 00 00 00 00
                a0 01 LEN: 1
                04 type = TENSOR
            0a 85 01 node[2] LEN: 133
            0a 1b input[0] LEN: 27
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 53 68 61 70 65 5f 6f 75 74 70 75 74 5f 30 '/transformer/Shape_output_0'
            0a 1e input[1] LEN: 30
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 43 6f 6e 73 74 61 6e 74 5f 6f 75 74 70 75 74 5f 30 '/transformer/Constant_output_0'
            12 1c output[0] LEN: 28
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 47 61 74 68 65 72 5f 6f 75 74 70 75 74 5f 30 '/transformer/Gather_output_0'
            1a 13 name LEN: 19
                2f 74 72 61 6e 73 66 6f 72 6d 65 72 2f 47 61 74 68 65 72  '/transformer/Gather'
            22 06 op_type LEN: 6
                47 61 74 68 65 72 'Gather'
            2a 0b attribute LEN: 11
                0a 04 name LEN: 4
                61 78 69 73 'axis'
                18 00 i = 0
                a0 01 type = FLOAT
                02 - ???

            0a 47 node[3] LEN: 71
            0a 09 input[0]
                69 6e 70 75 74 5f 69 64 73 input_ids
            12 ...
    00000150: ...
"""

# class ProtobufParsingKey(ProtobufParsingState):
#     """
#     TODO: Things not done:
#     - No zigzag support
#     - No map support
#     - No 2's complement
#     - No signed vs unsigned
#     - Needs heuristic guessing when pb2 can't help.
#     - Deferred loading not tested.
#     - No support for sgroup/egroup.
#     """

#     def parse_data(self, node: pparse.Node):
#         ctx = node.ctx()
#         parser = ctx.parser()

#         if ctx.left() == 0:
#             if ctx._parent is None:
#                 raise pparse.EndOfDataException("Nothing more to process.")

#             # Node length not set until after _end_container_node()
#             parser._end_container_node(ctx)

#             ctx._next_state(ProtobufParsingKey)
#             return

#         # if ctx.node().msgtype().name not in [
#         #     'ModelDef', 'graph', 'GraphDef', 's', 'AttrEntry', 'input',
#         #     'op', 'OpDef', 'attr', 'AttrDef', 'ListValue', 'b', 'i', 'dst_name',
#         #     'dst_index', 'output_i', 'input_desc', 'dtype', 'TensorDescriptor',

#         #     ]:
#         #     breakpoint()

#         # Get the key data.
#         wire_type, field_num, meta_length, value_length = parser.peek_varint_key(ctx)

#         field = None
#         if isinstance(ctx.node(), NodeMap):
#             field = ctx.node().field_by_id(field_num)
#         elif isinstance(ctx.node(), NodeArray):
#             try:
#                 field = ctx._parent.field_by_id(field_num)
#             except KeyError as e:
#                 breakpoint()
#         else:  # UNLIKELY
#             breakpoint()

#         log.debug(
#             f"\nPROCESSING FIELD (off: {ctx.tell()} left: {ctx.left()}): {field.name}   {field.type_name}\n"
#         )

#         if (
#             isinstance(parser.current, NodeArray)
#             and ctx.key()
#             and field.name != ctx.key().name
#         ):
#             # Pop NodeArray if complete, but not done with parent NodeMap.
#             log.debug(f"Ending NodeArray for repeated field {ctx.key().name}")
#             parser._end_container_node(ctx)
#             return

#         # The following things are in an array, set that up first.
#         # Note: Assuming you can not do NodeArray.value = [NodeArray]
#         if field.label == Field.LABEL_REPEATED and not isinstance(
#             parser.current, NodeArray
#         ):
#             log.debug(f"Creating NodeArray for repeated field {field.name}")

#             ctx.mark_field_start()
#             parent = parser.current
#             # Note: ctx.reader() returns duplicate.
#             # 'field' is more universal than 'msgtype' for array nodes
#             newarr = NodeArray(parent, ctx.reader(), field)

#             # Assuming array parent is always a map.
#             parser.current.value[field.name] = newarr
#             parser.current = parser.current.value[field.name]

#             # We're in a new _repeated_ _numeric_ field with wire_type == 2,
#             # we're likely packed. Lets peek the length and verify it matches
#             # value_length.
#             # if value_length == 6:
#             #     if wire_type == Protobuf.LEN and field.type in [
#             #         Field.TYPE_INT64, Field.TYPE_UINT64,
#             #     ]:
#             #         # TODO: Should be new state.
#             #         # Read varints until value_length bytes consumed.
#             #         while (ctx.left() - meta_length) > 0:
#             #             print(parser.parse_varint(ctx))
#             #         parser._end_container_node(ctx)
#             #         breakpoint()
#             #         return
#             # else:
#             ctx._next_state(ProtobufParsingKey)

#             return

#         # Progress past the key.
#         ctx.set_key(field)
#         ctx.skip(meta_length)

#         # if field.type in [Field.TYPE_INT64, Field.TYPE_UINT64] and wire_type == Protobuf.LEN:
#         #     breakpoint()
#         #     return

#         if field.type == Field.TYPE_MESSAGE and value_length:
#             log.debug(
#                 f"  LENGTH: {value_length} (meta_length: {meta_length}) range: {ctx.tell()} - {ctx.tell() + value_length}"
#             )

#             # Create the new node and make it active.
#             parser._start_map_node(ctx, field)

#             # Save the length of the message in the new node.
#             parser.current.ctx().reinit(ctx.tell(), value_length)
#             return

#         # if field.type == Field.TYPE_BOOL:
#         #     value = parser.parse_varint(ctx)
#         #     parser._apply_value(ctx, field, value)
#         #     ctx._next_state(ProtobufParsingKey)
#         #     return

#         if field.type == Field.TYPE_INT64 or field.type == Field.TYPE_INT32 or \
#             field.type == Field.TYPE_UINT64 or field.type == Field.TYPE_UINT32 or \
#             field.type == Field.TYPE_BOOL:

#             if wire_type == Protobuf.LEN and isinstance(parser.current, NodeArray):
#                 #breakpoint()
#                 # Handle repeated-packed numerical things
#                 while ctx.left() > 0:
#                     val = parser.parse_varint(ctx)
#                     #print(val)
#                     parser._apply_value(ctx, field, val)

#                 ctx._next_state(ProtobufParsingKey)
#                 return

#             # TODO: Should this handle 2's compliment?
#             value = parser.parse_varint(ctx)
#             parser._apply_value(ctx, field, value)
#             ctx._next_state(ProtobufParsingKey)
#             return

#         if field.type == Field.TYPE_ENUM and wire_type == Protobuf.VARINT:
#             # Get the length of the sub-message.
#             enum = parser.parse_varint(ctx)
#             parser._apply_value(ctx, field, enum)

#             ctx._next_state(ProtobufParsingKey)
#             return

#         if field.type == Field.TYPE_FLOAT and wire_type == Protobuf.I32:
#             # Get the length of the sub-message.
#             value = ctx.read(4)
#             float_value = struct.unpack("<f", value)[0]
#             parser._apply_value(ctx, field, float_value)

#             ctx._next_state(ProtobufParsingKey)
#             return

#         if field.type == Field.TYPE_STRING and wire_type == Protobuf.LEN:
#             data = ctx.read(value_length)
#             if len(data) <= 40:
#                 log.debug(f"Whole String: {data}")
#             else:
#                 log.debug(
#                     f"Part of String (length {len(data)}): {data.decode('utf-8')[:40]}"
#                 )

#             log.debug(f"String: {data}")
#             if (value_length > 0 and not data) or len(data) < value_length:
#                 msg = (
#                     "Not enough data to parse Protobuf LEN data. "
#                     f"Offset: {ctx.tell()} Read: {len(data)} of {value_length}"
#                 )
#                 raise pparse.EndOfDataException(msg)
#             parser._apply_value(ctx, field, data.decode("utf-8"))

#             ctx._next_state(ProtobufParsingKey)
#             return

#         if field.type == Field.TYPE_BYTES:
#             data = ctx.read(value_length)
#             if len(data) <= 40:
#                 log.debug(f"All Bytes: {data}")
#             else:
#                 log.debug(f"First Bytes (length {len(data)}): {data[:40]}")

#             if (value_length > 0 and not data) or len(data) < value_length:
#                 msg = (
#                     "Not enough data to parse Protobuf LEN data. "
#                     f"Offset: {ctx.tell()} Read: {len(data)} of {value_length}"
#                 )
#                 raise pparse.EndOfDataException(msg)

#             parser._apply_value(ctx, field, data)

#             ctx._next_state(ProtobufParsingKey)
#             return

#         log.debug(f"UNKNOWN FIELD OR WIRE TYPE {wire_type} {field.type}")
#         breakpoint()

#         msg = f"Not a valid Protobuf wire type. Type: {wire_type} ({Protobuf.wire_type_str[wire_type]})"
#         raise pparse.UnsupportedFormatException(msg)
