#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.safetensors.state import SafetensorsParsingLength


class Node(pparse.Node):
    def __init__(self, parent: "Node", reader: pparse.Reader):
        self._reader: Reader = reader.dup()
        self.value = pparse.UNLOADED_VALUE
        self._ctx = pparse.NodeContext(self, parent, reader.dup())
        self.ctx()._next_state(SafetensorsParsingLength)

    def final_length(self, length):
        self._reader = pparse.Range(self._reader.dup(), length)
        return self

    # Assumed that this method is not run until after the Extraction parsing is complete.
    def load(self, parser):
        # Create a headless node to parse the data.
        self._ctx = pparse.NodeContext(self, None, self._reader.dup())
        # Reset to beginning of field.
        self.ctx()._next_state(SafetensorsParsingLength)
        self.ctx().seek(0)

        # Run the parser.
        parser.current = self
        # While not end of data, keep parsing via states.
        try:
            while True:
                ctx = parser.current.ctx()
                state = ctx.state()
                state.parse_data(parser, ctx)
        except pparse.EndOfNodeException as e:
            pass
        except pparse.EndOfDataException as e:
            pass
        except pparse.UnsupportedFormatException:
            raise

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [
            f'{spacer}<SafetensorsNode length="{self.length()}" offset="{self.tell()}">'
        ]
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth + step)}")
        else:
            result.append(f"{spacer}{' ' * step}{self.value}")
        result.append(f"{spacer}</SafetensorsNode>")
        return "\n".join(result)


class NodeInit(Node):
    def __init__(
        self, parent: Node, reader: pparse.Reader, parser: pparse.Parser = None
    ):
        super().__init__(parent, reader)

        # Since there is only 1 NodeInit, we can keep more stuff here.
        self.parser = parser

    def dumps(self, depth=0, step=2):
        spacer = " " * depth
        result = [f"{spacer}<SafetensorsNodeInit>"]
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth + step)}")
        else:
            result.append(f"{spacer}{self.value}")
        result.append(f"{spacer}</SafetensorsNodeInit>")
        return "\n".join(result)
