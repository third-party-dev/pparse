## the graph for this model, with these inputs, on this execution

PyTorch (& Chainer)
Tensorflow 2
JAX
MindSpore

## complete graph possible:

Tensorflow 1.x (graph mode)
Onnx
TVM / Relay
Tensorflow MLIR
Torch-MLIR
IREE
Theano (Legacy)

XLA / HLO (as a target IR) Used by Tensorflow, JAX, PyTorch ... only on traced regions.

## Testing for graph-ability

### data dependent control flows

not convertable:

```python
def forward(x):
    if x.sum() > 0:
        return x * 2
    else:
        return x / 2
```

convertable:

```python
def forward(x):
    return torch.where(x.sum() > 0, x * 2, x / 2)
```

### side effects

```python
self.counter += 1
self.cache.append(x)
```

### dynamic shapes

cant do:

```python
y = torch.zeros(x.sum().item())
```

can do:

```python
y = torch.zeros_like(x)
```

### recommended

- only torch.nn
- avoid .item()
- avoid conditionals (`if`)

### easy test

```python
torch.onnx.export(
    model,
    example_inputs,
    "model.onnx",
    opset_version=17,
    dynamo=True,  # IMPORTANT
)
```

Errors:

- PythonOp - Unconvertible python logic
- getitem on tensor - Dynamic Indexing
- aten:: op missing - Unsupported op
- Tensor.item() - Python scalar escape
- control flow - Python if / while

Inspect with:

- `onnxsim model.onnx` and `netron model.onnx`.

Onnx may fail for other reasons:

- Missing ops (including new-ish torch.nn ops)
- Complex indexing

## Other checks

runs in torch.compile()?
runs in toch.fx.symbolic_trace()?

## Another test method that is less complete

- heuristic scan

```python
import torch.fx as fx
gm = fx.symbolic_trace(model)
print(gm.graph)
```

- call_function - bad
- getattr - bad
- .item() - bad
