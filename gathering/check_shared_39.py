#!/usr/bin/env python3
"""Check all shared suites/demos in place and from a source-only isolated copy."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'shared/api_bundle'
SUITES = ['selftest.py','parameter_selftest.py','status_selftest.py',
          'fallback_selftest.py','dispatch_selftest.py','map_selftest.py',
          'key_selftest.py','tuple_selftest.py']
DEMOS = ['demo.py','parameter_demo.py','server_demo.py','status_demo.py',
         'fallback_demo.py','dispatch_demo.py','map_demo.py','key_demo.py','tuple_demo.py']


def run(cwd):
    rows=[]
    for script in SUITES+DEMOS:
        result=subprocess.run(['python3','-B','shared/api_bundle/'+script],cwd=cwd,
            capture_output=True,text=True,timeout=90)
        match=re.search(r'Ran (\d+) tests?', result.stderr)
        if script in DEMOS and result.returncode==0: json.loads(result.stdout)
        rows.append(dict(script=script,exit=result.returncode,tests=int(match[1]) if match else 0,
                         output_sha256=hashlib.sha256((result.stdout+result.stderr).encode()).hexdigest(),
                         evidence=(result.stdout+result.stderr)[-180:] if result.returncode else 'passed'))
    return rows


def main():
    manifest=json.loads((FOLDER/'SOURCES.json').read_text())
    for target, item in manifest.items():
        assert hashlib.sha256((FOLDER/target).read_bytes()).hexdigest()==item['sha256']
        assert hashlib.sha256((ROOT/item['source']).read_bytes()).hexdigest()==item['source_sha256']
    in_place=run(ROOT)
    scratch=ROOT/'test/scratch'
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='shared39-',dir=scratch) as tmp:
        isolated=Path(tmp)
        shutil.copytree(FOLDER,isolated/'shared/api_bundle',ignore=shutil.ignore_patterns('__pycache__'))
        standalone=run(isolated)
    result=dict(round=39,vendor_sources=len(manifest),in_place=in_place,standalone=standalone,
        tests=sum(r['tests'] for r in in_place),demos=len(DEMOS),
        passed=all(r['exit']==0 for r in in_place+standalone))
    (ROOT/'gathering/shared-check-results-39.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return int(not result['passed'])


if __name__=='__main__':
    raise SystemExit(main())
