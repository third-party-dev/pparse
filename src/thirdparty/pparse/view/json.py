#!/usr/bin/env python3

import logging
import os
import struct

import numpy

log = logging.getLogger(__name__)

from pprint import pprint

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json import Parser as LazyJsonParser


class Json:
    def __init__(self, extraction=None):
        self._extraction = extraction

    def open_fpath(self, fpath):

        JSON_PARSER = { "json": LazyJsonParser, }

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(JSON_PARSER)
            self._extraction.scan_data()
        
        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self

    