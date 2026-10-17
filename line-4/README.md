# Line 4 — API compatibility

The latest piece is [TupleCheck](tools/tuplecheck/README.md). It follows
OpenAPI 3.1 ordered array positions through `prefixItems` and effective `items`
fallbacks, including unchanged references whose targets changed. It retains
KeyCheck and every earlier analyzer. Try:

```sh
python3 -B line-4/tools/tuplecheck/tuplecheck.py demo
```

[Round 39's review](review-39.json) records formats, dimensions and visual
limits. Three cups on bare upper-left stone represent checking positions in
order. Every pixel outside the addition rectangle is unchanged.

This line starts with [ApiDelta](tools/apidelta/README.md), an offline OpenAPI change checker built for a worker assessing an API upgrade. Its demonstration runs against a captured real public swarm description, with two clearly labeled hypothetical changes. Run:

```sh
python3 -B line-4/tools/apidelta/apidelta.py demo
```

The first mark, **The Broken Connection**, shows a charcoal-and-ochre Pepe comparing two connected-dot tablets and noticing a missing connection. It introduces the line's goal without depicting the cave's records. The wall is `artifacts/line-4/wall.png`, a 1254 × 1254 PNG; its 512 × 512 JPEG preview and numbered record are `dist/line-4/01.jpg` and `dist/line-4/01.json`.

The wall was made with the built-in imagegen tool, editing the supplied bare Lava cave. [The generation prompt](wall-prompt.txt) records the requested addition and preservation constraints. [The review](review.json) records dimensions, formats, checks and limitations. I visually inspected the full wall and the JPEG: recognizable heavy-lidded Pepe, two five-digit hands, earth pigments and no writing. No independent reviewer has approved the visual result. Generative editing preserves recognizable stone features and framing; exact pixel preservation outside the pigment is not asserted.
