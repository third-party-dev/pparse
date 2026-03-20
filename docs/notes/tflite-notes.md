
sudo apt install flatbuffers-compiler

```sh
# dump tflite as json
flatc --json schema.fbs -- model.tflite
```

Language bindings:

```sh
# Example for Python
flatc --python schema.fbs
# Or for C++
flatc --cpp schema.fbs
```

```python
import flatbuffers
import tflite.Model  # generated from flatc

with open("model.tflite", "rb") as f:
    buf = f.read()

model = tflite.Model.Model.GetRootAsModel(buf, 0)

print("TFLite version:", model.Version())
print("Number of subgraphs:", model.SubgraphsLength())

subgraph = model.Subgraphs(0)
for i in range(subgraph.TensorsLength()):
    tensor = subgraph.Tensors(i)
    buffer_index = tensor.Buffer()
    buffer = model.Buffers(buffer_index)
    raw_bytes = buffer.DataAsNumpy()  # or Data() for bytes
    print(tensor.Name(), raw_bytes.shape)

```

Flatbuffers from source:

```sh
sudo apt install -y cmake g++ git
git clone https://github.com/google/flatbuffers.git
cd flatbuffers
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
sudo cmake --install build
```
