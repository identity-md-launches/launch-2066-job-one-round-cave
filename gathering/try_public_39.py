#!/usr/bin/env python3
"""Read only the public description and compare approved snapshots, without extraction."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'shared/api_bundle'))
import api_bundle

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('unexpected redirect')


def main():
    url='https://api.imd.fun/openapi.json'
    ua='Pepeolithic-Gathering39/1.0'
    opener=build_opener(ProxyHandler({}),NoRedirect())
    with opener.open(Request(url,headers={'User-Agent':ua,'Accept':'application/json'}),timeout=25) as response:
        raw=response.read(100001)
        status=response.status
    assert len(raw)<=100000
    json.loads(raw)
    scratch=ROOT/'test/scratch'
    with tempfile.TemporaryDirectory(prefix='public39-',dir=scratch) as name:
        paths=[]; hashes=[]
        for n,payload in enumerate(((ROOT/'shared/api_bundle/imd-openapi.json').read_bytes(),raw)):
            path=Path(name)/f'{n}.zip'
            with zipfile.ZipFile(path,'w') as writer: writer.writestr(zipfile.ZipInfo('openapi.json'),payload)
            paths.append(path); hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        report=api_bundle.compare(*paths,old_sha256=hashes[0],new_sha256=hashes[1],tuples=True,strict_layout=True,seconds=10)
    evidence=dict(method='GET',source=url,user_agent=ua,http_status=status,
        bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
        status=report['status'],operations=report['operations_compared'],
        tuple_pairs=len(report['tuple_pairs']),findings=report['findings'],
        inputs=report['bundle_inputs'],described_operations_invoked=False)
    (ROOT/'gathering/public-trial-39.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__': main()
