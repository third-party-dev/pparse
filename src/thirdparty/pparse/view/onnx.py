#!/usr/bin/env python3

import logging
import os
import struct
import numpy

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
# from thirdparty.pparse.lazy.protobuf.node import Node, NodeArray, NodeMap
from thirdparty.pparse.lazy.onnx.meta import OnnxDataType

"""
  Bulk tensor data is stored in GraphProto.initializer = []
  Graph structure is stoed in GraphProto.node = []
"""

class Tensor(pparse.Tensor):

    def __init__(self, onnx_view, init_node, name):
        self._name = name
        self._view = onnx_view
        self._init_node = init_node

    def get_onnx_type(self):
        return self._init_node.value['data_type']

    # Return (safetensors equivalent) type
    def get_type(self) -> str:
        return OnnxDataType.sttype(self.get_onnx_type())

    # Return (safetensors equivalent) shape
    def get_shape(self):
        shape = self._init_node.value['dims']
        return shape

    # Return raw data as extracted from source
    def get_data_bytes(self):
        return self._init_node.value['raw_data'].value

    # Return raw data as python array of dtype
    def as_array(self):
        raise NotImplementedError()

    # Return raw data as numpy array of dtype
    def as_numpy(self):
        dtype = OnnxDataType.nptype(self.get_onnx_type())

        arr = numpy.frombuffer(self.get_data_bytes(), dtype=dtype)

        if 'dims' in self._init_node.value:
            return arr.reshape(self.get_shape())
        return arr.reshape(())

class Onnx:
    def __init__(self):
        self._extraction = None
        self._tensor_meta = {}

    def open_fpath(self, fpath):
        from importlib import resources
        data_path = resources.files("thirdparty.pparse") / "data"
        proto = PbImport(data_path / "proto" / "onnx.pb")

        try:
            data_source = pparse.FileData(path=fpath)
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=data_range)
            parser = make_protobuf_parser(ext_list=[".onnx"], init_msgtype=".onnx.ModelProto", proto=proto)
            self._extraction.discover_parsers({"protobuf": parser})
            self._extraction._parser['protobuf']._root.load()

            # Some light post processing.
            self.root = self._extraction._result["protobuf"]
            self.model = self.root.value
            self.graph = self.model["graph"].value
            self.nodes = self.graph["node"]
            self.initializers = self.graph["initializer"]

            for tnode in self.graph['initializer']:
                self._tensor_meta[tnode.value['name']] = Tensor(self, tnode, tnode.value['name'])

        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self

    def tensor_names(self):
        return list(self._tensor_meta.keys())

    def tensor(self, name):
        return self._tensor_meta[name]

    def find_node(self, name):
        for node in self.nodes:
            if node.value["name"] == name:
                return node
        return None

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
