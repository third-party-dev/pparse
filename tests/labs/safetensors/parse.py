#!/usr/bin/env python3

from safetensors.numpy import load_file
import sys

tensors = load_file(sys.argv[1])

for name, array in tensors.items():
    print("Name:", name)
    print("Shape:", array.shape)
    print("Dtype:", array.dtype)
    print("Data length (bytes):", array.nbytes)
    print("-" * 40)