#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser


class Flatbuffers:
    def __init__(self):
        self._extraction = None


    def _parse(self, data_source, json_schema_path, fname="unnamed.flatbuffers.bin"):

        import json
        from pathlib import Path
        with open(json_schema_path, "r") as fobj:
            json_schema = json.loads(fobj.read())

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            parser = make_flatbuffers_parser(ext_list=[Path(fpath).suffix], json_schema=json_schema)
            self._extraction.discover_parsers({"flatbuffers": parser})
            self._extraction._parser['flatbuffers']._root.load()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def open_fpath(self, fpath, json_schema_path):
        return self._parse(pparse.FileData(path=fpath), json_schema_path, fname=fpath)


    def from_bytesio(self, bytes_io, json_schema_path, fname="unnamed.flatbuffers.bin"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), json_schema_path, fname=fname)

