#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pickle import Parser as LazyPickleParser

class Pickle:

    def _parse(self, data_source, fname="unnamed.pkl"):

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers({"pkl": LazyPickleParser})
            self._extraction._parser['pkl']._root.load()
        
        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['pkl']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.pkl"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)

