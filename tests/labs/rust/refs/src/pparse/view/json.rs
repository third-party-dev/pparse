/*

#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json import Parser as LazyJsonParser


class Json:
    def __init__(self, extraction=None):
        self._extraction = extraction

    def _parse(self, data_source, fname="unnamed.json"):

        JSON_PARSER = { "json": LazyJsonParser, }

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers(JSON_PARSER)
            # TODO: Generalize the 'json' key below?
            self._extraction._parser['json']._root.load()
        
        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['json']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.json"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)

*/


// pub struct JsonView
// new(extraction)
// parse(data_source, fname)
// root_node()
// open_fpath()
// from_bytesio
//   - use alloc::vec::Vec;
//   - use core::io::{Cursor, Read, Write};