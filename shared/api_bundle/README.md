# API Bundle — approved ZIP snapshots and conservative OpenAPI comparison

Gathering 39 joins line 4 **TupleCheck** to line 2 **ZipSeal** in the existing
shared pipeline. `--tuples` (Python `tuples=True`) selects the most inclusive
analyzer, including key/map/dispatch and every earlier finding. Strict ZIP
layout remains independently opt-in. No installation or network is needed.

```sh
python3 -B shared/api_bundle/tuple_demo.py
python3 -B shared/api_bundle/tuple_selftest.py
```

Observed: the demo wraps the historical real IMD operation in approved ZIPs,
then hypothetically widens an enum behind an unchanged second-position tuple
reference. Earlier key mode retains review; tuple mode finds a potential
response break. Unchanged inputs are clean. This is an illustration, not a live
service change. Neither archive is extracted and no API operation is called.

For received workspace archives, run:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --tuples --strict-layout
```

Add `--old-sha256` / `--new-sha256` with independently reviewed actual digests to
bind approval to the exact in-memory bytes. Digest, directory bounds, strict
record coverage, safe paths and **every payload's CRC** precede analysis.
When several analyzer flags are supplied, `--tuples` wins. Existing modes and
positional Python arguments retain their behavior. Exits: 0 no detected break
in the modeled subset; 1 potential break; 2 refused input; 3 unresolved review.
Only exit 0 passes this static check; it does not certify runtime compatibility.

Tuple mode follows OpenAPI 3.1 effective `prefixItems` positions and `items`
fallbacks, resolving local references independently. It keeps the source bounds
of 64 prefix entries and 1,024 position/tail pairs. Remote references, malformed
visited schemas and exhausted bounds refuse. Older dialects retain review.
Position regions are conservative: lengths, `contains`, `unevaluatedItems`,
composition and reachability are not solved, and inherited raw `items` findings
may concern different index ranges when prefix lengths change.

All **113 shared integration tests and nine demos** passed in place and from an
isolated copy containing only this shared folder. Nine new checks exercise
reference targets, direction, dialect review, prefix/tail migration, retained
findings, flags and CLI exits, digest ordering, CRC/layout refusal before
analysis, cancellation and resource exhaustion. The 22 vendored ordinary Python
modules are recorded in `SOURCES.json`; TupleCheck changes only sibling import
and demonstration-capture paths. Line sources remain untouched.

A read-only GET of `https://api.imd.fun/openapi.json` with User-Agent
`Pepeolithic-Gathering39/1.0` returned 23,132 bytes on 2026-10-17, matching the
historical capture. Strict approved-ZIP tuple comparison found five common
operations and no findings. It visited zero tuple positions, so this checks
integration rather than live tuple semantics. Evidence: `gathering/public-trial-39.json`.

## Earlier API Bundle

Compare OpenAPI descriptions inside untrusted ZIPs without extracting or executing any member. Python 3.9+ and the standard library only. No installation, line folders, network or accounts are needed.

Current complete comparison: add `--keys` to include every supported
analyzer, including OpenAPI 3.1 object-key policies. Add `--strict-layout` to
require exact local ZIP record coverage before payload parsing. Try
`python3 -B shared/api_bundle/key_demo.py` for a fully offline example.
Earlier modes remain available;
the dated sections below describe how each part was added and its limits.

## Object-key policies and strict ZIP records (gathering 38)

Line 4 KeyCheck now works inside line 2 ZipSeal's optional structural gate.
Use `--keys` (Python: `keys=True`) for the most inclusive analyzer; this takes
precedence over earlier analyzer flags. Use `--strict-layout` (Python:
`strict_layout=True`) independently with any analyzer. Earlier flags and
their default archive policy retain their previous behavior.

```sh
python3 -B shared/api_bundle/key_demo.py
python3 -B shared/api_bundle/key_selftest.py
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --keys --strict-layout
```

Add the existing `--old-sha256` and `--new-sha256` options with actual reviewed
digests to require approved bytes. Approval precedes layout checks; layout,
directory/path limits and every payload/CRC check precede API analysis. Strict
mode checks local headers against the directory, descriptors, and contiguous
record coverage from byte zero, rejecting hidden gaps and overlaps. It uses
the same in-memory snapshot as payload inspection, without a pathname reread.
The report includes byte-accounting `layout` fields and
`strict_layout_checked: true` for each input. Nothing is extracted or executed.

The demo uses a saved real public IMD operation with hypothetical OpenAPI 3.1
key policies. An unchanged local reference hides an enum expansion from
`pending, done` to `pending, done, retry`. Map mode leaves review; key mode
finds a potential response-key break and retains reviews. A second trial
shows that even a correctly SHA-approved archive can contain an unclaimed
gap: the earlier gate accepts it, while strict layout refuses it before
API analysis. These are illustrative changes, not live service observations.

KeyCheck projects `propertyNames` onto string names: type, enum, const and
inclusive Unicode code-point length bounds. Request narrowing and response
widening are potential breaks. Pattern/format/composition/custom semantics
stay explicit review; unsupported dialects stay review. At most 1,024 key
pairs and 1,024 enum entries per visited policy are accepted. Remote targets,
malformed policies and exhausted budgets refuse the comparison. A projected
name may be unreachable under other object constraints; findings do not prove
whole-object or runtime incompatibility. All earlier limits still apply.

Strict layout is deliberately conservative classic stored/deflated ZIP
accounting, not a content-safety guarantee or operating-system sandbox.
Comments, extra fields and payloads remain byte containers. Hash approval
establishes byte identity, not publisher trust. Cooperative filesystem access
and cancellation/deadlines retain the limits described below. CLI exits stay
0 (no detected break within the subset), 1 (potential break), 2 (refusal),
3 (unresolved review). Review is not approval.

The folder carries all 21 vendored modules as ordinary source files, with
original and adapted hashes in `SOURCES.json`. The two new snapshots change
only sibling imports and demo-capture paths. No line folder is needed at
runtime; no installation, network, wallet or account is needed.

## Discriminator targets inside approved ZIPs (gathering 36)

Line 4's DispatchCheck now runs after line 2's ZIP approval, central-directory
gate and complete payload/CRC inspection. It compares the local target schema
behind each common explicit discriminator tag even when the mapping string did
not change. It retains the previous response-header, status, parameter,
destination, security and schema findings. No archive member is extracted or
executed, and no described API operation is called.

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --old-sha256 OLD_APPROVED_SHA256 --new-sha256 NEW_APPROVED_SHA256 --dispatch
python3 -B shared/api_bundle/dispatch_selftest.py
python3 -B shared/api_bundle/dispatch_demo.py
```

Replace the digest labels with independently reviewed SHA-256 hashes of your
archives. Python callers use `compare(..., dispatch=True)`. This most complete
mode takes precedence if older mode flags are also set; older flags keep their
existing behavior on their own. The demo uses the saved public IMD API
description with an invented response union. An unchanged `done` mapping points
to a target whose `receipt` type changes from string to integer. The previous
mode calls for review; dispatch mode identifies a potential branch-level break.
Unchanged approved inputs remain clean. The demo data does not describe a live
API change.

The analysis covers explicit common tags at inherited visited schema sites,
with local pointers or component schema names. Added/removed hints, tag-property
changes and coverage changes remain reviews. It does not infer implicit
dispatch, whole-union satisfiability, unreachable branches or remote targets.
The inherited limits and refusal states still apply: 64 mappings per visited
discriminator, 512 target pairs, 20,000 schema visits and 2,000 findings in
addition to the archive and operation limits below. A branch-level finding is
evidence to test against real clients, not proof of whole-union incompatibility.
`SOURCES.json` records the unmodified line source hash and the standalone
adapter hash.

Gathering 35 joins line 4's FallbackHeaders with the approved, bounded ZIP
snapshots from line 2. An exact `200` response can override a general `2XX`
response and silently omit a required header. This mode checks the headers of
both effective responses, reusing case folding, references and response-direction
schema rules. Required-header loss or relaxation is a potential break; optional
header loss and additions stay reviews. All earlier findings remain. Nothing
extracts or executes archive content, and no described API endpoint is called.

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --old-sha256 OLD_APPROVED_SHA256 --new-sha256 NEW_APPROVED_SHA256 --fallback-headers
python3 -B shared/api_bundle/fallback_selftest.py
```

Python callers use `compare(..., fallback_headers=True)`. This implies the
status, parameter, server and OAuth analyzers; with several flags, the most
complete selected mode wins. The new demo reports one potential break and
three reviews for invented response declarations on a saved public IMD path.
It compares unchanged inputs cleanly. Ten integration tests exercise digest,
CRC, cancellation and inventory refusals before analysis, header cases,
references, schema direction, grouping, inherited findings, determinism, resource
limits and all four CLI exits. All 80 tests and five demos also pass from a copy
containing only this shared folder. `SOURCES.json` records all 17 modules.

Limits stay conservative: common inline top-level operations, HTTP 100–599,
at most 40 common operations, 20,000 status visits and 20,000 header visits,
plus inherited schema/findings limits. These are cooperative analysis bounds,
not a hard process sandbox. Missing response coverage, links, broad metadata
and unsupported schema reasoning may still require review. This static analysis
cannot prove runtime compatibility or publisher trust. `--statuses` keeps its
previous behavior; the new header analysis is explicitly opt-in.

Gathering 29 adds line 4's OAuthCheck as an optional extension of the existing
line 2 ZIP gate and line 4 comparison pipeline. Add `--oauth` to compare
effective OAuth acquisition flows and endpoint references alongside the
existing schema and transport checks:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --old-sha256 OLD_APPROVED_SHA256 --new-sha256 NEW_APPROVED_SHA256 --oauth
```

Replace the digest labels with the actual reviewed ZIP digests. OAuth mode
validates effective OAuth flows and refuses unusable declarations. Its finding
is a potential integration break, not a live authorization test. Without
`--oauth`, the previous SchemeCheck behavior and report remain available.
The new vendored source is included in `SOURCES.json` and runs in this folder
without access to any line folder. The local suite now has **49 tests**;
its two new tests cover approved public-capture ZIPs with a hypothetical
OAuth token endpoint change, CLI exit 1, no extraction, and malformed-flow
refusal. No illustrative endpoint is contacted.

Run from a workspace root:

```sh
python3 -B shared/api_bundle/selftest.py
```

Gathering 28 result: **47 integration tests passed**, including six new transport
checks through approved archives: Bearer/Basic changes, API-key name/location,
header case, surviving OR alternatives, anonymous overrides, malformed effective
definitions, comparison limits and CLI refusal/review behavior. Earlier schema,
authentication, digest, CRC, resource and cancellation checks still pass.
All tests and the demo also pass from a workspace containing only this folder.
Scratch lives in `test/scratch/` and is never a runtime dependency.

For two archives you received:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --member openapi.json
```

Use caller-reviewed archive hashes to require the exact approved bytes:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --old-sha256 OLD_APPROVED_SHA256 --new-sha256 NEW_APPROVED_SHA256
```

For a cooperative archive-processing budget, add `--seconds 10`. The limit covers both archive snapshots, their inventories and payload reads, with checkpoints before and after comparison. It does not interrupt a single long schema-analysis call or impose an operating-system CPU limit. Python callers can pass a `cancelled` callback to `compare(...)`; no thread or signal handler is started.

Replace the uppercase argument labels with the real 64-character hex digests from your review process. They are not shipped example hashes. Obtain a snapshot's archive hash with SafeZip's inspect command or your own trusted hashing tool; the previous bundle report also includes it. A hash establishes byte identity, not publisher identity or safety. Approval is optional for backward compatibility; each input report says whether it was checked. An incorrect or malformed approval returns exit 2 before that archive's ZIP parsing. Comparison uses exactly the in-memory bytes that passed approval, so replacing the path after capture cannot swap the description.

Paths must be in the current workspace with no symlink components, and the exact selected member must exist in both ZIPs. JSON goes to stdout. Exit **0** means no detected breakage, **1** potential breaking change, **2** invalid input/error, **3** unresolved review. Only exit 0 passes this static check; it does not prove runtime compatibility.

The shared snapshot joins ZipGate and SafeZip (line 2) with ApiDelta, BoundCheck,
MultipleCheck, ConstCheck, UniqueCheck, DependCheck, AuthCheck, SchemeCheck and optional OAuthCheck (line 4). `vendor/` contains ordinary
source files; `SOURCES.json` records original/delivered hashes. SafeZip and
ApiDelta are byte-identical snapshots. Extensions only adapt sibling module and
demo capture paths to the shared layout. No line source was modified. Refresh
these copies deliberately and rerun tests when upstream changes.

Each archive is read once, at most 32 MiB. ZipGate walks its classic ZIP central
directory before Python's parser creates entry objects, bounding directory bytes
and entry count. The gate, parser and approval all see the same in-memory bytes.
Add `--directory-bytes 65536` (Python `directory_bytes=65536`) to change the
2,097,152-byte default per archive. Names, extras and member comments count;
the archive-wide comment is separately bounded by ZIP's field and archive limit.
The fixed 1,000-entry budget also applies before parsing. Invalid budgets fail
before reads; overflows fail before ZIP parsing. Returned `bundle_inputs` include
`preflight` counts for each archive. Gate success is only a prerequisite to all
remaining validation. Every member is validated for paths, types, compression, collisions and declared limits. Every file is streamed to check CRC, actual byte counts and SHA-256, including files not selected for comparison. Only the selected JSON is retained, at most 1 MiB. Nothing is extracted or imported from an archive. Inventories identify all checked files and selected-member/archive hashes.

BoundCheck adds numeric and size-bound findings: narrowing requests or widening responses can break clients. A hypothetical reduction of `clientNote.maxLength` from 160 to 80 in the captured real IMD API yields one breaking and one review finding through the ZIP flow. It is a synthetic upgrade, not an observed service change. Bound relaxations retain the base review findings. No comparison discards an unresolved review just because it recognizes a bound.

MultipleCheck adds rational `multipleOf` findings. It detects when a revised request rejects formerly accepted multiples or a revised response permits multiples that violate the old contract. In the included ZIP test, integer request `multipleOf` changing from 2 to 3 produces a breaking finding. The integer-only `multipleOf: 0.5` case is treated as equivalent to an unrestricted integer domain. Existing review findings remain visible.

ConstCheck adds fixed-value findings for OpenAPI 3.1: adding/changing a request
`const` or removing/changing a response `const` may break callers. It distinguishes
JSON booleans, null, strings and numbers, and preserves inherited review findings.
For OpenAPI 3.0 and cross-version changes, `const` remains an unresolved review.

UniqueCheck adds array-uniqueness findings for OpenAPI 3.0 and 3.1. Requiring
unique request items can reject old repeated values; dropping response
uniqueness can violate old consumers' expectations. Missing means false, visited
values must be JSON booleans, and both explicitly non-array schemas skip the
breaking rule. Inherited reviews remain even for relaxations. This does not
prove duplicate values are reachable under all other schema constraints.

DependCheck adds OpenAPI 3.1 `dependentRequired` findings. A new request
obligation such as `clientReference` requiring `clientContext` can reject an old
caller; removing an old response obligation can surprise consumers. It computes
transitive presence implications, including unconditional required seeds. Adding
an already implied edge creates no new dependency break, but retains the generic
review. OpenAPI 3.0/cross-version changes also remain reviews. Visited dependency
graphs are limited to 256 names and 1,024 edges; values must be unique-string
arrays. This does not prove object satisfiability under other constraints or
interpret `dependentSchemas`, conditionals or custom dialects.

Add `--nodes 200` (Python `compare(..., nodes=200)`) to bound distinct member
paths plus implicit parent directories in each archive. For example,
`docs/openapi.json` consumes two nodes even when the ZIP has one entry. Default:
32,000. Every member counts, including unselected files and empty directories.
The check runs during inventory before payload decompression. This limits the
inventory structure; no filesystem objects are extracted. Positive integers only;
invalid values fail before reading. The directory gate runs before parsing; the
filesystem-node inventory still runs after parsing.

See the complete offline flow with one command:

```sh
python3 -B shared/api_bundle/demo.py
```

Observed: hypothetically changing the captured HTTP Bearer definition to Basic
produces **six potential breaking findings and one retained review over five
operations**, including aliases of the changed definition. Reproducible ZIPs
carry approved SHA-256 hashes. An exact 63-byte directory budget and two-node
budget accept `docs/openapi.json`; a 62-byte directory budget and one-node
budget each refuse it. Nothing is extracted or executed. The demo exits 0 after
asserting its expected outcomes and cleans up disposable `test/scratch/` data.
This hypothetical revision does not claim the live API changed.

SchemeCheck additionally checks declared scheme type, API-key name/location and
HTTP authentication scheme for effective common-operation policies. API-key
header names and HTTP schemes compare without ASCII case; query/cookie names
compare exactly. A surviving OR alternative with compatible obligations and
transport can prevent a transport finding. Anonymous overrides remain public
in this symbolic model. Invalid supported fields in effective schemes fail even
when both documents are identical. No credential or actual authorization is
examined. In the default mode, OAuth flow URLs, OpenID discovery, TLS trust and
bearerFormat remain unresolved reviews; `--oauth` checks the declared flow URLs
and scopes described above. Nothing is fetched. Same-name schemes only; renames are not
inferred. An additional 100,000 transport-alternative comparison cap refuses
rather than returning a partial report.

AuthCheck compares effective operation/root authentication requirements as OR
alternatives of AND obligations. If an old alternative cannot satisfy any new
alternative with its declared schemes and scopes/roles, it reports a potential
break. Anonymous overrides, OpenAPI 3.0 OAuth scopes, and 3.1 roles are included;
malformed effective policies are refused even for identical documents. Earlier
schema findings and unresolved reviews remain. No credential is accepted or
examined, and no authentication is attempted. Scheme renames may conservatively
produce findings; scope hierarchies and actual grants are not inferred. Only
common operations' effective policies are analyzed. Limits: 64 alternatives,
32 schemes per alternative, 64 scope/role entries per scheme and 100,000
alternative comparisons. See the source's bounded symbolic model, not a claim
of live authorization or complete OpenAPI validation.

Limits: the gate is deliberately stricter than general ZIP readers. It rejects
ZIP64 central structures, multi-disk/prefixed/noncontiguous layouts, ambiguous
end records and trailing data; some valid archives will therefore be refused.
Local ZIP64 headers with classic central sizes may still pass the inherited
payload reader. This is input bounding, not an operating-system RAM/CPU sandbox.
Stored/deflated ZIPs, 1,000 entries, 16 MiB per file, 64 MiB total uncompressed, ratio 200, normalized portable names. Memory/CPU are not hard sandboxed; initial path access requires a cooperative local workspace. API analysis covers a bounded OpenAPI 3.0/3.1 subset and local object-member references. It does not fetch external references, fully validate schemas, model every constraint interaction or prove compatibility. MultipleCheck normalizes integer domains only when both sides are explicitly integer-only; other numeric precision follows ApiDelta's JSON float parser. Regexes, compositions and other unsupported semantics still need review. Description hashes cannot detect undocumented runtime changes.

A gathering-28 read-only GET of `https://api.imd.fun/openapi.json` on 2026-10-16 matched the bundled capture: 23,132 bytes, SHA-256 `be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`. Comparing approved ZIP snapshots with `--seconds 10` returned five operations and no findings. Only the public description GET was used; no payment or mutation endpoint or transaction was called. The bundled public capture is test/demo data, not required by the comparison CLI.

## Effective server destinations (gathering 30)

Add `--servers` to the existing CLI comparison to include line 4 ServerCheck.
The Python API accepts `servers=True`. This includes OAuth acquisition, security
transport and all earlier schema checks; `--oauth` alone and the default keep
their earlier behavior. No declared destination is contacted.

ServerCheck compares effective operation/path/root destination references,
bounded finite template domains and default selections. Missing old finite
destinations are potential breaks; open template coverage remains review.
It compares literal references, with no base resolution, URL normalization,
DNS, runtime behavior or full compatibility proof. Limits and conservative
refusals from ServerCheck and the archive gate remain in force.

Run `python3 -B shared/api_bundle/server_demo.py` from the repository root.
Observed: a hypothetical operation destination change in the historical public
IMD capture produces a destination-removal finding through two SHA-approved
ZIPs. Unchanged capture comparison is clean. Nothing is extracted or sent.
`python3 -B shared/api_bundle/selftest.py` passed 53 tests, including four new
server/archive integrations. The standalone folder contains every dependency
as ordinary Python source; `SOURCES.json` records original and adapted hashes.

## Parameter encodings and generated-client handoffs (gathering 33)

Use `--parameters` (Python: `parameters=True`) to include line 4's ParamCheck,
HeaderCheck and IdCheck alongside all server, OAuth, transport and schema
checks. Existing default, `--oauth`, and `--servers` modes retain their scope.

```sh
python3 -B shared/api_bundle/parameter_demo.py
python3 -B shared/api_bundle/parameter_selftest.py
```

The demo adds an illustrative array query parameter to the saved public IMD
API description, then hypothetically changes repeated keys to comma-separated
values. It compares two SHA-approved ZIPs without extraction or network access,
finds `parameter_wire_explode_changed`, and retains inherited reviews. The
unchanged ZIP comparison is clean. These invented parameter declarations are
explicit test inputs, not claims about the live service. All files needed by
these commands are ordinary files in this folder.

For received archives, use the existing positional paths and approval flags
with `--parameters`. The flag compares effective `style`, `explode` and query
`allowReserved`, parameter content schemas, response-header guarantees, and
operation identifiers used by generated clients. It includes all earlier
analyzers. It never serializes or sends a request, authenticates, follows a
reference over the network, or extracts/executes archive members. JSON output
and CLI exits stay 0 (no detected breakage), 1 (potential break), 2 (invalid
input), 3 (unresolved review). Review-only output is not a pass.

Observed in gathering 33: 53 existing integration tests and eight new tests
passed from an isolated copy containing only this folder. New tests cover
unchanged public capture, wire defaults and changes, retained ID/header/server
findings, malformed unchanged declarations, approval and directory checks
before analysis, CRC checking of an unselected file, and all CLI exits.
The three vendored analyzer snapshots have only sibling-import and demo-capture
path adaptations; `SOURCES.json` records their source and delivered hashes.

Limits remain conservative: a changed wire setting is a possible break, not
proof that an old concrete request fails. No percent-encoding, parser quirks,
style/type legality, runtime API behavior or full schema satisfiability is
proved. The extension allows 20,000 effective parameter visits and inherits
header/identifier, schema, finding, document and archive limits. Exceeding a
limit refuses the whole comparison. All earlier unsupported-case reviews
remain. Headers compare names without ASCII case; identifier renames are
potential generated-client breaks even if an HTTP operation still works.

A read-only GET on 2026-10-17 with User-Agent `Pepeolithic-Gathering/33.0`
returned the same 23,132-byte public description as the historical capture,
SHA-256 `be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`.
Comparing the approved archive snapshots with `parameters=True` found five
operations and no findings. This checks the published description, not service
behavior. No described API operation was called.

## Response status fallbacks (gathering 34)

Use `--statuses` (Python: `statuses=True`) to include line 4's StatusCheck in
the line 2 archive boundary. It includes parameter, header, identifier, server,
OAuth, transport and schema checks. Earlier flags retain their previous scope.
All dependencies remain ordinary files in this folder; no installation or
line directory is needed. `SOURCES.json` records the source and adapted hashes.

```sh
python3 -B shared/api_bundle/status_demo.py
python3 -B shared/api_bundle/status_selftest.py
```

The offline demo changes the saved public IMD quote operation's response
declarations hypothetically: a `2XX` string response acquires an explicit `200`
integer response. Two SHA-approved ZIP snapshots are compared without extraction
or network access. Previous parameter mode reports review; status mode finds one
potential schema break and retains two reviews. Its selector group identifies
exactly HTTP 200, and an unchanged comparison is clean. These illustrative
response declarations are not observations of the public service.

For received archives, add `--statuses` to the usual comparison command:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --member openapi.json --statuses
```

Add the existing `--old-sha256` and `--new-sha256` flags with your reviewed archive
digests when byte approval is required. The report retains archive/member hashes,
CRC checks and inventories. Exit codes remain 0 (no detected breakage), 1
(potential break), 2 (invalid input), and 3 (unresolved review); only 0 passes
this static check. Combining earlier extension flags with `--statuses` selects
the full status analyzer.

For common inline top-level operations, status mode checks each HTTP code
100–599 using exact code, uppercase class range, then `default` precedence.
When selectors differ, inherited response-direction schema checks compare the
effective declarations. `selector_groups` lists the concrete affected codes.
Status remapping and lost description coverage retain reviews because actual
status emission and client dispatch are unknown. Headers and links across
different selector keys receive a broad metadata review; they are not individually
analyzed across those keys. Nothing is fetched, serialized into a request, or sent.

The extension allows 20,000 status visits (40 common operations) and inherits
all document, schema, finding and archive budgets. Invalid unchanged selectors,
external response references, malformed response objects and exhausted budgets
refuse the comparison. This is bounded static analysis, not full OpenAPI validation
or a proof of runtime compatibility.

Observed in gathering 34: all **70 integration tests** passed, including nine
new status/archive tests, and they passed again from an isolated copy of this
folder. The new tests cover exact/range/default selection, response direction,
lost coverage, local references, invalid unchanged declarations, inherited
findings, all CLI exits, previous-mode compatibility, archive refusal before
analysis and status-budget refusal. The demo also passed in isolation.

The public description captured on 2026-10-17 by gathering 34 remains 23,132 bytes,
SHA-256 `be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`.
An approved-ZIP comparison against the bundled historical capture with
`statuses=True` found five common operations, 2,500 status visits and no findings.
Only the public-description GET supplied by gathering was used; the shared
comparison and all demonstrations were offline.


## Map-value schemas (gathering 37)

Use `--maps` (Python: `maps=True`) to inspect the schemas governing
`additionalProperties` values. This includes DispatchCheck and every earlier
analyzer; earlier flags keep their previous scope. The MapCheck source is
copied from line 4 with only sibling import and demo-capture path adaptations.
Line 2's updated ZipGate snapshot also records whole-archive captured bytes
when its `process` API is used. `SOURCES.json` identifies all 19 source snapshots.

```sh
python3 -B shared/api_bundle/map_demo.py
python3 -B shared/api_bundle/map_selftest.py
```

The demo wraps a saved public IMD API operation in two SHA-approved ZIPs. Its
hypothetical response map keeps the same local value reference while the
referenced integer enum grows from `[1, 2]` to `[1, 2, 3]`. Dispatch mode leaves
a component-change review; map mode finds one potential response break at
`additionalProperties/enum` and retains that review. Unchanged input is clean.
This is illustrative schema data, not an observed service change. No archive
member is extracted or executed, no external reference is fetched, and no
API operation is invoked. Temporary demonstration archives live in
`test/scratch/` and are removed automatically.

For received archives:

```sh
python3 -B shared/api_bundle/api_bundle.py old.zip new.zip --member openapi.json --maps
```

Add `--old-sha256` and `--new-sha256` with the digests you reviewed to bind the
comparison to approved archive bytes. Approval, directory budgets, path checks,
complete payload/CRC inspection and all earlier limits precede map analysis.
When flags are combined, `--maps` selects the most inclusive analyzer. Exits
remain 0 (no detected break within the subset), 1 (potential break), 2 (refusal),
and 3 (unresolved review). A review is not approval.

Map mode compares request narrowing and response widening, true/omitted/closed
policies, and independently resolved local value targets. It traverses nested
maps, inherited schema sites, explicit discriminator targets and remapped
response headers. At most 1,024 nontrivial map pairs are accepted; exhaustion
refuses the comparison. Findings concern a potentially used map-value region,
not whole-schema implication. Named-key migrations, `patternProperties`,
composition, reachability and live server behavior remain unresolved. All
inherited review findings remain. Descriptions and content hashes establish
neither publisher trust nor runtime compatibility.

Observed in gathering 37: all 93 integration tests and seven demos passed both
in place and in a standalone copy containing only this folder. The eight new
integration tests cover unchanged captures, unchanged references with changed
targets, request/response policy direction, status-remapped headers, retained
reviews, all CLI exits and flag precedence, malformed/remote values, budget
refusals, CRC failure on an unselected member before analysis, and ZipGate's
whole-snapshot count including final comments. No installation is needed.

A read-only public-description GET on 2026-10-17 with User-Agent
`Pepeolithic-Gathering37/1.0` returned 23,132 bytes, SHA-256
`be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`.
An approved-ZIP comparison against the historical capture in map mode found
five common operations and no findings. This checks the published description;
no described operation or transaction was sent.
