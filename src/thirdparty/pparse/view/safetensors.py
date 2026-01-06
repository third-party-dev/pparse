#!/usr/bin/env python3

import logging
import os
import struct

import numpy

log = logging.getLogger(__name__)

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.json import Parser as LazyJsonParser
from thirdparty.pparse.lazy.safetensors import Parser as LazySafetensorsParser
from thirdparty.pparse.lazy.safetensors.index import (
    Parser as LazySafetensorsIndexParser,
)


class Tensor:
    STTYPE_STRUCT = {
        "i8": "b",
        "u8": "B",
        "i16": "h",
        "u16": "H",
        "i32": "i",
        "u32": "I",
        "i64": "q",
        "u64": "Q",
        "f32": "f",
        "f64": "d",
    }

    STTYPE_SIZE = {
        "i8": 1,
        "u8": 1,
        "i16": 2,
        "u16": 2,
        "i32": 4,
        "u32": 4,
        "i64": 8,
        "u64": 8,
        "f32": 4,
        "f64": 8,
    }

    def __init__(self, safetensors, node_map):
        self._safetensors = safetensors
        self._reader = self._safetensors._extraction.open()
        self._node_map = node_map

    def get_type(self):
        return self._node_map.value["dtype"].lower()

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
    PARSER_REGISTRY = {
        "safetensors": LazySafetensorsParser,
    }

    def __init__(self, extraction=None):
        self._extraction = extraction

    def header_length(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        return self._extraction._result["safetensors"].header_length

    def header(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        st_init = self._extraction._result["safetensors"]
        hdr_init = st_init.parser.source()._extractions[0]._result["json"]
        hdr_map = hdr_init.value.value

        return hdr_map

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
        tensor_dict = self._extraction._extractions[0]._result["json"].value.value
        return [k for k in tensor_dict if k != "__metadata__"]
        # return self.header().keys()

    def open_fpath(self, fpath):
        try:
            cursor = pparse.FileData(path=fpath).open()
            length = os.path.getsize(fpath)
            rrange = pparse.Range(cursor, length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=rrange)
            self._extraction.discover_parsers(SafeTensors.PARSER_REGISTRY)
            self._extraction.scan_data()
        except pparse.EndOfDataException:
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


class SafeTensorsIndex:
    PARSER_REGISTRY = {"safetensors_index": LazySafetensorsIndexParser}

    def __init__(self):
        self._extraction = None
        self._safetensors_files = {}

    def safetensors_names(self):
        return self._safetensors_files.keys()

    def safetensors(self, name):
        return self._safetensors_files[name]

    def metadata(self):
        if not self._extraction:
            raise Exception("No parsed extraction found.")

        return self._extraction._result["safetensors_index"].value.value["metadata"]

    def tensor(self, name):
        fname = (
            self._extraction._result["safetensors_index"]
            .value.value["weight_map"]
            .value[name]
        )
        return self._safetensors_files[fname].tensor(name)

    def tensor_names(self):
        return (
            self._extraction._result["safetensors_index"]
            .value.value["weight_map"]
            .value.keys()
        )

    # fpath - Index file.
    def open_fpath(self, fpath):
        try:
            # Process the index file.
            idx_data = pparse.Data(path=fpath)
            idx_range = pparse.Range(idx_data.open(), idx_data.length)
            self._extraction = pparse.BytesExtraction(name=fpath, reader=idx_range)
            self._extraction.discover_parsers(SafeTensorsIndex.PARSER_REGISTRY)
            self._extraction.scan_data()

            # Create SafeTensor objects
            for st_extr in self._extraction._extractions:
                self._safetensors_files[st_extr.name()] = SafeTensors(st_extr)

        except pparse.EndOfDataException:
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self
