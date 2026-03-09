Formats _capable_ of containing a full model:
- PyTorch (.pt/.pth) - Ultralytics source of truth.
- Tensorflow SavedModel (saved_model.pb) - Contains graph and weights.
- Full ONNX (.onnx) - Model interchange with standardized graph ops.
- Keras (.h5)
- MindSpore Checkpoint (.ckpt)
- Paddle (.pdparams, .pdmodel)

Typically Inference Only
- TFLite (.tflite)
- TensorRT (.engine, .plan) - NVIDIA Runtime Format
- OpenVINO (.xml, .bin) - Intel IR
- EdgeTPU / Coral - For TPU
- CoreML (.mlmodel, .mlmodelc) - Apple Inference
- NNAPI - Android Inference
- DirectML / DML - Windows GPU Inference
- SNPE DLR / DLC (.dlc, .dlr) - Qualcomm Inference
- MindIR (.mindir)
- PaddleLite - (.nb)
- Huawei Ascend CANN
- Cambricon - (.mlu, .model)
- Huawei "Offline Model" (.om)



atc \
  --model=model.onnx \
  --framework=5 \
  --input_shape="input:1,3,640,640" \
  --output=yolov5s \
  --soc_version=Ascend310 \
  --input_format=NCHW \
  --output_type=FP32

docker pull huggingface/transformers-pytorch-cpu:4.18.0
docker pull huggingface/transformers-pytorch-cpu:latest (1.2GB, 4yrs old)

docker pull huggingface/transformers-all-latest-gpu-test:latest (12GB, 3mo old)

docker pull huggingface/transformers-pytorch-amd-gpu:latest (11.7GB, 4d old)

docker pull huggingface/transformers-all-latest-gpu-push-ci:latest (9.2GB 3mo old)

docker pull huggingface/transformers-cpu:4.18.0 (1.3GB, 4yrs old)

docker pull huggingface/transformers-pytorch-amd-gpu-push-ci:latest (28.7GB, 4mo old)

Note: transformers-cli will not create or train. Its does conversion (amongst other things)

```sh
docker pull hexchip/ascend-dev:cann8.0.0-310b-pytorch2.1.0-mindie1.0.0 (3.9GB, 9mo old)

source /home/HwHiAiUser/Ascend/ascend-toolkit/8.0.0/bin/setenv.bash

$ atc --model=/workspace/yolov5su.onnx --framework=5 --output=/workspace/yolov5su --input_format=NCHW --input_shape="images:1,3,640,640" --soc_version=Ascend310
ATC start working now, please wait for a moment.
...
ATC run success, welcome to the next use.
```



http://repo.huaweicloud.com/ubuntu

```sh
# Unhappy about onnx Op with this one ...
atc \
  --model=/workspace/yolov5su.onnx \
  --framework=5 \
  --output=/workspace/yolov5su \
  --input_format=NCHW \
  --input_shape="images:1,3,640,640" \
  --soc_version=Ascend310
```