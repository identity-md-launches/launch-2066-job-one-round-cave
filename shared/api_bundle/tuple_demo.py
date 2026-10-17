#!/usr/bin/env python3
"""Compare a changed tuple reference in approved, strictly accounted ZIPs."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
import api_bundle


def documents():
    capture = Path(__file__).with_name('imd-openapi.json').read_bytes()
    old = json.loads(capture)
    old['openapi'] = '3.1.0'
    old.setdefault('components', {}).setdefault('schemas', {})['OrderedState'] = {
        'type': 'string', 'enum': ['pending', 'done']}
    old['paths']['/requests/quote']['post']['responses'] = {
        '200': {'description': 'Hypothetical ordered result', 'content': {
            'application/json': {'schema': {'type': 'array', 'items': False,
                'prefixItems': [{'type': 'integer'}, {'$ref': '#/components/schemas/OrderedState'}]}}}}}
    new = copy.deepcopy(old)
    new['components']['schemas']['OrderedState']['enum'].append('retry')
    return capture, old, new


def archive(path, document):
    with zipfile.ZipFile(path, 'w') as writer:
        writer.writestr(zipfile.ZipInfo('docs/openapi.json'), json.dumps(document))
        writer.writestr(zipfile.ZipInfo('unselected.txt'), b'inert payload')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def demo():
    capture, old, new = documents()
    scratch = Path('test/scratch')
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tuple-bundle-', dir=scratch) as name:
        root = Path(name)
        a, b = root/'old.zip', root/'new.zip'
        ah, bh = archive(a, old), archive(b, new)
        options = dict(member='docs/openapi.json', old_sha256=ah, new_sha256=bh, strict_layout=True)
        prior = api_bundle.compare(a, b, keys=True, **options)
        changed = api_bundle.compare(a, b, tuples=True, **options)
        same = api_bundle.compare(a, a, tuples=True, **{**options, 'new_sha256': ah})
        assert prior['status'] == 'review_required'
        assert changed['status'] == 'breaking'
        assert any(f['code']=='schema_enum_incompatible' and '/prefixItems/1/' in f['location']
                   for f in changed['findings'])
        assert all(f in changed['findings'] for f in prior['findings'])
        assert same['status'] == 'no_detected_breakage'
        assert sorted(p.name for p in root.iterdir()) == ['new.zip', 'old.zip']
        return dict(baseline_source='https://api.imd.fun/openapi.json',
            capture_sha256=hashlib.sha256(capture).hexdigest(),
            trial='Hypothetical response tuple: a referenced position enum widens; not a live service change.',
            network_used=False, extracted_files=0, previous_mode=prior['status'],
            unchanged=same['status'], changed=changed)


if __name__ == '__main__':
    print(json.dumps(demo(), indent=2))
