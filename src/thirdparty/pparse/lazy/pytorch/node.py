#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse


# class NodeTensorContext(pparse.NodeContext):
#     def __init__(self, parent: "Node", reader: pparse.Range, parser: pparse.Parser):
#         if type(reader).__name__ != "Range":
#             raise Exception("protobuf NodeContext reader must be a pparse.Range")
#         super().__init__(parent, reader, parser)

#         self.proto = None
#         self.current_op = None
#         self.stack = []
#         self.memo = {}
#         self.next_memo = 0

#         # Note: Save the history to the node, forever allocating that memory.
#         self.history = []

#     def vmstate(self):
#         return self._vmstate