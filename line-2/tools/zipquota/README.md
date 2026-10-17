# ZipQuota — separate limits for each top-level path

ZipQuota extracts an untrusted ZIP only when every member belongs to an
approved top-level root and each root stays within its own file, byte and
filesystem-node quota. It counts implicit parent directories as nodes. A
general package can therefore admit a large `api/` tree while giving a small
`notes.txt` root much less room. The inherited ZipSeal, ZipGate and SafeZip
checks still validate the complete archive, strict local-record layout, paths,
special file types, compression, payloads, CRCs and global resource limits.
Python 3.9+ standard library only; keep those sibling tool folders with it.

From the repository root, run this one command to see it work:

```sh
python3 -B line-2/tools/zipquota/demo.py
```

Tried here: the demo packed the shipped historical public IMD OpenAPI capture
(23,132 bytes, SHA-256
`be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`)
under `api/` with a short `notes.txt`. It extracted both byte-identically at
their exact separate quotas. Lowering only the `api` byte quota by one refused
the same archive without creating the destination. This is an offline replay of
public data, not a fresh network observation. No archive content is executed.

## Policy and use

A trusted JSON policy has this exact form:

```json
{"roots":[{"name":"api","files":1,"bytes":23132,"nodes":2},{"name":"notes.txt","files":1,"bytes":19,"nodes":1}]}
```

Each name is one safe top-level path segment. Every ZIP member must be under
exactly one listed root. Quotas are maxima; zero is allowed. A root may be a
single file or a directory tree. Nodes include all distinct files and both
explicit and implicit directories under the root. Missing listed roots are
allowed. Root names cannot collide after Unicode case folding. Unknown or
duplicate JSON keys are refused. The policy itself has a 64 KiB default cap.
Obtain it independently of the untrusted ZIP when its approval matters.

```sh
python3 -B line-2/tools/zipquota/zipquota.py inspect input.zip policy.json --sha256 REVIEWED_ARCHIVE_SHA256
python3 -B line-2/tools/zipquota/zipquota.py extract input.zip policy.json unpacked --sha256 REVIEWED_ARCHIVE_SHA256
```

All input, policy and output paths must stay inside the current workspace with
no existing symlink component. Extraction requires an absent destination with
an existing parent. Success exits 0 and prints the complete checked inventory,
archive digest, policy digest, strict layout counts and per-root usage. Refusal
exits 2, prints `ok: false`, and leaves no new destination. The approved archive
digest binds inspection to the later extraction pass; if the source changes,
publication is refused. `process(archive, policy, output=None, ...)` is the
Python API. `--policy-bytes`, `--entries`, `--directory-bytes`,
`--archive-bytes`, `--nodes`, `--file-bytes`, `--total-bytes`, `--ratio` and
`--seconds` provide additional global caps. The cooperative deadline is shared
across policy read, inspection and extraction. The API also accepts a
cooperative `cancelled` callback. Whole-archive defaults match ZipSeal's
documented limits.

Run `python3 -B line-2/tools/zipquota/selftest.py` for the 16 focused checks.
They passed after repairing one expected-error assertion. Cases include exact
limits, unapproved roots, implicit nodes, duplicate and unsafe policy names,
bounded policy read, digest approval, source replacement, hidden ZIP bytes,
cancellation and existing-output preservation.

This tool enforces path and resource quotas, not publisher identity or whether
extracted files are safe to execute. Strict classic ZIP and cooperative
filesystem limitations are inherited from ZipSeal. Time and memory limits are
cooperative or logical, not operating-system reservations. No coin, wallet,
payment or transaction is needed for local extraction.
