#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lib import NodeContext as BaseNodeContext


class UnloadedValue:
    def __repr__(self):
        return "<UNLOADED_VALUE />"


UNLOADED_VALUE = UnloadedValue()


class NodeContext(BaseNodeContext):
    def __init__(
        self,
        node: "Node",
        parent: "Node",
        state: "FlatbuffersParsingState",
        reader: pparse.Range,
    ):
        if type(reader).__name__ != "Range":
            raise Exception("flatbuffer NodeContext reader must be a pparse.Range")
        super().__init__(node, parent, reader)
        self._next_state(state)
        self._key = None
        self.just_set_node = False
        self.just_set_field = None

    def key(self):
        return self._key

    def set_key(self, field):
        self._key = field

    def left(self):
        return self._reader.left()

    def reinit(self, start_offset, length, current_offset=-1):
        return self._reader._init(start_offset, length, current_offset)


class Node:
    # Note: All readers are Ranges. Range is required to process protobuf.
    def __init__(self, parent: "Node", reader: pparse.Reader, abs_offset=0):
        from thirdparty.pparse.lazy.flatbuffers.state import FlatbuffersParsingRootTableOffset
        self._reader = reader.dup()
        self._ctx = NodeContext(self, parent, FlatbuffersParsingRootTableOffset, reader.dup())

        # top_reader offset
        self._abs_offset = abs_offset
        self.value = UNLOADED_VALUE

    def abs_offset(self):
        return self._abs_offset

    def field_by_id(self, field_num):
        return self._type.by_id(field_num)

    def ctx(self):
        return self._ctx

    def clear_ctx(self):
        self._ctx = None
        return self

    def tell(self):
        return self._reader.tell()

    def final_length(self, length):
        self._reader = pparse.Range(self._reader.dup(), length)
        return self

    def length(self):
        return self._reader.length()

    def msgtype(self):
        return self._type

    # Assumed that this method is not run until after the Extraction parsing is complete.
    # TODO: Test this.
    def load(self, parser):
        raise NotImplementedError("load() not yet implemented")
        # from thirdparty.pparse.lazy.flatbuffers import ProtobufParsingKey

        # # Create a headless node to parse the data.
        # self._ctx = NodeContext(self, None, ProtobufParsingKey(), self._reader.dup())
        # # Reset to beginning of field.
        # self._ctx.seek(0)

        # parser.current = self
        # # While not end of data, keep parsing via states.
        # try:
        #     while True:
        #         ctx = parser.current.ctx()
        #         state = ctx.state()
        #         state.parse_data(parser, ctx)
        # except pparse.EndOfNodeException as e:
        #     pass
        # except pparse.EndOfDataException as e:
        #     pass
        # except pparse.UnsupportedFormatException:
        #     raise

    def unload(self):
        self.value = UNLOADED_VALUE

    def dumps(self, depth=0, step=2):
        # spacer = " " * depth
        # result = [
        #     f'{spacer}<ProtobufNode length="{self.length()}" offset="{self.tell()}">'
        # ]
        # if isinstance(self.value, Node):
        #     result.append(f"{spacer}{self.value.dumps(depth + step)}")
        # else:
        #     result.append(f"{spacer}{' ' * step}{self.value}")
        # result.append(f"{spacer}</ProtobufNode>")
        # return "\n".join(result)
        return ''

    # def __repr__(self):
    #     # Designed for usage in breakpoint()s and REPLs
    #     # py_type = "Node"
    #     # msg_type = "UNKNOWN"
    #     # if self._type:
    #     #     msg_type = self._type.name
    #     # val_type = type(self.value).__name__
    #     # return f"{py_type}(_type={msg_type}, value={val_type})"
    #     return ''


class NodeVTable(Node):
    def __init__(self, parent: Node, reader: pparse.Reader, abs_offset=0, type_desc=None):
        super().__init__(parent, reader, abs_offset)
        self._type = type_desc
        self.table_length = 0
        self.vtable_length = 0
        self.field_lengths = []

    def type_desc(self):
        return self._type

class NodeTable(Node):
    def __init__(self, parent: Node, reader: pparse.Reader, abs_offset=0, type_desc=None):
        super().__init__(parent, reader, abs_offset)
        self._type = type_desc
        self.vtable = None
        self.value = {}

    def type_desc(self):
        return self._type

    def dumps(self, depth=0, step=2):
        # spacer = " " * depth
        # proto_type = self.msgtype().name
        # result = [
        #     f'{spacer}<ProtobufMapNode type="{proto_type}" offset="{self.tell()}">{{'
        # ]
        # for k, v in self.value.items():
        #     if isinstance(v, Node):
        #         result.append(f"{spacer}{' ' * step}{k}:")
        #         result.append(f"{v.dumps(depth + (step * 2))}")
        #     else:
        #         v_str = f"{v}"
        #         if len(v_str) < 40:
        #             result.append(f"{spacer}{' ' * step}{k}: {v}")
        # result.append(f"{spacer}}}</ProtobufMapNode>")
        # return "\n".join(result)
        return ''

    # def __repr__(self):
    #     # Designed for usage in breakpoint()s and REPLs
    #     # py_type = "NodeMap"
    #     # msg_type = "UNKNOWN"
    #     # if self._type:
    #     #     msg_type = self._type.name
    #     # val_type = type(self.value).__name__
    #     # name = ""
    #     # if self.value and "name" in self.value:
    #     #     name = f"name={self.value['name']}, "
    #     # return f"{py_type}(_type={msg_type}, {name}value={val_type})"
    #     return ''


class NodeVector(Node):
    def __init__(self, parent: Node, reader: pparse.Reader, abs_offset=0, type_desc=None):
        super().__init__(parent, reader, abs_offset)
        self._type = type_desc
        self.value = []

    def type_desc(self):
        return self._type

    def dumps(self, depth=0, step=2):
        # spacer = " " * depth
        # proto_type = self.msgtype().name
        # result = [
        #     f'{spacer}<ProtobufArrayNode type="{proto_type}" offset="{self.tell()}">['
        # ]
        # for e in self.value:
        #     if isinstance(e, Node):
        #         result.append(f"{e.dumps(depth + step)}")
        #     else:
        #         result.append(f"{spacer}{' ' * step}{e}")
        # result.append(f"{spacer}]</ProtobufArrayNode>")
        # return "\n".join(result)
        return ''

    # def __repr__(self):
    #     # # Designed for usage in breakpoint()s and REPLs
    #     # py_type = "NodeArray"
    #     # msg_type = "UNKNOWN"
    #     # if self._type:
    #     #     msg_type = self._type.name
    #     # val_type = type(self.value).__name__
    #     # return f"{py_type}(_type={msg_type}, value={val_type})"
    #     return ''
