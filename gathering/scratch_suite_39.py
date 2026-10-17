#!/usr/bin/env python3
"""Run a read-only line suite, redirecting its temporary directories to scratch."""
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    target = (ROOT / sys.argv[1]).resolve()
    assert target.is_relative_to(ROOT) and target.name == 'selftest.py'
    scratch = ROOT / 'test/scratch/gathering39'
    scratch.mkdir(parents=True, exist_ok=True)
    original = tempfile.TemporaryDirectory
    def temporary(*args, **kwargs):
        kwargs['dir'] = scratch
        return original(*args, **kwargs)
    sys.path.insert(0, str(target.parent))
    sys.argv = [str(target)]
    with patch.object(tempfile, 'TemporaryDirectory', temporary):
        runpy.run_path(str(target), run_name='__main__')
