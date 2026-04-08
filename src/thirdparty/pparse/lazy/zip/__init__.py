import logging
import os
import sys

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.zip.meta import Zip
from thirdparty.pparse.lazy.zip.state import ZipParsingMagic


class Parser(pparse.Parser):
    @staticmethod
    def match_extension(fname: str):
        if not fname:
            return False
        for ext in [".zip"]:
            if fname.endswith(ext):
                return True
        return False


    @staticmethod
    def match_magic(cursor: pparse.Cursor):
        if cursor.peek(len(Zip.SIGNATURE)) == Zip.SIGNATURE:
            return True
        return False


    def __init__(self, source: pparse.Extraction, id: str = "zip", parent: pparse.Node = None):
        super().__init__(source, id)

        self._root = pparse.Node(source.open(), self, default_value = [], parent = parent)
        self._root.ctx()._next_state(ZipParsingMagic)
        source._result[id] = self._root


    @staticmethod
    def from_reader(reader: pparse.Reader, parent: pparse.Node = None):
        extraction = pparse.BytesExtraction(name="data.zip", reader=reader.dup())
        return Parser(extraction, parent=parent)


    def new_map_node(self, parent):
        return pparse.Node(parent.ctx().reader(), self, default_value = {}, parent = parent)


    def new_data_node(self, parent):
        return pparse.Node(parent.ctx().reader(), self, parent = parent)


    def _end_container_node(self, node: pparse.Node):
        ctx = node.ctx()
        parent = ctx.parent()
        if parent:
            log.debug(f"end_container (off:{ctx.tell()}): Backtracking to parent.")

            # Set the end pointer to advance parent past field.
            ctx.mark_end(node)

            # Fast forward past the bit we just parsed.
            parent.ctx().seek(ctx._end)


    # def scan_data(self):
    #     # While not end of data, keep parsing via states.
    #     try:
    #         while True:
    #             self.current.ctx().state().parse_data(self, self.current.ctx())
    #     except pparse.EndOfNodeException as e:
    #         pass
    #     except pparse.EndOfDataException as e:
    #         pass
    #     except pparse.UnsupportedFormatException:
    #         raise

    #     # TODO: Do all the children.

    #     return self
