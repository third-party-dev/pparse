#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

# from thirdparty.pparse.lazy.protobuf import ProtobufParsingState, ProtobufParsingKey
import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lib import NodeContext as BaseNodeContext


class NodeContext(BaseNodeContext):
    def __init__(self, parent: pparse.Node, reader: pparse.Range, parser: pparse.Parser):
        if type(reader).__name__ != "Range":
            raise Exception("protobuf NodeContext reader must be a pparse.Range")
        super().__init__(parent, reader, parser)
        self._key = None
        self._type_desc = None

    def type_desc(self):
        return self._type_desc

    def key(self):
        return self._key

    def set_key(self, field):
        self._key = field
