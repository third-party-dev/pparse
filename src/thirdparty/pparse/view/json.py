#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json import Parser as LazyJsonParser


class Json:
    def __init__(self, extraction=None):
        self._extraction = extraction

    def _parse(self, data_source, fname="unnamed.json", recursion=None):

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            parser = LazyJsonParser(self._extraction, 'json')

            self._extraction.add_result('json', parser.make_root_node())
            self._extraction._result['json'].load(recursion=recursion)

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._result['json']


    def open_fpath(self, fpath, recursion=None):
        return self._parse(pparse.FileData(path=fpath), fname=fpath, recursion=recursion)


    def from_bytesio(self, bytes_io, fname="unnamed.json", recursion=None):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname, recursion=recursion)