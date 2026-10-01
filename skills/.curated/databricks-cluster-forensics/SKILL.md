---
name: databricks-cluster-forensics
description: |
  Diagnose broken or unexplained Databricks compute — slow cold starts, failed
  cluster launches, Photon paying its premium without the speedup, DBR-upgrade
  landmines, and spot-interruption shuffle aborts — by correlating a cluster's
  live event stream across API surfaces. Use when a Databricks cluster won't
  start, died mid-run, is randomly slow to start, when planning a Databricks
  Runtime upgrade, or when a job keeps failing on spot loss. Trigger with
  "databricks cluster won't start", "cluster failed", "why is my cluster slow",
  "NPIP_TUNNEL_SETUP_FAILURE", "databricks runtime upgrade", "photon not helping".
allowed-tools: Read, Write, Edit, Bash(databricks:*), Bash(jq:*), Bash(python3:*), Bash(bash:*), Glob, mcp__databricks-workspace-mcp__clusters_get, mcp__databricks-workspace-mcp__clusters_events, mcp__databricks-workspace-mcp__clusters_list
version: 2.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, databricks, clusters, sre, forensics]
---

# Databricks Cluster Forensics

The operational SRE spine of the pack — what a Databricks engineer reaches for at
2 AM when the compute layer is broken or unexplained. It correlates a cluster's
live event stream across API surfaces to name the failure with its **actual error
code** and its **version-specific mitigation**, not "network problem, try again".

## Overview

Six real compute-layer failures live in this skill; each has a deterministic
detector and an on-demand reference:

1. **Cold-start long-tail** (D01) — on VNet/VPC-injected workspaces a 5-minute
   start randomly takes 20-35, and Databricks reports only the aggregate.
   `scripts/cluster-coldstart-forensics.py` splits the PENDING window into stages
   (provisioning / init-scripts / spark-startup) so you see *which* stage spiked.
2. **Photon premium without the speedup** (D02) — Photon silently falls back to
   Spark on UDFs while the cluster still bills the ~2× Photon DBU premium for its
   whole uptime. See `references/photon-eligibility-and-fallback.md`.
3. **DBR upgrade landmines** (D03/D04/D05) — 14.x moved the working dir to the
   workspace filesystem (a ~500 MB cap that silently breaks large intermediate
   writes); 15.1 removed DBFS-root library storage and JDK 11; 15.4 flipped a JDBC
   calendar default. `scripts/find-cwd-writes.py` (AST) and `scripts/scan-jar-jdk.sh`
   (bytecode target) are the pre-upgrade detectors; `references/dbr-upgrade-paths.md`
   is the per-hop encyclopedia.
4. **The launch-failure umbrella** (D06) — `CLOUD_PROVIDER_LAUNCH_FAILURE` /
   `NPIP_TUNNEL_SETUP_FAILURE` each hide five distinct causes (subnet IP
   exhaustion, DNS, NSG/security-group block, deleted VNet, cloud throttling).
   `references/termination-codes.md` disambiguates them.
5. **Spot shuffle aborts** (D10) — a reclaimed spot node forces a shuffle
   recompute; lose another mid-recompute and the stage exceeds
   `spark.stage.maxConsecutiveAttempts` and the job aborts.
   `references/spot-vs-ondemand-decision.md` is the config decision tree.

It is architecturally distinct from the v1 `databricks-common-errors` and
`databricks-incident-runbook` skills: those narrate. This one reads live cluster
events, buckets them deterministically (the arithmetic is in `scripts/`, never
eyeballed), fans out parallel root-cause threads via the `cluster-event-investigator`
subagent, and loads deep knowledge from `references/` only when a symptom needs it.

**Two data planes.** Cluster control-plane evidence (spec, state, event stream)
comes from the custom **`databricks-workspace-mcp`** (`clusters_get` /
`clusters_events` / `clusters_list`). The Photon audit's `system.query.history`
read runs through the **CLI Statement Execution API** (`databricks api post
/api/2.0/sql/statements`) — the same path `databricks-cost-leak-hunter` uses.
Either surface absent, the skill degrades to **advisory mode** and accepts pasted
event JSON / query plans so it still produces value.

## Prerequisites

- **`databricks-workspace-mcp` registered** — the source of `clusters_get`,
  `clusters_events`, `clusters_list`. Absent, the skill accepts a pasted
  `clusters.events` response and says so (advisory mode).
- **Databricks CLI** authenticated (`databricks auth login`, or the
  `DATABRICKS_HOST` + `DATABRICKS_TOKEN` env pair) and `jq` — for the Photon
  `system.query.history` read.
- **`DATABRICKS_WAREHOUSE_ID`** set to a running SQL warehouse — required only for
  the Photon audit (Step 2); the cold-start / launch-failure flows need only the
  workspace MCP.
- **`unzip`** (and ideally a JDK's `javap`) on PATH for the DBR-15.1 JAR scan
  (`scan-jar-jdk.sh` falls back to reading class-file bytes if `javap` is absent).

The skill checks which surfaces are present in Step 0 and reports what is missing
before starting a flow it cannot finish.

## Instructions

Pick the flow by symptom. Each is independent; run only what the question needs.

### Step 0: Detect Available Surfaces

Confirm the workspace MCP answers (`clusters_list` returns) and, for a Photon
audit, that the CLI is authenticated and `DATABRICKS_WAREHOUSE_ID` is set. Name
any missing surface and switch that flow to advisory mode (pasted input) rather
than failing mid-diagnosis.

### Step 1: Cold-Start / Launch-Failure Forensics (D01, D06)

Pull the cluster's event stream and bucket its PENDING time:

```bash
# events from the workspace MCP (clusters_events) or the CLI, saved to a file:
databricks clusters events --cluster-id "$CLUSTER_ID" --output json > "$OUT/events.json"
python3 "${CLAUDE_SKILL_DIR}/scripts/cluster-coldstart-forensics.py" \
  --input "$OUT/events.json"
```

- If the start **succeeded but was slow**, the dominant stage names the layer:
  provisioning → cloud VM allocation or network/DNS/NPIP; init-scripts → a slow
  init script or library install; spark-startup → driver spin-up.
- If the start **failed**, read the terminal `termination_reason.code` and
  disambiguate with
  [`${CLAUDE_SKILL_DIR}/references/termination-codes.md`](references/termination-codes.md)
  — especially the `CLOUD_PROVIDER_LAUNCH_FAILURE` / `NPIP_TUNNEL_SETUP_FAILURE`
  umbrella and its five sub-causes.

For a messy failure, hand the `cluster_id` to the **`cluster-event-investigator`**
subagent (`/investigate-cluster <id>`): it fans out one thread per cause class and
returns the single most-likely cause with its evidence.

### Step 2: Photon Fallback Audit (D02)

Check whether Photon is earning its premium. Query recent query history for plans
that fell back to Spark, then corroborate the cluster is Photon (`runtime_engine`
via `clusters_get`):

```bash
databricks api post /api/2.0/sql/statements --json "$(jq -n --arg wh "$DATABRICKS_WAREHOUSE_ID" \
  '{warehouse_id:$wh, wait_timeout:"30s",
    statement:"SELECT statement_id, executed_by, total_duration_ms FROM system.query.history WHERE end_time > now() - INTERVAL 1 DAY ORDER BY total_duration_ms DESC LIMIT 50"}')"
```

Then read the physical plan of the slow statements for the "Photon does not
support" seam and the `ColumnarToRow` / `RowToColumnar` boundaries — the detection
recipe and the UDF-rewrite fixes are in
[`${CLAUDE_SKILL_DIR}/references/photon-eligibility-and-fallback.md`](references/photon-eligibility-and-fallback.md).

### Step 3: DBR Upgrade Readiness (D03, D04, D05)

Before bumping the runtime, run the two pre-upgrade detectors against the job's
code and libraries:

```bash
# D03 — writes to the CWD that the DBR-14 500 MB workspace-FS cap will break:
python3 "${CLAUDE_SKILL_DIR}/scripts/find-cwd-writes.py" --risk-only path/to/job/

# D04 — JARs built for a pre-17 JDK that DBR 15.1's JDK 17 may reject at runtime:
bash "${CLAUDE_SKILL_DIR}/scripts/scan-jar-jdk.sh" path/to/libs/
```

Cross-reference each hop's landmines (the 14.x CWD cap, the 15.1 DBFS-root-library
and JDK-11 removals, the 15.4 JDBC calendar flip) in
[`${CLAUDE_SKILL_DIR}/references/dbr-upgrade-paths.md`](references/dbr-upgrade-paths.md).

### Step 4: Spot Configuration Review (D10)

If a job keeps aborting after `NODES_LOST` / `SPOT_INSTANCE_TERMINATION` around a
shuffle, read the cluster's `aws_attributes` (`clusters_get`) and check the
driver-on-demand rule and the spot ratio against
[`${CLAUDE_SKILL_DIR}/references/spot-vs-ondemand-decision.md`](references/spot-vs-ondemand-decision.md).
The #1 fix is pinning the driver (and a floor of workers) to on-demand so a spot
reclaim can never take the driver.

## Output

- **A cold-start stage breakdown** — total PENDING time split into
  provisioning / init-scripts / spark-startup, the dominant stage named, and the
  layer to investigate (or, for a failed start, the terminal code + its cause).
- **A root-cause verdict** (from `cluster-event-investigator`) — the single
  most-likely cause with the specific events/codes that point to it, and the
  cause classes ruled out.
- **A Photon audit** — the queries paying the premium while falling back to Spark,
  with the plan seam and the UDF-rewrite fix.
- **A DBR-upgrade risk list** — the CWD writes at risk under the 500 MB cap and
  the JARs built for a pre-17 JDK, each with its line/file, plus the per-hop
  breaking-change notes.
- **A spot recommendation** — the corrected `aws_attributes` (driver on-demand,
  spot ratio) for the job class.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `NPIP_TUNNEL_SETUP_FAILURE` / `CLOUD_PROVIDER_LAUNCH_FAILURE` | One of five sub-causes (IP exhaustion, DNS, NSG, deleted VNet, throttling) | Disambiguate via `termination-codes.md`; the fix differs per sub-cause — do not blanket-retry. |
| `clusters_events` empty or truncated | Databricks prunes old events | Note the truncation; a missing `INIT_SCRIPTS_FINISHED` may mean "pruned", not "hung" — do not infer an init-script hang from absence alone. |
| Workspace MCP not registered | Connector not set up | Advisory mode: accept a pasted `clusters.events` JSON and run the forensics script on it. |
| Photon audit returns nothing | No `system.query.history` grant, or `DATABRICKS_WAREHOUSE_ID` unset | Confirm the warehouse id and the `system.query` grant chain; degrade to reading a pasted query plan. |
| `scan-jar-jdk.sh` reports JDK `?` | JAR has no class files, or `unzip` missing | Install `unzip`; a JDK `?` means the JAR is resources-only (no bytecode to check). |
| Cold-start script says "unmeasured" for a stage | The boundary events are absent (no init scripts, or pruned events) | Expected — the script never folds an unmeasured stage into another; investigate the measured stages. |

## Examples

### Example 1: "My cluster randomly takes 25 minutes to start."

Step 1 buckets the events: `provisioning 21m (84%), init-scripts 1m,
spark-startup 3m`. Dominant is provisioning → the skill points at cloud VM
allocation / subnet-IP / DNS, not init scripts, and loads `termination-codes.md`
for the provisioning sub-causes to check.

### Example 2: "Cluster failed with NPIP_TUNNEL_SETUP_FAILURE."

The investigator subagent runs its threads; the network/NPIP thread owns it and
disambiguates to "custom DNS could not resolve the control-plane hostname" (vs the
other four causes), citing the exact check from `termination-codes.md`.

### Example 3: "We're upgrading DBR 13.3 → 15.4. What breaks?"

Step 3 runs `find-cwd-writes.py` (flags 3 `to_parquet("staging/…")` writes at risk
under the 14.x cap) and `scan-jar-jdk.sh` (flags 2 JARs built for JDK 11), and
`dbr-upgrade-paths.md` surfaces the 15.4 JDBC calendar flip for the pipeline's
pre-Gregorian date handling.

### Example 4: "Job keeps dying after losing spot nodes."

Step 4 reads `aws_attributes`, finds the driver is on spot, and recommends
`first_on_demand` covering the driver + a worker floor with `SPOT_WITH_FALLBACK`,
citing the shuffle-recompute cascade in `spot-vs-ondemand-decision.md`.

## Resources

- [`${CLAUDE_SKILL_DIR}/references/termination-codes.md`](references/termination-codes.md) — codebook for every `termination_reason.code`, with the five-cause launch-failure umbrella.
- [`${CLAUDE_SKILL_DIR}/references/dbr-upgrade-paths.md`](references/dbr-upgrade-paths.md) — per-hop DBR breaking changes (14.x CWD cap, 15.1 lib/JDK removals, 15.4 calendar flip).
- [`${CLAUDE_SKILL_DIR}/references/photon-eligibility-and-fallback.md`](references/photon-eligibility-and-fallback.md) — what drops Photon to Spark and how to detect the premium-without-speedup.
- [`${CLAUDE_SKILL_DIR}/references/spot-vs-ondemand-decision.md`](references/spot-vs-ondemand-decision.md) — the spot config decision tree + driver-on-demand rule.
- [`${CLAUDE_SKILL_DIR}/scripts/cluster-coldstart-forensics.py`](scripts/cluster-coldstart-forensics.py) — buckets cold-start PENDING time by stage.
- [`${CLAUDE_SKILL_DIR}/scripts/find-cwd-writes.py`](scripts/find-cwd-writes.py) — AST scanner for DBR-14 CWD writes.
- [`${CLAUDE_SKILL_DIR}/scripts/scan-jar-jdk.sh`](scripts/scan-jar-jdk.sh) — JAR bytecode-target (JDK) scanner.
- [`${CLAUDE_SKILL_DIR}/agents/cluster-event-investigator.md`](agents/cluster-event-investigator.md) — parallel root-cause fanout subagent.
- [Databricks cluster events API](https://docs.databricks.com/api/workspace/clusters/events) · [Databricks Runtime release notes](https://docs.databricks.com/aws/en/release-notes/runtime/) · [Photon](https://docs.databricks.com/aws/en/compute/photon)
