#!/usr/bin/env python3

import sys
from pprint import pprint
import torch
from torch.fx import symbolic_trace

from importlib import resources
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Enable running test script without pytest.
from thirdparty.pparse.utils import find_project_root
sys.path.insert(0, str(find_project_root()))

from transformers import AutoConfig, AutoModel, GPT2Model

# config = AutoConfig.from_pretrained("whisper")
# model = AutoModel.from_config(config)

#scripted_model = torch.jit.script(model)

# example_input = torch.randint(0, model.config.vocab_size, (1, 16))
# traced_model = torch.jit.trace(model, example_input)

class GPT2ForTracing(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.model = GPT2Model.from_pretrained("gpt2")

    def forward(self, input_ids):
        outputs = self.model(input_ids=input_ids)
        return outputs.last_hidden_state

wrapper = GPT2ForTracing().eval()
dummy_ids = torch.ones(1, 16, dtype=torch.long)
#graph = symbolic_trace(wrapper)
traced_model = torch.jit.trace(wrapper, dummy_ids)

#scripted_model = torch.jit.script(model)

#dummy_ids = torch.ones(1, 10, dtype=torch.long)
#traced_model = torch.jit.trace(model, dummy_ids)

# Requires installing onnxscript
# torch.onnx.export(
#     model,
#     dummy,
#     "gpt2.onnx",
#     input_names=["input_ids"],
#     output_names=['hidden_states'],
#     opset_version=17,
#     do_constant_folding=True,
# )

print("ALL DONE")
breakpoint()

