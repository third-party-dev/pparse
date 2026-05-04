#!/usr/bin/env python3

import struct
import sys

class RKNNHeader:

    MAGIC = 0x4E4E4B52

    def __init__(self, path):
        with open(path, 'rb') as fh:
            self._buf = fh.read()

        if len(self._buf) < 0x18:
            raise ValueError("Not enough data to parse file header.")
        raw_magic = struct.unpack_from('<Q', self._buf, 0x00)[0]

        # Note: 0x4e4e4b5254505943 'NNKRTPYC' is also a valid magic number.
        if (raw_magic) != RKNNHeader.MAGIC:
            raise ValueError(f"Bad magic: {raw_magic:#018x}")

        self.magic        = struct.unpack_from('<Q', self._buf, 0x00)[0]
        self.version      = struct.unpack_from('<Q', self._buf, 0x08)[0]
        self.export_size  = struct.unpack_from('<Q', self._buf, 0x10)[0]
        self.export_start = 0x40 if self.version >= 2 else 0x18
        self.export_end   = self.export_start + self.export_size

        # librknnrt.so code references a configSize after exportData
        self.config_start = self.export_end + 8
        if self.export_end + 8 <= len(self._buf):
            self.config_size = struct.unpack_from('<Q', self._buf, self.export_end)[0]
        else:
            self.config_size = 0
        self.config_end = self.config_start + self.config_size

        # Assuming export_start is flatbuffers, Note: flatbuffers is 32 bit.
        self._fb_base = self.export_start
        self._root_off =  struct.unpack_from('<I', self._buf, self._fb_base)[0]
        self._root_abs = self._fb_base + self._root_off

        self._fb_magic  = struct.unpack_from('<I', self._buf, self._fb_base + 4)[0]
        if self._fb_magic != RKNNHeader.MAGIC:
            raise ValueError(f"Bad FlatBuffer file identifier (magic): {self._fb_magic:08x}")


    def __str__(self):
        lines = [
            "RKNN File Header",
            f"  magic      : {self.magic:16x}",
            f"  version    : {self.version}",
            f"  export_size: {self.export_size:#012x}  ({self.export_size:,} bytes)",
            f"  export_blob: 0x{self.export_start:08x} – 0x{self.export_end:08x}",
            f"  config_size: {self.config_size:#012x}  ({self.config_size:,} bytes)",
            f"  config_blob: 0x{self.config_start:08x} – 0x{self.config_end:08x}",
            "",
            f"FlatBuffer (export blob) @ 0x{self._fb_base:08x}",
            f"  file_id    : {self._fb_magic:08x}",
            f"  root table : 0x{self._root_abs:08x}",
            #f"  vtable     : 0x{self._root.vtable_abs:08x}",
            #f"  n_fields   : {self._root.n_fields}",
        ]
        return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <model.rknn>", file=sys.stderr)
        sys.exit(1)
    print(RKNNHeader(sys.argv[1]))

if __name__ == "__main__":
    main()
