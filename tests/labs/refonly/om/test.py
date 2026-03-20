#!/usr/bin/env python3

import sys
import struct
import re


# -----------------------------
# Low-level parsing
# -----------------------------

def read_varint(data, offset):
    result = 0
    shift = 0

    while True:
        if offset >= len(data):
            raise ValueError("Varint overflow")

        b = data[offset]
        offset += 1

        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break

        shift += 7

    return result, offset


def parse_fields(data, start, end, depth=0, max_depth=5):
    """
    Recursively parse protobuf-like fields.
    Returns nested structure.
    """
    offset = start
    fields = []

    while offset < end:
        try:
            key, offset = read_varint(data, offset)
        except Exception:
            break

        field_num = key >> 3
        wire_type = key & 0x7

        if wire_type == 0:  # varint
            val, offset = read_varint(data, offset)

        elif wire_type == 1:  # 64-bit
            val = data[offset:offset+8]
            offset += 8

        elif wire_type == 2:  # length-delimited
            length, offset = read_varint(data, offset)
            val = data[offset:offset+length]

            # recurse if reasonable
            if depth < max_depth:
                try:
                    sub = parse_fields(val, 0, len(val), depth+1, max_depth)
                    val = sub
                except Exception:
                    pass

            offset += length

        elif wire_type == 5:  # 32-bit
            val = data[offset:offset+4]
            offset += 4

        else:
            break

        fields.append((field_num, wire_type, val))

    return fields


# -----------------------------
# OM container parsing
# -----------------------------

def read_header(data):
    magic = data[0:4]

    version, dummy, header_size, part_count = struct.unpack_from("<HHII", data, 4)
    part_offset = struct.unpack_from("<Q", data, 16)[0]

    return {
        "magic": magic,
        "version": version,
        "header_size": header_size,
        "part_count": part_count,
        "part_offset": part_offset,
    }


def read_partitions(data, offset, count):
    parts = []

    for i in range(count):
        base = offset + i * 16

        p_type, p_off, p_size, flags = struct.unpack_from("<IIII", data, base)

        parts.append({
            "type": p_type,
            "offset": p_off,
            "size": p_size,
            "flags": flags
        })

    return parts


def get_partition(data, parts, ptype):
    for p in parts:
        if p["type"] == ptype:
            return data[p["offset"]:p["offset"] + p["size"]]
    return None


# -----------------------------
# Utility
# -----------------------------

def extract_strings(data):
    return re.findall(rb"[A-Za-z_][A-Za-z0-9_/]{3,}", data)


def print_tree(fields, indent=0, max_items=10):
    """
    Pretty print parsed field tree (limited)
    """
    for i, (num, wt, val) in enumerate(fields[:max_items]):
        prefix = "  " * indent

        if isinstance(val, list):
            print(f"{prefix}Field {num} (len-delim -> submessage)")
            print_tree(val, indent+1, max_items)
        elif isinstance(val, bytes):
            if len(val) < 32:
                print(f"{prefix}Field {num} (bytes): {val}")
            else:
                print(f"{prefix}Field {num} (bytes len={len(val)})")
        else:
            print(f"{prefix}Field {num} (varint): {val}")


# -----------------------------
# Main
# -----------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <model.om>")
        sys.exit(1)

    path = sys.argv[1]

    with open(path, "rb") as f:
        data = f.read()

    print("== HEADER ==")
    header = read_header(data)
    for k, v in header.items():
        print(f"{k}: {v}")

    print("\n== PARTITIONS ==")
    parts = read_partitions(data, header["part_offset"], header["part_count"])

    for p in parts:
        print(p)

    # type 0 is usually MODEL_DEF
    model_def = get_partition(data, parts, 0)

    if not model_def:
        print("\n[!] No MODEL_DEF partition found")
        return

    print(f"\n== MODEL_DEF size: {len(model_def)} bytes ==")

    print("\n== STRINGS (quick scan) ==")
    strings = extract_strings(model_def)
    for s in strings[:50]:
        print(s.decode(errors="ignore"))

    print("\n== PARSED FIELD TREE (truncated) ==")
    fields = parse_fields(model_def, 0, len(model_def))
    print_tree(fields, max_items=10)


if __name__ == "__main__":
    main()