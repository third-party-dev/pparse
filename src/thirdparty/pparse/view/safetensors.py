#!/usr/bin/env python3

import logging
import os
import struct

import numpy

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.safetensors import Parser as LazySafetensorsParser
from thirdparty.pparse.lazy.safetensors.index import Parser as LazySafetensorsIndexParser


class Tensor:
    STTYPE_STRUCT = {
        "I8": "b",
        "U8": "B",
        "I16": "h",
        "U16": "H",
        "I32": "i",
        "U32": "I",
        "I64": "q",
        "U64": "Q",
        "F32": "f",
        "F64": "d",
    }

    STTYPE_SIZE = {
        "I8": 1,
        "U8": 1,
        "I16": 2,
        "U16": 2,
        "I32": 4,
        "U32": 4,
        "I64": 8,
        "U64": 8,
        "F32": 4,
        "F64": 8,
    }

    def __init__(self, safetensors, node_map):
        self._safetensors = safetensors
        self._reader = self._safetensors._extraction.open()
        self._node_map = node_map

    def get_type(self):
        return self._node_map.value["dtype"].upper()

    def get_shape(self):
        return self._node_map.value["shape"].value

    def get_offsets(self):
        return self._node_map.value["data_offsets"].value

    def get_data_bytes(self):
        # TODO: Sanity check input.
        header_length = self._safetensors.header_length()
        offsets = self.get_offsets()
        length = offsets[1] - offsets[0]
        self._reader.seek(offsets[0] + header_length + 8)
        # TODO: Do we have type aligned length of data?
        self._data = self._reader.read(length)

        if len(self._data) < length:
            raise Exception(f"Missing tensor data: {len(data)}/{length} @ {offset[0]}")

    def as_array(self):
        # TODO: Sanity check input.
        self.get_data_bytes()
        dtype = self.get_type()
        struct_type = Tensor.STTYPE_STRUCT[dtype]
        sttype_size = Tensor.STTYPE_SIZE[dtype]
        count = int(len(self._data) / sttype_size)
        return struct.unpack(f"<{struct_type * count}", self._data)

    def as_numpy(self):
        self.get_data_bytes()
        dtype = self.get_type()
        struct_type = Tensor.STTYPE_STRUCT[dtype]
        shape = self.get_shape()
        return numpy.frombuffer(
            self._data, dtype=numpy.dtype(f"<{struct_type}")
        ).reshape(shape)


class SafeTensors:

    def __init__(self, extraction=None):
        self._extraction = extraction


    def header_length(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        return self._extraction._result['safetensors'].value['header_length']


    def header(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        st_init = self._extraction._result['safetensors']
        hdr_init = st_init.value['header']
        hdr_map = hdr_init.value.value

        return hdr_map


    # ! UNTESTED
    def metadata(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        hdr_map = self.header()
        return hdr_map["__metadata__"]


    def tensor(self, name):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        hdr_map = self.header()
        if name not in hdr_map:
            raise ValueError(f"No tensor found with name: {name}")
        return Tensor(self, hdr_map[name])


    def tensor_names(self):

        tensor_dict = self._extraction._parser['safetensors']._root.value['tensors']
        return [k for k in tensor_dict if k != "__metadata__"]
        # return self.header().keys()


    # ! UNTESTED
    def as_arc_hash(self, hashed_data_path=None):
        import hashlib
        import json
        from collections import OrderedDict

        result = OrderedDict()
        tensor_names = sorted(self.tensor_names())

        for tensor_name in tensor_names:
            tensor = self.tensor(tensor_name)

            result[tensor_name] = OrderedDict()
            result[tensor_name]["dtype"] = tensor.get_type()
            result[tensor_name]["shape"] = tensor.get_shape()

        sane_json = json.dumps(result, indent=None, separators=(",", ":"))
        if not hashed_data_path is None:
            with open(hashed_data_path, "wb") as fobj:
                fobj.write(sane_json.encode("utf-8"))
        return hashlib.sha256(sane_json.encode("utf-8")).hexdigest()



    def _parse(self, data_source, fname="unnamed.safetensors"):
        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers({"safetensors": LazySafetensorsParser})
            self._extraction._parser['safetensors']._root.load()

        except pparse.EndOfDataException:
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['safetensors']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.safetensors"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)


# ! UNTESTED
class SafeTensorsIndexTensor(pparse.Tensor):

    STTYPE_STRUCT = {
        "I8": "b",
        "U8": "B",
        "I16": "h",
        "U16": "H",
        "I32": "i",
        "U32": "I",
        "I64": "q",
        "U64": "Q",
        "F32": "f",
        "F64": "d",
    }

    STTYPE_SIZE = {
        "I8": 1,
        "U8": 1,
        "I16": 2,
        "U16": 2,
        "I32": 4,
        "U32": 4,
        "I64": 8,
        "U64": 8,
        "F32": 4,
        "F64": 8,
    }

    def __init__(self, name, tensor_node):
        self._name = name
        self._tensor_node = tensor_node


    # Return (safetensors equivalent) type
    def get_type(self) -> str:
        return self._tensor_node['header'].value['dtype']


    # Return (safetensors equivalent) shape
    def get_shape(self):
        return self._tensor_node['header']._value['shape'].value


    # Return raw data as extracted from source
    def get_data_bytes(self):
        return self._tensor_node['data'].value


    # Return raw data as python array of dtype
    def as_array(self):
        raise NotImplementedError()


    def as_numpy(self):
        dtype = numpy.dtype(f"<{SafeTensorsIndexTensor.STTYPE_STRUCT[self.get_type()]}")
        shape = self.get_shape()
        data = self.get_data_bytes()
        return numpy.frombuffer(data, dtype=dtype).reshape(shape)


# ! UNTESTED
class SafeTensorsIndex:

    def __init__(self):
        self._extraction = None
        self._safetensors_files = {}

    # def safetensors_names(self):
    #     return self._safetensors_files.keys()

    # def safetensors(self, name):
    #     return self._safetensors_files[name]

    # def metadata(self):
    #     if not self._extraction:
    #         raise Exception("No parsed extraction found.")

    #     return self._extraction._result["safetensors_index"].value.value["metadata"]

    def tensor(self, name):
        tensor_node = self._root.value['tensors'][name]
        return SafeTensorsIndexTensor(name, tensor_node)

    def tensor_names(self):
        return list(self._root.value['tensors'].keys())

    # fpath - Index file.
    def _parse(self, idx_data, fname="unnamed.index.json"):
        try:
            # Process the index file.
            idx_range = pparse.Range(idx_data.open(), idx_data.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=idx_range)
            self._extraction.discover_parsers({"safetensors_index": LazySafetensorsIndexParser})
            self._root = self._extraction._parser['safetensors_index']._root
            self._root.load()
            

        except pparse.EndOfDataException:
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['safetensors_index']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.index.json"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)
