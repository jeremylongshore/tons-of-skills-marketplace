---
title: "Versioned Scoring Rules for a Reproducible Published Index"
description: "Store raw facets, give each scoring rule a content-hashed id, pin each date to its rules, and refuse overwrites so index reruns stay reproducible."
date: "2026-11-20"
tags: ["data-engineering", "reproducibility", "architecture", "testing", "stci", "python"]
featured: false
canonical: "https://startaitools.com/posts/store-facets-not-grades-rerun-safe-index/"
---
If you publish a scored dataset every day, the scoring rule will change, and the first rerun after that change can quietly rewrite every date you already published. This is how I restructured a daily token price index so rules can change without touching history: keep the raw facts (facets, the attributes each seller reports about itself), version the rules as entries identified by a hash of their content, pin each date to the rulebook in force that day, and refuse overwrites.

The dataset is STCI (the Standardized Token Cost Index), a daily index of what open-weight models (models whose weights anyone can download and host) cost per token across providers. It was first built in one day, as [STCI Zero to v0.1.0](https://startaitools.com/posts/stci-zero-to-v010-token-cost-index/). Each published day carries a verification hash, which makes the file tamper-evident: anyone can check that it has not been altered. That hash is the thing a careless rule change breaks.

## The problem: a stored grade freezes yesterday's rule into the data

The previous day's data showed one open-weight model priced 16.08x apart across endpoints (separately priced deployments of the same model). The spread record is in [the 16.08x post](https://startaitools.com/posts/same-model-different-price-open-weight-spread/). The obvious follow-up question was whether the cheap endpoints are cheap because they serve a lower precision (fewer bits per model weight). The first plan was to grade each endpoint A, B or C from the precision the provider reports, and write that grade into the daily file.

Two read-only plan reviews (an ML review and a data-model review) rejected that plan before any code was written. Their reasons are the core of this post.

The ML review attacked the input. Between 30 and 40 percent of endpoints report precision as the literal string `unknown`. On the flagship example it was 19 of 50. Folding those into "Grade C" grades reporting hygiene, not tokens. The precision ladder is also wrong per model: fp8 is the native release precision for DeepSeek, gpt-oss ships mxfp4, and Kimi K2 ships int4. A rule like "fp8 means B" would penalize models for shipping exactly as their authors released them.

The data-model review attacked the storage. A grade written at collection time is a frozen copy of whatever rule existed that morning. When the rule changes, you cannot recompute old grades, because the facts that produced them were thrown away. Your only options are to leave stale verdicts in place or to rewrite history.

So the methodology doc now opens with one line: STCI measures; it does not judge.

## The approach: four changes in methodology 2.1.0

Methodology 2.1.0 shipped with four pieces. Each one closes a specific failure.

### 1. A private, hashed snapshot of the raw facts

For every model that clears the endpoint minimum, the collector keeps one row per priced endpoint: model id, provider, tag, quantization, context length, max completion tokens, sorted supported parameters, and the three prices as the source's own strings. Rows are written as canonical JSON (sorted keys, no spaces) to a private, git-ignored file per date. The file is never published. Its SHA-256 is.

That split matters. The raw rows stay available for re-derivation. The public file commits to them through `endpoint_snapshot_sha256`, so a later rerun can prove it started from the same facts.

Uptime, throughput and latency move minute to minute, so they live in a separate `observed` block that no hash covers and the public site never shows. If they were hashed, two honest runs a minute apart would disagree.

### 2. Facet cells instead of verdicts

Per model, endpoints are cut into cells by three facets:

- **precision** as reported, with missing or `unknown` as its own `undisclosed` bucket, never folded into a named precision
- **context bucket**: `<=32k`, `32-128k`, `128k+`, `1M+`, or `unknown`
- **tools**: true when the endpoint's supported parameters include `tools`

Each cell reports `n`, min, p25, median, p75, max and the p75/p25 ratio of the blended price. Below three endpoints the statistics are null and `n` is still reported. A dated snapshot id such as a `-1017` suffix is a different model from the undated id and is never pooled with it.

None of this is a judgment. It is what the endpoints say about themselves, cut so a reader can compare like with like.

### 3. Rules as append-only, content-hashed entries

Rules live in one append-only YAML file. As shipped, it holds a single entry:

```yaml
rules:
  - effective_from: "2026-11-20"
    view: disclosed_vs_undisclosed_precision
    # Precision values that count as undisclosed. Everything else a provider
    # reports (fp8, fp4, mxfp4, nvfp4, int4, bf16, fp16, ...) is disclosed.
    undisclosed_values: [undisclosed]
```

The entry is dated 2026-11-20, but a rule only enters the output from methodology 2.1.0, whose first date is 2026-11-21. The 2026-11-20 index itself runs under 2.0.0 and carries no rule id.

There are no A/B/C grades in it. The only view is disclosed versus undisclosed precision, published per model as a pair of counts. The id of a rule is never typed by hand. It is computed:

```python
def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def rule_id(rule: dict) -> str:
    """SHA-256 over the canonical content of a rule (any rule_id key ignored)."""
    content = {k: v for k, v in rule.items() if k != "rule_id"}
    return hashlib.sha256(canonical_json(content).encode()).hexdigest()
```

The consequence is the point. Editing an entry changes its id. A published file that names a `rule_id` can always be checked against the rules file, and a quietly edited rule shows up as a different id instead of passing as the old one. A test pins it: change `undisclosed_values` to include `fp8` and the id must differ.

### 4. A verification hash that covers the new inputs, version-gated

The verification hash keeps its 16-hex-character convention. For 2.1.0 and later it additionally covers the snapshot digest, the `rule_id` in force, and the canonical spread output with every `observed` block removed. For 2.0.0 dates the hash input is unchanged, so the recipe stays backward compatible and published hashes still verify. When the private snapshot file is present, the pipeline re-hashes it and refuses to run on a mismatch with the digest recorded in the spread file.

That was the implementation that went up for review: 110 tests passing, 85 existing plus 25 new, including planted-fault tests for pooling dated with undated snapshots, folding unknown precision into a named one, an unhashed price change, and determinism.

## What broke: the rerun that would have rewritten history

The work ran through subagents. A Claude Opus 5.5 session orchestrated; a python-pro subagent implemented; a code-reviewer subagent reviewed the pull request. The reviewer reported a critical bug minutes after dispatch.

The version gate in part 4 decided which hash recipe to use from the methodology version. But the pipeline always loaded the current methodology file. A forced rerun of 2026-11-19, a date already published under 2.0.0, would have loaded 2.1.0, taken the new hash path, and rewritten the published file with a new hash. Every reader holding the old hash would see a tampered file. The suite was green anyway: the end-to-end rerun test for an old date arrived only with the fix.

This is the failure the whole design exists to prevent, and the first version still had it. Versioned rules are not enough if the code picks the rulebook by "whatever is current."

## The fix: resolve the rulebook per date, then refuse overwrites

The findings went back to the implementer. Two structural changes landed. First, a resolver maps each date to the rulebook that governed it:

```python
ARCHIVED_RULEBOOKS = [
    ("1.0.0", "2026-03-06"),   # dates up to and including
    ("2.0.0", "2026-11-20"),
]

def resolve_methodology_path(target_date: date, data_dir: Path) -> Path:
    fixtures = Path(data_dir) / "fixtures"
    iso = target_date.isoformat()
    for version, last_day in ARCHIVED_RULEBOOKS:
        archived = fixtures / f"methodology-{version}.yaml"
        if iso <= last_day and archived.exists():
            if version == "2.0.0" and iso < "2026-11-19":
                continue  # the gap before 2.0.0 started is not 2.0.0's
            return archived
    return fixtures / "methodology.yaml"
```

The resolver now drives the indexing pipeline, the index computation and the spread CLI. The methodology version comes from the resolved file, and facets, snapshot and rule id are skipped entirely before 2.1.0. Dates through 2026-03-06 resolve to 1.0.0, 2026-11-19 and 2026-11-20 to 2.0.0, and 2026-11-21 onward to the current 2.1.0 file. No index was published between 2026-03-07 and 2026-11-18, so the resolver sends those dates to the current file.

Second, a guard for the case where someone forces a rulebook anyway:

```python
def _refuse_rulebook_change(self, target_date: date) -> None:
    """Never overwrite a published index computed under a different methodology."""
    existing = self.data_dir / "indices" / f"{target_date}.json"
    if not existing.exists():
        return
    published = json.loads(existing.read_text()).get("methodology_version")
    resolved = self.indexer.methodology.get("methodology_version")
    if published and published != resolved:
        raise ValueError(
            f"{existing} was published under methodology {published}, but {resolved} "
            f"resolves for {target_date}; refusing to overwrite it"
        )
```

The resolver is the normal path. The guard is the backstop. A test constructs a pipeline with an explicit path to the 2.1.0 file, points it at a date published under 2.0.0, and asserts the run raises "refusing to overwrite". The same test then confirms the resolved pipeline runs fine.

The test that would have caught the original bug now exists too. It runs the full pipeline on 2026-11-19 and asserts three things: the version is 2.0.0, neither `rule_id` nor `endpoint_snapshot_sha256` appears in the output, and the hash equals a golden value built from the 2.0.0 path before facets existed. It checks both with and without a spread file. The review fix also made the snapshot sort total (sorted canonical lines), made the digest-mismatch error name the file and the fix, and moved `observed` out of the committed spread file into a git-ignored one. The suite went from 110 to 125.

## Why not just store the grade and add a version column?

It is the obvious approach. Store `grade = "B"` plus `rule_version = 3`, and when the rule changes, write new grades going forward.

It fails the first time someone asks what an old date would score under the new rule. The facts that produced the old grade are gone, so the answer is unknowable. It also does nothing about the precision problem: a hypothetical "B" from the rejected plan for an fp8 DeepSeek endpoint would carry a judgment the reviews already showed was wrong, with no way to recompute it. And a version column is a label you trust, while a content-hashed `rule_id` is a claim you can check. The same argument, applied to pipeline receipts, is in [when a gate should re-run the step instead of trusting its receipt](https://startaitools.com/posts/stop-trusting-the-stored-claim/).

Facets plus rule ids cost a private snapshot file and one more digest in the hash input. In exchange, a grade becomes a pure function over retained facts and a named rule, and old dates stay verifiable forever.

| | Store the grade plus a version column | Store facets plus a content-hashed rule_id |
|---|---|---|
| What is written at collection time | A grade such as "B" plus a rule_version number | Raw endpoint facets in a private snapshot whose SHA-256 is published |
| Can an old date be re-scored under a new rule? | No. The facts that produced the grade are gone | Yes. The grade is a pure function of retained facts and a named rule |
| What the version means | A label you have to trust | A claim you can check against the rules file |

Grades may still arrive. The plan sets the bar: an audited test that sends the same prompts through reference-precision and fp4 or undisclosed endpoints. That test has not been run. Until it is, the public site shows what the facets support, rows like "fp8 from $0.24 / fp4 from $0.12 / precision undisclosed from $0.20", next to the honest counterpoint that OpenRouter's 2026-11-11 test found no clear accuracy gap between fp16, fp8 and fp4 on one model. Methodology 2.1.0 first applies to 2026-11-21 data.

The full rules live in 000-docs (the repo's numbered folder of dated records) as the [methodology 2.1.0 facets doc](https://github.com/jeremylongshore/stci-standard-inference-token-cost-index/blob/main/000-docs/022-DR-STND-stci-methodology-2-1-facets.md).

## Also shipped

- The public site now renders per-precision "from" prices per spread row, falling back to the cheapest endpoint's precision for 2.0.0 files.
- The site gained a methodology section titled "What a grade is and is not".
- The publish script allow-lists the published keys and refuses any document containing per-endpoint fields. See [how that allow-list publishing works](https://startaitools.com/posts/publish-derived-data-from-an-allow-list/).
- New JSON schema for the spread file, including the additive `rule_id` and `endpoint_snapshot_sha256` fields.

## Use this

- Write raw facets to a canonical, hashed snapshot at collection time, and compute any grade later as a view over that snapshot plus a named rule.
- Give every rule an id equal to the SHA-256 of its canonical content, keep the rules file append-only, and record the id in each file published under the new methodology.
- Resolve the rulebook as of the date being computed, add a golden-hash rerun test for an old date, and make the pipeline refuse to overwrite a file whose recorded methodology version differs from the resolved one.

## Frequently asked questions

### How do you version a scoring rule without changing old results?

Keep the raw facts and compute each grade later as a view over them. Each rule lives in an append-only file, and its id is the SHA-256 of its canonical content, so editing a rule changes its id instead of passing as the old one. Every file published under 2.1.0 or later records the rule_id in force.

### How do you keep a rerun of a published dataset reproducible?

Resolve the rulebook from the date being computed, not from whichever methodology file is current. Add a golden-hash rerun test for an old date, so the hash must equal a fixed value. Make the pipeline refuse to overwrite a file whose recorded methodology version differs from the resolved one. A code review caught the version of this bug that would have rewritten a file already published under 2.0.0.

### Should a published dataset store grades or raw facts?

Store the raw facts. A grade written at collection time is a frozen copy of whatever rule existed that morning, and once the facts are discarded it cannot be recomputed under a new rule. A version column labels a grade you have to trust, while a content-hashed rule_id is a claim you can check. The cost is a private snapshot file and one more digest in the hash input.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do you version a scoring rule without changing old results?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Keep the raw facts and compute each grade later as a view over them. Each rule lives in an append-only file, and its id is the SHA-256 of its canonical content, so editing a rule changes its id instead of passing as the old one. Every file published under 2.1.0 or later records the rule_id in force."
      }
    },
    {
      "@type": "Question",
      "name": "How do you keep a rerun of a published dataset reproducible?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Resolve the rulebook from the date being computed, not from whichever methodology file is current. Add a golden-hash rerun test for an old date, so the hash must equal a fixed value. Make the pipeline refuse to overwrite a file whose recorded methodology version differs from the resolved one. A code review caught the version of this bug that would have rewritten a file already published under 2.0.0."
      }
    },
    {
      "@type": "Question",
      "name": "Should a published dataset store grades or raw facts?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Store the raw facts. A grade written at collection time is a frozen copy of whatever rule existed that morning, and once the facts are discarded it cannot be recomputed under a new rule. A version column labels a grade you have to trust, while a content-hashed rule_id is a claim you can check. The cost is a private snapshot file and one more digest in the hash input."
      }
    }
  ]
}
</script>

## Related Posts

- [The 16.08x price spread for one open-weight model that raised the grading question](https://startaitools.com/posts/same-model-different-price-open-weight-spread/)
- [How the token cost index was first built](https://startaitools.com/posts/stci-zero-to-v010-token-cost-index/)
- [Publishing derived data from an allow-list so no raw field leaks](https://startaitools.com/posts/publish-derived-data-from-an-allow-list/)
