#!/usr/bin/env python3

import logging
import numbers

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
#from thirdparty.pparse.lib import NodeContext as BaseNodeContext


class NodeContext(pparse.NodeContext):
    def __init__(self, parent: pparse.Node, reader: pparse.Reader, parser: pparse.Parser):
        super().__init__(parent, reader, parser)

        self._type_desc = None
        self._abs_off = None

        self._fields_created = False

    def type_desc(self):
        return self._type_desc


# class NodeContext(BaseNodeContext):
#     def __init__(
#         self,
#         node: "Node",
#         parent: "Node",
#         state: "FlatbuffersParsingState",
#         reader: pparse.Range,
#     ):
#         if type(reader).__name__ != "Range":
#             raise Exception("flatbuffer NodeContext reader must be a pparse.Range")
#         super().__init__(node, parent, reader)
#         self._next_state(state)
#         self._key = None
#         self.just_set_node = False
#         self.just_set_field = None

#     def key(self):
#         return self._key

#     def set_key(self, field):
#         self._key = field

#     def left(self):
#         return self._reader.left()

#     def reinit(self, start_offset, length, current_offset=-1):
#         return self._reader._init(start_offset, length, current_offset)


# class Node(pparse.Node):
#     # Note: All readers are Ranges. Range is required to process protobuf.
#     def __init__(self, parent: "Node", reader: pparse.Reader, abs_offset=0):
#         from thirdparty.pparse.lazy.flatbuffers.state import FlatbuffersParsingRootTableOffset
#         self._reader = reader.dup()
#         self._ctx = NodeContext(self, parent, FlatbuffersParsingRootTableOffset, reader.dup())

#         # top_reader offset
#         self._abs_offset = abs_offset
#         self._value = pparse.UNLOADED_VALUE

#     @property
#     def value(self):
#         if self._value == pparse.UNLOADED_VALUE:
#             # parse it now
#             pass
#         return self._value

#     def abs_offset(self):
#         return self._abs_offset

#     def field_by_id(self, field_num):
#         return self._type.by_id(field_num)

#     def msgtype(self):
#         return self._type

#     # Assumed that this method is not run until after the Extraction parsing is complete.
#     # TODO: Test this.
#     def load(self, parser):
#         raise NotImplementedError("load() not yet implemented")
#         # from thirdparty.pparse.lazy.flatbuffers import ProtobufParsingKey

#         # # Create a headless node to parse the data.
#         # self._ctx = NodeContext(self, None, ProtobufParsingKey(), self._reader.dup())
#         # # Reset to beginning of field.
#         # self._ctx.seek(0)

#         # parser.current = self
#         # # While not end of data, keep parsing via states.
#         # try:
#         #     while True:
#         #         ctx = parser.current.ctx()
#         #         state = ctx.state()
#         #         state.parse_data(parser, ctx)
#         # except pparse.EndOfNodeException as e:
#         #     pass
#         # except pparse.EndOfDataException as e:
#         #     pass
#         # except pparse.UnsupportedFormatException:
#         #     raise


#     def dumps(self, depth=0, step=2):
#         # spacer = " " * depth
#         # result = [
#         #     f'{spacer}<ProtobufNode length="{self.length()}" offset="{self.tell()}">'
#         # ]
#         # if isinstance(self.value, Node):
#         #     result.append(f"{spacer}{self.value.dumps(depth + step)}")
#         # else:
#         #     result.append(f"{spacer}{' ' * step}{self.value}")
#         # result.append(f"{spacer}</ProtobufNode>")
#         # return "\n".join(result)
#         return ''

#     # def __repr__(self):
#     #     # Designed for usage in breakpoint()s and REPLs
#     #     # py_type = "Node"
#     #     # msg_type = "UNKNOWN"
#     #     # if self._type:
#     #     #     msg_type = self._type.name
#     #     # val_type = type(self.value).__name__
#     #     # return f"{py_type}(_type={msg_type}, value={val_type})"
#     #     return ''


# class NodeVTable(Node):
#     def __init__(self, parent: Node, reader: pparse.Reader, type_desc=None):
#         super().__init__(parent, reader)
#         self._type = type_desc
#         self.table_length = 0
#         self.vtable_length = 0
#         self.field_lengths = []

#     def type_desc(self):
#         return self._type

# class NodeTable(Node):
#     def __init__(self, parent: Node, reader: pparse.Reader, type_desc=None):
#         super().__init__(parent, reader)
#         self._type = type_desc
#         self.vtable = None
#         self._value = pparse.UNLOADED_VALUE

#     @property
#     def value(self):
#         if self._value == pparse.UNLOADED_VALUE:
#             # parse it now
#             pass
#         return self._value


#     def type_desc(self):
#         return self._type

#     def type_name(self):
#         return self.type_desc()['name'] if 'name' in self.type_desc() else 'UNSET'

#     def dumps(self, depth=0, step=2):
#         spacer = " " * depth
#         # proto_type = self.msgtype().name
#         result = [
#             f'{spacer}<FlatbuffersNodeTable abs_off="0x{self.abs_offset():x}" type="{self.type_name()}">{{'
#         ]
#         for k, v in self.value.items():
#             if isinstance(v, Node):
#                 result.append(f"{spacer}{' ' * step}{k}:")
#                 result.append(f"{v.dumps(depth + (step * 2))}")
#             else:
#                 if isinstance(v, numbers.Number):
#                     result.append(f"{spacer}{' ' * step}{k}: {v} {hex(v)}")
#                 else:
#                     v_str = f"{v}"
#                     if len(v_str) < 40:
#                         result.append(f"{spacer}{' ' * step}{k}: {v}")
#         result.append(f"{spacer}}}</FlatbuffersNodeTable>")
#         return "\n".join(result)

#     # def __repr__(self):
#     #     # Designed for usage in breakpoint()s and REPLs
#     #     # py_type = "NodeMap"
#     #     # msg_type = "UNKNOWN"
#     #     # if self._type:
#     #     #     msg_type = self._type.name
#     #     # val_type = type(self.value).__name__
#     #     # name = ""
#     #     # if self.value and "name" in self.value:
#     #     #     name = f"name={self.value['name']}, "
#     #     # return f"{py_type}(_type={msg_type}, {name}value={val_type})"
#     #     return ''


# def hex_sample(data):
#     if len(data) <= 16:
#         return " ".join(f"{b:02x}" for b in data)

#     return (
#         " ".join(f"{b:02x}" for b in data[:8])
#         + " ... "
#         + " ".join(f"{b:02x}" for b in data[-8:])
#     )


# class NodeField(Node):
#     def __init__(self, parent: Node, reader: pparse.Reader, abs_offset=0, type_desc=None):
#         super().__init__(parent, reader, abs_offset)
#         self._type_desc = type_desc
#         self.value = None

#     def name(self):
#         return self._type_desc['name']
    
#     def type_desc(self):
#         return self._type_desc

#     def base_type(self):
#         return self._type_desc['type']['base_type']

#     def parse_value(self, parser: "Parser", ctx: "NodeContext"):
#         # Scalars are inplace, do those first.
#         if self.base_type() in parser.schema.TYPE_SIZES:
#             # Scalar value stored inline
#             ctx.seek(field_pos)
#             self.value = parser.read_scalar(ctx, base_type)
#             return
#         # Strings are nice and simple.
#         if self.base_type() == 'String':
#             # Seek to string offset
#             ctx.seek(field_pos)
#             ctx.seek(field_pos + parser.peek_u32(ctx))
#             # TODO: Do we create a NodeString? Pythonic str for now.
#             self.value = parser.read_string(ctx)
#             return
#         # Vectors are common and require a new node.
#         if self.base_type() == 'Vector':
#             breakpoint() # ! ... we want to scan all vector values ... then decend!
#             # Seek to vector offset
#             ctx.seek(field_pos)
#             vector_pos = field_pos + parser.peek_u32(ctx)

#             self.value = NodeVector(ctx.node(), ctx.reader(), vector_pos, field_type)
#             #parser.current = table.value[field_name]
#             #parser.current.ctx()._next_state(FlatbuffersParsingVector)
#             ctx.field_idx += 1
#             return
#         '''
#             # if self.base_type() == 'Union':
#             #     # Skip and let the UType base_type drive both Union and UType parsing.
#             #     ctx.field_idx += 1
#             #     return
#             # if self.base_type() == 'UType':
#             #     breakpoint() # ! deferred
#             #     # Get the UType index
#             #     utype_idx = field_type.get('index', 0)

#             #     # # Check if the union has content.
#             #     # if utype_idx == 0:
#             #     #     # Nothing
#             #     #     table.value[field_name] = None
#             #     #     ctx.field_idx += 1
#             #     #     return

#             #     # Locate the paired Union field
#             #     union_desc = None
#             #     for field_entry in ctx.fields_desc:
#             #         if 'type' in field_entry and 'index' in field_entry['type'] and \
#             #             field_entry['type']['index'] == utype_idx:
#             #             union_desc = field_entry
#             #             break
#             #     if union_desc is None:
#             #         raise ValueError(f"Union index {utype_idx} not found for {field_name}.")

#             #     union_name = union_desc['name']

#             #     # Get the enum type associated with utype_idx
#             #     enum_type = parser.schema.enums_by_index[utype_idx]
                
#             #     # Get the enum value (utype). (enum_value == 0 means no content.)
#             #     # NOTE: Defined by underlying_type, but assuming 1 byte with 3 padded zeros.
#             #     ctx.seek(field_pos)
#             #     # TODO: Check for return.
#             #     enum_value = struct.unpack('B', ctx.peek(1))[0]
#             #     #enum_value = parser.peek_u32(ctx)
                
#             #     forward_align = lambda value: value + (4 - value % 4) if value % 4 != 0 else value
#             #     union_offset_pos = forward_align(field_pos + 1)

#             #     # Get the union table offset (union)
#             #     ctx.seek(union_offset_pos)
#             #     union_pos = union_offset_pos + parser.peek_u32(ctx)

#             #     # Get the entry from enum_type who has the enum_value as value
#             #     enum_desc = None
#             #     for enum_entry in enum_type['values']:
#             #         if enum_entry['value'] == enum_value:
#             #             enum_desc = enum_entry
#             #             break
#             #     if enum_desc is None:
#             #         raise ValueError(f"Enum {utype_idx} desc for value {enum_value} not found.")
                
#             #     union_base_type = enum_desc['union_type']['base_type']

#             #     if union_base_type == 'Obj':
#             #         table_pos = union_pos
#             #         type_index = enum_desc['union_type']['index']
#             #         type_desc = parser.schema.objects_by_index[type_index]
#             #         table.value[union_name] = NodeTable(ctx.node(), ctx.reader(), union_pos, type_desc)

#             #         parser.current = table.value[union_name]
#             #         parser.current.ctx()._next_state(FlatbuffersParsingTable)
#             #         ctx.field_idx += 1
#             #         return

#             #     # Catch all for unsupported union_base_type
#             #     msg = f"Unsupported base type while parsing union {union_name} at {table.abs_offset()}"
#             #     print(msg)
#             #     breakpoint()
#             #     raise ValueError(msg)
#         '''

#         if self.base_type() == 'Obj':
#             # Seek to vector offset
#             ctx.seek(field_pos)
#             table_pos = field_pos + parser.peek_u32(ctx)

#             # Get the table schema stuff
#             breakpoint() # ! ... we want to scan all vector values ... then decend!
#             type_index = self.type_desc()['index']
#             if type_index is None:
#                 raise ValueError("Vector of objects missing 'index' field")
#             if type_index not in parser.schema.objects_by_index:
#                 raise ValueError(f"Unknown object index: {type_index}")

#             type_desc = parser.schema.objects_by_index[type_index]
#             self.value = NodeTable(ctx.node(), ctx.reader(), table_pos, type_desc)

#             #parser.current = table.value[field_name]
#             #parser.current.ctx()._next_state(FlatbuffersParsingTable)
#             ctx.field_idx += 1
#             return


#         # Catch all for unsupported element_types
#         print(f"Unsupported byte type while parsing table: {base_type}")
#         breakpoint()
#         raise ValueError(f"Unsupported byte type while parsing table: {base_type}")


# class NodeVector(Node):
#     def __init__(self, parent: Node, reader: pparse.Reader, abs_offset=0, type_desc=None):
#         super().__init__(parent, reader, abs_offset)
#         self._type = type_desc
#         self.value = []

#     def type_desc(self):
#         return self._type
    
#     def type_name(self):
#         # Look up vector types by index.
#         if self.type_desc()['element'] == 'Obj' and hasattr(self, 'elem_desc'):
#             return self.elem_desc['name']
#         if self.type_desc()['element'] in ['UByte', 'String']:
#             return self.type_desc()['element']
#         return 'UNSET'

#     def dumps(self, depth=0, step=2):
#         spacer = " " * depth
#         # proto_type = self.msgtype().name
#         result = [
#             f'{spacer}<FlatbuffersNodeVector abs_off="0x{self.tell():x}" count="{len(self.value)}" type="{self.type_name()}">['
#         ]
#         if self.type_desc()['element'] == 'UByte':
#             result.append(f"{spacer}{' ' * step}{hex_sample(self.value)}")
#         else:
#             for e in self.value:
#                 if isinstance(e, Node):
#                     result.append(f"{e.dumps(depth + step)}")
#                 else:
#                     result.append(f"{spacer}{' ' * step}{e}")
#         result.append(f"{spacer}]</FlatbuffersNodeVector>")
#         return "\n".join(result)

#     # def __repr__(self):
#     #     # # Designed for usage in breakpoint()s and REPLs
#     #     # py_type = "NodeArray"
#     #     # msg_type = "UNKNOWN"
#     #     # if self._type:
#     #     #     msg_type = self._type.name
#     #     # val_type = type(self.value).__name__
#     #     # return f"{py_type}(_type={msg_type}, value={val_type})"
#     #     return ''
