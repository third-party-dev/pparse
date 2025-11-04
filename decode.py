import io
import struct
from google.protobuf import descriptor_pb2

def read_varint(stream):
    shift = 0
    result = 0
    while True:
        b = stream.read(1)
        if not b:
            raise EOFError
        byte = b[0]
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result

def read_length_delimited(stream):
    length = read_varint(stream)
    return stream.read(length)

def read_fixed32(stream):
    return struct.unpack("<I", stream.read(4))[0]

def read_fixed64(stream):
    return struct.unpack("<Q", stream.read(8))[0]

def decode_field(wire_type, stream):
    if wire_type == 0:
        return read_varint(stream)
    elif wire_type == 1:
        return read_fixed64(stream)
    elif wire_type == 2:
        return read_length_delimited(stream)
    elif wire_type == 5:
        return read_fixed32(stream)
    else:
        raise ValueError(f"Unsupported wire type {wire_type}")

def parse_message(stream, msg_desc, desc_lookup):
    msg = {}
    while True:
        try:
            key = read_varint(stream)
        except EOFError:
            break
        field_number = key >> 3
        wire_type = key & 0x7

        field_desc = None
        for f in msg_desc.field:
            if f.number == field_number:
                field_desc = f
                break
        if not field_desc:
            # Skip unknown
            decode_field(wire_type, stream)
            continue

        value = decode_field(wire_type, stream)

        # Recursively decode if it’s a submessage
        if field_desc.type == field_desc.TYPE_MESSAGE and wire_type == 2:
            substream = io.BytesIO(value)
            subdesc = desc_lookup[field_desc.type_name.strip(".")]
            value = parse_message(substream, subdesc, desc_lookup)

        # Store it
        msg[field_desc.name] = value
    return msg



desc_set = descriptor_pb2.FileDescriptorSet()
desc_set.ParseFromString(open("onnx.pb", "rb").read())

desc_lookup = {}

for file in desc_set.file:
    for msg in file.message_type:
        desc_lookup[f".{file.package}.{msg.name}"] = msg

# Assume we want to parse message type “.my.package.Person”
msg_desc = desc_lookup[".my.package.Person"]

with open("person.bin", "rb") as f:
    stream = io.BytesIO(f.read())

decoded = parse_message(stream, msg_desc, desc_lookup)
print(decoded)

