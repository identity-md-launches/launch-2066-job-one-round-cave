#!/usr/bin/env python3
"""Offline handoff, exact-byte, mutation and CLI checks for Planseal."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
import planseal as p


class Tests(unittest.TestCase):
    def setUp(self):
        self.b = p.example()

    def verify(self, b=None, workers=2, budget=6):
        b = self.b if b is None else b
        return p.verify(b, p.digest(b), workers, budget)

    def test_demo_and_external_authority(self):
        self.assertTrue(self.verify()['valid'])
        self.assertFalse(self.verify(budget=5)['valid'])
        self.assertFalse(self.verify(workers=1)['valid'])

    def test_digest_first(self):
        before = p.digest(self.b)
        self.b['tasks'] = {'not_tasks': 'malformed'}
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            p.verify(self.b, before, 2, 6)

    def test_recomputed_digest_does_not_approve_bad_plan(self):
        self.b['plan']['schedule'][1].update(start=1, finish=2)
        report = self.verify()
        self.assertFalse(report['valid'])
        self.assertTrue(report['schedule']['violations'])
        self.assertEqual(report['gates']['milestones'], [])
        self.assertEqual(report['resources']['resources'], [])

    def test_gate_violation(self):
        self.b['gates']['gates'][0]['due'] = Decimal('2.99')
        self.assertFalse(self.verify()['gates']['valid'])

    def test_resource_violation(self):
        self.b['limits']['demands']['review'] = {'gpu': 1}
        self.assertFalse(self.verify()['resources']['valid'])

    def test_refuse_pack_invalid(self):
        self.b['budget'] = 5
        with self.assertRaisesRegex(ValueError, 'refusing'):
            p.pack(*(self.b[k] for k in ('tasks', 'plan', 'gates', 'limits', 'workers', 'budget')))

    def test_exact_decimal_roundtrip(self):
        for number in (Decimal('0.1'), Decimal('1e-100'), Decimal('9' * 100), Decimal('1e100')):
            b = copy.deepcopy(self.b)
            b['tasks'] = {'tasks': [{'id': 'a', 'minutes': number}]}
            b['plan'] = {'workers': 1, 'finish': number, 'schedule': [
                {'task': 'a', 'worker': 1, 'start': 0, 'finish': number}]}
            b['gates'] = {'gates': [{'id': 'g', 'tasks': ['a'], 'due': number}]}
            b['limits'] = {'capacities': {'cpu': 1}, 'demands': {'a': {'cpu': 1}}}
            b.update(workers=1, budget=number)
            raw = p.encode(b)
            decoded = json.loads(raw, parse_float=Decimal)
            self.assertEqual(p.encode(decoded), raw)
            self.assertTrue(p.verify(decoded, p.digest(b), 1, number)['valid'])

    def test_object_order_and_array_order(self):
        reordered = dict(reversed(list(self.b.items())))
        self.assertEqual(p.digest(self.b), p.digest(reordered))
        reordered = copy.deepcopy(self.b)
        reordered['plan']['schedule'].reverse()
        self.assertNotEqual(p.digest(self.b), p.digest(reordered))
        self.assertTrue(self.verify(reordered)['valid'])

    def test_mutable_snapshot(self):
        packed = p.pack(*(self.b[k] for k in ('tasks', 'plan', 'gates', 'limits', 'workers', 'budget')))
        self.b['plan']['finish'] = 99
        self.assertEqual(packed['plan']['finish'], 6)

    def test_schema_refusals(self):
        for key, value in (('schema', 'planseal/2'), ('budget', None), ('budget', True),
                           ('budget', -1), ('workers', True), ('workers', 65)):
            b = copy.deepcopy(self.b)
            b[key] = value
            with self.assertRaises(ValueError):
                p.validate(b)
        self.b['plan']['validation'] = {'valid': True}
        with self.assertRaises(ValueError):
            p.validate(self.b)

    def test_encoding_and_hash_contract(self):
        raw = p.encode({'z': [Decimal('0.10'), 'é'], 'a': 1})
        self.assertEqual(raw, b'{"a":1,"z":[0.10,"\\u00e9"]}')
        self.assertEqual(p.digest(self.b), hashlib.sha256(p.encode(self.b)).hexdigest())
        for value in (float('nan'), Decimal('1e101'), 'x' * 100001, {'x': object()}):
            with self.assertRaises(ValueError):
                p.encode(value)
        for bad in ('A' * 64, '0' * 63, None):
            with self.assertRaises(ValueError):
                p.verify(self.b, bad, 2, 6)

    def test_seeded_handoffs(self):
        rng = random.Random(3901)
        for _ in range(120):
            durations = [rng.randint(1, 9) for _ in range(rng.randint(1, 9))]
            tasks, rows, elapsed = [], [], 0
            for i, duration in enumerate(durations):
                name = str(i)
                tasks.append({'id': name, 'minutes': duration,
                              'after': [str(i - 1)] if i else []})
                rows.append({'task': name, 'worker': 1, 'start': elapsed, 'finish': elapsed + duration})
                elapsed += duration
            b = p.pack({'tasks': tasks}, {'workers': 1, 'finish': elapsed, 'schedule': rows},
                       {'gates': [{'id': 'delivery', 'tasks': [str(len(tasks) - 1)], 'due': elapsed}]},
                       {'capacities': {'cpu': 1}, 'demands': {t['id']: {'cpu': 1} for t in tasks}},
                       1, elapsed)
            self.assertTrue(p.verify(b, p.digest(b), 1, elapsed)['valid'])
            self.assertFalse(p.verify(b, p.digest(b), 1, elapsed - 1)['valid'])
            b['gates']['gates'][0]['due'] -= 1
            self.assertFalse(p.verify(b, p.digest(b), 1, elapsed)['valid'])

    def test_cli_and_duplicate_keys(self):
        scratch = Path('test/scratch/planseal')
        scratch.mkdir(parents=True, exist_ok=True)
        path = scratch / 'bundle.json'
        path.write_bytes(p.encode(self.b))
        command = [sys.executable, '-B', str(Path(p.__file__)), 'verify', '--bundle', str(path),
                   '--sha256', p.digest(self.b), '--workers', '2', '--budget']
        for budget, code in (('6', 0), ('5', 2), ('NaN', 1)):
            result = subprocess.run(command + [budget], capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)
        path.write_text('{"schema":1,"schema":2}')
        result = subprocess.run(command + ['6'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('duplicate JSON key', result.stderr)
        self.assertEqual(result.stdout, '')
        inputs = []
        for key in ('tasks', 'plan', 'gates', 'limits'):
            file = scratch / (key + '.json')
            file.write_bytes(p.encode(self.b[key]))
            inputs.extend(['--' + key, str(file)])
        result = subprocess.run([sys.executable, '-B', str(Path(p.__file__)), 'pack'] + inputs +
                                ['--workers', '2', '--budget', '6'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.strip(), p.digest(self.b))
        self.assertEqual(p.encode(json.loads(result.stdout)), p.encode(self.b))


if __name__ == '__main__':
    unittest.main()
