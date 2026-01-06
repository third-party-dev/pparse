#!/usr/bin/env python3

from thirdparty.pparse.transformers import TransformersModelFactory

factory = TransformersModelFactory()
gpt2 = factory.auto_model_combos["AutoModelForCausalLM"]["gpt2"]

tmodel = factory.reconstruct_model("AutoModelForCausalLM", "gpt2")

# tmodel.save_torch_safetensors('./output/gpt2-safetensors')
# tmodel.save_torch_weights('./output/gpt2-weights')
# BROKEN tmodel.save_traced('./output/gpt2-traced')
# tmodel.save_torch_onnx('./output/gpt2onnx')

breakpoint()
