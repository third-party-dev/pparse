#!/usr/bin/env python3

"""
rknn_parser.py — RKNN binary format parser
Based on observed file layout from hex analysis.

Confirmed structure:
  0x0000: "RKNN" magic
  0x0008: u32 LE  — number of sections (= 6 in sample)
  0x0011: u32 LE  — file size (bytes 0x11–0x14 = 1c da 9d 00 → read as u32 LE from 0x10)
  0x0040: u32 LE  — inner block size (= 0x50 = 80)
  0x0044: "RKNN" — nested inner header magic
  0x0060: u16[] table — relative offsets inside the inner block
  0x0090: u32 LE  — section descriptor block size (= 0x30 = 48)
  0x0094: padding / version byte (0x02 seen)
  0x0098: u32 LE  — section count again (= 6)
  0x009C+: 6 × section descriptor entries (size TBD, contains offset+size+type)
"""

import struct
import zlib
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

MAGIC = b"RKNN"

OUTER_HEADER_SIZE = 0x40   # 64 bytes
INNER_HEADER_SIZE = 0x50   # 80 bytes (read from 0x40–0x43)
SECTION_TABLE_OFFSET = 0x90

KNOWN_SECTION_TYPES = {
    0x00: "container_metadata",
    0x01: "model_config",
    0x02: "graph",
    0x03: "tensor_info",
    0x04: "weights",
    0x05: "quantization",
    0x06: "npu_binary",
    0x07: "platform_info",
}


# ── Low-level reader ──────────────────────────────────────────────────────────

class Reader:
    def __init__(self, data: bytes):
        self._d = data
        self._p = 0

    @property
    def pos(self): return self._p

    @property
    def remaining(self): return len(self._d) - self._p

    def seek(self, n: int): self._p = n

    def skip(self, n: int): self._p += n

    def peek(self, n: int = 4) -> bytes:
        return self._d[self._p : self._p + n]

    def read(self, n: int) -> bytes:
        chunk = self._d[self._p : self._p + n]
        if len(chunk) < n:
            raise EOFError(f"Read {n} @ {self._p:#010x}: only {len(chunk)} bytes left")
        self._p += n
        return chunk

    def u8(self)  -> int: return struct.unpack_from("<B", self.read(1))[0]
    def u16(self) -> int: return struct.unpack_from("<H", self.read(2))[0]
    def u32(self) -> int: return struct.unpack_from("<I", self.read(4))[0]
    def u64(self) -> int: return struct.unpack_from("<Q", self.read(8))[0]

    def bytes_at(self, offset: int, n: int) -> bytes:
        return self._d[offset : offset + n]

    def u32_at(self, offset: int) -> int:
        return struct.unpack_from("<I", self._d, offset)[0]

    def u16_at(self, offset: int) -> int:
        return struct.unpack_from("<H", self._d, offset)[0]

    def u64_at(self, offset: int) -> int:
        return struct.unpack_from("<Q", self._d, offset)[0]


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class OuterHeader:
    magic: bytes          # 0x00: "RKNN"
    version: int          # 0x04: u32
    num_sections: int     # 0x08: u32
    file_size: int        # 0x10: u32  (bytes 0x10–0x13 based on sample)
    # 0x14–0x3F: reserved/padding


@dataclass
class InnerHeader:
    block_size: int       # 0x40: u32 — size of this inner header block
    magic: bytes          # 0x44: "RKNN"
    offset_table: list    # u16 values starting at 0x60
    # 0x80 onward: more fields TBD


@dataclass
class SectionDescriptor:
    index: int
    section_type: int
    type_name: str
    data_offset: int      # absolute offset into file
    data_size: int
    # Additional fields (alignment, flags, etc.) TBD


@dataclass
class Section:
    descriptor: SectionDescriptor
    raw: bytes = field(repr=False)
    sub_format: str = "raw"
    decoded: Optional[bytes] = field(default=None, repr=False)


# ── Sub-format detection ──────────────────────────────────────────────────────

def detect_sub_format(data: bytes) -> str:
    if len(data) < 2:
        return "raw"
    sig = data[:4]
    if data[:2] in (b"\x78\x9c", b"\x78\x01", b"\x78\xda"):
        return "zlib"
    if data[:2] == b"\x1f\x8b":
        return "gzip"
    if sig == MAGIC:
        return "rknn_nested"
    # Crude protobuf check: wire type in low 3 bits of first byte
    if data[0] & 0x07 in {0, 1, 2, 5} and len(data) > 4:
        return "protobuf_candidate"
    try:
        data[:128].decode("utf-8")
        if any(c in data[:128] for c in (b"{", b"<", b"name")):
            return "text"
    except UnicodeDecodeError:
        pass
    return "raw"


def try_decompress(data: bytes) -> Optional[bytes]:
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS, zlib.MAX_WBITS | 16):
        try:
            return zlib.decompress(data, wbits)
        except zlib.error:
            pass
    return None


# ── Protobuf field scanner ────────────────────────────────────────────────────

def scan_protobuf(data: bytes, max_fields: int = 32) -> list[dict]:
    r = Reader(data)
    fields = []
    while not r.remaining == 0 and len(fields) < max_fields:
        try:
            # read varint tag
            result, shift = 0, 0
            while True:
                b = r.u8()
                result |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
        except EOFError:
            break
        wire = result & 0x07
        fnum = result >> 3
        try:
            if wire == 0:       # varint value
                v, shift = 0, 0
                while True:
                    b = r.u8(); v |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                fields.append({"field": fnum, "wire": 0, "value": v})
            elif wire == 1:     # 64-bit fixed
                fields.append({"field": fnum, "wire": 1, "value": r.u64()})
            elif wire == 2:     # length-delimited
                length, shift = 0, 0
                while True:
                    b = r.u8(); length |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                if length > r.remaining: break
                payload = r.read(length)
                fields.append({"field": fnum, "wire": 2, "length": length,
                               "preview": payload[:32].hex()})
            elif wire == 5:     # 32-bit fixed
                fields.append({"field": fnum, "wire": 5, "value": r.u32()})
            else:
                break  # unknown wire type → bail
        except EOFError:
            break
    return fields


# ── Hex dump ─────────────────────────────────────────────────────────────────

def hexdump(data: bytes, base_offset: int = 0, width: int = 16, rows: int = 8) -> str:
    lines = []
    limit = min(len(data), width * rows)
    for i in range(0, limit, width):
        chunk = data[i:i+width]
        hex_col   = " ".join(f"{b:02x}" for b in chunk)
        ascii_col = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        lines.append(f"  {base_offset+i:08x}:  {hex_col:<{width*3}}  |{ascii_col}|")
    if len(data) > limit:
        lines.append(f"  ... ({len(data) - limit} more bytes)")
    return "\n".join(lines)


# ── Main parser ───────────────────────────────────────────────────────────────

class RKNNParser:

    def __init__(self, path: str):
        self.path = Path(path)
        self.raw  = self.path.read_bytes()
        self.r    = Reader(self.raw)
        self.outer: Optional[OuterHeader]    = None
        self.inner: Optional[InnerHeader]    = None
        self.descriptors: list[SectionDescriptor] = []
        self.sections:    list[Section]           = []

    # ── Step 1: outer header ────────────────────────────────────────────────

    def _parse_outer_header(self) -> OuterHeader:
        r = self.r
        r.seek(0x00)
        magic = r.read(4)
        if magic != MAGIC:
            raise ValueError(f"Bad magic: {magic!r} — not an RKNN file")

        version      = r.u32()          # 0x04
        num_sections = r.u32()          # 0x08
        r.skip(4)                       # 0x0C — unknown u32 (= 0 in sample)
        file_size    = r.u32()          # 0x10 → 1c da 9d 00 in sample

        # Sanity check
        if file_size != 0 and file_size != len(self.raw):
            print(f"  [!] Header file_size {file_size:#x} != actual {len(self.raw):#x} — may be wrong field offset")

        # 0x14–0x3F are reserved; skip to end of outer header
        return OuterHeader(magic, version, num_sections, file_size)

    # ── Step 2: inner / nested header ───────────────────────────────────────

    def _parse_inner_header(self) -> InnerHeader:
        r = self.r
        r.seek(0x40)

        block_size = r.u32()            # 0x40: = 0x50 in sample
        magic      = r.read(4)          # 0x44: "RKNN"
        r.skip(8)                       # 0x48–0x4F: unknown

        # 0x50–0x5F: more unknown fields (two u64s? two u32 pairs?)
        r.skip(0x10)

        # 0x60: u16 offset table — read until we hit non-incrementing or 0-gap
        offset_table = []
        r.seek(0x60)
        for _ in range(24):             # maximum reasonable entries
            val = r.u16()
            if val == 0 and offset_table:
                break
            offset_table.append(val)

        return InnerHeader(block_size, magic, offset_table)

    # ── Step 3: section descriptor table ───────────────────────────────────

    def _parse_section_table(self) -> list[SectionDescriptor]:
        """
        From 0x90 onward. Observed bytes:
          30 00 00 00   → descriptor block or entry size = 48
          00 00 00 02   → flags/version = 0x02000000? or padding + u8 0x02
          06 00 00 00   → section count = 6
          40 04 00 00   → entry[0].data_size  (= 0x0440 = 1088)
          4c 04 00 00   → entry[0].data_offset? (= 0x044c)
          78 01 00 00   → entry[1].data_size  (= 0x0178 = 376)
          4f 4f 00 00   → entry[1] something  ("OO" as ASCII)
          24 01 00 00   → ...
          14 01 00 00   →
          04 01 00 00   →
          f8 00 00 00   →
          b8 00 00 00   →
        The pattern of alternating pairs of u32 strongly suggests
        each section = { data_size: u32, data_offset: u32 } or vice-versa.
        We'll try both interpretations and validate against file bounds.
        """
        r = self.r
        r.seek(SECTION_TABLE_OFFSET)

        descriptor_block_size = r.u32()   # 0x90: = 0x30 = 48
        _flags_or_version     = r.u32()   # 0x94: = 0x02000000
        section_count         = r.u32()   # 0x98: = 6
        r.skip(4)                         # 0x9C: padding / alignment

        # From 0xA0 onward — parse pairs of u32
        # Based on observed data:
        #   0xA0: 40 04 00 00 = 0x0440
        #   0xA4: 4c 04 00 00 = 0x044c
        #   0xA8: 78 01 00 00 = 0x0178
        #   0xAC: 4f 4f 00 00 = 0x4f4f   ← odd; "OO" in ASCII — may be a tag/type
        # Let's try {offset: u32, size: u32} AND {size: u32, offset: u32}
        raw_pairs = []
        for _ in range(section_count):
            a = r.u32()
            b = r.u32()
            raw_pairs.append((a, b))

        # Heuristic: the larger of {a, b} is more likely the offset
        # (offsets grow through the file; sizes tend to be smaller than offsets for large files)
        descriptors = []
        file_len = len(self.raw)
        for i, (a, b) in enumerate(raw_pairs):
            # Try interpretation A: a=offset, b=size
            # Try interpretation B: a=size, b=offset
            if b < file_len and a < b:
                # a is likely size, b is offset (size < offset makes sense for early sections)
                offset, size = b, a
            elif a < file_len and b <= a:
                # a is offset, b is size
                offset, size = a, b
            else:
                # Fallback — treat larger as offset
                offset, size = (a, b) if a > b else (b, a)

            section_type  = i  # we don't have the type byte yet; use index as placeholder
            descriptors.append(SectionDescriptor(
                index       = i,
                section_type= section_type,
                type_name   = KNOWN_SECTION_TYPES.get(section_type, f"section_{i}"),
                data_offset = offset,
                data_size   = size,
            ))

        return descriptors

    # ── Step 4: load section payloads ───────────────────────────────────────

    def _load_sections(self) -> list[Section]:
        sections = []
        for desc in self.descriptors:
            raw = self.r.bytes_at(desc.data_offset, desc.data_size)
            fmt = detect_sub_format(raw)
            decoded = None
            if fmt in ("zlib", "gzip"):
                decoded = try_decompress(raw)
                if decoded:
                    fmt = f"{fmt}→raw ({len(decoded):,} bytes decompressed)"
            sections.append(Section(desc, raw, fmt, decoded))
        return sections

    # ── Public API ──────────────────────────────────────────────────────────

    def parse(self) -> "RKNNParser":
        print(f"\n{'─'*60}")
        print(f"  Parsing: {self.path.name}  ({len(self.raw):,} bytes)")
        print(f"{'─'*60}\n")

        print("[1] Outer header (0x0000–0x003F)")
        self.outer = self._parse_outer_header()
        print(f"  magic        : {self.outer.magic!r}")
        print(f"  version      : {self.outer.version:#010x}")
        print(f"  num_sections : {self.outer.num_sections}")
        print(f"  file_size    : {self.outer.file_size:#010x}  ({self.outer.file_size:,} bytes)")

        print("\n[2] Inner / nested header (0x0040–0x008F)")
        self.inner = self._parse_inner_header()
        print(f"  block_size   : {self.inner.block_size:#010x}")
        print(f"  magic        : {self.inner.magic!r}")
        print(f"  offset_table : {[hex(v) for v in self.inner.offset_table]}")

        print("\n[3] Section descriptor table (0x0090+)")
        self.descriptors = self._parse_section_table()
        for d in self.descriptors:
            print(f"  [{d.index}] type={d.section_type:#04x} ({d.type_name})"
                  f"  offset={d.data_offset:#010x}  size={d.data_size:,}")

        print("\n[4] Loading section payloads")
        self.sections = self._load_sections()
        for s in self.sections:
            size = len(s.raw)
            print(f"  [{s.descriptor.index}] {s.descriptor.type_name:<20}"
                  f"  {size:>10,} bytes  [{s.sub_format}]")

        return self

    def dump_section(self, index: int, rows: int = 16):
        s = self.sections[index]
        data = s.decoded if s.decoded else s.raw
        d = s.descriptor
        print(f"\n── Section [{index}]: {d.type_name}"
              f"  offset={d.data_offset:#010x}  size={d.data_size:,} ──")
        print(hexdump(data, base_offset=d.data_offset, rows=rows))

        if "protobuf" in s.sub_format or "zlib" in s.sub_format:
            payload = s.decoded if s.decoded else s.raw
            fields = scan_protobuf(payload[:1024])
            if fields:
                print(f"\n  Protobuf fields (first {len(fields)}):")
                for f in fields[:12]:
                    if "value" in f:
                        print(f"    field={f['field']:<4} wire={f['wire']}  value={f['value']}")
                    else:
                        print(f"    field={f['field']:<4} wire={f['wire']}  len={f['length']}  {f['preview']}")

    def dump_all_sections(self, rows: int = 4):
        for i in range(len(self.sections)):
            self.dump_section(i, rows=rows)

    def extract(self, index: int, out_path: str):
        s = self.sections[index]
        data = s.decoded if s.decoded else s.raw
        Path(out_path).write_bytes(data)
        print(f"  Wrote section [{index}] ({len(data):,} bytes) → {out_path}")

    def raw_range(self, start: int, length: int = 128):
        """Dump a raw byte range for manual analysis."""
        print(hexdump(self.raw[start:start+length], base_offset=start))


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python rknn_parser.py <model.rknn> [section_index [out_file]]")
        sys.exit(1)

    p = RKNNParser(sys.argv[1]).parse()
    p.dump_all_sections(rows=4)

    if len(sys.argv) >= 3:
        idx = int(sys.argv[2])
        out = sys.argv[3] if len(sys.argv) >= 4 else f"section_{idx}.bin"
        p.extract(idx, out)