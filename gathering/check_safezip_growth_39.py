#!/usr/bin/env python3
"""Reproduce the inherited growth-test path mismatch, then test the real bound."""
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'line-2/tools/safezip'))
import safezip


def main():
    scratch=ROOT/'test/scratch'
    with tempfile.TemporaryDirectory(prefix='growth39-',dir=scratch) as name:
        folder=Path(name)
        source=folder/'input.zip'
        with zipfile.ZipFile(source,'w') as writer: writer.writestr('ok',b'x')
        size=source.stat().st_size
        original=Path.open
        hook_calls=[]
        def grow(path,*args,**kwargs):
            if path==source and args==('rb',):
                hook_calls.append(str(path.relative_to(ROOT)))
                with original(path,'ab') as writer: writer.write(b'X'*1024)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',grow):
            try:
                safezip.process(source,folder/'out',archive_bytes=size)
            except safezip.Rejected as error:
                refusal=str(error)
            else: raise AssertionError('actual snapshot growth accepted')
        assert len(hook_calls)==1 and 'while reading' in refusal
        assert not (folder/'out').exists()
    result=dict(inherited_test='test_actual_input_size_checked_after_stat',
        inherited_failure='Relative fixture path compared with absolute local_path result: mutation hook never fires.',
        real_growth_refusal=refusal,mutation_hook_calls=1,output_created=False,
        line_source_modified=False)
    checked=subprocess.run([sys.executable,'-B','gathering/scratch_suite_39.py',
        'line-2/tools/safezip/selftest.py'],cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert checked.returncode==0 and 'Ran 44 tests' in checked.stderr, checked.stderr
    result['absolute_scratch_suite']={'exit':checked.returncode,'tests':44,
        'output_sha256':hashlib.sha256((checked.stdout+checked.stderr).encode()).hexdigest()}
    (ROOT/'gathering/safezip-growth-39.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
