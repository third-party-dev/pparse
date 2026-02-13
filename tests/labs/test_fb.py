#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_tflite_parser
from thirdparty.pparse.lazy.flatbuffers.node import Node, NodeVector, NodeTable

'''
NOTE:
Because of the nature of the TFLite memory layout, the entire file 
must be accessible. For example, each table in TFlite has a vTable 
that is required to understand the ordering of the table's values. 
The vTable could be very far from the the table itself.
'''

class TFlite:
    def __init__(self):
        self._extraction = None

    def open_fpath(self, fpath):
        TFLITE_PARSER = {
            "flatbuffers": make_tflite_parser(ext_list=[".tflite"]),
        }

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(TFLITE_PARSER)
            self._extraction.scan_data()

            # Some light post processing.
            #self.model = self._extraction._result["protobuf"].value
            #self.graph = self.model["graph"].value
            #self.nodes = self.graph["node"].value
            #self.initializers = self.graph["initializer"].value

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


res = TFlite().open_fpath("./tests/data/models/yolo/yolov5su_float32.tflite")
obj = res._extraction._result['flatbuffers'].value
# obj.value.value['buffers'].value[0].value['data'].value
breakpoint()


