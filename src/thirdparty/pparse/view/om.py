#!/usr/bin/env python3

import logging
import os
import struct

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
from thirdparty.pparse.lazy.om import Parser as LazyOmParser

class Om:
    def __init__(self):
        self._extraction = None

    def open_fpath(self, fpath, header_only=False):
        

        try:
            print("Parsing the OM container file.")
            OM_PARSER = { "om": LazyOmParser }
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            self._extraction.discover_parsers(OM_PARSER)
            self._extraction.scan_data()

            if not header_only:
                print("Parsing the OM (Protobuf) ModelDef")
                from importlib import resources
                data_path = resources.files("thirdparty.pparse") / "data"
                proto = PbImport(data_path / "proto" / "ge_ir.pb")
                PROTOBUF_PARSER = {
                    "protobuf": make_protobuf_parser(
                        ext_list=[".pb"], init_msgtype=".ge.proto.ModelDef", proto=proto
                    ),
                }

                # ! Assuming MODEL_DEF is 2nd partition for now.
                part = self._extraction._result['om'].value['partitions'].value[1]
                part_off = 0x100
                modeldef_hdrsz = 0x80
                true_offset = part.value['offset'] + part_off + modeldef_hdrsz
                true_size = part.value['size'] - modeldef_hdrsz

                pb_range = pparse.Range(data_source.open(true_offset), true_size)
                pb_extraction = pparse.BytesExtraction(name="modeldef.pb", reader=pb_range)
                # Manually shove the extraction where its intended to be.
                self._extraction._extractions.append(pb_extraction)
                pb_extraction.discover_parsers(PROTOBUF_PARSER).scan_data()


        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self

    # def find_node(self, name):
    #     for node in self.nodes:
    #         if node.value["name"] == name:
    #             return node
    #     return None

    # def _recursive_callback(self, tgt, callback=None, callback_arg=None):
    #     if callable(callback):
    #         callback(tgt, callback_arg)

    #     if isinstance(tgt, NodeArray):
    #         for elem in tgt.value:
    #             self._recursive_callback(elem, callback, callback_arg)
    #     elif isinstance(tgt, NodeMap):
    #         for k, v in tgt.value.items():
    #             if isinstance(v, Node):
    #                 self._recursive_callback(v, callback, callback_arg)

    #     return self

    # # results = onnx.find_tensor('transformer.ln_f.weight')
    # def find_tensor(self, name):
    #     def name_check(tgt, results):
    #         if (
    #             isinstance(tgt, Node)
    #             and tgt.msgtype()
    #             and "TensorProto" in tgt.msgtype().name
    #         ):
    #             if "name" in tgt.value and tgt.value["name"] == name:
    #                 results.append(tgt)
    #                 return

    #     results = []
    #     self._recursive_callback(
    #         self._extraction._result["protobuf"], name_check, results
    #     )
    #     return results

    # # results = onnx.list_tensor_names()
    # def list_tensor_names(self):
    #     def has_name(tgt, results):
    #         if (
    #             isinstance(tgt, Node)
    #             and tgt.msgtype()
    #             and "TensorProto" in tgt.msgtype().name
    #         ):
    #             if "name" in tgt.value:
    #                 results.append(tgt.value["name"])

    #     results = []
    #     self._recursive_callback(
    #         self._extraction._result["protobuf"], has_name, results
    #     )
    #     return results

    # # results = onnx.find_node('transformer.ln_f.weight')
    # def find_node(self, name):
    #     def name_check(tgt, results):
    #         if (
    #             isinstance(tgt, Node)
    #             and tgt.msgtype()
    #             and "NodeProto" in tgt.msgtype().name
    #         ):
    #             if "name" in tgt.value and tgt.value["name"] == name:
    #                 results.append(tgt)
    #                 return

    #     results = []
    #     self._recursive_callback(
    #         self._extraction._result["protobuf"], name_check, results
    #     )
    #     return results

    # # results = onnx.list_node_names()
    # def list_node_names(self):
    #     def has_name(tgt, results):
    #         if (
    #             isinstance(tgt, Node)
    #             and tgt.msgtype()
    #             and "NodeProto" in tgt.msgtype().name
    #         ):
    #             if "name" in tgt.value:
    #                 results.append(tgt.value["name"])

    #     results = []
    #     self._recursive_callback(
    #         self._extraction._result["protobuf"], has_name, results
    #     )
    #     return results
