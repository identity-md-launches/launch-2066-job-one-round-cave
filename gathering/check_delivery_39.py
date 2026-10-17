#!/usr/bin/env python3
"""Check wall bytes, preserved pixels, record coverage, line integrity and export size."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

from check_delivery_35 import Gallery, GROUPS, jpeg, png, sha

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text())


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def export_budget():
    # Artifact PNG outputs are uploaded separately. Do not leave an archive.
    tracked=set(git('ls-files','-z').decode().split('\0'))
    new=set(git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))
    files=sorted(n for n in tracked|new if n and not n.startswith(('artifacts/','test/'))
                 and (ROOT/n).is_file())
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w',format=tarfile.PAX_FORMAT) as archive:
        for name in files: archive.add(ROOT/name,arcname=name,recursive=False)
    gzip_size=len(gzip.compress(buffer.getvalue(),compresslevel=9,mtime=0))
    return dict(source_files=len(files),tar_gzip_bytes=gzip_size,
                limit=8388608,margin=8388608-gzip_size,
                scope='Local tar.gz trial of all tracked and nonignored new non-artifact source files; scratch excluded; no archive saved. Daemon packaging is external.')


def main():
    wall=ROOT/'artifacts/gathering/wall-v20.png'
    previous=ROOT/'artifacts/gathering/wall-v19.png'
    record=read('dist/gathering/39.json')
    assert set(record)=={'name','image','attributes'}
    attrs={a['trait_type']:a['value'] for a in record['attributes']}
    assert len(record['attributes'])==6 and set(attrs)=={'Cave','Wall','Number','Left behind','Meaning','One thing'}
    assert (attrs['Cave'],attrs['Wall'],attrs['Number'],attrs['One thing'])==('Lava','Gathering',39,'Gathering')
    assert type(attrs['Number']) is int
    assert record['image']=='https://api.imd.fun/artifacts/'+sha(wall.read_bytes())
    assert not git('ls-files','--','artifacts/gathering/wall-v20.png')
    assert (ROOT/'artifacts/gathering/wall.png').read_bytes()==wall.read_bytes()
    assert read('dist/gathering/38.json')['image'].endswith(sha(previous.read_bytes()))
    dimensions,pixels=png(wall); old_dimensions,old_pixels=png(previous)
    assert dimensions==old_dimensions==[1254,1254]
    preserve=read('gathering/preservation-39.json')
    assert preserve['wall_sha256']==sha(wall.read_bytes())
    assert preserve['previous_sha256']==sha(previous.read_bytes())
    x,y,w,h=preserve['mark_rectangle']; changed=outside=0
    for row in range(1254):
        for col in range(1254):
            at=(row*1254+col)*3
            if pixels[at:at+3]!=old_pixels[at:at+3]:
                changed+=1
                outside+=not(x<=col<x+w and y<=row<y+h)
    assert changed==preserve['changed_pixels']==4530 and outside==preserve['pixels_changed_outside']==0
    assert jpeg(ROOT/'dist/gathering/39.jpg')==[512,512]
    assert read('dist/goals.json')==[{'line':n,'goal':(ROOT/f'line-{n}/GOAL.md').read_text().strip()} for n in range(1,5)]
    parser=Gallery(); parser.feed((ROOT/'dist/index.html').read_text())
    assert parser.sections==GROUPS
    expected=[]; painted=placeholders=0
    for folder in GROUPS:
        for path in sorted((ROOT/'dist'/folder).glob('[0-9][0-9].json'),reverse=True):
            item=json.loads(path.read_text()); expected.append(folder+'/'+path.name)
            assert re.fullmatch(r'https://api\.imd\.fun/artifacts/[0-9a-f]{64}',item['image'])
            if item['name']=='Not painted yet':
                placeholders+=1; assert not path.with_suffix('.jpg').exists()
            else: painted+=1
        actual=[p for p in parser.records if p.startswith(folder+'/') and read('dist/'+p)['name']!='Not painted yet']
        assert actual==sorted(actual,reverse=True)
    assert sorted(parser.records)==sorted(expected)
    for name,item in read('shared/api_bundle/SOURCES.json').items():
        assert sha((ROOT/'shared/api_bundle'/name).read_bytes())==item['sha256']
        assert sha((ROOT/item['source']).read_bytes())==item['source_sha256']
    audit=read('gathering/audit-lines-39.json')
    assert len(audit['commands'])==138
    failures=[r for r in audit['commands'] if not r['passed']]
    assert len(failures)==1 and failures[0]['tool']=='safezip' and failures[0]['kind']=='check'
    assert sum(r['unittest_cases'] for r in audit['commands'])==916
    growth=read('gathering/safezip-growth-39.json')
    assert growth['mutation_hook_calls']==1 and not growth['output_created']
    assert 'while reading' in growth['real_growth_refusal']
    assert growth['absolute_scratch_suite']['exit']==0 and growth['absolute_scratch_suite']['tests']==44
    shared=read('gathering/shared-check-results-39.json')
    assert shared['passed'] and shared['tests']==113 and shared['demos']==9
    assert len(shared['in_place'])==len(shared['standalone'])==17
    review=read('gathering/review-39.json')
    assert review['wall_sha256']==sha(wall.read_bytes()) and review['visual_requirements_unmet']==[]
    assert (ROOT/'gathering/COINS.md').read_text().startswith('none\n')
    integrity=read('gathering/line-integrity-39.json')
    files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for n in range(1,5)
           for p in sorted((ROOT/f'line-{n}').rglob('*')) if p.is_file()}
    assert len(files)==integrity['files'] and sha(json.dumps(files,sort_keys=True).encode())==integrity['before']==integrity['after']
    compression=read('gathering/preview-compression-39.json')
    for item in compression['previews']:
        path=ROOT/item['path']
        assert sha(path.read_bytes())==item['after_sha256'] and path.stat().st_size==item['after_bytes']
        assert sha((ROOT/item['source']).read_bytes())==item['source_sha256']
        assert jpeg(path)==[512,512]
    paths=set((git('diff','--name-only','-z','HEAD')+git('ls-files','--others','--exclude-standard','-z')).decode().split('\0'))-{''}
    for name in paths:
        assert name.startswith(('gathering/','shared/','dist/','artifacts/gathering/','test/scratch/')),name
        assert not name.startswith(('dist/line-1/','dist/line-2/','dist/line-3/','dist/line-4/')),name
        path=ROOT/name
        if path.is_file() and not name.startswith(('artifacts/','test/scratch/')):
            assert path.stat().st_size<=100000,name
    budget=export_budget()
    assert budget['margin']>0,budget
    result=dict(passed=True,png_dimensions=dimensions,png_format='RGB PNG',png_bytes=wall.stat().st_size,
        jpeg_dimensions=[512,512],jpeg_format='JPEG',jpeg_bytes=(ROOT/'dist/gathering/39.jpg').stat().st_size,
        records=len(expected),painted=painted,placeholders=placeholders,
        changed_pixels=changed,pixels_changed_outside=outside,line_files_unchanged=len(files),
        line_commands=138,line_tests=916,inherited_fixture_failures=1,
        shared_tests_each=113,shared_demos_each=9,previews_reencoded=len(compression['previews']),
        preview_bytes_saved=compression['saved_bytes'],export=budget,unmet_visual_requirements=[])
    (ROOT/'gathering/delivery-check-39.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
