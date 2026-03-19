#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
from thirdparty.pparse.lazy.protobuf.node import Node, NodeArray, NodeMap


class ProtobufParser:
    def __init__(self):
        self._extraction = None

    def open_fpath(self, fpath, pbpath, msgtype):
        from importlib import resources

        PROTOBUF_PARSER = {
            "protobuf": make_protobuf_parser(
                ext_list=[".pb"], init_msgtype=msgtype, proto=PbImport(pbpath)
            ),
        }

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(PROTOBUF_PARSER)
            self._extraction.scan_data()

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self

