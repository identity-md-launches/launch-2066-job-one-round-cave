#!/usr/bin/env python3
"""Tuple integration checks and a direct finite-array acceptance oracle."""
import contextlib
import copy
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import tuplecheck as tool


def doc(schema, direction='response', version='3.1.0'):
    media = {'application/json': {'schema': copy.deepcopy(schema)}}
    op = {'responses': {}}
    if direction == 'response':
        op['responses']['200'] = {'description': 'test', 'content': media}
    else:
        op['requestBody'] = {'content': media}
    return {'openapi': version, 'paths': {'/probe': {'post': op}}}


def root(d, direction='response'):
    op = d['paths']['/probe']['post']
    body = op['responses']['200'] if direction == 'response' else op['requestBody']
    return body['content']['application/json']['schema']


def codes(report):
    return {f['code'] for f in report['findings']}


def tuple_break(report):
    return any(f['severity'] == 'breaking' and
               ('/prefixItems/' in f['location'] or '/tupleTail' in f['location'])
               for f in report['findings'])


def accepts(schema, values):
    # Independent direct value predicate, not the analyzer's effective-slot code.
    for index, value in enumerate(values):
        if index < len(schema.get('prefixItems', [])):
            constraint = schema['prefixItems'][index]
        else:
            constraint = schema.get('items', True)
        if constraint is False:
            return False
        if isinstance(constraint, dict) and value not in constraint.get('enum', [0, 1, 2]):
            return False
    return True


class Tests(unittest.TestCase):
    def test_finite_array_oracle(self):
        # Equal prefixes with enum-only regions are exactly characterized by
        # arrays of lengths 0..3 over this alphabet. No reachability confounders.
        choices = [{'enum': [0]}, {'enum': [1]}, {'enum': [0, 1]}, {'enum': [0, 1, 2]}]
        schemas = [{'type': 'array', 'prefixItems': [a, b], 'items': {'enum': [0, 1, 2]}}
                   for a, b in itertools.product(choices, repeat=2)]
        arrays = [v for n in range(4) for v in itertools.product(range(3), repeat=n)]
        checked = 0
        for direction, a, b in itertools.product(('request', 'response'), schemas, schemas):
            before = {v for v in arrays if accepts(a, v)}
            after = {v for v in arrays if accepts(b, v)}
            unsafe = bool(before - after) if direction == 'request' else bool(after - before)
            self.assertEqual(tuple_break(tool.compare(doc(a, direction), doc(b, direction))),
                             unsafe, (direction, a, b))
            checked += 1
        self.assertEqual(checked, 512)

    def test_unchanged_reference_changed_target(self):
        for direction in ('request', 'response'):
            a = doc({'type': 'array', 'prefixItems': [{'$ref': '#/components/schemas/Item'}]}, direction)
            a['components'] = {'schemas': {'Item': {'enum': [0, 1]}}}
            b = copy.deepcopy(a)
            b['components']['schemas']['Item']['enum'] = [0] if direction == 'request' else [0, 1, 2]
            prior = tool.previous.compare(a, b)
            report = tool.compare(a, b)
            self.assertFalse(tuple_break(prior))
            self.assertTrue(tuple_break(report))
            self.assertTrue(all(f in report['findings'] for f in prior['findings']))

    def test_prefix_to_tail_and_tail_to_prefix(self):
        a = {'type': 'array', 'prefixItems': [{'enum': [0, 1]}], 'items': {'enum': [0, 1]}}
        b = {'type': 'array', 'items': {'enum': [0]}}
        report = tool.compare(doc(a, 'request'), doc(b, 'request'))
        self.assertTrue(tuple_break(report))
        self.assertEqual(report['tuple_pairs'][0]['new_source'], 'items')
        report = tool.compare(doc(b), doc(a))
        self.assertTrue(tuple_break(report))
        self.assertEqual(report['tuple_pairs'][0]['old_source'], 'items')

    def test_homogeneous_tail_after_both_prefixes(self):
        a = {'prefixItems': [{'type': 'integer'}], 'items': {'enum': [0]}}
        b = {'prefixItems': [{'type': 'integer'}, {'enum': [0]}], 'items': {'enum': [0, 1]}}
        report = tool.compare(doc(a), doc(b))
        self.assertTrue(any(f['code'] == 'schema_enum_incompatible' and '/tupleTail/enum' in f['location']
                            for f in report['findings']))
        self.assertEqual(len(report['tuple_pairs']), 3)

    def test_boolean_closure_and_omission(self):
        a = {'prefixItems': [True]}
        b = {'prefixItems': [False]}
        self.assertIn('tuple_position_closed_incompatible', codes(tool.compare(doc(a, 'request'), doc(b, 'request'))))
        self.assertIn('tuple_position_closed_incompatible', codes(tool.compare(doc(b), doc(a))))
        self.assertFalse(tuple_break(tool.compare(doc(a), doc(b))))
        self.assertFalse(tuple_break(tool.compare(doc(b, 'request'), doc(a, 'request'))))
        c = {'prefixItems': [True], 'items': True}
        self.assertFalse(tuple_break(tool.compare(doc(a), doc(c))))
        # A false position doesn't require an element; [] still fits.
        self.assertTrue(accepts(b, ()))

    def test_true_to_schema_variance(self):
        a = {'prefixItems': [True]}
        b = {'prefixItems': [{'type': 'integer'}]}
        self.assertTrue(tuple_break(tool.compare(doc(a, 'request'), doc(b, 'request'))))
        self.assertTrue(tuple_break(tool.compare(doc(b), doc(a))))
        self.assertFalse(tuple_break(tool.compare(doc(a), doc(b))))

    def test_nested_tuple_and_key_rules(self):
        a = doc({'type': 'object', 'properties': {'a/~': {'type': 'array', 'prefixItems': [
            {'type': 'object', 'propertyNames': {'enum': ['a']}}]}}})
        b = copy.deepcopy(a)
        root(b)['properties']['a/~']['prefixItems'][0]['propertyNames']['enum'].append('b')
        report = tool.compare(a, b)
        self.assertIn('property_names_incompatible', codes(report))
        self.assertTrue(any('/properties/a~1~0/prefixItems/0/propertyNames' in f['location']
                            for f in report['findings']))

    def test_recursive_tuple_terminates(self):
        a = doc({'$ref': '#/components/schemas/Node'})
        a['components'] = {'schemas': {'Node': {'prefixItems': [
            {'$ref': '#/components/schemas/Node'}, {'enum': [0]}]}}}
        b = copy.deepcopy(a)
        b['components']['schemas']['Node']['prefixItems'][1]['enum'].append(1)
        report = tool.compare(a, b)
        self.assertTrue(tuple_break(report))
        self.assertLess(report['schema_visits'], 20)

    def test_older_dialects_review(self):
        for va, vb in (('3.0.3', '3.0.3'), ('3.0.3', '3.1.0'), ('3.1.0', '3.0.3')):
            a, b = doc({'prefixItems': [{'enum': [0]}]}, version=va), doc({'prefixItems': [{'enum': [1]}]}, version=vb)
            report = tool.compare(a, b)
            self.assertIn('tuple_dialect_unchecked', codes(report))
            self.assertEqual(report['tuple_pairs'], [])

    def test_invalid_prefixes_references_and_tail_refuse(self):
        for schema in ({'prefixItems': []}, {'prefixItems': {}}, {'prefixItems': None},
                       {'prefixItems': [3]}, {'prefixItems': [{'type': 'invalid'}]},
                       {'prefixItems': [{'enum': []}]},
                       {'prefixItems': [True], 'items': []},
                       {'prefixItems': [{'$ref': 'https://example.invalid/schema'}]},
                       {'prefixItems': [{'$ref': '#/missing'}]},
                       {'prefixItems': [{'$ref': '#/bad~2'}]}):
            with self.subTest(schema=schema), self.assertRaises(tool.api.Invalid):
                tool.compare(doc(schema), doc(schema))

    def test_budgets_and_no_partial_success(self):
        a = doc({'prefixItems': [{'enum': [0]}]})
        for owner, field in ((tool, 'MAX_PREFIX'), (tool, 'MAX_TUPLE_PAIRS'), (tool.api, 'MAX_STEPS')):
            with patch.object(owner, field, 0), self.assertRaises(tool.api.Invalid):
                tool.compare(a, a)
        with patch.object(tool.api, 'MAX_FINDINGS', 0), self.assertRaises(tool.api.Invalid):
            tool.compare(a, doc({'prefixItems': [{'enum': [0, 1]}]}))

    def test_response_remapped_headers_and_request_parameter(self):
        a = doc({})
        op = a['paths']['/probe']['post']
        op['responses'] = {'2XX': {'description': 'test', 'headers': {'X-Order': {
            'schema': {'prefixItems': [{'enum': [0]}]}}}}}
        b = copy.deepcopy(a)
        bop = b['paths']['/probe']['post']
        bop['responses'] = {'200': copy.deepcopy(op['responses']['2XX'])}
        bop['responses']['200']['headers']['X-Order']['schema']['prefixItems'][0]['enum'].append(1)
        self.assertTrue(tuple_break(tool.compare(a, b)))
        a = doc({})
        a['paths']['/probe']['post']['parameters'] = [{'name': 'tuple', 'in': 'query',
            'schema': {'prefixItems': [{'enum': [0, 1]}]}}]
        b = copy.deepcopy(a)
        b['paths']['/probe']['post']['parameters'][0]['schema']['prefixItems'][0]['enum'].pop()
        self.assertTrue(tuple_break(tool.compare(a, b)))

    def test_determinism_nonmutation_and_capture(self):
        capture = Path(__file__).resolve().parents[1] / 'apidelta/imd-openapi.json'
        a, _ = tool.api.load(capture)
        saved = copy.deepcopy(a)
        report = tool.compare(a, a)
        self.assertEqual(report['findings'], [])
        self.assertEqual(report['operations_compared'], 5)
        self.assertEqual(a, saved)
        a, b = doc({'prefixItems': [{'enum': [0]}]}), doc({'prefixItems': [{'enum': [1]}]})
        saved = copy.deepcopy((a, b))
        self.assertEqual(tool.compare(a, b), tool.compare(a, b))
        self.assertEqual((a, b), saved)

    def test_cli_all_states_and_demo(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main(['demo']), 0)
        # Tests create no repository scratch files.
        with tempfile.TemporaryDirectory(dir='/tmp') as folder:
            # Isolate exit/report tests from workspace-loader tests already
            # covered by the inherited suites; these inputs live only in /tmp.
            from unittest.mock import patch
            p, q = Path(folder) / 'old.json', Path(folder) / 'new.json'
            a = doc({'prefixItems': [{'enum': [0]}]})
            p.write_text(json.dumps(a))
            with patch.object(tool.api, 'path_in_workspace', side_effect=lambda v: Path(v)):
                for b, expected in ((a, 0), (doc({'prefixItems': [{'enum': [0, 1]}]}), 1),
                                    (doc({'prefixItems': [{'enum': [0]}], 'description': 'new'}), 3), ({}, 2)):
                    q.write_text(json.dumps(b))
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(tool.main(['compare', str(p), str(q)]), expected)


if __name__ == '__main__':
    unittest.main()
