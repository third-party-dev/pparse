import io
import pathlib

import logging
log = logging.getLogger(__name__)

def has_mmap():
    try:
        import mmap
    except:
        return None

    try:
        with mmap.mmap(-1, 1) as m:
            m[0] = b"x"[0]
    except:
        return None
    
    return mmap

mmap = has_mmap()

def hexdump(data, length=None):
    if isinstance(data, io.BytesIO):
        data = data.getvalue()

    if length is None:
        length = len(data)
    data = data[:length]

    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{byte:02x}' for byte in chunk)
        ascii_part = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        print(f'{i:08x}: {hex_part:<47}  {ascii_part}')

def find_project_root(start: pathlib.Path = None) -> pathlib.Path:
    if start is None:
        start = pathlib.Path(__file__).resolve()
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    raise FileNotFoundError("pyproject.toml not found.")