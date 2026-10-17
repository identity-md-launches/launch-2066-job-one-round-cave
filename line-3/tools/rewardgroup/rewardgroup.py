#!/usr/bin/env python3
"""Roll up verified ZTO allocations into a complete, disjoint review partition."""
import argparse
import importlib.util
from pathlib import Path
import re
import sys

RECEIPT = Path(__file__).resolve().parents[1] / 'rewardreceipt' / 'rewardreceipt.py'
SPEC = importlib.util.spec_from_file_location('rewardgroup_receipt', RECEIPT)
rr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rr)
rs = rr.rs
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}')
SCOPE = ('Unsigned review totals of existing contributor shares; no reallocation, '
         'group recipient, entitlement, identity, balance or payment established.')


def partition(policy, identifiers):
    """Require every contributor exactly once, including contributors with zero units."""
    rs.require(isinstance(policy, dict) and set(policy) == {'groups'},
               'policy must contain exactly groups')
    groups = policy['groups']
    rs.require(isinstance(groups, list) and 1 <= len(groups) <= len(identifiers),
               'groups must be a nonempty list no larger than the roster')
    names, seen, parsed = set(), set(), []
    for group in groups:
        rs.require(isinstance(group, dict) and set(group) == {'id', 'members'},
                   'each group must contain exactly id and members')
        name, members = group['id'], group['members']
        rs.require(isinstance(name, str) and ID.fullmatch(name), 'invalid group id')
        rs.require(name not in names, 'duplicate group id')
        names.add(name)
        rs.require(isinstance(members, list) and 1 <= len(members) <= len(identifiers),
                   'group members must be a nonempty bounded list')
        for member in members:
            rs.require(isinstance(member, str) and member in identifiers,
                       'unknown contributor in group')
            rs.require(member not in seen, 'contributor assigned more than once')
            seen.add(member)
        parsed.append((name, sorted(members)))
    rs.require(seen == identifiers, 'every contributor must be assigned, including zero shares')
    return sorted(parsed)


def summarize(request, report, metadata, policy):
    receipt = rr.verify(request, report, metadata)
    by_id = {row['id']: row for row in report['allocations']}
    groups = partition(policy, set(by_id))
    decimals = report['token']['decimals']
    totals = []
    for name, members in groups:
        units = sum(int(by_id[member]['units']) for member in members)
        totals.append({'id': name, 'members': members, 'units': str(units),
                       'amount': rs.display_units(units, decimals),
                       'rounding_units_awarded': sum(by_id[m]['rounding_unit_awarded'] for m in members),
                       'contributors_without_address': sum('address' not in by_id[m] for m in members)})
    rs.require(sum(int(group['units']) for group in totals) == int(report['budget_units']),
               'group totals do not conserve the verified budget')
    return {'schema': 'rewardgroup-v1', 'scope': SCOPE, 'source_receipt': receipt,
            'policy_sha256': rr.digest(policy), 'groups': totals,
            'budget_units': report['budget_units'], 'budget_amount': report['budget_amount'],
            'grouped_units': str(sum(int(group['units']) for group in totals)),
            'contributors': len(by_id)}


def verify(request, report, metadata, policy, summary):
    expected = summarize(request, report, metadata, policy)
    rs.require(rr.canonical_bytes(summary) == rr.canonical_bytes(expected),
               'group summary differs from recomputed review totals')
    return {'schema': 'rewardgroup-receipt-v1', 'result': 'verified complete group totals',
            'summary_sha256': rr.digest(summary), 'scope': SCOPE}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    for command in ('summarize', 'verify'):
        p = sub.add_parser(command)
        p.add_argument('--request', required=True)
        p.add_argument('--report', required=True)
        p.add_argument('--policy', required=True)
        p.add_argument('--metadata', default=str(rr.ROOT / 'zto-mainnet.json'))
        p.add_argument('--output')
        if command == 'verify':
            p.add_argument('--summary', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            request = rs.read_json(rr.ROOT / 'example.json')
            metadata = rs.read_json(rr.ROOT / 'zto-mainnet.json')
            report = rs.allocate(request, metadata)
            policy = {'groups': [{'id': 'delivery', 'members': ['build', 'review']},
                                 {'id': 'discovery', 'members': ['research']}]}
        else:
            request, report, metadata, policy = [rs.read_json(getattr(args, name))
                                                for name in ('request', 'report', 'metadata', 'policy')]
        result = summarize(request, report, metadata, policy)
        if args.command == 'verify':
            result = verify(request, report, metadata, policy, rs.read_json(args.summary))
        rs.write_json(result, getattr(args, 'output', None))
    except (rs.Invalid, OSError, ValueError, OverflowError, RecursionError) as exc:
        print('rewardgroup: ' + (str(exc) if isinstance(exc, rs.Invalid) else type(exc).__name__), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
