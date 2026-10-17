#!/usr/bin/env python3
"""Carry and recheck a complete offline plan and its declared constraints."""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
for sibling in ('plancheck', 'gatecheck', 'lockcheck'):
    sys.path.insert(0, str(HERE.parent / sibling))
import plancheck
import gatecheck
import lockcheck

SCHEMA = 'planseal/1'


def encode(value):
    """Deterministic JSON bytes, preserving bounded decimal tokens exactly.

    Object keys are sorted; array order is significant. Numeric spellings such
    as 1 and 1.0 remain distinct. This is a versioned wire format, not JCS.
    """
    def emit(item, depth=0):
        if depth > 32:
            raise ValueError('bundle nesting exceeds 32')
        if item is None or type(item) in (str, bool):
            return json.dumps(item, ensure_ascii=True, allow_nan=False)
        if type(item) in (int, float, Decimal):
            plancheck.number(item, 'JSON number')
            return str(item) if type(item) is not float else str(Decimal(str(item)))
        if type(item) is list:
            return '[' + ','.join(emit(v, depth + 1) for v in item) + ']'
        if type(item) is dict and all(type(k) is str for k in item):
            return '{' + ','.join(json.dumps(k, ensure_ascii=True) + ':' +
                                  emit(item[k], depth + 1) for k in sorted(item)) + '}'
        raise ValueError('unsupported JSON value')
    raw = emit(value).encode('ascii')
    if len(raw) > plancheck.LIMIT:
        raise ValueError('complete bundle exceeds 100 KB')
    return raw


def digest(bundle):
    return hashlib.sha256(encode(bundle)).hexdigest()


def validate(bundle):
    plancheck.keys(bundle, ('schema', 'tasks', 'plan', 'gates', 'limits',
                            'workers', 'budget'))
    if bundle['schema'] != SCHEMA:
        raise ValueError('unsupported bundle schema')
    if plancheck.number(bundle['budget'], 'budget') < 0:
        raise ValueError('budget must be nonnegative')
    # Do not carry opaque planner commentary or claimed validation results.
    plancheck.keys(bundle['plan'], ('workers', 'finish', 'schedule'), ('units',))
    workers, budget = bundle['workers'], bundle['budget']
    baseline = plancheck.check(bundle['tasks'], bundle['plan'], workers, budget)
    gates = gatecheck.check(bundle['tasks'], bundle['plan'], bundle['gates'], workers, budget)
    resources = lockcheck.check(bundle['tasks'], bundle['plan'], bundle['limits'], workers, budget)
    encode(bundle)
    return {'valid': baseline['valid'] and gates['valid'] and resources['valid'],
            'schedule': baseline, 'gates': gates, 'resources': resources}


def pack(tasks, plan, gates, limits, workers, budget):
    bundle = {'schema': SCHEMA, 'tasks': tasks, 'plan': plan, 'gates': gates,
              'limits': limits, 'workers': workers, 'budget': budget}
    if not validate(bundle)['valid']:
        raise ValueError('refusing to package a plan that fails its declared constraints')
    # Return an independent JSON snapshot, not mutable caller-owned references.
    return json.loads(encode(bundle), parse_float=Decimal)


def verify(bundle, expected_sha256, workers, budget):
    if not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('expected SHA-256 must be 64 lowercase hexadecimal characters')
    actual = digest(bundle)
    if actual != expected_sha256:
        raise ValueError('bundle digest mismatch; no plan checks performed')
    result = validate(bundle)
    # Caller authority cannot silently be replaced by a self-declared bundle.
    external = plancheck.check(bundle['tasks'], bundle['plan'], workers, budget)
    result['recipient_schedule'] = external
    result['valid'] = result['valid'] and external['valid']
    result['sha256'] = actual
    result['scope'] = ('Integrity relative to the supplied digest and feasibility under declared '
                       'constraints plus recipient workers/budget; no identity, optimality, '
                       'real availability or execution guarantee.')
    return result


def example():
    tasks = {'tasks': [{'id': 'draft', 'minutes': 2},
                       {'id': 'review', 'minutes': 1, 'after': ['draft']},
                       {'id': 'background', 'minutes': 4}]}
    plan = {'workers': 2, 'finish': 6, 'schedule': [
        {'task': 'draft', 'worker': 1, 'start': 0, 'finish': 2},
        {'task': 'review', 'worker': 1, 'start': 2, 'finish': 3},
        {'task': 'background', 'worker': 2, 'start': 2, 'finish': 6}]}
    gates = {'gates': [{'id': 'handoff', 'tasks': ['review'], 'due': 3}]}
    limits = {'capacities': {'gpu': 1}, 'demands': {
        'draft': {'gpu': 1}, 'review': {}, 'background': {'gpu': 1}}}
    return pack(tasks, plan, gates, limits, 2, 6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    modes.add_parser('demo')
    create = modes.add_parser('pack')
    for name in ('tasks', 'plan', 'gates', 'limits'):
        create.add_argument('--' + name, required=True)
    check = modes.add_parser('verify')
    check.add_argument('--bundle', required=True)
    check.add_argument('--sha256', required=True)
    for sub in (create, check):
        sub.add_argument('--workers', required=True, type=int)
        sub.add_argument('--budget', required=True, type=Decimal)
    args = parser.parse_args()
    try:
        if args.mode == 'pack':
            bundle = pack(*(plancheck.read_json(getattr(args, n)) for n in
                            ('tasks', 'plan', 'gates', 'limits')), args.workers, args.budget)
            # stdout is only the bundle; the digest goes to stderr for handoff.
            print(digest(bundle), file=sys.stderr)
            print(encode(bundle).decode('ascii'))
            return 0
        if args.mode == 'demo':
            bundle = example()
            result = verify(bundle, digest(bundle), 2, 6)
            result['tighter_recipient_budget'] = verify(bundle, digest(bundle), 2, 5)['valid']
        else:
            result = verify(plancheck.read_json(args.bundle), args.sha256, args.workers, args.budget)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result['valid'] else 2
    except (ValueError, InvalidOperation, OSError, OverflowError, RecursionError) as exc:
        print('planseal: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
