#!/usr/bin/env python3

import sys
import struct

with open("./models/sense-voice-encoder.rknn", "rb") as f:
    magic = f.read(4)
    version = struct.unpack("<I", f.read(4))[0]
    section_cnt = struct.unpack("<I", f.read(4))[0]
    dummy = struct.unpack("<I", f.read(4))[0]
    file_size = struct.unpack("<I", f.read(4))[0]

breakpoint()