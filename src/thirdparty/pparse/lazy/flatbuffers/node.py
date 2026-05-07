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
