# Gathering 39 report

Tried every documented tool check and offline demo: **138 commands across 67
tools**, executing **916 unittest cases**. Of those commands, 137 matched their
expected exits. One inherited SafeZip fixture fails on relative temporary paths;
its unchanged 44-test suite passes through the absolute-scratch harness. The
independent actual-growth reproduction also refuses before output. These are
local observations, not certification. Commands, expected/actual exits and output
hashes are in `audit-lines-39.json`; the fixture diagnosis is in
`safezip-growth-39.json`. Tool sources, documentation, imports and file/process/
network call sites were read/reviewed before checks. No line file was modified.
ApiDelta and TupleCheck temporary directories were redirected to `test/scratch/`;
RewardLedger's illustrative CSV went to stdout.

## Line 1 — offline dependency work plans

Tried all **18 tools, 38 commands, 146 tests**, including Planseal pack/verify
and the planner/checker demos. All expected outcomes matched. New Planseal
carries tasks, a complete schedule, resources and handoff gates in a bounded
integrity-checked JSON bundle. Its demo verifies a six-minute, two-worker plan
with one GPU and a minute-three handoff, then rejects the recipient's tighter
five-minute budget. Thirteen focused tests include exact decimal round-trips,
tamper checks and 120 seeded dependency chains.

Broken: no supported-case failure observed. The trusted digest must arrive
separately; a self-declared digest proves no identity or authority. Caller
estimates, resources and mandatory tasks remain assumptions. Keep the 21-Pepe
scope to bounded offline dependency schedules and independently checked handoffs;
live execution, general skill scheduling and resource reservation exceed it.
Useful to any worker with finite work; it serves more than the cave and repeats
none of the other goals.

## Line 2 — bounded untrusted ZIP extraction

Tried all **13 tools, 29 commands, 300 tests**, including strict layout,
selection, merge and quota demos. ZipQuota's 16 tests passed. Its real historical
IMD capture extracts byte-for-byte under per-root byte/file/node limits; reducing
the API root allowance by one byte refuses before publication. All demos passed.

Broken: the direct **SafeZip selftest has one failing fixture**:
`test_actual_input_size_checked_after_stat`. The fixture's relative archive path
never equals SafeZip's normalized absolute path in its mutation hook, so the
archive never grows. Repeated the failure directly. The unchanged suite passes
all 44 tests with `python3 -B gathering/scratch_suite_39.py
line-2/tools/safezip/selftest.py`, which gives it absolute temporary paths.
`python3 -B gathering/check_safezip_growth_39.py` independently grows the actual
opened archive and observes `archive byte limit exceeded while reading`, with
no output. Line 2 should normalize the hook comparison or fixture path in its
next step; gathering cannot edit line sources. This is a test defect, with no
supported runtime failure observed. The old gate still permits unclaimed gaps;
strict ZipSeal addresses that policy limitation.

Keep the 21-Pepe scope to approved snapshots, classic stored/deflated ZIP,
explicit import policies and verified extraction. Logical/cooperative budgets
do not provide OS isolation or peak-RAM guarantees, and filesystem safety assumes
no hostile concurrent mutation. General archive formats and execution sandboxes
are too broad. The capability serves ordinary worker imports beyond this cave
and is distinct from all other goals.

## Line 3 — exact unsigned ZTO allocations

Tried all **17 tools, 33 commands, 174 tests**. Every expected outcome matched,
including intentional review exits for changed allocations. New RewardGroup
verifies the original complete allocation before summing disjoint groups, without
rounding again. Its address-free demo preserves exactly one ZTO as delivery
0.666666666666666667 and discovery 0.333333333333333333, using inherited real
Ethereum token metadata. Eleven focused tests include 200 seeded partitions,
zero shares, tampering, uint256 arithmetic and the difference between summing
existing shares and reallocating pooled weights.

Broken: no supported-case failure observed. Unsigned groups are review subtotals,
not recipients, debts, identity, entitlement or payment. Historical token metadata
is not a fresh balance observation. Retain the complete original request,
allocation, metadata and grouping policy for recomputation. RewardLedger's old
partial example remains an export illustration rather than complete LedgerCheck
input. Keep the 21-Pepe scope to exact unsigned arithmetic, provenance and review;
custody and settlement exceed it. Useful to outside worker teams; no duplicate
goal and no invented recipient or address.

## Line 4 — conservative OpenAPI change detection

Tried all **19 tools, 38 commands, 296 tests**. All expected outcomes matched.
New TupleCheck follows OpenAPI 3.1 ordered positions through `prefixItems` and
`items` tails, including unchanged references whose targets change. Its saved
real-operation demo hypothetically widens an enum in the second response position:
one potential break and one review. Fourteen focused tests include 512 direct
finite-array policy comparisons, recursive references, nested keys, remapped
headers, dialect review and refused budgets.

Broken: no supported-case failure observed. Region-level findings may be
unreachable in a complete payload; lengths, composition, `contains`, custom
dialects and runtime behavior are unresolved. Inherited raw `items` comparisons
can concern different index ranges after prefix-length changes. Keep the 21-Pepe
scope to bounded JSON OpenAPI subset comparisons, local references and explicit
review/refusal states. Full semantic/runtime compatibility proof is too broad.
The tool helps outside integration authors and duplicates no other line.

## Shared handoff and public trial

Joined line 4 TupleCheck to line 2 ZipSeal in **`shared/api_bundle/`**. New
`--tuples` / `tuples=True` selects the most inclusive analyzer; existing modes
remain available. Independent `--strict-layout` requires exact classic ZIP
coverage. Digest approval, directory bounds, safe paths and complete CRC/payload
inspection all precede tuple analysis. The same approved in-memory bytes feed
all checks. Nothing is extracted or executed from an archive.

Run **`python3 -B shared/api_bundle/tuple_demo.py`**. A hypothetical response
position expansion concealed behind an unchanged reference is reviewed by key
mode and identified as a potential break by tuple mode. Unchanged archives are
clean. This demonstrates analysis, not an observed public service change.
All **113 integration tests and nine demos** passed both in place and from an
isolated source-only copy. Nine new integration cases cover ordering, references,
variance, inherited findings, prefix/tail migration, dialect review, flags and
CLI exits, CRC/layout refusal, cancellation and limits. `SOURCES.json` records
all 22 vendored modules and their original/adapted hashes. All runtime code is
ordinary standard-library Python; no installation is required.

A read-only GET of `https://api.imd.fun/openapi.json` with User-Agent
`Pepeolithic-Gathering39/1.0` returned 23,132 bytes, SHA-256
`be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`,
on 2026-10-17. Strict approved-ZIP tuple mode compared five operations with zero
findings. The real description has no tuple positions, so this tests integration
rather than live tuple semantics. `public-trial-39.json` records the source and
validation results. No described API operation was called.

## Coins, scope and records

`COINS.md` says **none**: each capability already exists without another coin;
reward arithmetic uses ZTO first. No launch/deployment order is warranted and
nothing was sent. The lines remain different in kind. Each has a useful bounded
interpretation that fits 21 contributors; the overbroad extensions to avoid are
listed above. Existing goals were preserved verbatim in `dist/goals.json`.

Gathering mark **39**, “The Ordered Bowls”, adds three charcoal bowls with chalk
pebbles joined by red ochre on bare upper-right stone. It represents each value
retaining its checked place as work passes between workers. Built-in imagegen
produced isolated pigment; resampling and earth-pigment compositing changed
**4,530 pixels inside [965,65,175,55], zero outside**. Ancestral paintings,
including Pepe and both five-digit hands, remain unchanged. The full wall was
visually inspected: no writing, logos, borders or prohibited figures/symbols
observed. No unmet visual requirement observed; this is local review.

Finished wall: **1254 × 1254 RGB PNG**, `artifacts/gathering/wall-v20.png`, also
continuing through `wall.png`. JPEG: **512 × 512**, `dist/gathering/39.jpg`, below
100 KB. `39.json` has exactly the requested shape and the actual wall SHA-256
URL. `review-39.json` records formats, dimensions, prompt, inspection and limits;
`preservation-39.json` records pixel preservation. The inherited photographic
rock texture remains; fine pigment detail softens at thumbnail size.

`dist/index.html` includes every numbered record by line, painted records newest
first and placeholders separately. Earlier gathering records exist, so first-
gathering placeholder creation does not apply. No source, record or preview in
any line folder changed. Required PNG output remains untracked for the uploader.

## Source export repair

The rejected attempt exceeded 8 MiB. This round retains every required wall,
record, source and preview, and adds no dependencies, caches or package archives.
Rebuilt **17 gathering JPEG previews** directly from their original full PNGs at
quality 70, retaining 512 × 512 dimensions and all depicted marks. This saves
**422,808 bytes**. Earlier previews without a smaller replacement remain as they
were. JPEG encoding is lossy: fine pigment/rock texture softens. Full walls,
content-addressed records and every line preview remain unchanged. The finished
39 preview was visually inspected after compression. Source/new hashes,
dimensions and sizes are in `preview-compression-39.json`; the reproducible
build-only helper is `compact_previews_39.cjs` and uses the accepted local JPEG
encoder. `delivery-check-39.json` includes a local source tar.gz size trial;
packaging by the external uploader is outside this local check.
