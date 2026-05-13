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

    # extraction = Extraction.from_xml("<job />")
    @classmethod
    def from_xml(cls, source):
        from thirdparty.pparse._xml import XmlNode, XmlEntry
        xml = XmlNode.as_node(source)

        # Do we have the correct node?
        # ** Assuming parser has type attribute.
        if xml.get_el().tag != "parser":
            raise Exception(f"Expected parser node. Got: {xml.get_el().tag}")
        if xml['type'] != "zip":
            raise Exception(f"Expected type zip parser. Got: {xml['type']}")
        
        
