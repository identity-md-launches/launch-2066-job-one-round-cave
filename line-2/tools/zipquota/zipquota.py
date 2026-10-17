#!/usr/bin/env python3
"""Extract a strictly checked ZIP only if every root stays within its own quota."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys
import time
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'safezip'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'zipseal'))
from safezip import Rejected, local_path, member_name
from zipseal import process as sealed_process

POLICY_BYTES = 65536


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected('duplicate JSON key: ' + key)
        result[key] = value
    return result


def _limit(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Rejected(label + ' must be a nonnegative integer')
    return value


def read_policy(path, *, policy_bytes=POLICY_BYTES):
    """Read a bounded local policy with disjoint, validated top-level roots."""
    if isinstance(policy_bytes, bool) or not isinstance(policy_bytes, int) or policy_bytes < 1:
        raise Rejected('policy_bytes must be a positive integer')
    source = local_path(path)
    if not source.is_file() or source.stat().st_size > policy_bytes:
        raise Rejected('policy missing, nonregular, or over policy byte limit')
    with source.open('rb') as reader:
        if not stat.S_ISREG(os.fstat(reader.fileno()).st_mode):
            raise Rejected('policy must be a regular file')
        data = reader.read(policy_bytes + 1)
    if len(data) > policy_bytes:
        raise Rejected('policy byte limit exceeded while reading')
    try:
        policy = json.loads(data.decode('utf-8'), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise Rejected('invalid policy JSON: ' + str(error)) from None
    if not isinstance(policy, dict) or set(policy) != {'roots'}:
        raise Rejected('policy must contain only roots')
    roots = policy['roots']
    if not isinstance(roots, list) or not roots or len(roots) > 1000:
        raise Rejected('roots must be a nonempty list of at most 1000 items')
    normalized = {}
    for row in roots:
        if not isinstance(row, dict) or set(row) != {'name', 'files', 'bytes', 'nodes'}:
            raise Rejected('each root needs only name, files, bytes and nodes')
        name = row['name']
        if not isinstance(name, str) or not name or '/' in name:
            raise Rejected('root name must be one safe path segment')
        try:
            checked = member_name(zipfile.ZipInfo(name))
        except (ValueError, UnicodeError) as error:
            raise Rejected('unsafe root name: ' + str(error)) from None
        if checked != name:
            raise Rejected('root name changed during validation')
        key = name.casefold()
        if key in normalized:
            raise Rejected('duplicate or case-colliding root: ' + repr(name))
        normalized[key] = {'name': name, 'files': _limit(row['files'], 'files'),
                           'bytes': _limit(row['bytes'], 'bytes'),
                           'nodes': _limit(row['nodes'], 'nodes')}
    return normalized, hashlib.sha256(data).hexdigest()


def check_quotas(entries, roots):
    """Account for files, bytes and distinct explicit or implicit nodes per root."""
    usage = {key: {'name': row['name'], 'files': 0, 'bytes': 0, 'nodes': set()}
             for key, row in roots.items()}
    for entry in entries:
        path = entry['path']
        parts = path.split('/')
        key = parts[0].casefold()
        if key not in roots or parts[0] != roots[key]['name']:
            raise Rejected('member outside approved roots: ' + repr(path))
        used = usage[key]
        for index in range(1, len(parts) + 1):
            used['nodes'].add('/'.join(parts[:index]))
            if len(used['nodes']) > roots[key]['nodes']:
                raise Rejected('node quota exceeded for ' + repr(roots[key]['name']))
        if entry['kind'] == 'file':
            used['files'] += 1
            used['bytes'] += entry['bytes']
            if used['files'] > roots[key]['files']:
                raise Rejected('file quota exceeded for ' + repr(roots[key]['name']))
            if used['bytes'] > roots[key]['bytes']:
                raise Rejected('byte quota exceeded for ' + repr(roots[key]['name']))
    return [{'name': used['name'], 'files': used['files'], 'bytes': used['bytes'],
             'nodes': len(used['nodes'])} for used in usage.values()]


def process(archive_path, policy_path, output=None, *, policy_bytes=POLICY_BYTES,
            entries=1000, directory_bytes=2097152, archive_bytes=33554432,
            nodes=32000, file_bytes=16777216, total_bytes=67108864,
            ratio=200, expected_sha256=None, seconds=None, cancelled=None):
    if seconds is not None and (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
                                or not math.isfinite(seconds) or seconds <= 0):
        raise Rejected('seconds must be a finite positive number')
    if cancelled is not None and not callable(cancelled):
        raise Rejected('cancelled must be callable')
    started = time.monotonic()

    def checkpoint():
        if cancelled is not None and cancelled():
            raise Rejected('operation cancelled')
        if seconds is not None and time.monotonic() - started >= seconds:
            raise Rejected('operation time budget exceeded')
        return False

    checkpoint()
    roots, policy_sha256 = read_policy(policy_path, policy_bytes=policy_bytes)
    checkpoint()
    limits = dict(entries=entries, directory_bytes=directory_bytes,
                  archive_bytes=archive_bytes, nodes=nodes, file_bytes=file_bytes,
                  total_bytes=total_bytes, ratio=ratio,
                  expected_sha256=expected_sha256, cancelled=checkpoint)
    inspected = sealed_process(archive_path, **limits)
    checkpoint()
    usage = check_quotas(inspected['entries'], roots)
    checkpoint()
    if output is None:
        result = inspected
    else:
        limits['expected_sha256'] = inspected['archive_sha256']
        result = sealed_process(archive_path, output, **limits)
        # The second pass is bound to the first archive digest. Check that its
        # complete inventory still satisfies the same in-memory policy.
        check_quotas(result['entries'], roots)
    result['policy_sha256'] = policy_sha256
    result['root_usage'] = usage
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('inspect', 'extract'))
    parser.add_argument('archive')
    parser.add_argument('policy')
    parser.add_argument('output', nargs='?')
    parser.add_argument('--policy-bytes', type=int, default=POLICY_BYTES)
    parser.add_argument('--sha256', dest='expected_sha256')
    for flag, default in [('entries', 1000), ('directory-bytes', 2097152),
                          ('archive-bytes', 33554432), ('nodes', 32000),
                          ('file-bytes', 16777216), ('total-bytes', 67108864),
                          ('ratio', 200)]:
        parser.add_argument('--' + flag, type=int, default=default)
    parser.add_argument('--seconds', type=float)
    args = vars(parser.parse_args(argv))
    command = args.pop('command')
    archive, policy, output = (args.pop(name) for name in ('archive', 'policy', 'output'))
    if (command == 'extract') != (output is not None):
        parser.error('extract requires output; inspect takes no output')
    try:
        report = process(archive, policy, output, **args)
    except (ValueError, OSError, zipfile.BadZipFile, NotImplementedError,
            RuntimeError, EOFError, zlib.error) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
