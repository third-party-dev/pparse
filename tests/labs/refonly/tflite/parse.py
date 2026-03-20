#!/usr/bin/env python3

import flatbuffers
import tflite.Model
import sys

# Read model
with open(sys.argv[1], "rb") as f:
    buf = f.read()

# Get root object
model = tflite.Model.Model.GetRootAsModel(buf, 0)

print("Version:", model.Version())

# Subgraphs
subgraphs_len = model.SubgraphsLength()
print("Subgraphs:", subgraphs_len)

subgraph = model.Subgraphs(0)

print("Tensors:", subgraph.TensorsLength())
print("Operators:", subgraph.OperatorsLength())

for i in range(subgraph.TensorsLength()):
    tensor = subgraph.Tensors(i)
    name = tensor.Name().decode()
    shape = tensor.ShapeAsNumpy()
    dtype = tensor.Type()
    buffer_index = tensor.Buffer()
    buffer = model.Buffers(buffer_index)

    print(i, name, tensor.ShapeAsNumpy())

    if buffer.DataLength() == 0:
        print("No data (likely runtime tensor)")
    else:
        raw_data = buffer.DataAsNumpy()
        print("Raw bytes length:", len(raw_data))

breakpoint()