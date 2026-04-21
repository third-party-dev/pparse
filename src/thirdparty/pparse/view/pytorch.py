#!/usr/bin/env python3

import logging
import os
import struct

import numpy

log = logging.getLogger(__name__)

from pprint import pprint

import thirdparty.pparse.lib as pparse
from thirdparty.pparse.lazy.pytorch import Parser as LazyPyTorchParser


class Tensor(pparse.Tensor):
    def __init__(self, name, tensor_node):
        self._name = name
        self._tensor = tensor_node

    # Return (safetensors equivalent) type
    def get_type(self) -> str:
        return self._tensor.value['type']


    # Return (safetensors equivalent) shape
    def get_shape(self):
        return self._tensor.value['shape']


    # Return raw data as extracted from source
    def get_data_bytes(self):
        return self._tensor.value['data'].value


    # Return raw data as python array of dtype
    def as_array(self):
        elem_cnt = self._tensor.value['elem_count']
        buffer = self.get_data_bytes().getbuffer()
        dtype = self.get_type()
        
        struct_type = pparse.Tensor.STTYPE_STRUCT[dtype]
        sttype_size = pparse.Tensor.STTYPE_SIZE[dtype]
        count = int(len(buffer) / sttype_size)
        return struct.unpack(f"<{struct_type * count}", buffer)


    # Return raw data as numpy array of dtype
    def as_numpy(self):
        elem_cnt = self._tensor.value['elem_count']
        buffer = self.get_data_bytes().getbuffer()
        np_type = pparse.Tensor.STTYPE_NP_MAP[self.get_type()]

        arr = numpy.frombuffer(buffer, dtype=np_type, count=elem_cnt)
        return arr.reshape(self.get_shape())


class PyTorch:
    def __init__(self, extraction=None, force_traverse=False):
        self._extraction = extraction

        self._tensor_meta = {}
        self._forced_traversal = force_traverse


    def _parse(self, data_source, fname="unnamed.pt"):
        try:
            data_range = pparse.Range(data_source.open(), data_source.length)
            self._extraction = pparse.BytesExtraction(name=fname, reader=data_range)
            self._extraction.discover_parsers({"pt": LazyPyTorchParser})
            self._extraction._parser['pt']._root.load()
        except pparse.EndOfDataException as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()

        return self


    def root_node(self):
        return self._extraction._parser['pt']._root


    def open_fpath(self, fpath):
        return self._parse(pparse.FileData(path=fpath), fname=fpath)


    def from_bytesio(self, bytes_io, fname="unnamed.pt"):
        return self._parse(pparse.BytesIoData(bytes_io=bytes_io), fname=fname)


    # ! UNTESTED
    def as_arc_hash(self, hashed_data_path=None, keep_lm_head=False):
        import hashlib
        import json
        from collections import OrderedDict

        result = OrderedDict()

        '''
        PyTorch files can be saved in a number of different formats and layouts. Three
        conventions that I've seen include:
        - 1. state_dict() only - Similar to the data in a safetensors. No compute graph.
        - 2. Graph with embedded parameters (i.e. `torch.save(model, 'model.pt')`).
        - 3. A combo of state_dict() and graph mapped into a top level dictionary:
             `{'model_architecture': model, 'model_state_dict': model.state_dict()}`
        - 4. A checkpoint dictionary:

             ```
             torch.save({
                 "epoch": epoch,
                 "model_state_dict": model.state_dict(),
                 "optimizer_state_dict": optimizer.state_dict(),
                 "loss": loss
             }, "checkpoint.pt")
             ```

        The following code was only written for #1. ... TODO: We _can_ try harder to detect
        the kind of data to improve the process. (See traverse_pt() above.)
        '''

        if len(self._tensor_meta.keys()) == 0:
            # This is not a weights_only pt file!
            raise Exception("No tensors found, likely not a weights only pt file.")

        for tensor_name in sorted(self._tensor_meta.keys()):
            if tensor_name == "lm_head.weight" and not keep_lm_head:
                continue

            tensor = self.tensor(tensor_name)
            result[tensor_name] = OrderedDict()
            result[tensor_name]["dtype"] = tensor.get_type()
            result[tensor_name]["shape"] = tensor.get_shape()

            # persid = tensor._reduce_call.arg[Tensor.PERSID_CALL]
            # result[tensor_name]["key"] = persid.arg[Tensor.DATA_KEY]

        sane_json = json.dumps(result, indent=None, separators=(",", ":"))
        if not hashed_data_path is None:
            with open(hashed_data_path, "wb") as fobj:
                fobj.write(sane_json.encode("utf-8"))
        print(f"Based on {len(self._tensor_meta.keys())} tensors seen.")
        return hashlib.sha256(sane_json.encode("utf-8")).hexdigest()


    # ! UNTESTED
    def as_safetensors(
        self,
        out_fpath="converted_output.safetensors",
        keep_lm_head=False,
        alignment_boundary=8,
    ):
        import json
        import struct
        from collections import OrderedDict

        result = OrderedDict()
        result["__metadata__"] = OrderedDict([("format", "pt")])

        # Calculate offsets
        current_offset = 0
        for tensor_name in sorted(self._tensor_meta.keys()):
            if tensor_name == "lm_head.weight" and not keep_lm_head:
                continue

            tensor = self.tensor(tensor_name)
            result[tensor_name] = OrderedDict()
            result[tensor_name]["dtype"] = tensor.get_type()
            result[tensor_name]["shape"] = tensor.get_shape()
            tensor_size = len(tensor.get_data_bytes())
            result[tensor_name]["data_offsets"] = [
                current_offset,
                current_offset + tensor_size,
            ]
            current_offset += tensor_size

        # Initially open file with truncation
        hdr_len = 0
        with open(out_fpath, "wb") as fobj:
            # Write 8 zeros
            fobj.write(struct.pack("<Q", hdr_len))
            # Write header
            json_str = json.dumps(result, indent=None, separators=(",", ":"))
            fobj.write(json_str.encode("utf-8"))

            # Padding between header and tensor data
            tensor_start = fobj.tell() + (alignment_boundary - 1)
            tensor_start //= alignment_boundary
            tensor_start *= alignment_boundary
            padding = (" " * (tensor_start - fobj.tell())).encode("utf-8")
            fobj.write(padding)
            # Update size (minus u64 size bytes themselves)
            hdr_len = fobj.tell() - 8

            # Write each tensor data section
            for tensor_name in result:
                if tensor_name == "__metadata__":
                    continue
                tensor = self.tensor(tensor_name)
                fobj.write(tensor.get_data_bytes())

        # Re-open file and overwrite first 8 bytes.
        with open(out_fpath, "r+b") as fobj:
            fobj.seek(0)
            fobj.write(struct.pack("<Q", hdr_len))


    def tensor(self, name):
        if name not in self.tensor_names():
            raise KeyError("Tensor name not found.")
        return Tensor(name, self._extraction._parser['pt']._root._value['tensors'][name])


    def tensor_names(self):
        return list(self._extraction._parser['pt']._root._value['tensors'].keys())


