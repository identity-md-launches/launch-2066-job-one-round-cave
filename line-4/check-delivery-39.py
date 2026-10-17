#!/usr/bin/env python3
"""Read-only checks of round 38's local delivery bytes and allowed paths."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def png(raw):
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    p = 8
    while p < len(raw):
        n = int.from_bytes(raw[p:p+4], 'big')
        kind, data = raw[p+4:p+8], raw[p+8:p+8+n]
        assert zlib.crc32(kind+data) == int.from_bytes(raw[p+8+n:p+12+n], 'big')
        if kind == b'IHDR':
            width, height, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', data)
            assert depth == 8 and color == 2 and interlace == 0
        p += n+12
        if kind == b'IEND':
            break
    assert p == len(raw)
    return [width, height]


def jpeg(raw):
    assert raw[:2] == b'\xff\xd8' and raw[-2:] == b'\xff\xd9'
    p = 2
    while p < len(raw):
        assert raw[p] == 255
        marker = raw[p+1]
        size = int.from_bytes(raw[p+2:p+4], 'big')
        if marker == 0xc0:
            height, width = struct.unpack('>HH', raw[p+5:p+9])
            return [width, height]
        p += 2+size
    raise AssertionError('missing JPEG SOF')


def main():
    records = sorted(Path('dist/line-4').glob('[0-9][0-9].json'))
    assert len(records) == 39
    assert [p.stem for p in records] == [f'{n:02}' for n in range(1, 40)]
    record = json.loads(records[-1].read_text())
    assert set(record) == {'name', 'image', 'attributes'}
    attributes = {a['trait_type']: a['value'] for a in record['attributes']}
    assert len(attributes) == 6
    assert attributes['Cave'] == 'Lava' and attributes['Wall'] == 'Line 4'
    assert attributes['Number'] == 39 and type(attributes['Number']) is int
    assert attributes['Left behind'] == 'TupleCheck'
    wall = Path('artifacts/line-4/wall-v20.png').read_bytes()
    assert Path('artifacts/line-4/wall.png').read_bytes() == wall
    assert record['image'] == 'https://api.imd.fun/artifacts/'+sha(wall)
    assert png(wall) == [1254, 1254]
    preview = Path('dist/line-4/39.jpg').read_bytes()
    assert jpeg(preview) == [512, 512] and len(preview) <= 100000
    assert Path('artifacts/line-4/39.jpg').read_bytes() == preview
    goal = subprocess.check_output(['git', 'show', 'HEAD:line-4/GOAL.md'])
    assert Path('line-4/GOAL.md').read_bytes() == goal
    changed = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
    for path in changed+untracked:
        assert path.startswith(('line-4/', 'artifacts/line-4/', 'dist/line-4/', 'test/scratch/')), path
        if not path.startswith(('artifacts/', 'test/scratch/')):
            assert Path(path).stat().st_size <= 100000, path
    assert not any(p.startswith('dist/line-4/') for p in changed), 'older records changed'
    assert not any(p.startswith('line-4/tools/') for p in changed), 'older tool changed'
    review = json.loads(Path('line-4/review-39.json').read_text())
    assert review['sha256'] == sha(wall) and review['pixels_changed_outside_addition'] == 0
    assert not review['visual_review'].startswith('Pending')
    ancestor = Path('artifacts/line-4/wall-v19.png').read_bytes()
    older = json.loads(Path('dist/line-4/38.json').read_text())
    assert older['image'] == 'https://api.imd.fun/artifacts/'+sha(ancestor)
    assert review['ancestor_sha256'] == sha(ancestor)
    def pixels(raw):
        blocks, pos = [], 8
        while pos < len(raw):
            size = int.from_bytes(raw[pos:pos+4], 'big')
            if raw[pos+4:pos+8] == b'IDAT':
                blocks.append(raw[pos+8:pos+8+size])
            pos += size+12
        w, h = png(raw)
        stride = w*3
        data = zlib.decompress(b''.join(blocks))
        assert len(data) == (stride+1)*h
        result = bytearray(stride*h)
        for y in range(h):
            f = data[y*(stride+1)]
            assert f in range(5)
            for x in range(stride):
                i = y*stride+x
                a = result[i-3] if x >= 3 else 0
                b = result[i-stride] if y else 0
                c = result[i-stride-3] if y and x >= 3 else 0
                p = a+b-c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                predictor = (0, a, b, (a+b)//2,
                    a if pa <= pb and pa <= pc else b if pb <= pc else c)[f]
                result[i] = (data[y*(stride+1)+x+1]+predictor) & 255
        return result
    a, b = pixels(ancestor), pixels(wall)
    x0, y0, width, height = review['addition_bounds']
    changed_pixels = 0
    for y in range(1254):
        for x in range(1254):
            i = (y*1254+x)*3
            if a[i:i+3] != b[i:i+3]:
                changed_pixels += 1
                assert x0 <= x < x0+width and y0 <= y < y0+height
    assert changed_pixels == review['changed_pixels'] > 0
    checks = json.loads(Path('line-4/check-results-39.json').read_text())
    assert all(s['exit'] == 0 for s in checks['suites'])
    result = dict(status='passed', records=39, new_record='39', goal_bytes_unchanged=True, changed_pixels=changed_pixels, pixels_changed_outside_addition=0,
                  earlier_records_and_tools_unchanged=True, allowed_paths_only=True,
                  wall_dimensions=png(wall), wall_format='RGB PNG', wall_sha256=sha(wall),
                  preview_dimensions=jpeg(preview), preview_format='JPEG', preview_bytes=len(preview),
                  regression_tests=sum(s['tests'] for s in checks['suites']), suites=len(checks['suites']),
                  named_output_untracked='artifacts/line-4/wall-v20.png' not in subprocess.check_output(
                      ['git', 'ls-files'], text=True).splitlines())
    assert result['named_output_untracked']
    Path('line-4/delivery-check-39.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
