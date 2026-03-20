#!/usr/bin/env python3

'''
Note: MNN _laughably_ requires an executable stack.
Hack: 
sudo apt install execstack
execstack -c /work/cache/venv/ml-venv-3.9/lib/python3.9/site-packages/_mnncengine.cpython-39-x86_64-linux-gnu.so
'''

import sys
import flatbuffers
import MNN.Net as MNNNet
from MNN.OpParameter import OpParameter
import MNN.Input
import numpy as np

def parse_mnn(filename):
    with open(filename, "rb") as f:
        buf = f.read()

    net = MNNNet.Net.GetRootAsNet(buf, 0)

    for i in range(net.OplistsLength()):
        obj = {}
        op = net.Oplists(i)
        obj['name'] = op.Name().decode()
        
        if op.MainType() == OpParameter.Input:
            from MNN.Input import Input
            _obj = Input()
            _obj.Init(op.Main().Bytes, op.Main().Pos)

            obj['dims'] = _obj.DimsAsNumpy() #-> array([   1,    2, 8400], dtype=int32)

            #obj['shape'] = [_obj.Dims(d) for d in range(_obj.DimsLength())]
            #dtype_map = {0:"float32", 1:"int32", 2:"uint8", 3:"int8", 4:"float16"}
            #obj['dtype'] = dtype_map.get(_obj.Dtype(), f"unknown({_obj.Dtype()})")

            print(f"{'-' * 40}\nName: {obj['name']}\nDims: {obj['dims']}")

        elif op.MainType() == OpParameter.Blob:
            from MNN.Blob import Blob
            _obj = Blob()
            _obj.Init(op.Main().Bytes, op.Main().Pos)

            obj['dims'] = _obj.DimsAsNumpy() #-> array([   1,    2, 8400], dtype=int32)

            #obj['shape'] = [_obj.Dims(d) for d in range(_obj.DimsLength())]
            
            if _obj.Uint8sLength() > 0:
                obj['numpy'] = _obj.Uint8sAsNumpy()
            elif _obj.Int8sLength() > 0:
                obj['numpy'] = _obj.Int8sAsNumpy()
            elif _obj.Int32sLength() > 0:
                obj['numpy'] = _obj.Int32sAsNumpy()
            elif _obj.Int64sLength() > 0:
                obj['numpy'] = _obj.Int64sAsNumpy()
            elif _obj.Float32sLength() > 0:
                obj['numpy'] = _obj.Float32sAsNumpy()
            elif _obj.StringsLength() > 0:
                obj['numpy'] = _obj.StringsAsNumpy()
            elif _obj.ExternalLength() > 0:
                obj['numpy'] = _obj.ExternalAsNumpy()
            else:
                raise NotImplementedError("Unknown data type for blob.")
            
            print(f"{'-' * 40}\nName: {obj['name']}\nDims: {obj['dims']}\nNumpy: {obj['numpy']}")

        else:
            print(f"{'-' * 40}\n{obj['name']} type({op.MainType()}) not implemented.")
            #breakpoint()
            #raise NotImplementedError(f"{op.MainType()} type not implemented.")

        # Tensor data length
        #data_len = obj.DataLength()
        #dtype_size = {0:4, 1:4, 2:1, 3:1, 4:2}
        #byte_len = data_len * dtype_size.get(obj.DataType(), 4)


if __name__ == "__main__":
    parse_mnn(sys.argv[1])