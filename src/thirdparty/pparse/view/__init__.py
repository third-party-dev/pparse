#!/usr/bin/env python3

from thirdparty.pparse.view.safetensors import SafeTensors

# ! BUG: Creating PARSER_REGISTRY in Onnx() assumes a relative file path.
#from thirdparty.pparse.view.onnx import Onnx