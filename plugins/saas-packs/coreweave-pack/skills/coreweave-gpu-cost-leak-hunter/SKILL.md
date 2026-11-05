---
name: coreweave-gpu-cost-leak-hunter
description: |
  Hunt down CoreWeave GPU cost leaks — idle reserved capacity, wrong-GPU-type
  right-sizing waste, allocated-but-idle instances, and on-demand spend that should
  be committed — then produce a CFO-grokkable, dollar-ranked FinOps report. CoreWeave
  ships no cost dashboard and no billing API, so the spend view is built from PromQL
  against its managed Grafana. Use when a user asks why their CoreWeave GPU bill is
  high, wants to find wasted GPU spend or idle reservations, or needs a GPU FinOps
  cost report. Trigger with "coreweave cost", "why is my coreweave bill",
  "wasted GPU spend", "idle reserved capacity", "GPU cost leak".
allowed-tools: Read, Write, Edit, Glob, Bash(curl:*), Bash(jq:*), Bash(kubectl get:*), Bash(python3:*)
version: 1.12.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, coreweave, gpu-cloud, finops, cost]
---

# CoreWeave GPU Cost Leak Hunter

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by
> CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

Audits a CoreWeave GPU cluster for real-dollar cost leaks — idle reserved capacity,
GPUs on the wrong SKU, allocated-but-idle instances, and steady on-demand spend that
should be committed — then emits a CFO-grokkable, dollar-ranked FinOps report.

## Overview

CoreWeave ships **no cost dashboard and no billing API** ([usage-monitoring
docs][um]). There is also **no single "dollars" metric** — spend is reconstructed by
querying usage from CoreWeave's managed Grafana in PromQL and multiplying each
resource's usage by its rate-card price. This skill does exactly that, then ranks the
leaks by monthly dollar impact.

The math is **deterministic**: PromQL returns usage counts, and the bundled
`scripts/rank-and-report.py` does every multiplication, sum, and ranking — the agent
never eyeballs a number. Two of the four categories are billed waste (**Confirmed**);
the other two are a right-sizing model (**Estimated**) and a commitment decision
(**At-risk**), labeled so a CFO never reads a modeled number as recoverable cash.
Deep domain knowledge lives in `references/`, loaded only when a leak needs it.

## Prerequisites

- **CoreWeave managed Grafana access** — the Prometheus data source is reachable only
  to a member of the `admin`, `metrics`, or `write` group in the CoreWeave Cloud
  Console ([usage-monitoring docs][um]). This is the hard dependency; Step 1 probes it
  and fails fast if the group is missing.
- **A Prometheus/Grafana query endpoint** in `$CW_PROM_URL` (the Grafana data-source
  proxy, e.g. `https://grafana.ORG.coreweave.com/api/datasources/proxy/uid/UID`)
  and a bearer token in `$CW_TOKEN` for `curl`.
- **`kubeconfig`** for the cluster (CoreWeave-issued) so `kubectl get` can corroborate
  live GPU allocation and node labels.
- **The rate card** — CoreWeave publishes no price metric, so on-demand and committed
  rates are supplied to the ranker from `references/gpu-right-sizing.md` (dated
  snapshot of [coreweave.com/pricing][pr]) or the customer's contract.
- **`jq`** and **`python3`** for parsing query JSON and running the ranker.

**Authentication.** All auth comes from the environment (`$CW_PROM_URL`, `$CW_TOKEN`,
`$KUBECONFIG`) — no secrets are hardcoded. Grafana enforces the group membership above
on every query.

## Instructions

The pipeline is **detect → price → rank → report**. PromQL returns usage; the dollar
arithmetic runs in `scripts/`; deep knowledge loads from `references/` on demand:

1. Verify metric access, fail fast if the group is missing.
2. Pull the 30-day spend baseline (usage × rate card).
3. Detect Leak 1 — idle reserved capacity (Confirmed).
4. Detect Leak 2 — wrong-GPU-type right-sizing waste (Estimated).
5. Detect Leak 3 — allocated-but-idle instances (Confirmed).
6. Detect Leak 4 — on-demand spend that should be committed (At-risk).
7. Rank by monthly dollar impact and render the CFO report.

### Step 1: Verify Metric Access (fail fast, not mid-flow)

Probe `billing:instance:total` before anything else. An HTTP 401/403 or empty result
means the token's principal is not in `admin`/`metrics`/`write` — STOP and report it;
do not continue into the scans.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" \
  --data-urlencode 'query=count(billing:instance:total)' \
  "$CW_PROM_URL/api/v1/query" | jq -r '.status, (.data.result | length)'
```

If `status` is not `success` with a non-empty result, load
[`references/promql-billing-setup.md`](references/promql-billing-setup.md) and report
the missing group access verbatim. Stop here.

### Step 2: Pull the Spend Baseline

Reconstruct 30-day GPU node-hours per instance type. CoreWeave has no dollars metric,
so this returns **usage** — the ranker multiplies by the rate card. Write the JSON to
the working dir for the ranker.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" \
  --data-urlencode 'query=sum by (instance_type) (sum_over_time(billing:instance:total[30d:1h]))' \
  "$CW_PROM_URL/api/v1/query" > "$OUT/baseline.json"
```

The rate card and the per-category PromQL live in
[`references/gpu-cost-leak-categories.md`](references/gpu-cost-leak-categories.md).
Load it now — the four scans below reference its recording-rule notes.

### Step 3: Leak 1 — Idle Reserved Capacity (Confirmed)

Reserved GPUs bill at the committed rate **whether used or not**. A reserved GPU
sitting below a utilization floor is confirmed waste — you paid for it and it did no
work. Cross reserved allocation (`billing_gpu`, filtered by the reservation label)
against SM-active from DCGM.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" --data-urlencode \
  'query=sum by (instance_type,node) (avg_over_time(billing_gpu{reservation!=""}[30d:1h]))
     and on(node) (avg by (node) (avg_over_time(DCGM_FI_PROF_SM_ACTIVE[30d:1h])) < 0.05)' \
  "$CW_PROM_URL/api/v1/query" > "$OUT/leak1-idle-reserved.json"
```

The `reservation` label key is provider-specific — confirm yours with `kubectl get
nodes --show-labels`. Waste = idle reserved GPU-hours × committed rate (ranker input).

### Step 4: Leak 2 — Wrong-GPU-Type Right-Sizing (Estimated)

H100/H200 running small-model (~7B–30B) inference is over-paying: for that regime
L40S is cheaper per token (directional — see `gpu-right-sizing.md`). Flag those
instance-hours; the ranker re-prices them at the L40S rate.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" --data-urlencode \
  'query=sum by (instance_type) (sum_over_time(billing:instance:total{instance_type=~".*(h100|h200).*"}[30d:1h]))' \
  "$CW_PROM_URL/api/v1/query" > "$OUT/leak2-wrong-gpu.json"
```

This is **Estimated**: the rate delta is exact rate-card math, but throughput
equivalence on L40S is a model. Confirm the served model size with the cluster owner
before acting; FP8 serving needs Hopper/Ada, not Ampere (see `gpu-right-sizing.md`).

### Step 5: Leak 3 — Allocated-but-Idle Instances (Confirmed)

On-demand GPUs that are allocated (billing) but running at low SM-utilization / low
MFU bill the full on-demand rate for no work — confirmed billed waste, the GPU twin of
an idle cluster.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" --data-urlencode \
  'query=(avg by (node,instance_type) (avg_over_time(DCGM_FI_PROF_SM_ACTIVE[30d:1h])) < 0.05)
     and on(node) (sum by (node) (avg_over_time(billing_gpu{reservation=""}[30d:1h])) > 0)' \
  "$CW_PROM_URL/api/v1/query" > "$OUT/leak3-idle-ondemand.json"
```

Corroborate with `kubectl get pods -A --field-selector=status.phase=Running` to
confirm nothing is actually scheduled on the flagged node. Waste = idle on-demand
GPU-hours × on-demand rate.

### Step 6: Leak 4 — On-Demand Spend That Should Be Committed (At-risk)

A stable on-demand floor — GPUs of one type always running across the window — is
paying on-demand for capacity a commitment discounts up to 60% ([pricing][pr]).
Measure the always-on floor with `min_over_time`.

```bash
curl -sS -H "Authorization: Bearer $CW_TOKEN" --data-urlencode \
  'query=min_over_time(sum by (instance_type) (billing:instance:total{reservation=""})[30d:1h])' \
  "$CW_PROM_URL/api/v1/query" > "$OUT/leak4-commit-gap.json"
```

This is **At-risk**: the up-to-60% saving is pending a commitment decision, and a
commitment is itself a paid obligation — see the over-reservation caution in
`gpu-cost-leak-categories.md`. Savings = floor GPU-hours × on-demand rate × discount.

### Step 7: Rank and Write the Report

Assemble one leak object per category from the PromQL usage results plus the rate
card, then pipe them to the deterministic ranker — the LLM does NOT do the arithmetic.
Because CoreWeave exposes no dollars metric, each object carries `usage_gpu_hours` and
its rate-card rate; **the ranker multiplies usage × rate itself** (and applies the
re-price or discount factor). Each object's `kind` (`confirmed` / `estimated` /
`at-risk`) tells the renderer to split the headline confirmed-vs-pending, rank
descending by monthly dollars, and stamp a `Confidence` column.

```bash
OUT="${OUT:-$(pwd)/cost-leak-out}" && mkdir -p "$OUT"
# Each Step wrote a leak-N.json {category, root_cause, fix, kind, usage_gpu_hours,
# rate_usd_per_gpu_hour, ...}; the ranker does usage × rate deterministically.
jq -s '.' "$OUT"/leak-*.json | \
  python3 scripts/rank-and-report.py \
    --monthly-spend 180000 --window-end "$WINDOW_END" \
    --out "$OUT/cost-leak-report.md"
```

Render the output using the verbatim template in
[`references/cfo-output-format.md`](references/cfo-output-format.md). Use `Glob` to
collect the per-leak JSON, `Write` the report, and `Edit` it to rescale the headline
spend on request.

## Output

- **A CFO-grokkable report** leading with a **split** headline that never sums
  confirmed and unconfirmed dollars under one verb — `A $180K/month CoreWeave GPU
  cluster is burning ~$40K/month (confirmed), plus up to ~$29K/month pending review` —
  each with a `/year` companion.
- **A trailing-30-day window stamp** so every figure has an explicit calendar window.
- **The ranked leak table** (`# | Where it's leaking | $/month | Confidence | The
  fix`), one row per category, highest dollar impact first, each fix a single change.
- **The #1-line callout** — the top leak annualized, named, with its confidence.
- **Per-leak detail artifacts** — the flagged nodes/instance types, the PromQL that
  found them, and the underlying `$/GPU-hour` rates for the cluster engineer.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| HTTP 401/403 on `/api/v1/query` | Token principal not in `admin`/`metrics`/`write` | Run Step 1; report the group requirement from `promql-billing-setup.md`. Stop. |
| Empty result for `billing:instance:total` | Wrong data-source proxy UID, or org has no billing metrics enabled | Verify `$CW_PROM_URL` points at the Grafana Prometheus proxy; confirm in Grafana Explore. |
| `DCGM_*` series absent | DCGM exporter not scraped on the node pool | Skip Leaks 1/3 utilization filter for that pool; note "utilization unavailable" rather than reporting $0. |
| `reservation` label missing | Provider label key differs per org | Confirm the reservation/committed label with `kubectl get nodes --show-labels`; substitute it in the query. |
| Ranker prints `~$0/month` confirmed | A `kind` value was mis-cased and dropped from the sum | The ranker normalizes case; verify each leak object's `kind` is one of the three tiers. |

## Examples

### Example 1: "Why is my CoreWeave bill so high?"

Runs the full pipeline. The access probe passes, the four scans return rows, and the
ranker emits a split, confidence-stamped report:

```text
### A $180K/month CoreWeave GPU cluster is burning **~$44,986/month** (confirmed), plus up to **~$29,110/month** pending review

Trailing 30 days ending 2026-06-22. Confirmed **~$540K/year**; up to **~$349K/year** more pending review. Spend is reconstructed from PromQL against CoreWeave's managed Grafana (no billing API). Every line below is one change.

| # | Where it's leaking | $/month | Confidence | The fix |
|---|---|--:|---|---|
| 1 | **Idle reserved GPUs** — reserved capacity billing around the clock below a utilization floor | **$26,280** | Confirmed | Right-size or release the reservation |
| 2 | **Allocated-but-idle on-demand GPUs** — nodes up at <5% SM-active, paying full rate for no work | **$18,706** | Confirmed | Scale-to-zero / deschedule the idle nodes |
| 3 | **H100/H200 on small-model inference** — L40S is cheaper per token in the 7B–30B regime | **$16,629** | Estimated | Move small inference to L40S |
| 4 | **Steady on-demand that should be committed** — an always-on floor paying on-demand | **$12,481** | At-risk | Commit the stable floor (up to 60% off) |

**The #1 line alone — idle reserved gpus (confirmed) — is ~$315K/year, fixed in one setting.**
```

### Example 2: Idle-Reservation Sweep

User asks "are we paying for idle reserved GPUs?" The skill runs Step 3 only, crosses
`billing_gpu{reservation!=""}` against `DCGM_FI_PROF_SM_ACTIVE`, and reports each
reserved node below the floor with its 30-day committed spend.

## Resources

- [`references/gpu-cost-leak-categories.md`](references/gpu-cost-leak-categories.md) — the four leak categories: definition, PromQL, root cause, the one fix.
- [`references/cfo-output-format.md`](references/cfo-output-format.md) — verbatim CFO report template + the never-sum invariant.
- [`references/gpu-right-sizing.md`](references/gpu-right-sizing.md) — L40S/H100/H200/A100/L40 decision table + the FP8 rule (figures flagged directional).
- [`references/promql-billing-setup.md`](references/promql-billing-setup.md) — the billing metrics + group access, cited.
- Sibling: `coreweave-cost-tuning` authors cost-control config; this skill detects leaks and dollarizes them.

[um]: https://docs.coreweave.com/docs/observability/usage-monitoring
[pr]: https://www.coreweave.com/pricing
