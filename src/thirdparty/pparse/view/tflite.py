#!/usr/bin/env python3

import logging
log = logging.getLogger(__name__)

import struct
import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.flatbuffers import make_flatbuffers_parser


class Tensor(pparse.Tensor):

    # TFlite3 Tensor Types
    FLOAT32 = 0     #
    FLOAT16 = 1     # not supported
    INT32 = 2       # 
    UINT8 = 3       #
    INT64 = 4       #
    STRING = 5      # not supported
    BOOL = 6        # not supported
    INT16 = 7       #
    COMPLEX64 = 8   # not supported
    INT8 = 9        #
    FLOAT64 = 10    # 
    COMPLEX128 = 11 # not supported
    UINT64 = 12     #
    UINT32 = 15     #
    UINT16 = 16     #

    TF_TO_ST_TYPE = {
        INT8: "I8",
        UINT8: "U8",
        INT16: "I16",
        UINT16: "U16",
        INT32: "I32",
        UINT32: "U32",
        INT64: "I64",
        UINT64: "U64",
        FLOAT32: "F32",
        FLOAT64: "F64",
    }

    def __init__(self, entry, buffer):
        self._entry = entry
        self._buffer = buffer

    def get_type(self):
        # Type defaults to FLOAT32 when not defined.
        _type = 0
        if 'type' in self._entry:
            _type = struct.unpack('B', self._entry['type'])[0]
        return Tensor.TF_TO_ST_TYPE[_type]

    def get_shape(self):
        return list(self._entry['shape'].value)

    def get_data_bytes(self):
        if 'data' not in self._buffer:
            return b''
        return self._buffer['data'].value

    def as_array(self):
        raise NotImplementedError()

    def as_numpy(self):
        # In tflite, if DataLength() is 0, DataAsNumpy returns 0.
        data = self.get_data_bytes()
        if len(data) == 0:
            return 0
        res = numpy.frombuffer(data, dtype=Tensor.STTYPE_NP_MAP[self.get_type()])
        res.reshape(self.get_shape())
        return res


class TFLite:
    def __init__(self):
        self._extraction = None
        self._tensors = {}

    def _parse(self, data_source, fname="unnamed.tflite"):

        import json
        from importlib import resources
        from pathlib import Path

        data_path = resources.files("thirdparty.pparse")/"data"
        with open(data_path/"fbs"/"tflite"/"schema.json", "r") as fobj:
            json_schema = json.loads(fobj.read())

        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            parser = make_flatbuffers_parser(ext_list=[Path(fname).suffix], json_schema=json_schema)
            self._extraction.discover_parsers({"flatbuffers": parser})
            self._extraction._parser['flatbuffers']._root.load()

            root_table = self.root_node().value['root_table'].value
            buffers = root_table['buffers'].value
            for _entry in root_table['subgraphs'].value[0].value['tensors'].value:
                entry = _entry.value
                buffer = buffers[entry['buffer']].value
                self._tensors[entry['name']] = Tensor(entry, buffer)


        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['flatbuffers']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.tflite"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)


    def tensor_names(self):
        return list(self._tensors.keys())


    def tensor(self, name):
        return self._tensors[name]