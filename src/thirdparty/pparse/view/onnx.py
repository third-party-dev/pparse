#!/usr/bin/env python3

import logging
import struct
import numpy

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.protobuf import make_protobuf_parser
from thirdparty.pparse.lazy.protobuf.meta import PbImport
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


    def _parse(self, data_source, fname="unnamed.onnx"):
        from importlib import resources
        data_path = resources.files("thirdparty.pparse") / "data"
        proto = PbImport(data_path / "proto" / "onnx.pb")

        try:
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


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.onnx"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)


    def tensor_names(self):
        return list(self._tensor_meta.keys())


    def tensor(self, name):
        return self._tensor_meta[name]


    def find_node(self, name):
        for node in self.nodes:
            if node.value["name"] == name:
                return node
        return None
