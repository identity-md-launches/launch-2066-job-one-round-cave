#!/usr/bin/env python3
"""Cross-line tuple checks after digest, ZIP layout and complete CRC validation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import api_bundle as bundle
from key_demo import insert_gap
from tuple_demo import archive, documents


class TupleBundleTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='tuple-tests-', dir=scratch)
        self.root = Path(self.temp.name)
        _, self.old, self.new = documents()

    def tearDown(self):
        self.temp.cleanup()

    def pair(self, old=None, new=None):
        a, b = self.root/'old.zip', self.root/'new.zip'
        ah = archive(a, self.old if old is None else old)
        bh = archive(b, self.new if new is None else new)
        return a, b, dict(member='docs/openapi.json', old_sha256=ah, new_sha256=bh,
                         strict_layout=True)

    def test_reference_and_retained_findings(self):
        a, b, opts = self.pair()
        before = bundle.compare(a, b, keys=True, **opts)
        result = bundle.compare(a, b, tuples=True, **opts)
        self.assertEqual(before['status'], 'review_required')
        self.assertEqual(result['status'], 'breaking')
        self.assertEqual(len(result['tuple_pairs']), 3)
        self.assertTrue(all(f in result['findings'] for f in before['findings']))
        self.assertTrue(any('/prefixItems/1/enum' in f['location'] for f in result['findings']))
        for side in result['bundle_inputs'].values():
            self.assertTrue(side['strict_layout_checked'])
            self.assertTrue(side['approved_sha256_checked'])
            self.assertTrue(side['all_payloads_crc_checked'])
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['new.zip', 'old.zip'])

    def test_unchanged_real_capture(self):
        capture = json.loads(Path(__file__).with_name('imd-openapi.json').read_bytes())
        a, b, opts = self.pair(capture, capture)
        result = bundle.compare(a, b, tuples=True, **opts)
        self.assertEqual(result['status'], 'no_detected_breakage')
        self.assertEqual(result['operations_compared'], 5)
        self.assertEqual(result['tuple_pairs'], [])

    def test_request_direction_and_dialect(self):
        old, new = copy.deepcopy(self.new), copy.deepcopy(self.old)
        for doc in (old, new):
            op = doc['paths']['/requests/quote']['post']
            op['requestBody'] = op['responses']['200']
            op['responses'] = {}
            doc['paths'] = {'/requests/quote': {'post': op}}
        a, b, opts = self.pair(old, new)
        result = bundle.compare(a, b, tuples=True, **opts)
        self.assertEqual(result['status'], 'breaking')
        self.assertEqual(result['tuple_pairs'][0]['direction'], 'request')
        for doc in (old, new):
            doc['openapi'] = '3.0.3'
        a, b, opts = self.pair(old, new)
        result = bundle.compare(a, b, tuples=True, **opts)
        self.assertIn('tuple_dialect_unchecked', {f['code'] for f in result['findings']})
        self.assertEqual(result['tuple_pairs'], [])

    def test_prefix_to_tail(self):
        new = copy.deepcopy(self.new)
        schema = new['paths']['/requests/quote']['post']['responses']['200']['content']['application/json']['schema']
        schema['prefixItems'].pop()
        schema['items'] = {'type': 'string', 'enum': ['pending', 'done', 'retry']}
        a, b, opts = self.pair(new=new)
        result = bundle.compare(a, b, tuples=True, **opts)
        self.assertEqual(result['status'], 'breaking')
        self.assertEqual(result['tuple_pairs'][1]['new_source'], 'items')

    def test_digest_refusal_precedes_layout(self):
        a, b, opts = self.pair()
        with patch.object(bundle.zipseal, 'layout') as layout:
            with self.assertRaisesRegex(ValueError, 'approved digest'):
                bundle.compare(a, b, tuples=True, **{**opts, 'old_sha256': '0'*64})
            layout.assert_not_called()

    def test_gap_and_crc_precede_analyzer(self):
        a, b, opts = self.pair()
        for payload, exception in ((insert_gap(b.read_bytes()), ValueError),
                (b.read_bytes().replace(b'inert payload', b'INERT PAYLOAD'), zipfile.BadZipFile)):
            b.write_bytes(payload)
            with patch.object(bundle.tuplecheck, 'compare') as analyzer:
                with self.assertRaises(exception):
                    bundle.compare(a, b, tuples=True, **{**opts, 'new_sha256': None})
                analyzer.assert_not_called()

    def test_remote_refs_and_pair_limit_refuse(self):
        old = copy.deepcopy(self.old)
        old['components']['schemas']['OrderedState'] = {'$ref': 'https://example.invalid/remote'}
        a, b, opts = self.pair(old, old)
        with self.assertRaises(ValueError):
            bundle.compare(a, b, tuples=True, **opts)
        a, b, opts = self.pair()
        with patch.object(bundle.tuplecheck, 'MAX_TUPLE_PAIRS', 0):
            with self.assertRaisesRegex(ValueError, 'tuple pair limit'):
                bundle.compare(a, b, tuples=True, **opts)

    def test_cancel_and_option_types(self):
        a, b, opts = self.pair()
        with patch.object(bundle.tuplecheck, 'compare') as analyzer:
            with self.assertRaisesRegex(ValueError, 'cancelled'):
                bundle.compare(a, b, tuples=True, cancelled=lambda: True, **opts)
            analyzer.assert_not_called()
        for value in (1, None, 'true'):
            with self.assertRaisesRegex(ValueError, 'booleans'):
                bundle.compare(a, b, tuples=value, **opts)

    def test_cli_exits_precedence_and_determinism(self):
        review = copy.deepcopy(self.old)
        review['components']['schemas']['OrderedState']['pattern'] = '^p'
        for doc, code in ((self.old, 0), (self.new, 1), ({}, 2), (review, 3)):
            a, b, opts = self.pair(self.old, doc)
            args = [sys.executable, '-B', bundle.__file__, str(a), str(b), '--tuples',
                    '--keys', '--maps', '--strict-layout', '--member', opts['member'],
                    '--old-sha256', opts['old_sha256'], '--new-sha256', opts['new_sha256']]
            done = subprocess.run(args, capture_output=True, text=True, timeout=20)
            self.assertEqual(done.returncode, code, done.stdout+done.stderr)
            if code != 2:
                self.assertTrue(json.loads(done.stdout)['extension'].startswith('tuplecheck-v1'))
        a, b, opts = self.pair()
        self.assertEqual(bundle.compare(a,b,tuples=True,**opts), bundle.compare(a,b,tuples=True,**opts))


if __name__ == '__main__':
    unittest.main(verbosity=2)
