---
name: databricks-cost-leak-hunter
description: |
  Hunt down Databricks cost leaks — wasted DBUs, idle clusters, oversized SQL
  warehouses, and untagged runaway spend — and produce a FinOps cost report.
  Use when a user asks why their Databricks bill is high, wants to find cost
  leaks / wasted DBUs / idle clusters, or needs a FinOps cost report.
  Trigger with "databricks cost", "why is my databricks bill",
  "find wasted spend", "cost leak".
allowed-tools: Read, Write, Edit, Bash(databricks:*), Bash(jq:*), Glob, mcp__databricks-workspace-mcp__clusters_get, mcp__databricks-workspace-mcp__clusters_events, mcp__databricks-workspace-mcp__clusters_list, mcp__databricks-workspace-mcp__instance_pools_list, mcp__databricks-workspace-mcp__pipelines_get
version: 2.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, databricks, finops, cost]
---

# Databricks Cost Leak Hunter

Audits a Databricks workspace for real-dollar cost leaks — idle compute, jobs on
the wrong SKU, overprovisioned clusters, and the Photon premium paid without the
speedup — then emits a CFO-grokkable, dollar-ranked FinOps remediation report.

## Overview

This skill finds where Databricks money is leaking and how much, in dollars, per
month. Confirmed-spend figures come from the customer's own `system.billing.usage`
joined to `system.billing.list_prices` — never an estimate. Two of the four
categories (overprovisioning, Photon premium) are explicitly modeled/at-risk
amounts, labeled as such so a CFO never confuses them with recoverable spend. The
skill surfaces four named leak categories, ranks them by monthly dollar impact, and
explains each root cause in FinOps language a CFO can act on without an engineer to
translate.

It is architecturally distinct from the v1 `databricks-cost-tuning` skill: that one
AUTHORS policy (creates cluster policies, spot configs). This one DETECTS leaks and
reports them, dollarized and ranked. The math is deterministic — bundled scripts in
`scripts/` do the arithmetic so the agent never eyeballs numbers — and deep domain
knowledge lives in `references/` loaded only when a leak needs it.

The skill uses two data planes. Dollar figures come from the **Databricks CLI
Statement Execution API** (`databricks api post /api/2.0/sql/statements`) reading
`system.*` — authenticated by the CLI's own `DATABRICKS_HOST`+`DATABRICKS_TOKEN` /
`databricks auth login`. The live config/event evidence that explains *why* a leak
exists (auto-termination setting, node type, autoscale floor, pool `min_idle`) comes
from the custom **`databricks-workspace-mcp`** control-plane tools — the one MCP
dependency. The SQL produces the number; the workspace MCP turns it into a verified,
single-config-change fix.

## Prerequisites

Read access to the billing system tables is the hard dependency and the most common
failure. `system.billing.usage` requires a **metastore-admin grant chain** — the
skill detects a missing grant upfront and reports it, rather than failing mid-flow.

- **Databricks Premium or Enterprise** workspace with Unity Catalog (system tables
  are UC-governed; not available on Standard).
- **Metastore-admin grant chain** on the billing schema, granted by a metastore
  admin to the running principal:
  - `GRANT USE CATALOG ON CATALOG system TO <principal>`
  - `GRANT USE SCHEMA ON SCHEMA system.billing TO <principal>`
  - `GRANT SELECT ON TABLE system.billing.usage TO <principal>`
  - `GRANT SELECT ON TABLE system.billing.list_prices TO <principal>`
- **Compute system schema** for config/utilization corroboration (same chain on
  `system.compute`): `system.compute.clusters`, `system.compute.node_timeline`.
- **Databricks CLI** authenticated (`databricks auth login`, or `DATABRICKS_HOST` + `DATABRICKS_TOKEN`)
  and `jq` for parsing JSON tool output. The dollar queries
  run through the CLI Statement Execution API — UC enforces the grant chain above.
- **`DATABRICKS_WAREHOUSE_ID`** env var set to a running SQL warehouse — every
  statement-execution call (Step 1's probe included) requires it.
- **`databricks-workspace-mcp` registered** (its own PAT/U2M/M2M auth; PAT
  unsupported in Databricks-App deployment mode). It reads the live REST API, not
  `system.*`, so it needs no system-table grants. If it is absent the skill still
  produces dollar figures but cannot corroborate live config — it then accepts
  pasted config input.

**Authentication.** The CLI Statement Execution API uses `DATABRICKS_HOST` +
`DATABRICKS_TOKEN` or `databricks auth login`; UC enforces the metastore grant chain
on every `system.*` read. The custom `databricks-workspace-mcp` authenticates
separately via its own PAT / U2M / M2M token. No secrets are hardcoded — all auth
comes from the environment or the registered MCP server.

Run the upfront grant check before any analysis — see Step 1.

## Instructions

The pipeline is **detect → compute → rank → report**. SQL detection runs through the
CLI Statement Execution API; config corroboration runs on `databricks-workspace-mcp`;
the dollar arithmetic runs in `scripts/`; deep knowledge loads from `references/` on
demand.

### Step 1: Verify the Grant Chain (fail fast, not mid-flow)

Probe the billing tables before anything else. If the probe errors with a
permission message, STOP and report the exact missing grant — do not continue into
the leak scans. Requires `DATABRICKS_WAREHOUSE_ID` (a running SQL warehouse).

```bash
databricks api post /api/2.0/sql/statements --json '{
  "warehouse_id": "'"$DATABRICKS_WAREHOUSE_ID"'",
  "statement": "SELECT 1 FROM system.billing.usage LIMIT 1",
  "wait_timeout": "30s"
}' | jq -r '.status.state, .status.error.message // "ok"'
```

If state is not `SUCCEEDED`, load
[`${CLAUDE_SKILL_DIR}/references/system-tables-setup.md`](references/system-tables-setup.md)
and report the missing grant chain to the user verbatim. Stop here.

### Step 2: Pull the Spend Baseline

Establish the trailing-30-day total spend so every leak can be expressed as a share
of a real number, and capture the window's `MAX(usage_date)` to stamp into the
report. The price-window join (usage × `list_prices.pricing.default`, matched on
`sku_name` AND `usage_unit` within the price-effective window, `currency_code='USD'`)
is the dollar primitive reused by every category query.

```bash
# The CLI does NOT expand ${VARS} inside a --json @file, so inject the warehouse
# id with jq at call time (the static template carries only wait_timeout + statement).
databricks api post /api/2.0/sql/statements --json "$(
  jq --arg wh "$DATABRICKS_WAREHOUSE_ID" '. + {warehouse_id: $wh}' \
    "${CLAUDE_SKILL_DIR}/scripts/sql/spend-baseline.sql.json"
)"
```

The canonical CTE and full per-category SQL live in
[`${CLAUDE_SKILL_DIR}/references/cost-leak-categories.md`](references/cost-leak-categories.md).
Load it now — the four detection queries below all reference its `priced` CTE.

### Step 3: Detect Leak 1 — Clusters That Never Auto-Terminate

Join priced All-Purpose usage to `system.compute.clusters`; flag clusters whose
latest-change `auto_termination_minutes = 0`. Rank by 30-day idle spend. This is
**confirmed spend** — money actually billed for idle compute.

```sql
SELECT p.usage_metadata.cluster_id AS cluster_id,
       COALESCE(c.cluster_name, 'unknown') AS cluster_name,
       c.auto_termination_minutes,
       ROUND(SUM(p.usd), 2) AS spend_30d_usd
FROM priced p
JOIN cluster_cfg c ON p.usage_metadata.cluster_id = c.cluster_id
WHERE p.billing_origin_product = 'ALL_PURPOSE'
  AND c.auto_termination_minutes = 0
GROUP BY p.usage_metadata.cluster_id, c.cluster_name, c.auto_termination_minutes
HAVING SUM(p.usd) > 0
ORDER BY spend_30d_usd DESC;
```

Corroborate each flagged cluster's live config with `databricks-workspace-mcp`
`clusters_get` (confirm `autotermination_minutes = 0` right now) and `clusters_events`
(measure the idle gap between `RUNNING` and `TERMINATING`).

### Step 4: Detect Leak 2 — Scheduled Jobs on All-Purpose Compute

The signature leak: a usage row with a `job_id` in `usage_metadata` AND
`billing_origin_product = 'ALL_PURPOSE'` (~$0.55/DBU) instead of `JOBS_COMPUTE`
(~$0.15/DBU). Re-price the same DBUs at the current Jobs rate to compute savings.
This is **confirmed savings** — a deterministic re-pricing delta. The `jobs_rate`
CTE is deduped to one USD rate per `usage_unit` so the join cannot fan out (see
`cost-leak-categories.md`).

```sql
SELECT p.usage_metadata.job_id AS job_id,
       ROUND(SUM(p.usd), 2) AS spend_on_all_purpose_30d_usd,
       ROUND(SUM(p.usd) - SUM(p.usage_quantity * jr.jobs_unit_price), 2)
         AS potential_savings_30d_usd
FROM priced p
JOIN jobs_rate jr ON p.usage_unit = jr.usage_unit
WHERE p.billing_origin_product = 'ALL_PURPOSE'
  AND p.usage_metadata.job_id IS NOT NULL
GROUP BY p.usage_metadata.job_id
HAVING SUM(p.usd) - SUM(p.usage_quantity * jr.jobs_unit_price) > 0
ORDER BY potential_savings_30d_usd DESC;
```

Confirm the live compute type is All-Purpose (not Jobs) with `clusters_list` /
`clusters_get` (`cluster_source`) before recommending the move. The `job_id` +
`ALL_PURPOSE` billing signal is itself dollar-accurate; the REST check is
belt-and-suspenders.

### Step 5: Detect Leak 3 — Overprovisioned Clusters Idling Below Floor

Aggregate mean CPU from `system.compute.node_timeline`, join to 30-day spend, flag
clusters burning real dollars at chronically low utilization (< 25%). This figure is
an **estimate** (`est_overprovision = spend × (1 − CPU%)`), not billed waste — it is
the one modeled number in the pipeline and is labeled `est_*` everywhere.

```sql
SELECT s.cluster_id,
       ROUND(u.avg_cpu_pct, 1) AS avg_cpu_pct,
       ROUND(s.spend_30d_usd, 2) AS spend_30d_usd,
       ROUND(s.spend_30d_usd * (1 - LEAST(u.avg_cpu_pct,100)/100.0), 2)
         AS est_overprovision_30d_usd
FROM spend s
JOIN util u ON s.cluster_id = u.cluster_id
WHERE u.avg_cpu_pct < 25 AND s.spend_30d_usd > 0
ORDER BY est_overprovision_30d_usd DESC;
```

Corroborate the configured floor with `clusters_get` (REST nested
`autoscale.min_workers` / `autoscale.max_workers`); for the idle-pool variant use
`instance_pools_list` (`min_idle_instances` + `stats.idle_count`) — pool waste is NOT
a billing row.

### Step 6: Detect Leak 4 — Photon Premium Without the Speedup

Photon is **not a column** on `system.compute.clusters`; it is billing-visible via
the SKU. Isolate usage whose `sku_name ILIKE '%PHOTON%'` and surface the ~2× premium
portion as the **at-risk** amount — money for review against actual runtime gain, not
confirmed waste.

```sql
SELECT p.usage_metadata.cluster_id AS cluster_id,
       ROUND(SUM(p.usd), 2)        AS photon_spend_30d_usd,
       ROUND(SUM(p.usd) / 2.0, 2)  AS photon_premium_at_risk_30d_usd
FROM priced p
WHERE p.sku_name ILIKE '%PHOTON%'
  AND p.billing_origin_product IN ('ALL_PURPOSE','JOBS_COMPUTE')
  AND p.usage_metadata.cluster_id IS NOT NULL
GROUP BY p.usage_metadata.cluster_id
HAVING SUM(p.usd) > 0
ORDER BY photon_premium_at_risk_30d_usd DESC;
```

Confirm Photon is live and worth keeping with `databricks-workspace-mcp`
`clusters_get` (REST `runtime_engine` — a config-plane field, not a system column);
for DLT pipelines use `pipelines_get` (`spec.photon` / `serverless` / `edition`). See
[`${CLAUDE_SKILL_DIR}/references/dlt-tier-cost-tradeoffs.md`](references/dlt-tier-cost-tradeoffs.md)
when the leak touches DLT/serverless tiers.

### Step 7: Compute, Rank, and Write the Report

Pass each category's query result to the deterministic ranker — the LLM does NOT do
the arithmetic. Each leak object carries a `kind` field
(`confirmed` / `estimated` / `at-risk`) so the renderer can split the headline into
confirmed-recoverable vs estimated/at-risk-pending-review and stamp a `Confidence`
column. The script sums per-category figures by kind, ranks descending by monthly
dollar impact, annualizes the headline and #1 line, stamps the trailing-30-day window
end date, and renders the CFO-grokkable report.

```bash
# Per-category results and the rendered report are RUNTIME outputs — they go to
# a working dir ($OUT), never the skill package. Steps 3–6 wrote leak-*.json here.
OUT="${OUT:-$(pwd)/cost-leak-out}" && mkdir -p "$OUT"
jq -s '.' "$OUT"/leak-*.json | \
  python3 "${CLAUDE_SKILL_DIR}/scripts/rank-and-report.py" \
    --monthly-spend 100000 \
    --window-end "$WINDOW_END_DATE" \
    --out "$OUT/cost-leak-report.md"
```

Use `Glob` to collect the per-category `leak-*.json` results, `Write` the rendered
report, and `Edit` it if the user wants the headline spend rescaled. Render the
output using the verbatim template in
[`${CLAUDE_SKILL_DIR}/references/cfo-output-format.md`](references/cfo-output-format.md).

## Output

- **A CFO-grokkable report file** (`$OUT/cost-leak-report.md` in the working dir) leading
  with a **split** headline that never sums confirmed and unconfirmed dollars under
  one verb — `### A $<spend>/month workspace is burning **~$<confirmed>/month**
  (confirmed), plus up to **~$<at-risk>/month** pending review` — each with its
  `~$<annualized>/year` companion.
- **A trailing-30-day window stamp** under the headline
  (`Trailing 30 days ending <window-end>`) so every figure has an explicit calendar
  window, not just a `/month` cadence label.
- **The ranked leak table** with a `Confidence` column
  (`# | Where it's leaking | $/month | Confidence | The fix`), one row per category,
  ranked highest dollar impact first, `$/month` right-aligned, each fix a single
  config change. Root-cause cells use plain-business language — no raw `DBU` unit in
  the CFO-visible text (DBU detail stays in the per-leak detail artifacts).
- **The #1-line callout** — the top leak annualized, named, with its confidence, and
  stated as fixed in one setting.
- **The assumed-vs-cited disclosure** — only the workspace-spend input is assumed;
  on a live run confirmed figures are computed from `system.billing.usage`, while
  overprovision (estimated) and Photon premium (at-risk) are labeled as modeled.
- **Per-leak detail artifacts**: idle-cluster list, all-purpose-job migration list
  with per-job savings, overprovisioned-cluster rightsizing list, Photon-premium
  at-risk list — each with the corroborating live config from `databricks-workspace-mcp`
  and the underlying `$/DBU` rates for engineers.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `PERMISSION_DENIED` on `system.billing.usage` | Metastore-admin grant chain missing | Run Step 1; report the exact `GRANT USE CATALOG / USE SCHEMA / SELECT` chain from `system-tables-setup.md`. Stop, do not continue. |
| CLI not authenticated / token expired | No valid `DATABRICKS_HOST` + token | Re-run `databricks auth login`; verify with `databricks current-user me`. |
| Empty / unset `DATABRICKS_WAREHOUSE_ID` | Required warehouse for statement execution not set | Set `DATABRICKS_WAREHOUSE_ID` to a running SQL warehouse before Step 1. |
| `list_prices` join returns NULL `usd` | Custom/negotiated pricing not in `list_prices`, or `usage_unit` mismatch | Join on `sku_name` AND `usage_unit` within the price window with `currency_code='USD'`; if still NULL, use the customer's contracted rate card from `references/cost-leak-categories.md`. |
| Workspace MCP missing | Server not registered | Degrade gracefully: report it absent, run the dollar half, accept pasted config for corroboration. Never fail silently mid-flow. |
| `node_timeline` empty for a cluster | Serverless/short-lived compute, or monitoring lag | Skip Leak 3 for that cluster; note "utilization unavailable" rather than reporting $0 overprovision. |
| Untagged spend / no `cluster_name` | Clusters lack `CostCenter`/`Team` tags | Attribute by `cluster_id`; flag attribution as incomplete in the report footer. |

## Examples

### Example 1: "Why is my Databricks bill high?"

Runs the full pipeline. The grant check passes, the four scans return rows, and the
ranker emits the CFO report with a split, confidence-stamped headline:

```text
### A $100K/month Databricks workspace is burning **~$19,000/month** (confirmed), plus up to **~$8,000/month** pending review

Trailing 30 days ending 2026-06-22. Confirmed ~$228K/year; up to ~$96K/year more pending review. Every line below is one config change.

| # | Where it's leaking | $/month | Confidence | The fix |
|---|---|--:|---|---|
| 1 | Clusters that never shut themselves off — paying around the clock for compute nobody is using | **$12,000** | Confirmed | Set auto-shutoff (e.g. 30 min) |
| 2 | Scheduled batch jobs running on the premium notebook tier — ~3.6× the batch rate for identical work | **$7,000** | Confirmed | Move job clusters to the batch tier |
| 3 | Clusters sized for peak, idling most of the time — typically 30–50% oversized | **$5,000** | Estimated | Turn on autoscaling, drop the floor |
| 4 | Paying a ~2× speed-engine premium on jobs that don't run faster | **$3,000** | At-risk | Turn off the speed engine where it adds no gain |

**The #1 line alone — idle clusters (confirmed) — is ~$144K/year, fixed in one setting.**
```

### Example 2: Idle-Cluster Sweep

User asks "find idle clusters wasting money." The skill runs Step 3 only, joins the
spend to `clusters_get`, and reports each `auto_termination_minutes = 0` cluster with
its 30-day idle spend and the live idle gap from `clusters_events`.

### Example 3: All-Purpose-Job Rightsizing

User asks "are any jobs on the wrong compute?" Step 4 returns each `job_id` running
on All-Purpose with `potential_savings_30d_usd`, corroborated by `clusters_get`
confirming `cluster_source` is not `JOB` — the single fix is "move to Jobs Compute."

## Resources

- [`${CLAUDE_SKILL_DIR}/references/cost-leak-categories.md`](references/cost-leak-categories.md) — the four leak categories: definition, real detection SQL, FinOps root cause, remediation.
- [`${CLAUDE_SKILL_DIR}/references/cfo-output-format.md`](references/cfo-output-format.md) — verbatim CFO report template + the 90-second-skim rules.
- [`${CLAUDE_SKILL_DIR}/references/system-tables-setup.md`](references/system-tables-setup.md) — metastore-admin grant chain + access verification.
- [`${CLAUDE_SKILL_DIR}/references/dlt-tier-cost-tradeoffs.md`](references/dlt-tier-cost-tradeoffs.md) — DLT / serverless / Photon cost-tier encyclopedia, loaded on demand.
- [Databricks system tables (billing)](https://docs.databricks.com/aws/en/admin/system-tables/billing)
- [Databricks list_prices reference](https://docs.databricks.com/aws/en/admin/system-tables/pricing)
