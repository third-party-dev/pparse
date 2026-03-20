#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser
from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeVector, NodeTable

'''
NOTE:
Because of the nature of the TFLite memory layout, the entire file 
must be accessible. For example, each table in TFlite has a vTable 
that is required to understand the ordering of the table's values. 
The vTable could be very far from the the table itself.
'''

class TFLite:
    def __init__(self):
        self._extraction = None

    def open_fpath(self, fpath):

        import json
        from importlib import resources
        from pathlib import Path
        data_path = resources.files("thirdparty.pparse")/"data"
        with open(data_path/"fbs"/"tflite"/"schema.json", "r") as fobj:
            json_schema = json.loads(fobj.read())
        TFLITE_PARSER = {
            "flatbuffers": make_flatbuffers_parser(
                ext_list=[Path(fpath).suffix], json_schema=json_schema),
        }

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(TFLITE_PARSER)
            self._extraction.scan_data()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self




