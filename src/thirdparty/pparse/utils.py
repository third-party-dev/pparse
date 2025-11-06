import io

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