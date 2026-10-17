#!/usr/bin/env python3
"""Offline trial with the shipped historical public IMD API capture."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from zipquota import Rejected, process


def main():
    sample = Path(__file__).resolve().parents[1] / 'safezip' / 'imd-openapi.json'
    payload = sample.read_bytes()
    scratch = Path('test/scratch')
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='zipquota-demo-', dir=scratch) as folder:
        root = Path(folder)
        archive = root / 'input.zip'
        policy = root / 'policy.json'
        output = root / 'accepted'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as writer:
            writer.writestr('api/openapi.json', payload)
            writer.writestr('notes.txt', b'public API capture\n')
        rules = {'roots': [{'name': 'api', 'files': 1, 'bytes': len(payload), 'nodes': 2},
                           {'name': 'notes.txt', 'files': 1, 'bytes': 19, 'nodes': 1}]}
        policy.write_text(json.dumps(rules), encoding='utf-8')
        report = process(archive, policy, output)
        assert (output / 'api/openapi.json').read_bytes() == payload
        assert (output / 'notes.txt').read_bytes() == b'public API capture\n'
        print(json.dumps({'accepted': True, 'capture_bytes': len(payload),
                          'capture_sha256': hashlib.sha256(payload).hexdigest(),
                          'root_usage': report['root_usage']}, sort_keys=True))
        rules['roots'][0]['bytes'] -= 1
        policy.write_text(json.dumps(rules), encoding='utf-8')
        refused = root / 'refused'
        try:
            process(archive, policy, refused)
        except Rejected as error:
            assert not refused.exists()
            print(json.dumps({'refused': str(error), 'output_created': False}))
        else:
            raise AssertionError('one-byte-short root quota was accepted')


if __name__ == '__main__':
    main()
