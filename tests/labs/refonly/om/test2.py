#!/usr/bin/env python3

"""
Huawei OM model file header extractor.

OM File Layout
--------------
Offset  Size  Field
------  ----  -----
0x000      4  magic            b'IMOD'
0x004      1  reserved         (always 0x00)
0x005      1  version_major    (e.g. 1)
0x006      2  version_minor    u16 LE (e.g. 0)
0x008     16  checksum         MD5 or zeros when unused
0x018     54  reserved/zeros
0x054     64  model_name       null-padded UTF-8 string
0x094      4  reserved
0x098      4  model_type       u32 LE  (0=OFFLINE, 1=ONLINE, …)
0x09c      4  target_type      u32 LE  (1=MINI, 2=LITE, …)
0x0a0     16  compiler_version null-padded ASCII (e.g. "1.11.z.0")
0x0b0      4  reserved
0x0b4      4  num_inputs       u32 LE
0x0b8      8  model_data_size  u64 LE  (file_size - HEADER_SIZE)
0x0c0     64  reserved/zeros
                                       total = 256 bytes
0x100      *  partition_table  (also listed as partition 0, type 8)

Partition Table (starts at 0x100)
----------------------------------
  [u64 LE] num_partitions
  num_partitions × 24-byte entries:
    [u64 LE] partition_type   (see PartitionType enum)
    [u64 LE] data_offset      relative to end of file header (byte 256)
    [u64 LE] data_size        in bytes
"""

import struct
import dataclasses
from enum import IntEnum
from pathlib import Path
from typing import List


MAGIC = b"IMOD"
HEADER_SIZE = 256          # fixed file header
PARTITION_ENTRY_SIZE = 24  # bytes per partition entry


class PartitionType(IntEnum):
    MODEL_DEF       = 0   # Graph IR (protobuf)
    WEIGHTS         = 1   # Weight tensors
    TBE_KERNELS     = 2   # Compiled TBE kernel binary
    TASK_INFO       = 3   # Task / schedule metadata
    PARTITION_TABLE = 8   # Self-referencing partition index
    UNKNOWN         = -1

    @classmethod
    def _missing_(cls, value):
        obj = int.__new__(cls, value)
        obj._name_ = f"UNKNOWN_{value}"
        obj._value_ = value
        return obj


@dataclasses.dataclass
class PartitionEntry:
    partition_type: PartitionType
    file_offset: int    # absolute offset within the file
    data_size: int      # size in bytes

    def __str__(self):
        return (
            f"{self.partition_type.name:<20}"
            f"  file_offset=0x{self.file_offset:08x}"
            f"  size={self.data_size:>12} bytes"
        )


@dataclasses.dataclass
class OMHeader:
    magic: bytes
    version_major: int
    version_minor: int
    checksum: bytes
    model_name: str
    model_type: int
    target_type: int
    compiler_version: str
    num_inputs: int
    model_data_size: int
    partitions: List[PartitionEntry]

    def __str__(self):
        lines = [
            "=== Huawei OM File Header ===",
            f"  magic            : {self.magic}",
            f"  version          : {self.version_major}.{self.version_minor}",
            f"  checksum         : {self.checksum.hex()}",
            f"  model_name       : {self.model_name!r}",
            f"  model_type       : {self.model_type}",
            f"  target_type      : {self.target_type}",
            f"  compiler_version : {self.compiler_version!r}",
            f"  num_inputs       : {self.num_inputs}",
            f"  model_data_size  : {self.model_data_size} bytes",
            "",
            f"  Partitions ({len(self.partitions)}):",
        ]
        for i, p in enumerate(self.partitions):
            lines.append(f"    [{i}] {p}")
        return "\n".join(lines)


class OMFormatError(ValueError):
    """Raised when the file does not look like a valid OM model."""


def parse_header(data: bytes) -> OMHeader:
    """
    Parse the 256-byte fixed header and partition table from raw bytes.

    Parameters
    ----------
    data : bytes
        At minimum the first 256 bytes of an OM file (the fixed header).
        Pass the full file contents to also parse the partition table.

    Returns
    -------
    OMHeader

    Raises
    ------
    OMFormatError
        If the magic number is wrong or the data is too short.
    """
    if len(data) < HEADER_SIZE:
        raise OMFormatError(
            f"Data too short: need at least {HEADER_SIZE} bytes, got {len(data)}"
        )

    # --- magic ---
    magic = data[0:4]
    if m1agic != MAGIC:
        raise OMFormatError(
            f"Bad magic: expected {MAGIC!r}, got {magic!r}"
        )

    # --- version ---
    version_major = data[5]
    version_minor = struct.unpack_from("<H", data, 6)[0]

    # --- checksum (16 bytes, may be all-zero) ---
    checksum = data[0x08:0x18]

    # --- model name (64 bytes, null-padded) ---
    model_name = data[0x54:0x94].split(b"\x00")[0].decode("utf-8", errors="replace")

    # --- model / target type ---
    model_type, target_type = struct.unpack_from("<II", data, 0x98)

    # --- compiler version string (16 bytes, null-padded) ---
    compiler_version = (
        data[0xA0:0xB0].split(b"\x00")[0].decode("ascii", errors="replace")
    )

    # --- num inputs, model data size ---
    num_inputs = struct.unpack_from("<I", data, 0xB4)[0]
    model_data_size = struct.unpack_from("<Q", data, 0xB8)[0]

    # --- partition table ---
    partitions: List[PartitionEntry] = []
    if len(data) > HEADER_SIZE + 8:
        num_partitions = struct.unpack_from("<Q", data, HEADER_SIZE)[0]
        table_end = HEADER_SIZE + 8 + num_partitions * PARTITION_ENTRY_SIZE
        if len(data) >= table_end:
            for i in range(num_partitions):
                entry_off = HEADER_SIZE + 8 + i * PARTITION_ENTRY_SIZE
                ptype_val, poffset, psize = struct.unpack_from(
                    "<QQQ", data, entry_off
                )
                partitions.append(
                    PartitionEntry(
                        partition_type=PartitionType(ptype_val),
                        file_offset=HEADER_SIZE + poffset,
                        data_size=psize,
                    )
                )

    return OMHeader(
        magic=magic,
        version_major=version_major,
        version_minor=version_minor,
        checksum=checksum,
        model_name=model_name,
        model_type=model_type,
        target_type=target_type,
        compiler_version=compiler_version,
        num_inputs=num_inputs,
        model_data_size=model_data_size,
        partitions=partitions,
    )


def read_header(path: str | Path) -> OMHeader:
    """
    Read and parse the header from an OM model file on disk.

    Only the first ~512 bytes are read — the weight data is never loaded.

    Parameters
    ----------
    path : str or Path
        Path to the .om file.

    Returns
    -------
    OMHeader
    """
    path = Path(path)
    # 256-byte fixed header + up to 10 partition entries (each 24 bytes) + 8-byte count
    read_size = HEADER_SIZE + 8 + 10 * PARTITION_ENTRY_SIZE
    with path.open("rb") as f:
        data = f.read(read_size)
    return parse_header(data)


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Usage: python {Path(__file__).name} <model.om>")
        sys.exit(1)

    header = read_header(sys.argv[1])
    print(header)