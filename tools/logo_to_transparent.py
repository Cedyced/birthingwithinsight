"""One-off: turn the flat-background logo PNG into a transparent line-art PNG (stdlib only).

Usage: python3 tools/logo_to_transparent.py in.png out.png [hex-line-colour]
"""
import struct, sys, zlib


def read_rgb_png(path):
    d = open(path, 'rb').read()
    i, idat = 8, b''
    while i < len(d):
        n, = struct.unpack('>I', d[i:i + 4])
        kind, chunk = d[i + 4:i + 8], d[i + 8:i + 8 + n]
        if kind == b'IHDR':
            w, h, depth, ctype = struct.unpack('>IIBB', chunk[:10])
            assert depth == 8 and ctype == 2, 'expects 8-bit RGB'
        elif kind == b'IDAT':
            idat += chunk
        i += 12 + n
    raw, bpp = zlib.decompress(idat), 3
    stride, rows, prev, p = w * bpp, [], bytearray(w * bpp), 0
    for _ in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line); prev = line
    return w, h, rows


def write_rgba_png(path, w, h, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    open(path, 'wb').write(png)


src, dst = sys.argv[1], sys.argv[2]
ink = bytes.fromhex(sys.argv[3] if len(sys.argv) > 3 else '6F554A')
w, h, rows = read_rgb_png(src)
lum = lambda r, g, b: 0.299 * r + 0.587 * g + 0.114 * b
bg = 205.0   # luminance of the flat mauve background (#DFCAD1)
dark = 60.0  # luminance treated as fully opaque line
out = []
for r in rows:
    line = bytearray()
    for x in range(w):
        l = lum(*r[x * 3:x * 3 + 3])
        a = max(0.0, min(1.0, (bg - 8 - l) / (bg - 8 - dark)))
        line += ink + bytes([int(a * 255)])
    out.append(line)
write_rgba_png(dst, w, h, out)
print(f'wrote {dst} ({w}x{h})')
