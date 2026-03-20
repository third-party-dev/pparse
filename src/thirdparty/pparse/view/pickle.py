#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pickle import Parser as LazyPickleParser
from thirdparty.pparse.utils import pparse_repr

class Pickle:

    def open_fpath(self, fpath, header_only=False):

        try:
            PICKLE_PARSER = {"pkl": LazyPickleParser}
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
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

