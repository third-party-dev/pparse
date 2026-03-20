#!/usr/bin/env python3

import json
import flatbuffers
from flatbuffers.number_types import Uint8Flags, Int32Flags, Float32Flags

# Load schema JSON
with open("schema.json") as f:
    schema = json.load(f)

# Load FlatBuffer binary
with open("yolov5su_float32.tflite", "rb") as f:
    data = f.read()

buf = bytearray(data)

# FlatBuffer base type mapping
BASE_TYPE_READERS = {
    "int": lambda buf, off: flatbuffers.encode.Get(Int32Flags, buf, off),
    "uint": lambda buf, off: flatbuffers.encode.Get(Uint8Flags, buf, off),
    "float": lambda buf, off: flatbuffers.encode.Get(Float32Flags, buf, off),
    "string": lambda buf, off: flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, off),
    # You can extend with more types as needed
}

def read_vector(buf, offset, elem_type, elem_count):
    """Reads a vector from the buffer"""
    vec = []
    # vector starts with uoffset pointing to data
    vec_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
    for i in range(elem_count):
        # Simplified: assume scalars
        vec.append(BASE_TYPE_READERS[elem_type](buf, vec_offset + i*4))
    return vec

def read_vector_of_objects(buf, table_start, vtable_offset, base_offset):
    """
    buf: entire flatbuffer bytes
    table_start: start of root table
    vtable_offset: field offset in table's vtable
    base_offset: table's starting offset
    """
    # 1. Read vtable offset
    vtable_rel = read_uoffset(buf, table_start - read_uoffset(buf, table_start))
    vtable_start = table_start - vtable_rel

    # 2. Read field offset from vtable
    field_offset = struct.unpack_from('<H', buf, vtable_start + vtable_offset)[0]
    if field_offset == 0:
        return []  # optional field is missing

    # 3. Absolute vector offset
    vec_start = table_start + field_offset

    # 4. Vector length (first 4 bytes)
    length = read_uoffset(buf, vec_start)
    vec_data_start = vec_start + 4

    # 5. Read each element offset
    elements = []
    for i in range(length):
        elem_offset = read_uoffset(buf, vec_data_start + i * 4)
        elem_abs = vec_data_start + i * 4 + elem_offset  # object start
        elements.append(elem_abs)  # you can later parse the object here
    return elements

'''
{
    "name": "buffers",
    "type": {
        "base_type": "Vector",
        "element": "Obj",
        "index": 15,
        "element_size": 4
    },
    "id": 4,
    "offset": 12,
    "optional": true
},
'''

def walk_table(buf, table_offset, table_schema):
    """Recursively walk a table"""
    result = {}

    breakpoint()
    for field in table_schema.get("fields", []):
        name = field["name"]
        base_type = field["type"]["base_type"]
        offset = field.get("offset", 4)  # default offset; in real FlatBuffers you get from vtable
        # Simplified: reading scalars and strings only

        if base_type in ("table", "Table"):
            nested_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, table_offset + offset)
            if nested_offset != 0:
                nested_table = walk_table(buf, table_offset + nested_offset, field["type"]["table"])
                result[name] = nested_table
            else:
                result[name] = None
        elif base_type in ("string", "String"):
            str_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, table_offset + offset)
            if str_offset != 0:
                str_start = table_offset + str_offset
                str_len = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, str_start)
                s = buf[str_start + 4: str_start + 4 + str_len].decode('utf-8')
                result[name] = s
            else:
                result[name] = None
        elif base_type in ("vector", "Vector"):
            vec_elem = field["type"].get("element", "unknown")
            if vec_elem in ("Obj"):
                result[name] = read_vector_of_objects(buf, table_start, table_offset, offset)

            vec_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, table_offset + offset)
            vec_count = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, table_offset + vec_offset)
            result[name] = read_vector(buf, table_offset + vec_offset, vec_info["base_type"], vec_count)
        else:  # scalar
            result[name] = BASE_TYPE_READERS.get(base_type, lambda b,o: None)(buf, table_offset + offset)
    return result

# Assuming root table is the first one in schema
root_table_schema = schema["root_table"]  # you may need to adjust key name
root_offset = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, 0)
data_dict = walk_table(buf, root_offset, root_table_schema)
breakpoint()

import pprint
pprint.pprint(data_dict)
