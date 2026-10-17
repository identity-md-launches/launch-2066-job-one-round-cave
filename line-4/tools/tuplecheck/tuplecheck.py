#!/usr/bin/env python3
"""Bounded offline OpenAPI 3.1 ordered array-position comparison."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('tuplecheck_previous',
    Path(__file__).resolve().parents[1] / 'keycheck/keycheck.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
api = previous.api
MAX_PREFIX = 64
MAX_TUPLE_PAIRS = 1024


def positions(document, schema):
    prefix = schema.get('prefixItems', [])
    api.require(isinstance(prefix, list) and len(prefix) <= MAX_PREFIX and
                ('prefixItems' not in schema or bool(prefix)),
                'prefixItems must be a nonempty array of at most 64 schemas')
    result = []
    for item in prefix:
        item = document.resolve(item)
        api.require(isinstance(item, (dict, bool)), 'tuple position must resolve to a schema')
        result.append(item)
    tail = document.resolve(schema.get('items', True))
    api.require(isinstance(tail, (dict, bool)), 'items must resolve to a schema')
    return result, tail


class Analyzer(previous.Analyzer):
    def __init__(self, old, new):
        super().__init__(old, new)
        self.tuple_pairs = []
        self.tuple_any = {}

    def slot(self, a, b, loc, direction):
        # Boolean schemas describe value admission, not whether an index exists.
        # A false slot permits shorter arrays; it does not require an element.
        if type(a) is bool or type(b) is bool:
            self.changed(a, b, loc, 'tuple_boolean_policy_changed',
                         'Tuple value admission changed; check position reachability.')
            unsafe = (b is False and a is not False) if direction == 'request' else (
                      a is False and b is not False)
            if unsafe:
                self.emit('breaking', 'tuple_position_closed_incompatible', loc,
                          'Potential break: request position is now forbidden.' if direction == 'request'
                          else 'Potential break: response position is now allowed.')
            if a is False or b is False:
                return
        self.schema(self.tuple_any if a is True else a,
                    self.tuple_any if b is True else b, loc, direction)

    def _schema(self, old, new, loc, direction):
        super()._schema(old, new, loc, direction)
        if 'prefixItems' not in old and 'prefixItems' not in new:
            return
        base = loc + '/prefixItems'
        if not (self.old.obj['openapi'].startswith('3.1.') and
                self.new.obj['openapi'].startswith('3.1.')):
            self.emit('review', 'tuple_dialect_unchecked', base,
                      'Ordered-position analysis requires OpenAPI 3.1 on both sides.')
            return
        ap, at = positions(self.old, old)
        bp, bt = positions(self.new, new)
        count = max(len(ap), len(bp))
        # One representative after both prefixes covers the homogeneous tail.
        for i in range(count + 1):
            api.require(len(self.tuple_pairs) < MAX_TUPLE_PAIRS,
                        'tuple pair limit exceeded; compare a smaller description')
            a = ap[i] if i < len(ap) else at
            b = bp[i] if i < len(bp) else bt
            place = base + '/' + str(i) if i < count else loc + '/tupleTail'
            self.tuple_pairs.append(dict(location=place, direction=direction,
                index=i if i < count else None,
                old_source='prefixItems' if i < len(ap) else 'items',
                new_source='prefixItems' if i < len(bp) else 'items'))
            self.slot(a, b, place, direction)


def compare(old, new):
    analyzer = Analyzer(old, new)
    report = analyzer.run()
    report.update(extension='tuplecheck-v1 (includes keycheck and earlier analyzers)',
                  tuple_pairs=analyzer.tuple_pairs, key_pairs=analyzer.key_pairs,
                  map_pairs=analyzer.map_pairs, dispatch_pairs=analyzer.dispatch_pairs,
                  schema_visits=analyzer.steps, selector_groups=analyzer.selector_groups,
                  status_visits=analyzer.status_visits,
                  remapped_header_pairs=analyzer.remapped_header_pairs,
                  tuple_scope='OpenAPI 3.1 effective prefix positions and homogeneous items tail. '
                              'Potential position-level breaks, not whole-array implication. '
                              'Length, contains, unevaluatedItems, composition and reachability '
                              'are not solved. All inherited findings are retained, including '
                              'raw items comparisons when prefix lengths differ.')
    return report


def demo():
    capture = Path(__file__).resolve().parents[1] / 'apidelta/imd-openapi.json'
    old, digest = api.load(capture)
    old = copy.deepcopy(old)
    old['openapi'] = '3.1.0'
    path = sorted(old['paths'])[0]
    method = sorted(old['paths'][path].keys() & api.METHODS)[0]
    schemas = old.setdefault('components', {}).setdefault('schemas', {})
    api.require('TupleState39' not in schemas, 'demo component collision')
    schemas['TupleState39'] = {'type': 'string', 'enum': ['pending', 'done']}
    old['paths'][path][method]['responses'] = {'200': {'description': 'Hypothetical tuple',
        'content': {'application/json': {'schema': {'type': 'array', 'items': False,
            'prefixItems': [{'type': 'integer'}, {'$ref': '#/components/schemas/TupleState39'}]}}}}}
    new = copy.deepcopy(old)
    new['components']['schemas']['TupleState39']['enum'].append('retry')
    report = compare(old, new)
    api.require(any(f['code'] == 'schema_enum_incompatible' and
                    '/prefixItems/1/enum' in f['location'] for f in report['findings']),
                'demo failed to inspect unchanged tuple reference')
    report.update(capture_sha256=digest, baseline_source='https://api.imd.fun/openapi.json',
                  demo='Saved real IMD operation, hypothetically using an OpenAPI 3.1 response '
                       'tuple. Only a referenced position enum expands. '
                       'Not an observed service change; no API operation called.')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    diff = commands.add_parser('compare')
    diff.add_argument('old')
    diff.add_argument('new')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            report = demo()
        else:
            old, oh = api.load(args.old)
            new, nh = api.load(args.new)
            report = compare(old, new)
            report.update(old_sha256=oh, new_sha256=nh)
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if args.command == 'demo' else {
            'breaking': 1, 'review_required': 3, 'no_detected_breakage': 0}[report['status']]
    except (api.Invalid, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print('tuplecheck: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
