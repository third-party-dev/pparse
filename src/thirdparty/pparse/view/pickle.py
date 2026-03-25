#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pickle import Parser as LazyPickleParser
from thirdparty.pparse.utils import pparse_repr

class Pickle:

    def _parse(self, data_source, fname="unnamed.pkl"):

        PICKLE_PARSER = {"pkl": LazyPickleParser}

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers(PICKLE_PARSER)
            self._extraction.scan_data()
        
        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.pkl"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)

