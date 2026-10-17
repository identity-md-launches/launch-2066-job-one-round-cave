#!/usr/bin/env python3
"""One-use build: consume generated RGBA pigment in wall-v20.png, add to wall 38.

No intermediate images are saved. The generated PNG is replaced by the complete
wall; a guard refuses use of an already assembled wall. The JPEG encoder already
in line 1 is used read-only at build time. All image processing here is offline.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib

from check_delivery_35 import png
from finish_wall_25 import encode


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rgba(raw):
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    at, parts = 8, []
    while at < len(raw):
        n = int.from_bytes(raw[at:at+4], 'big')
        kind, data = raw[at+4:at+8], raw[at+8:at+8+n]
        assert zlib.crc32(kind + data) & 0xffffffff == int.from_bytes(raw[at+8+n:at+12+n], 'big')
        if kind == b'IHDR':
            w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            assert (depth, color, compression, filtering, interlace) == (8, 6, 0, 0, 0)
        if kind == b'IDAT':
            parts.append(data)
        at += n + 12
    scan = zlib.decompress(b''.join(parts))
    stride = w * 4
    assert len(scan) == (stride + 1) * h
    pixels = bytearray(stride * h)
    for y in range(h):
        mode = scan[y * (stride + 1)]
        assert mode in range(5)
        for x in range(stride):
            i = y * stride + x
            a = pixels[i-4] if x >= 4 else 0
            b = pixels[i-stride] if y else 0
            c = pixels[i-stride-4] if y and x >= 4 else 0
            p = a + b - c
            pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
            predictor = (0, a, b, (a+b)//2,
                         a if pa <= pb and pa <= pc else b if pb <= pc else c)[mode]
            pixels[i] = (scan[y*(stride+1)+x+1] + predictor) & 255
    return w, h, pixels


def main():
    target = Path('artifacts/gathering/wall-v20.png')
    generated = target.read_bytes()
    gw, gh, pigment = rgba(generated)
    assert (gw, gh) == (2172, 724), 'requires the isolated RGBA generation'
    previous = Path('artifacts/gathering/wall-v19.png')
    dimensions, original = png(previous)
    width, height = dimensions
    result = bytearray(original)
    # Bare upper-right stone, clear of every inherited painting.
    x, y, w, h = 965, 65, 175, 55
    sx, sy, sw, sh = 40, 140, 2100, 440
    for row in range(h):
        for column in range(w):
            weights, colors = 0, [0, 0, 0]
            for dy in range(3):
                for dx in range(3):
                    px = int(sx + (column + (dx+.5)/3) * sw/w)
                    py = int(sy + (row + (dy+.5)/3) * sh/h)
                    r, g, b, a = pigment[(py*gw+px)*4:(py*gw+px)*4+4]
                    # Remove faint generator halo; retain worn pigment holes.
                    if a < 180:
                        continue
                    if r > 160 and g > 140 and b > 105 and r-b < 105:
                        color = (215, 197, 159)  # dirty chalk
                    elif r > g * 1.12 and r-b > 45:
                        color = (176, 76, 33) if g < r*.62 else (190, 133, 52)
                    else:
                        color = (48, 37, 25)  # charcoal twig
                    weight = a / 255 / 9
                    weights += weight
                    for c in range(3):
                        colors[c] += color[c] * weight
            if weights < .08:
                continue
            offset = ((y+row)*width + x+column)*3
            rock = original[offset:offset+3]
            grain = .72 + .28 * ((column*73 + row*37) % 29) / 28
            alpha = .78 * weights * grain
            result[offset:offset+3] = bytes(round(c*(1-alpha) + p/weights*alpha)
                for c, p in zip(rock, colors))
    encoded = encode(width, height, result)
    target.write_bytes(encoded)
    assert png(target)[1] == result
    canonical = Path('artifacts/gathering/wall.png')
    assert canonical.is_symlink()
    canonical.unlink()
    canonical.symlink_to('wall-v20.png')
    subprocess.run(['node', '-e', "const fs=require('node:fs'); const c=require('./line-1/media/finish-wall.cjs'); const p=c.thumbnail(c.decode(fs.readFileSync('artifacts/gathering/wall-v20.png'))); if(p.length>100000)throw Error('preview too large'); fs.writeFileSync('dist/gathering/39.jpg',p);"], check=True)
    changed = outside = 0
    for row in range(height):
        for column in range(width):
            i = (row*width+column)*3
            if original[i:i+3] != result[i:i+3]:
                changed += 1
                outside += not (x <= column < x+w and y <= row < y+h)
    assert changed > 500 and outside == 0
    report = dict(previous_sha256=sha(previous.read_bytes()), wall_sha256=sha(encoded),
        generated_mark_sha256=sha(generated), png_dimensions=dimensions,
        mark_rectangle=[x,y,w,h], source_crop=[sx,sy,sw,sh],
        changed_pixels=changed, pixels_changed_outside=outside,
        method='Imagegen RGBA pigment resampled and limited to earth pigments, then alpha-composited on bare stone; no intermediate image saved.')
    Path('gathering/preservation-39.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
