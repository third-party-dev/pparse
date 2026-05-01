/*

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

*/