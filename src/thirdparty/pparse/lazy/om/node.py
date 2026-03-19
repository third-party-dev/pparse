#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lib import NodeContext as BaseNodeContext


class NodeContext(BaseNodeContext):
    def __init__(
        self,
        node: "Node",
        parent: "Node",
        state: "OmParsingState",
        reader: pparse.Range,
    ):
        if type(reader).__name__ != "Range":
            raise Exception("om NodeContext reader must be a pparse.Range")
        super().__init__(node, parent, reader)
        self._next_state(state)
        self._key = None

    # def key(self):
    #     return self._key

    # def set_key(self, field):
    #     self._key = field

    # DUP
    # def left(self):
    #     return self._reader.left()

    def reinit(self, start_offset, length, current_offset=-1):
        return self._reader._init(start_offset, length, current_offset)


class Node(pparse.Node):
    # Note: All Protobuf readers are Ranges. Range is required to process protobuf.
    def __init__(self, parent: "Node", reader: pparse.Range):
        if type(reader).__name__ != "Range":
            raise Exception("protobuf Node reader must be a pparse.Range")
        self._reader: pparse.Range = reader.dup()

        from thirdparty.pparse.lazy.om.state import OmParsingHeader

        self._ctx = NodeContext(self, parent, OmParsingHeader, reader.dup())

        self.value = pparse.UNLOADED_VALUE

    # Assumed that this method is not run until after the Extraction parsing is complete.
    # TODO: Test this.
    def load(self, parser):
        pass

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<OmNode length="{self.length()}" offset="{self.tell()}">'
        ]
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth + step)}")
        else:
            result.append(f"{spacer}{' ' * step}{self.value}")
        result.append(f"{spacer}</OmNode>")
        return "\n".join(result)


class NodeMap(Node):
    def __init__(self, parent: Node, reader: pparse.Reader):
        super().__init__(parent, reader)
        self.value = {}

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<OmMapNode offset="{self.tell()}">{{'
        ]
        for k, v in self.value.items():
            if isinstance(v, Node):
                result.append(f"{spacer}{' ' * step}{k}:")
                result.append(f"{v.dumps(depth + (step * 2))}")
            else:
                v_str = f"{v}"
                if len(v_str) < 40:
                    result.append(f"{spacer}{' ' * step}{k}: {v}")
        result.append(f"{spacer}}}</OmMapNode>")
        return "\n".join(result)


class NodeArray(Node):
    def __init__(self, parent: Node, reader: pparse.Reader):
        super().__init__(parent, reader)
        self.value = []

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<OmArrayNode offset="{self.tell()}">['
        ]
        for e in self.value:
            if isinstance(e, Node):
                result.append(f"{e.dumps(depth + step)}")
            else:
                result.append(f"{spacer}{' ' * step}{e}")
        result.append(f"{spacer}]</OmArrayNode>")
        return "\n".join(result)
