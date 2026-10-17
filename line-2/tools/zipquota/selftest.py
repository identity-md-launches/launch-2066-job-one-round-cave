#!/usr/bin/env python3
"""Focused quota, refusal and publication checks."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import zipquota


class ZipQuotaTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='zipquota-test-', dir=scratch)
        self.old_cwd = Path.cwd()
        os.chdir(self.temp.name)
        self.archive = Path('archive.zip')
        self.policy = Path('policy.json')
        self.output = Path('out')
        self.files = {'api/a.json': b'abc', 'api/sub/b.json': b'12345',
                      'notes.txt': b'note'}
        self.make_archive()
        self.rules = {'roots': [
            {'name': 'api', 'files': 2, 'bytes': 8, 'nodes': 4},
            {'name': 'notes.txt', 'files': 1, 'bytes': 4, 'nodes': 1}]}
        self.save_policy()

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def make_archive(self):
        with zipfile.ZipFile(self.archive, 'w', compression=zipfile.ZIP_DEFLATED) as writer:
            for name, payload in self.files.items():
                writer.writestr(name, payload)

    def save_policy(self):
        self.policy.write_text(json.dumps(self.rules), encoding='utf-8')

    def refuse(self, phrase):
        with self.assertRaisesRegex(zipquota.Rejected, phrase):
            zipquota.process(self.archive, self.policy, self.output)
        self.assertFalse(self.output.exists())

    def test_extract_and_exact_usage(self):
        report = zipquota.process(self.archive, self.policy, self.output)
        self.assertEqual(report['root_usage'], [
            {'name': 'api', 'files': 2, 'bytes': 8, 'nodes': 4},
            {'name': 'notes.txt', 'files': 1, 'bytes': 4, 'nodes': 1}])
        for name, content in self.files.items():
            self.assertEqual((self.output / name).read_bytes(), content)

    def test_inspect_only(self):
        report = zipquota.process(self.archive, self.policy)
        self.assertEqual(report['mode'], 'inspect')
        self.assertFalse(self.output.exists())

    def test_byte_limit(self):
        self.rules['roots'][0]['bytes'] = 7
        self.save_policy()
        self.refuse('byte quota')

    def test_file_limit(self):
        self.rules['roots'][0]['files'] = 1
        self.save_policy()
        self.refuse('file quota')

    def test_implicit_node_limit(self):
        self.rules['roots'][0]['nodes'] = 3
        self.save_policy()
        self.refuse('node quota')

    def test_unapproved_root(self):
        self.rules['roots'].pop()
        self.save_policy()
        self.refuse('outside approved roots')

    def test_case_colliding_root_policy(self):
        self.rules['roots'].append({'name': 'API', 'files': 1, 'bytes': 1, 'nodes': 1})
        self.save_policy()
        self.refuse('case-colliding root')

    def test_duplicate_json_key(self):
        self.policy.write_text('{"roots":[],"roots":[]}', encoding='utf-8')
        self.refuse('duplicate JSON key')

    def test_unsafe_root(self):
        self.rules['roots'][0]['name'] = '..'
        self.save_policy()
        self.refuse('unsafe root name')

    def test_policy_size_bound(self):
        with self.assertRaisesRegex(zipquota.Rejected, 'policy byte limit'):
            zipquota.process(self.archive, self.policy, self.output, policy_bytes=5)
        self.assertFalse(self.output.exists())

    def test_digest_approval(self):
        with self.assertRaisesRegex(zipquota.Rejected, 'approved digest'):
            zipquota.process(self.archive, self.policy, self.output,
                             expected_sha256='0' * 64)
        self.assertFalse(self.output.exists())

    def test_replaced_archive_between_passes(self):
        real = zipquota.sealed_process
        calls = 0

        def replacement(*args, **kwargs):
            nonlocal calls
            calls += 1
            result = real(*args, **kwargs)
            if calls == 1:
                self.archive.write_bytes(self.archive.read_bytes() + b'junk')
            return result

        with patch.object(zipquota, 'sealed_process', side_effect=replacement):
            self.refuse('approved digest')

    def test_strict_layout_gap(self):
        data = self.archive.read_bytes()
        end = data.rfind(b'PK\x05\x06')
        cd_start = int.from_bytes(data[end + 16:end + 20], 'little')
        data = bytearray(data[:cd_start] + b'gap' + data[cd_start:])
        new_end = end + 3
        data[new_end + 16:new_end + 20] = (cd_start + 3).to_bytes(4, 'little')
        self.archive.write_bytes(data)
        self.refuse('unclaimed bytes after local payload')

    def test_existing_output_preserved(self):
        self.output.mkdir()
        marker = self.output / 'marker'
        marker.write_text('keep', encoding='utf-8')
        with self.assertRaisesRegex(zipquota.Rejected, 'output exists'):
            zipquota.process(self.archive, self.policy, self.output)
        self.assertEqual(marker.read_text(encoding='utf-8'), 'keep')

    def test_cancelled_before_output(self):
        with self.assertRaisesRegex(zipquota.Rejected, 'cancelled'):
            zipquota.process(self.archive, self.policy, self.output, cancelled=lambda: True)
        self.assertFalse(self.output.exists())

    def test_bad_deadline(self):
        with self.assertRaisesRegex(zipquota.Rejected, 'seconds'):
            zipquota.process(self.archive, self.policy, self.output, seconds=float('inf'))
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
