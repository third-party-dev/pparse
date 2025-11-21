#!/usr/bin/env python3

#from thirdparty.pparse.lazy.protobuf import ProtobufParsingState, ProtobufParsingKey
import thirdparty.pparse.lib as pparse


def trace(*args, **kwargs):
    print(*args, **kwargs)
    pass

class NodeContext(pparse.NodeContext):
    def __init__(self, node: 'Node', parent: 'Node', reader: pparse.Range):
        if type(reader).__name__ != 'Range':
            raise Exception("protobuf NodeContext reader must be a pparse.Range")
        super().__init__(node, parent, reader)


# An array of NodePickle objects.
class NodePickleArray(pparse.Node):
    def __init__(self, parent: pparse.Node, reader: pparse.Reader):
        super().__init__(parent, reader, NodeContext(self, parent, reader.dup()))
        self.value = []


# An array of PklOp objects.
class NodePickle(pparse.Node):
    def __init__(self, parent: pparse.Node, reader: pparse.Reader):
        super().__init__(parent, reader, NodeContext(self, parent, reader.dup()))
        self.ctx().pickle_entry = None
        self.value = []