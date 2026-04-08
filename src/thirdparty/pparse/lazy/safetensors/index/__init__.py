import logging
log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.safetensors.index.state import SafetensorsIndexParsingIndex


class Parser(pparse.Parser):
    @staticmethod
    def match_extension(fname: str):
        if not fname:
            return False
        for ext in [".json"]:
            if fname.endswith(ext):
                return True
        return False


    @staticmethod
    def match_magic(cursor: pparse.Cursor):
        return False


    def __init__(self, source: pparse.Extraction, id: str = "safetensors_index", parent: pparse.Node = None):
        super().__init__(source, id)

        self._root = pparse.Node(source.open(), self, default_value={}, parent=parent)
        self._root.ctx()._next_state(SafetensorsIndexParsingIndex)
        source._result[id] = self._root



