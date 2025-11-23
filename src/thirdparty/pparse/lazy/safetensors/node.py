#!/usr/bin/env python3

import logging
log = logging.getLogger(__name__)

from thirdparty.pparse.lazy.safetensors.state import SafetensorsParsingLength
from thirdparty.pparse import lib as pparse

from thirdparty.pparse.lib import (
    EndOfDataException,
    UnsupportedFormatException,
    EndOfNodeException
)


class UnloadedValue():
    def __repr__(self): return "<UNLOADED_VALUE />"
UNLOADED_VALUE = UnloadedValue()


class Node():
    def __init__(self, parent: 'Node', reader: pparse.Reader):
        self._reader : Reader = reader.dup()        
        self.value = UNLOADED_VALUE
        self._ctx = pparse.NodeContext(self, parent, SafetensorsParsingLength(), reader.dup())

    
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


    # Assumed that this method is not run until after the Extraction parsing is complete.
    def load(self, parser):
        # Create a headless node to parse the data.
        self._ctx = pparse.NodeContext(self, None, SafetensorsParsingLength(), self._reader.dup())
        # Reset to beginning of field.
        self._ctx.seek(0)

        # Run the parser.
        parser.current = self
        # While not end of data, keep parsing via states.
        try:
            while True:
                ctx = parser.current.ctx()
                state = ctx.state()
                # if isinstance(state, JsonParsingString):
                #     breakpoint()
                state.parse_data(parser, ctx)
        except EndOfNodeException as e:
            pass
        except EndOfDataException as e:
            pass
        except UnsupportedFormatException:
            raise

    
    def unload(self):
        self.value = UNLOADED_VALUE


    def dumps(self, depth=0, step=2):
        spacer = ' ' * depth
        result = [f"{spacer}" f'<SafetensorsNode length="{self.length()}" offset="{self.tell()}">']
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth+step)}")
        else:
            result.append(f"{spacer}{' '*step}{self.value}")
        result.append(f"{spacer}</SafetensorsNode>")
        return '\n'.join(result)


class NodeInit(Node):
    def __init__(self, parent: Node, reader: pparse.Reader, parser: pparse.Parser = None):
        super().__init__(parent, reader)

        # Since there is only 1 NodeInit, we can keep more stuff here.
        self.parser = parser

    
    def dumps(self, depth=0, step=2):
        spacer = ' ' * depth
        result = [f"{spacer}" f'<SafetensorsNodeInit>']
        if isinstance(self.value, Node):
            result.append(f"{spacer}{self.value.dumps(depth+step)}")
        else:
            result.append(f"{spacer}{self.value}")
        result.append(f"{spacer}</SafetensorsNodeInit>")
        return '\n'.join(result)



