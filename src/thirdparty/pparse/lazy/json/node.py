#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json.state import JsonParsingStart


class NodeContext(pparse.NodeContext):
    def __init__(self, node: "Node", parent: "Node", reader: pparse.Reader):
        super().__init__(node, parent, reader)
        self._key_reg = None

    def key(self):
        return self._key_reg

    def set_key(self, v):
        self._key_reg = v
        return self


class Node(pparse.Node):
    def __init__(
        self, parent: "Node", reader: pparse.Reader, ctx: pparse.NodeContext = None
    ):
        super().__init__(parent, reader, ctx)
        self.ctx()._next_state(JsonParsingStart)

    def final_length(self, length):
        self._reader = pparse.Range(self._reader.dup(), length)
        return self

    # Assumed that this method is not run until after the Extraction parsing is complete.
    def load(self, parser):
        # Create a headless node to parse the data.
        self._ctx = NodeContext(self, None, self._reader.dup())
        self.ctx()._next_state(JsonParsingStart)
        # Reset to beginning of field.
        self._ctx.seek(0)

        parser.current = self
        # While not end of data, keep parsing via states.
        try:
            while True:
                ctx = parser.current.ctx()
                state = ctx.state()
                # if isinstance(state, JsonParsingString):
                #     breakpoint()
                state.parse_data(parser, ctx)
        except pparse.EndOfNodeException as e:
            pass
        except pparse.EndOfDataException as e:
            pass
        except pparse.UnsupportedFormatException:
            raise

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [f'{spacer}<JsonNode length="{self.length()}" offset="{self.tell()}">']
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth + step)}")
        else:
            result.append(f"{spacer}{' ' * step}{self.value}")
        result.append(f"{spacer}</JsonNode>")
        return "\n".join(result)


class NodeInit(Node):
    def __init__(
        self, parent: Node, reader: pparse.Reader, parser: pparse.Parser = None
    ):
        ctx = NodeContext(self, parent, reader)
        super().__init__(parent, reader, ctx)

        # Since there is only 1 NodeInit, we can keep more stuff here.
        self.parser = parser

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        # result = [f"{spacer}" f'<NodeInit length="{self.length()}">']
        result = [f"{spacer}<JsonNodeInit>"]
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth + step)}")
        else:
            result.append(f"{spacer}{self.value}")
        result.append(f"{spacer}</JsonNodeInit>")
        return "\n".join(result)


class NodeMap(Node):
    def __init__(self, parent: Node, reader: pparse.Reader):
        ctx = NodeContext(self, parent, reader)
        super().__init__(parent, reader, ctx)
        self.value = {}

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<JsonMapNode length="{self.length()}" offset="{self.tell()}">{{'
        ]
        for k, v in self.value.items():
            if isinstance(v, Node):
                result.append(f"{spacer}{' ' * step}{k}:")
                result.append(f"{v.dumps(depth + (step * 2))}")
            else:
                result.append(f"{spacer}{' ' * step}{k}: {v}")
        result.append(f"{spacer}}}</JsonMapNode>")
        return "\n".join(result)


class NodeArray(Node):
    def __init__(self, parent: Node, reader: pparse.Reader):
        ctx = NodeContext(self, parent, reader)
        super().__init__(parent, reader, ctx)
        self.value = []

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<JsonArrayNode length="{self.length()}" offset="{self.tell()}">['
        ]
        for e in self.value:
            if isinstance(e, Node):
                result.append(f"{spacer}{e.dumps(depth + step)}")
            else:
                result.append(f"{spacer}{' ' * step}{e}")
        result.append(f"{spacer}]</JsonArrayNode>")
        return "\n".join(result)
