# Planseal

Carry a complete offline dependency plan, its task estimates, handoff deadlines,
shared resource limits, worker count and budget in one bounded JSON document.
A recipient checks an independently supplied SHA-256 and recomputes feasibility
using the existing Plancheck, Gatecheck and Lockcheck validators. No saved
approval or planner claim is trusted. Python 3.10+, standard library only.

One command from the repository root shows it working:

```sh
python3 -B line-1/tools/planseal/planseal.py demo
```

Observed here: three tasks finish at minute 6 with two workers and one shared
GPU; review meets its minute-3 handoff exactly. All checks pass. Rechecking
against a recipient budget of 5 fails, even with the original matching digest.
The bundled constraints cannot silently replace the recipient's worker count
and budget. This is offline feasibility at estimates, not task execution.

## Make and receive a handoff

Create a bundle from existing planner/checker JSON files. The shell redirection
below writes a file; Planseal itself writes only stdout and stderr.

```sh
python3 -B line-1/tools/gatelock/gatelock.py --demo --plan-only > line-1/tools/planseal/example-plan.json
python3 -B line-1/tools/planseal/planseal.py pack --tasks line-1/tools/gatelock/tasks.json --plan line-1/tools/planseal/example-plan.json --gates line-1/tools/gatelock/gates.json --limits line-1/tools/gatelock/limits.json --workers 2 --budget 6 > line-1/tools/planseal/bundle.json
```

`pack` emits only the bundle on stdout and its lowercase SHA-256 on stderr.
Give the recipient that digest through a channel they trust. Then run, replacing
`EXPECTED_DIGEST` with the received digest:

```sh
python3 -B line-1/tools/planseal/planseal.py verify --bundle line-1/tools/planseal/bundle.json --sha256 EXPECTED_DIGEST --workers 2 --budget 6
```

The bundle has exactly `schema` (`planseal/1`), `tasks`, `plan`, `gates`, `limits`,
`workers` and `budget`. The four data objects use the existing validators'
schemas. Plan fields are limited to `workers`, `finish`, `schedule` and optional
`units`; strip unrelated planner commentary before packaging. Gates and resources
are required. Supply their real constraints; do not invent a resource to satisfy
the schema. Tasks are labels and are never executed.

All files must be ordinary workspace-local JSON, at most 100,000 bytes, with
duplicate keys rejected. The complete encoded bundle must also fit 100,000 bytes.
Inherited bounds: 1–500 tasks, 1–64 workers/resources, 1–500 gates, positive
durations, positive integer resource units up to one billion, finite decimal
numbers with at most 100 coefficient digits and exponent magnitude 100.
The final budget is required and nonnegative. Numeric time tokens stay numeric
and exact; resource capacities, demands and worker IDs must be JSON integers.

Digest input is the versioned encoding produced by `encode`: sorted object keys,
no extra whitespace, ASCII JSON escapes, original array order and Python's exact
bounded decimal spelling. Trailing file newline and JSON whitespace are ignored
on parsing; object order does not matter. Array order and `1` versus `1.0` do
matter. This is a documented Python wire format, not RFC 8785/JCS or a semantic
graph hash. Never substitute the raw file's SHA-256 for this canonical digest.

Digest mismatch refuses before schedule validation. A matching digest still
requires recomputation of every bundled constraint and a second schedule check
against the recipient's explicit worker count and deadline. Recipient worker
count must match the plan exactly, including unused worker slots. Exit 0 means
all checks passed, 2 means a well-formed matching bundle failed feasibility, and
1 means malformed input, digest mismatch or a refused pack. Argparse syntax
errors use exit 2. No partial bundle is emitted on a failed pack.

## Checks and limits

```sh
python3 -B line-1/tools/planseal/selftest.py
```

Observed: 13 tests passed, including 120 seeded dependency chains with exact
handoff boundaries and tighter-deadline refusals, digest-first ordering, tamper
rechecks, resource conflicts, invalid packing, duplicate keys, CLI exits,
canonical encoding, independent snapshots and 100-digit/exponent numeric
round-trips. Plancheck's unchanged 15 tests also passed. These are local checks.

Keep sibling `plancheck/`, `gatecheck/` and `lockcheck/` with this folder. The
bundle is portable data; verification requires these Python sources. No network,
installation, clock, environment read, wallet, key, payment, signature, transaction
or task execution occurs. A digest supplies integrity relative to a separately
trusted value, not identity or authorization. An attacker replacing both digest
and data can change the declared graph, gates and capacities. Recipients must
review those assumptions and know what work is mandatory. Results establish
neither optimality nor real availability, durations, actual completion or safe
execution of the labels.
