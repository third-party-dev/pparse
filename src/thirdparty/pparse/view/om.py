#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
from thirdparty.pparse.lazy.om import Parser as LazyOmParser

class Om:
    def __init__(self):
        self._extraction = None


    def _parse(self, data_source, recursion=None, header_only=False, fname="unnamed.om"):
        try:
            log.info("Parsing the OM container file.")
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            parser = LazyOmParser(self._extraction, 'om')
            self._extraction.add_parser('om', parser)
            self._extraction._parser['om']._root.load(recursion=recursion)

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['om']._root


    def open_fpath(self, fpath, recursion=None, header_only=False):
        return self._parse(pparse.FileData(path=fpath), recursion=recursion, header_only=header_only, fname=fpath)


    def from_bytesio(self, bytes_io, recursion=None, header_only=False, fname="unnamed.om"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), recursion=recursion, header_only=header_only, fname=fname)
