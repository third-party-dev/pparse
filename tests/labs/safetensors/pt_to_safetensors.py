#!/usr/bin/env python3

# Note: For yolo, run from ultralytics docker recommended.

'''
Example:
  docker run --rm -ti -u $(id -u):$(id -g) \
    -v $(pwd):/opt/work -w /opt/work \
    ultralytics/ultralytics:8.4.8-python-export bash
'''

import torch
from safetensors.torch import save_file
import sys

model = torch.load(sys.argv[1], map_location="cpu", weights_only=False)

if "model" in model:
    state_dict = model["model"].state_dict()
elif hasattr(model, "state_dict"):
    state_dict = model.state_dict()
else:
    state_dict = model

save_file(state_dict, sys.argv[2])

print("Completed conversion.")