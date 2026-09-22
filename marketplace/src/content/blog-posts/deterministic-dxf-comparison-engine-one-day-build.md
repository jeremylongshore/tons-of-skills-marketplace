---
title: "Building a Deterministic DXF Comparison Engine in One Day"
description: "Four PRs and 5000+ lines. How to compare two versions of an engineering drawing when the coordinates might be slightly different."
date: "2026-02-26"
tags: ["ai-agents", "python", "testing", "architecture", "cad"]
featured: false
canonical: "https://startaitools.com/posts/deterministic-dxf-comparison-engine-one-day-build/"
---
How do you compare two versions of an engineering drawing when one has been translated, rotated, or just has slightly different coordinate precision?

This is the core problem in [cad-dxf-agent](https://github.com/jeremylongshore/cad-dxf-agent). The AI edit pipeline produces a modified DXF file, but you need to tell the user *exactly* what changed — which entities moved, which were added, which were deleted. And you need to do it deterministically, with confidence scores, even when floating-point noise makes coordinates drift by 0.0001 inches.

I shipped the complete solution in four PRs across one day. Here's how each layer builds on the last.

## E1: Canonical Model + Stable Entity IDs

The first problem is identity. DXF files don't have stable entity IDs — handles can change between saves, and there's no built-in concept of "this LINE in file A is the same LINE in file B."

I audited every entity identity path and found six gaps: no stable IDs, no disambiguation, no coordinate normalization, no quantization, no spatial binning, no deterministic ordering. All six had to be solved together.

The foundation is `QuantizationConfig`:

```python
@dataclass
class QuantizationConfig:
    decimal_places: int = 4          # 0.00005" precision
    epsilon: float = 0.0001          # coordinate comparison tolerance
    spatial_bin_size: float = 0.25   # inches — groups nearby entities
```

Every coordinate in the system passes through quantization before anything else. Two points that differ by less than epsilon land in the same spatial bin.

Next: geometry normalization. A LINE from (0,0) to (5,5) and a LINE from (5,5) to (0,0) are the same entity. Polyline vertices get deduplicated. Everything gets a canonical direction.

The key abstraction is `GeometrySignature` — a noise-tolerant fingerprint for each entity type:

```python
class GeometrySignature:
    """Noise-tolerant matching signature for DXF entities."""

    @staticmethod
    def for_line(entity) -> str:
        length = quantize(entity.length)
        angle = quantize_angle(entity.angle)
        mid = spatial_bin(entity.midpoint)
        return f"LINE|{length}|{angle}|{mid}"

    @staticmethod
    def for_polyline(entity) -> str:
        vcount = len(entity.vertices)
        perimeter = quantize(entity.perimeter)
        turn_hash = hash_turn_angles(entity.vertices)
        return f"POLYLINE|{vcount}|{perimeter}|{turn_hash}"

    @staticmethod
    def for_circle(entity) -> str:
        radius = quantize(entity.radius)
        center = spatial_bin(entity.center)
        return f"CIRCLE|{radius}|{center}"

    @staticmethod
    def for_insert(entity) -> str:
        attribs = sorted_attrib_hash(entity.attribs)
        return f"INSERT|{entity.block_name}|{attribs}"
```

Stable IDs are a hash of signature + spatial bin + layer + entity type. When two entities collide (same signature, same bin), they get `#N` suffixes sorted by centroid position. Deterministic, reproducible, no randomness anywhere.

82 canonical tests, 176 comparison tests. All green.

## E2: Alignment Ladder with Kabsch Rigid Transform

Stable IDs only work if both files share the same coordinate system. In practice, one drawing might be offset by (100, 200) or rotated 15 degrees. You need to align them first.

The alignment ladder tries three strategies in order:

**1. Anchor-based alignment.** If both files share INSERT blocks (title blocks, drawing borders, standard symbols), use those as anchor points. Find the rigid transform that maps anchors in file A to their counterparts in file B using the Kabsch algorithm — SVD decomposition to find optimal rotation + translation:

```python
def kabsch_align(source_points, target_points):
    """SVD-based rigid alignment. Returns rotation matrix + translation."""
    src_centroid = np.mean(source_points, axis=0)
    tgt_centroid = np.mean(target_points, axis=0)

    src_centered = source_points - src_centroid
    tgt_centered = target_points - tgt_centroid

    H = src_centered.T @ tgt_centered
    U, S, Vt = np.linalg.svd(H)

    d = np.linalg.det(Vt.T @ U.T)
    sign_matrix = np.diag([1, 1, np.sign(d)])

    rotation = Vt.T @ sign_matrix @ U.T
    translation = tgt_centroid - rotation @ src_centroid
    return rotation, translation
```

**2. Feature-based alignment.** No shared anchors? Fall back to RANSAC with a deterministic seed. Sample point correspondences, fit transforms, reject outliers, keep the best.

**3. Identity.** If alignment quality is too low, skip it and report that the files can't be reliably compared. Better to say "I don't know" than to produce garbage matches.

Each alignment gets a quality score: RMS residual, overlap ratio, inlier count, combined confidence. The ladder picks the highest-confidence result.

1,624 insertions across 9 files. 814 tests pass.

## E3: Confidence-Scored Matching Pipeline

With entities identified and files aligned, you need to match entities across the two files. Not just "same or different" — you need confidence scores so the UI can flag ambiguous matches.

Three match methods, tried in priority order:

```python
class MatchMethod(Enum):
    FINGERPRINT = "fingerprint"   # exact stable_id match
    SIGNATURE = "signature"       # geometry signature match
    SPATIAL = "spatial"           # nearest-neighbor within tolerance
```

Per-type scoring handles the specifics. INSERT matching uses block name equality + Jaccard similarity on attributes + spatial proximity. Geometry matching compares signatures component by component. TEXT matching uses Levenshtein distance on content + position proximity.

The matcher runs greedy best-match picking: sort all candidate pairs by score, pick the best, remove both entities from the pool, repeat. But it also tracks the runner-up for each match — if the best and second-best scores are close, that match gets flagged as ambiguous.

```python
@dataclass
class MatchResult:
    source_id: str
    target_id: str
    confidence: float          # 0.0 to 1.0
    method: MatchMethod
    runner_up_score: float     # ambiguity detection
    is_ambiguous: bool         # confidence - runner_up < threshold
```

26 new scorer tests, 743 total pass.

## E4: Apply Approved Changes + Export Bundle

The last layer converts matched pairs into actionable operations. Each `EntityChange` (added, deleted, modified, moved) becomes a `RevisionOp` — but only if the confidence score exceeds the approval threshold.

Operations execute in a fixed order: modify → move → delete → add. This ordering matters. If you delete before modifying, you might delete an entity that was supposed to be updated. If you add before deleting, you might create ID collisions.

```python
class RevisionApplier:
    OPERATION_ORDER = ["modify", "move", "delete", "add"]

    def apply(self, ops: list[RevisionOp], dxf_doc) -> ApplyResult:
        sorted_ops = sorted(ops, key=lambda o: self.OPERATION_ORDER.index(o.op_type))
        results = []
        for op in sorted_ops:
            if op.confidence < self.min_confidence:
                results.append(Skip(op, reason="below confidence threshold"))
                continue
            results.append(self._execute(op, dxf_doc))
        return ApplyResult(results)
```

Bundle export packages the result: original DXF, modified DXF, change manifest, and optional dry-run mode that shows what *would* change without modifying anything.

During PR review, the overlay and changelog rendering got delegated back to `ComparisonEngine` instead of living in the applier — cleaner separation of concerns.

54 new tests. 1,875 insertions across 11 files. All green.

## The Numbers

| Metric | Value |
|--------|-------|
| PRs merged | 4 (#47–#50) |
| Lines added | ~5,000+ |
| Time | 1 day |
| Flaky tests | 0 (deterministic by design) |

Zero flaky tests is the direct payoff of the quantization/binning strategy. No floating-point comparison anywhere in the test suite depends on exact equality. Everything goes through epsilon-tolerant comparison or spatial bins.

## Sidebar: OTel Deadlocking Login

While the comparison engine was building, I hit an unrelated nightmare in [hustle](https://github.com/jeremylongshore/hustle) (a sports management app). Login was hanging — no timeout, no error, just an infinite spinner.

The culprit: OpenTelemetry auto-instrumentations for `undici` and `gRPC` were deadlocking the Firebase Auth session flow. The undici instrumentation wraps `fetch()`, and the gRPC instrumentation wraps Firestore client calls. When the login handler calls both in sequence — authenticate via Firebase Auth, then read the user profile from Firestore — the instrumentation layers created a circular wait.

Fix was surgical: disable the specific instrumentations rather than ripping out OTel entirely.

```javascript
// Before: blanket auto-instrumentation
registerInstrumentations({ instrumentations: [getNodeAutoInstrumentations()] });

// After: skip the problematic ones
registerInstrumentations({
  instrumentations: [getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-undici': { enabled: false },
    '@opentelemetry/instrumentation-grpc': { enabled: false },
  })],
});
```

Found it by adding a single `console.log` to the session handler and watching which line it never got past. Sometimes the oldest debugging tool is the right one.

## What Made This Possible

Four PRs of this density in a single day only works because each layer has a clean contract with the next. E1 produces stable IDs. E2 aligns coordinate systems. E3 matches entities. E4 applies changes. No layer reaches into another's internals.

The test count matters less than the test *design* — every test is deterministic, every boundary condition has explicit coverage, and the quantization config is injected so tests can use tighter or looser tolerances as needed.

The comparison engine is the foundation for everything cad-dxf-agent does next: visual diffs, change summaries in natural language, and confidence-gated automated approval of AI-planned edits.

---

*Related posts:*

- [The Silent Killer: How Bare catch {} Blocks Hide Failures](/blog/silent-killer-bare-catch-blocks-hide-failures/) — the previous cad-dxf-agent deep-dive on debugging invisible frontend failures
- [Production Release Engineering: Shipping v4.5.0](/blog/production-release-engineering-v450/) — automated release workflows and safety gates at scale
- [Python Class Identity Mismatch: The CI Bug That Broke 9 PRs](/blog/python-class-identity-mismatch-ci-debugging-guide/) — another case where identity semantics caused subtle breakage
