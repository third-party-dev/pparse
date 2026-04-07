#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser
#from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeVector, NodeTable


class Flatbuffers:
    def __init__(self):
        self._extraction = None

    def open_fpath(self, fpath, json_schema_path):

        import json
        from pathlib import Path
        with open(json_schema_path, "r") as fobj:
            json_schema = json.loads(fobj.read())

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            parser = make_flatbuffers_parser(ext_list=[Path(fpath).suffix], json_schema=json_schema)
            self._extraction.discover_parsers({"flatbuffers": parser})
            self._extraction._parser['flatbuffers']._root.load()
            #self._extraction.scan_data()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self




