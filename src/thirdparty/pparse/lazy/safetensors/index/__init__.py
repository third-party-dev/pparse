import logging
log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.safetensors.index.state import SafetensorsIndexParsingIndex

def configure_pparser(**kwargs):

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


        def make_root_node(self, parent: pparse.Node = None, init_state = SafetensorsIndexParsingIndex):
            init_state = globals()[init_state] if isinstance(init_state, str) else init_state

            root = pparse.Node(self._source.open(), self, default_value={}, parent=parent)
            root.ctx()._next_state(init_state)
            return root


        def __init__(self, source: pparse.Extraction, id: str = "safetensors_index"):
            super().__init__(source, id)

    return Parser

