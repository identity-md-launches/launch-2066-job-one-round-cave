#!/usr/bin/env python3
"""Behavioral checks; all fixtures are address-free and offline."""
import contextlib
import copy
import io
from pathlib import Path
import random
import tempfile
import unittest
import rewardgroup as rg


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.metadata = rg.rs.read_json(rg.rr.ROOT / 'zto-mainnet.json')
        self.request = rg.rs.read_json(rg.rr.ROOT / 'example.json')
        self.policy = {'groups': [{'id': 'delivery', 'members': ['review', 'build']},
                                  {'id': 'discovery', 'members': ['research']}]}

    def summary(self, request=None, policy=None):
        request = request or self.request
        return rg.summarize(request, rg.rs.allocate(request, self.metadata), self.metadata,
                            policy or self.policy)

    def test_exact_one_zto(self):
        result = self.summary()
        self.assertEqual([g['units'] for g in result['groups']],
                         ['666666666666666667', '333333333333333333'])
        self.assertEqual(result['grouped_units'], '1000000000000000000')
        self.assertEqual(result['groups'][0]['contributors_without_address'], 2)

    def test_does_not_reallocate_group_weights(self):
        request = copy.deepcopy(self.request)
        request['budget'] = '0.000000000000000001'
        policy = {'groups': [{'id': 'single', 'members': ['build']},
                             {'id': 'pair', 'members': ['research', 'review']}]}
        groups = self.summary(request, policy)['groups']
        self.assertEqual([(g['id'], g['units']) for g in groups], [('pair', '0'), ('single', '1')])
        # Reallocating group weights would give the pair the only unit, which is wrong here.
        pooled = {'budget': request['budget'], 'contributors': [
            {'id': 'single', 'weight': '1'}, {'id': 'pair', 'weight': '2'}]}
        self.assertEqual(rg.rs.allocate(pooled, self.metadata)['allocations'][0]['units'], '1')

    def test_zero_weight_must_be_present(self):
        request = copy.deepcopy(self.request)
        request['contributors'][0]['weight'] = '0'
        policy = {'groups': [{'id': 'all', 'members': ['research', 'review']}]}
        with self.assertRaises(rg.rs.Invalid): self.summary(request, policy)

    def test_invalid_partitions(self):
        policies = [None, {}, {'groups': []}, {'groups': [None]},
                    {'groups': [{'id': 'a', 'members': []}]},
                    {'groups': [{'id': 'a', 'members': ['unknown']}]},
                    {'groups': [{'id': 'a', 'members': ['build', 'build', 'review']}]},
                    {'groups': [{'id': 'a', 'members': [['build']]}]},
                    {'groups': [{'id': 'bad id', 'members': ['build']}]},
                    {'groups': [{'id': 'a', 'members': ['build'], 'address': 'forbidden'}]},
                    {'groups': [{'id': 'a', 'members': ['build']},
                                {'id': 'a', 'members': ['research', 'review']}]},
                    {'groups': [{'id': 'a', 'members': ['build', 'review']},
                                {'id': 'b', 'members': ['build', 'research']}]}]
        for policy in policies:
            with self.subTest(policy=policy), self.assertRaises(rg.rs.Invalid):
                rg.partition(policy, {'build', 'research', 'review'})

    def test_policy_order_and_hash_binding(self):
        policy = copy.deepcopy(self.policy)
        policy['groups'].reverse()
        policy['groups'][1]['members'].reverse()
        a, b = self.summary(), self.summary(policy=policy)
        self.assertEqual(a['groups'], b['groups'])
        self.assertNotEqual(a['policy_sha256'], b['policy_sha256'])

    def test_full_source_verification(self):
        report = rg.rs.allocate(self.request, self.metadata)
        for field, value in [('units', '2'), ('amount', '0'), ('rounding_unit_awarded', 1)]:
            changed = copy.deepcopy(report)
            changed['allocations'][0][field] = value
            with self.assertRaises(rg.rs.Invalid):
                rg.summarize(self.request, changed, self.metadata, self.policy)
        changed = copy.deepcopy(report)
        changed['paid'] = True
        with self.assertRaises(rg.rs.Invalid):
            rg.summarize(self.request, changed, self.metadata, self.policy)

    def test_summary_tampering(self):
        report = rg.rs.allocate(self.request, self.metadata)
        summary = self.summary()
        self.assertEqual(rg.verify(self.request, report, self.metadata, self.policy, summary)['result'],
                         'verified complete group totals')
        for change in ('units', 'membership', 'scope', 'type'):
            altered = copy.deepcopy(summary)
            if change == 'units': altered['groups'][0]['units'] = '0'
            elif change == 'membership': altered['groups'][0]['members'].pop()
            elif change == 'scope': altered['scope'] = 'payment authorized'
            else: altered['contributors'] = 3.0
            with self.assertRaises(rg.rs.Invalid):
                rg.verify(self.request, report, self.metadata, self.policy, altered)

    def test_uint256_and_fractional_weights(self):
        request = copy.deepcopy(self.request)
        request['budget'] = rg.rs.display_units(rg.rs.UINT256_MAX, 18)
        request['contributors'][0]['weight'] = '0.000000000000000001'
        result = self.summary(request)
        self.assertEqual(sum(int(g['units']) for g in result['groups']), rg.rs.UINT256_MAX)

    def test_seeded_partitions_and_coarsening(self):
        rng = random.Random(737)
        for _ in range(200):
            n = rng.randint(1, 30)
            rows = [{'id': 'worker%02d' % i, 'weight': str(rng.randint(0, 50))} for i in range(n)]
            rows[0]['weight'] = '1'
            request = {'budget': rg.rs.display_units(rng.randint(1, 10**22), 18), 'contributors': rows}
            buckets = {}
            for row in rows: buckets.setdefault('group%d' % rng.randrange(5), []).append(row['id'])
            policy = {'groups': [{'id': k, 'members': v} for k, v in buckets.items()]}
            result = self.summary(request, policy)
            report = rg.rs.allocate(request, self.metadata)
            direct = {row['id']: int(row['units']) for row in report['allocations']}
            for group in result['groups']:
                self.assertEqual(int(group['units']), sum(direct[m] for m in group['members']))
            coarse = self.summary(request, {'groups': [{'id': 'all', 'members': list(direct)}]})
            self.assertEqual(int(coarse['groups'][0]['units']), sum(int(g['units']) for g in result['groups']))

    def test_cli_round_trip_and_overwrite_refusal(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as name:
            root = Path(name)
            for filename, data in [('request', self.request), ('report', rg.rs.allocate(self.request, self.metadata)),
                                   ('policy', self.policy)]:
                rg.rs.write_json(data, root / filename)
            args = ['--request', str(root/'request'), '--report', str(root/'report'),
                    '--policy', str(root/'policy')]
            out = root/'summary'
            self.assertEqual(rg.main(['summarize', *args, '--output', str(out)]), 0)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rg.main(['verify', *args, '--summary', str(out)]), 0)
            before = out.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(rg.main(['summarize', *args, '--output', str(out)]), 2)
            self.assertEqual(out.read_bytes(), before)

    def test_duplicate_json_and_input_bounds(self):
        with self.assertRaises(rg.rs.Invalid): rg.rs.parse_json('{"groups":[],"groups":[]}')
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as name:
            path = Path(name)/'large'
            path.write_bytes(b' ' * (rg.rs.MAX_BYTES + 1))
            with self.assertRaises(rg.rs.Invalid): rg.rs.read_json(path)


if __name__ == '__main__':
    unittest.main()
