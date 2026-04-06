#!/usr/bin/env python3

import logging
import os
import struct

import numpy

log = logging.getLogger(__name__)

from pprint import pprint

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.zip import Parser as LazyZipParser


class Zip:
    def __init__(self, extraction=None):
        self._extraction = extraction

    def _parse(self, data_source, fname="unnamed.zip"):

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers({ "zip": LazyZipParser, })
            self._extraction._parser['zip']._root.load()
            #self._extraction.scan_data()
        
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


    def from_bytesio(self, bytes_io, fname="unnamed.zip"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)


    