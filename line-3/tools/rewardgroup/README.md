# RewardGroup

RewardGroup totals an existing exact ZTO allocation by team, work package or other caller-defined groups. It first recomputes the full contributor allocation against its request and token metadata. It then requires a complete disjoint partition: every contributor appears exactly once, including zero-unit contributors. It never reruns allocation on group weights, which can change who receives a rounding unit.

From the repository root, with Python 3.9+ and only the standard library:

```sh
python3 -B line-3/tools/rewardgroup/rewardgroup.py demo
```

Tried here: exit 0. Using the inherited real Ethereum ZTO metadata capture at block 26205319, the address-free illustrative demo totals build and review as **0.666666666666666667 ZTO**, and research as **0.333333333333333333 ZTO**. Together they retain exactly **1 ZTO**. This is historical metadata, not a fresh chain observation. No recipient or group address is invented.

For your own complete RewardSplit request and unmodified allocation report, create a policy JSON such as:

```json
{"groups":[{"id":"delivery","members":["build","review"]},{"id":"discovery","members":["research"]}]}
```

Then run:

```sh
python3 -B line-3/tools/rewardgroup/rewardgroup.py summarize --request REQUEST.json --report REPORT.json --policy POLICY.json --output SUMMARY.json
python3 -B line-3/tools/rewardgroup/rewardgroup.py verify --request REQUEST.json --report REPORT.json --policy POLICY.json --summary SUMMARY.json
```

Use `--metadata PATH` on both commands if allocation used another capture. Paths must resolve within the current working workspace. Inputs and outputs retain RewardSplit's 256 KiB JSON bound and outputs refuse overwrite. CLI exit 0 means complete verified arithmetic; exit 2 means refused input, mismatch or file error. Group IDs use the same 1–64 ASCII letter/digit/dot/underscore/hyphen form as contributor IDs. Empty groups, extra policy fields, overlapping memberships, omissions and unknown IDs refuse. No implicit remainder group exists.

Group rows are sorted by ASCII group ID, with sorted member IDs, exact integer units and decimal amounts, counts of inherited rounding awards, and counts of members without addresses. Counts of rounding awards describe the original allocation; they are not another distribution. The source receipt binds request, metadata and allocation canonical hashes. The policy hash binds the exact JSON value, including array order; rearranging the policy retains group totals but changes that hash. Verification recomputes the whole summary and emits its canonical SHA-256 receipt. Keep all four inputs with the summary.

A group total is an unsigned review subtotal, not a recipient, transfer, identity or entitlement. It establishes neither funds available nor payment. This tool does no network I/O and accesses no keys, wallet or environment settings. It depends on inherited sibling RewardReceipt and RewardSplit sources, all present in this repository.

Run the focused checks:

```sh
python3 -B line-3/tools/rewardgroup/selftest.py
```

Eleven tests passed, including 200 seeded exact rollups/coarsenings, uint256 maximum, fractional weights, omitted zero shares, malformed/overlapping partitions, changed source and summary data, type substitution, duplicate JSON keys, input bounds, file CLI verification and overwrite refusal. A one-atomic-unit test proves why summing existing contributor shares can differ from allocating to pooled group weights. Eight inherited RewardReceipt tests also passed. These are local checks, not independent certification.
