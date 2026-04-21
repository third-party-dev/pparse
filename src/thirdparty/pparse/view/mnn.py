#!/usr/bin/env python3

import logging

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser

class MNN:
    def __init__(self):
        self._extraction = None

    def _parse(self, data_source, fname="unnamed.mnn"):

        import json
        from importlib import resources
        from pathlib import Path
        data_path = resources.files("thirdparty.pparse")/"data"
        with open(data_path/"fbs"/"mnn"/"MNN.json", "r") as fobj:
            json_schema = json.loads(fobj.read())
        MNN_PARSER = {
            "flatbuffers": make_flatbuffers_parser(
                ext_list=[Path(fpath).suffix], json_schema=json_schema),
        }

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(MNN_PARSER)
            self._extraction.scan_data()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    #def root_node(self):
    #    return self._extraction._parser['mnn']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.mnn"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)

