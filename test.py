#!/usr/bin/env python3

'''
apt-get install protobuf-compiler
pip install protobuf
'''

from google.protobuf import descriptor_pb2

# Load the descriptor set
with open("onnx.pb", "rb") as f:
    desc_set = descriptor_pb2.FileDescriptorSet.FromString(f.read())

breakpoint()

# Iterate over the files and messages
for file_desc in desc_set.file:
    print("File:", file_desc.name)
    for msg in file_desc.message_type:
        print("  Message:", msg.name)
        for field in msg.field:
            print("    Field:", field.name, field.number, field.type_name)
