# TupleCheck

Find potential breaking changes at ordered array positions in OpenAPI 3.1
JSON descriptions. An unchanged `prefixItems` reference can hide a changed
component; TupleCheck resolves each side independently and compares those
positions. It extends KeyCheck and retains every earlier analyzer and finding.
Python 3.9+ and the standard library suffice. Keep the sibling tool folders.
The tool reads descriptions and never calls their described operations.

Run from the repository root, with no network or installation:

```sh
python3 -B line-4/tools/tuplecheck/tuplecheck.py demo
```

Tried successfully: five operations compared, **one potential break and one
review**, exit 0. The saved real IMD description supplies an operation; its
response is hypothetically replaced with a two-position tuple. A referenced
second-position enum expands from `pending, done` to `pending, done, retry`.
The reference itself stays unchanged. KeyCheck does not follow that position;
TupleCheck finds the response enum expansion. This is an illustration, not
an observed change to the public service.

For your own JSON descriptions within the current workspace:

```sh
python3 -B line-4/tools/tuplecheck/tuplecheck.py compare old.json new.json
```

Compare prints deterministic JSON with exact input-byte hashes. Exit **0**:
no detected break in the subset; **1**: potential break; **2**: refusal of
invalid/unsupported input or resource exhaustion; **3**: unresolved review.
`compare(old_dict, new_dict)` returns the report without byte hashes and
without mutating either document. `tuple_pairs` identifies visited positions,
request/response direction and whether each effective schema came from
`prefixItems` or `items`. `/tupleTail` is a virtual report location for the
homogeneous region after both prefixes, not a JSON Pointer into the document.
Other tuple locations identify effective positions and can exceed one side's
literal prefix length.

## Behavior and boundaries

The [JSON Schema 2020-12 array rules](https://json-schema.org/draft/2020-12/json-schema-core.html#section-10.3.1)
state: “This keyword does not constrain the length of the array.” `prefixItems`
constrains values at matching positions; `items` constrains remaining values.
The [OpenAPI 3.1 Schema Object](https://spec.openapis.org/oas/v3.1.0.html#schema-object)
uses this vocabulary.

TupleCheck visits every position up to the longer prefix, comparing a prefix
entry against the other side's `items` when necessary. It also compares one
representative tail region. Omitted `items` and `true` allow any value; `false`
forbids a value at that position but still allows shorter arrays. Supported
inherited rules compare types, enums, bounds, maps, keys and other schema
regions. Boolean admission changes retain review; closing a request position
or opening a response position also adds a potential break. Local references
and recursive graphs use the inherited resolver and active-pair guard.

OpenAPI 3.0 or mixed-version pairs get explicit tuple-dialect review rather
than tuple inference. At most **64 prefix entries per schema** and **1,024
position/tail pairs** are visited, alongside inherited limits: 1 MiB/input,
50,000 nodes, depth 80, 20,000 schema visits, 2,000 findings and the previous
operation/status/header/security limits. Malformed visited positions,
non-schema tails, empty declared prefixes, remote/missing references, alias
cycles, semantic reference siblings and budget overflow refuse without a
partial success report. No reference URL is fetched.

This is a conservative region comparison, not whole-array implication or
complete OpenAPI validation. Length restrictions, `contains`,
`unevaluatedItems`, composition, custom dialects and other constraints can
make a reported position unreachable or alter its meaning. A potential break
does not prove an actual payload exists. All prior findings remain, including
raw `items` comparisons even when prefix lengths change; those may concern
different index ranges and need manual review. Unknown or unvisited schema
semantics and runtime behavior remain outside the proof scope. A clean report
is not compatibility certification.

## What happened when tried

```sh
python3 -B line-4/tools/tuplecheck/selftest.py
python3 -B line-4/check-39.py
```

All **14 new tests** passed, including **512 independent finite-array policy
comparisons**, both directions, unchanged reference targets, prefix/tail
migration, boolean admission, recursive/nested tuples, nested KeyCheck rules,
remapped response headers, request parameters, dialect review, malformed
inputs, budgets, nonmutation, deterministic output and CLI exit states.
All **296 tests across 19 suites** passed, retaining every inherited suite.
Round-check temporary files are redirected to the authorized `test/scratch/`.

The optional `python3 -B line-4/check-39.py --live` trial fetched only
`https://api.imd.fun/openapi.json`, with User-Agent
`Pepeolithic-TupleCheck/39.0`. It returned 23,132 bytes matching the saved
capture: five operations compared, zero findings. No tuple positions occur in
that real description, so the live trial checks integration, not live tuple
semantics. Evidence is in `line-4/check-results-39.json`. No coin, account,
credential, payment, signature, deployment or mutation is needed.
