---
name: databricks-streaming-guardian
description: |
  Guard production Databricks data pipelines — Delta Lake, Liquid Clustering,
  Structured Streaming, Auto Loader, and DLT — against the twelve foot-guns that
  fire at scale: OPTIMIZE/auto-compaction conflicts, Liquid-Clustering merge
  conflicts, VACUUM breaking a streaming checkpoint, RocksDB OOM, Auto Loader
  schema-evolution stops, and DLT refresh data loss. Includes a PreToolUse hook
  that blocks DROP/CREATE-OR-REPLACE/VACUUM on a table with active streaming
  consumers. Use when a Delta MERGE/OPTIMIZE fails with a concurrency exception, a
  stream breaks after VACUUM or a table replace, an Auto Loader stream stops on a
  new column, a DLT refresh drops data, or before running a destructive op on a
  streamed-from table. Trigger with "ConcurrentAppendException",
  "ConcurrentDeleteDeleteException", "DELTA_FILE_NOT_FOUND", "streaming checkpoint
  broke", "vacuum broke my stream", "autoloader UnknownFieldException", "dlt full
  refresh".
allowed-tools: Read, Write, Edit, Bash(databricks:*), Bash(jq:*), Bash(python3:*), Bash(bash:*), Glob, mcp__databricks-workspace-mcp__clusters_events, mcp__databricks-workspace-mcp__clusters_list, mcp__databricks-workspace-mcp__pipelines_get
version: 2.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, databricks, streaming, delta, data-ops]
---

# Databricks Streaming Guardian

The data-ops spine of the pack. Delta Lake, Liquid Clustering, Structured
Streaming, and DLT each ship a different set of foot-guns that fire most visibly
when production data flows through them at scale — and most of them are documented
platform *decisions* that surprise engineers, not bugs. This skill's job is
friction at trigger time (a hook that blocks the genuinely-irreversible op) plus
deterministic recovery when something already broke.

## Overview

Twelve foot-guns, grouped by the surface that triggers them. Eleven are owned
outright (D01–D10, D12); the twelfth — D11, DLT rebuild cost — is shared with
`databricks-cost-leak-hunter`: this skill checks the rebuild cost as part of
pre-refresh safety, that skill owns ongoing cost optimization.

**Delta write conflicts.** D01 `ConcurrentDeleteDeleteException` — a manual
`OPTIMIZE` colliding with auto-compaction, which is silently enabled on any table
touched by `MERGE`/`UPDATE`/`DELETE`. D02 `ConcurrentAppendException` after moving
to Liquid Clustering — LC keeps file-set-level writer conflicts; a fan-out `MERGE`
breaks unless its predicate is narrowed to the clustering keys.

**Streaming + checkpoint.** D03 `DELTA_FILE_NOT_FOUND_DETAILED` — `VACUUM` deletes
files the checkpoint pins to. D04 silent checkpoint corruption / reset to batch 0.
D05 RocksDB state-store off-heap OOM (the heap looks fine while off-heap state pins
multi-GB). D12 `DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE` — `CREATE OR
REPLACE` mints a new UUID and kills every active consumer.

**Migration + evolution.** D06 Liquid-Clustering migration's hidden full-rewrite
cost + downstream partition-predicate breakage. D07 time travel breaking silently
when `VACUUM` crosses the retention boundary. D10 Auto Loader
`UnknownFieldException` stopping the stream on every new column.

**DLT.** D08 the `@dlt.table` thread race (out-of-order registration). D09 full
refresh silently dropping data from a non-replayable source. D11 the rebuild cost
multiplier (checked before a full refresh; ongoing DLT cost is
`databricks-cost-leak-hunter`'s job).

**The hook (AP02/AP06 — this pack's only blocking hook).** A `PreToolUse` hook
(`hooks/streaming-guard-hook.py`) intercepts a Bash command that runs `DROP TABLE`,
`CREATE OR REPLACE TABLE`, or `VACUUM` against a table and — only when it confirms
via `system.streaming.query_progress` that an active stream reads that table —
**blocks it** with a message naming the consumers and the pain. It is precise by
design: it matches only real SQL-execution surfaces (never a `git commit` mentioning
"drop table"), and it **fails open** — if it cannot verify consumers, it allows
rather than false-block. Blocking is reserved for the genuinely irreversible.

Deterministic work lives in `scripts/`; deep knowledge in `references/`; the
Liquid-Clustering predicate rewrite in the `merge-rewriter` subagent. Two data
planes: the `databricks-workspace-mcp` control plane (cluster/pipeline events) and
the CLI Statement Execution API for `system.*` reads. Either absent → advisory mode
on pasted input.

## Prerequisites

- **`databricks-workspace-mcp` registered** — for `clusters_events` (RocksDB OOM
  correlation) and `pipelines_get` (DLT event log). Absent → advisory mode.
- **Databricks CLI** authenticated + `jq`, and **`DATABRICKS_WAREHOUSE_ID`** set —
  for the `system.streaming.query_progress` reads the hook and recovery flows use.
  The hook fails open (allows) if these are absent, so it never false-blocks.
- **The hook is a plugin-level `PreToolUse` hook** — it runs on Bash commands once
  the pack is installed. It is silent on everything except a confirmed-unsafe
  destructive op.

## Instructions

Pick the flow by symptom. **Always name the exact, searchable Databricks error
string** — `ConcurrentAppendException`, `ConcurrentDeleteDeleteException`,
`DELTA_FILE_NOT_FOUND_DETAILED`, `DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE`,
`UnknownFieldException` — even when the user paraphrases it or gives a short form;
the full code is what an operator greps logs and docs for.

### Step 1: Before a destructive op (the hook does this automatically)

Running `DROP TABLE` / `CREATE OR REPLACE TABLE` / `VACUUM` on a table? The hook
checks for active streaming consumers first and blocks if any exist. To check
manually, query `system.streaming.query_progress` for a stream whose
`source_description` names the table. If consumers exist: do NOT `CREATE OR
REPLACE` (use `ALTER`/in-place — D12) and do NOT `VACUUM` below the consumers'
checkpoint lag (D03/D07). See
[`${CLAUDE_SKILL_DIR}/references/checkpoint-recovery.md`](references/checkpoint-recovery.md).

### Step 2: A Delta write conflict (D01, D02)

- **`ConcurrentDeleteDeleteException` (D01)** — before a manual `OPTIMIZE`, probe
  the table for auto-compaction:

  ```bash
  bash "${CLAUDE_SKILL_DIR}/scripts/pre-optimize-check.sh" --table main.sales.orders
  ```

  If it reports COLLISION RISK, don't run manual `OPTIMIZE` (or disable
  auto-compaction first). Details:
  [`${CLAUDE_SKILL_DIR}/references/concurrency-conflicts.md`](references/concurrency-conflicts.md).
- **`ConcurrentAppendException` on a Liquid-Clustering table (D02)** — hand the
  failing `MERGE` to the **`merge-rewriter`** subagent; it fetches the target's
  clustering keys via `DESCRIBE DETAIL` and narrows the `ON` predicate so writers
  touch disjoint file sets.

### Step 3: A broken streaming source (D03, D04, D12)

Map the symptom to the failure class and its exact error code, then get the
recovery tier from the decision tree:

- `file-not-found` → **`DELTA_FILE_NOT_FOUND_DETAILED`** (VACUUM deleted pinned files — D03)
- `uuid-changed` → **`DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE`** (CREATE OR REPLACE minted a new UUID — D12)
- `checkpoint-reset` → silent batchId regression / checkpoint corruption (D04)
- `transient` → a restartable blip with an intact checkpoint

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/recover-streaming-source.py" \
  --failure file-not-found --time-travel yes    # or uuid-changed / checkpoint-reset / transient
```

It echoes the canonical error code and recommends SAFE_RESTART /
REPROCESS_FROM_OFFSET / RESTORE_FROM_TIME_TRAVEL / FULL_RESET_BACKFILL with the
data-loss tradeoff stated up front. Name that full code in your answer — not just
the short class. The full
three-tier reasoning is in
[`${CLAUDE_SKILL_DIR}/references/checkpoint-recovery.md`](references/checkpoint-recovery.md).

### Step 4: RocksDB state-store OOM (D05)

A driver/executor OOM while the JVM heap looks healthy points at off-heap RocksDB
state. Correlate the OOM to state size with `clusters_events`, then bound the
memory and enable changelog checkpointing per
[`${CLAUDE_SKILL_DIR}/references/rocksdb-state-store-tuning.md`](references/rocksdb-state-store-tuning.md).

### Step 5: Auto Loader schema evolution (D10)

A stream stopping with `UnknownFieldException` on a new column is the default
`addNewColumns` mode. Choose the mode deliberately (evolve-and-restart vs
`rescue`'s silent widening) and pin types with `schemaHints` per
[`${CLAUDE_SKILL_DIR}/references/autoloader-schema-evolution.md`](references/autoloader-schema-evolution.md).

### Step 6: DLT rebuild safety (D08, D09, D11)

Before a DLT full refresh, confirm every source is replayable (a Kafka topic past
retention or a truncate-and-load source loses data on refresh — D09) and that
`@dlt.table` registration is deterministic (the thread race — D08). Read the DLT
event log with `pipelines_get`; the checklist is in
[`${CLAUDE_SKILL_DIR}/references/dlt-rebuild-safety.md`](references/dlt-rebuild-safety.md).

## Output

- **A hook decision** — a destructive op on a streamed-from table is blocked with
  the active consumers named and the pain (D12 / D03-D07) explained; everything
  else passes silently.
- **A pre-OPTIMIZE verdict** — SAFE or COLLISION RISK (auto-compaction on) with the
  disable-or-serialize fix.
- **A rewritten MERGE** — the LC clustering-key-scoped predicate (from
  `merge-rewriter`) that stops `ConcurrentAppendException`.
- **A recovery recommendation** — the recovery tier + steps + the data-loss risk,
  for the specific failure class.
- **A tuning / mode / refresh-safety recommendation** — RocksDB bounds, Auto Loader
  mode, or the DLT full-refresh checklist, from the matching reference.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `ConcurrentDeleteDeleteException` | Manual OPTIMIZE races auto-compaction (D01) | Run `pre-optimize-check.sh`; don't manually OPTIMIZE an auto-compacted table, or disable auto-compact first. |
| `ConcurrentAppendException` on an LC table | MERGE predicate not scoped to clustering keys (D02) | Route the MERGE to `merge-rewriter`; narrow the ON predicate to the clustering keys. |
| `DELTA_FILE_NOT_FOUND_DETAILED` | VACUUM deleted checkpoint-pinned files (D03) | `recover-streaming-source.py --failure file-not-found`; restore via time travel if in retention, else reprocess/reset. |
| `DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE` | CREATE OR REPLACE minted a new UUID (D12) | The old checkpoint is dead — new checkpoint + backfill; the hook prevents this going forward. |
| Driver OOM, heap looks fine | Off-heap RocksDB state (D05) | Bound state-store memory + changelog checkpointing; size state with a watermark. |
| `UnknownFieldException`, stream stopped | Auto Loader `addNewColumns` default (D10) | Restart to evolve (idempotent sink), or choose `rescue`/`schemaHints` deliberately. |
| Hook allowed a destructive op with a warning | Could not verify consumers (no CLI/warehouse) | Advisory — the hook fails open; verify `system.streaming.query_progress` manually before running it. |

## Examples

### Example 1: "About to CREATE OR REPLACE a table other jobs stream from."

The `PreToolUse` hook fires, confirms 2 active consumers via
`system.streaming.query_progress`, and **blocks** with: *"CREATE OR REPLACE mints a
new UUID → both consumers die with DIFFERENT_DELTA_TABLE_READ_BY_STREAMING_SOURCE;
use ALTER / in-place."*

### Example 2: "My MERGE into a Liquid-Clustering table fails with ConcurrentAppendException."

The `merge-rewriter` subagent reads the target's clustering keys via `DESCRIBE
DETAIL` and rewrites the `ON` predicate to include them, so concurrent writers
touch disjoint file sets — the exception stops without serializing the jobs.

### Example 3: "My stream died with DELTA_FILE_NOT_FOUND after a VACUUM."

`recover-streaming-source.py --failure file-not-found --time-travel yes` →
RESTORE_FROM_TIME_TRAVEL (no data loss): restore the source to a pre-VACUUM version,
restart on the existing checkpoint, then align VACUUM retention with the checkpoint lag.

### Example 4: "Before I OPTIMIZE this table."

`pre-optimize-check.sh --table main.sales.orders` reports COLLISION RISK because
`delta.autoOptimize.autoCompact` is on — so the skill recommends letting
auto-compaction do it, or disabling it for the maintenance window first.

## Resources

- [`${CLAUDE_SKILL_DIR}/references/concurrency-conflicts.md`](references/concurrency-conflicts.md) — Delta OCC, auto-compaction collisions (D01), Liquid-Clustering writer conflicts (D02).
- [`${CLAUDE_SKILL_DIR}/references/checkpoint-recovery.md`](references/checkpoint-recovery.md) — the three-tier streaming checkpoint recovery (D03/D04/D12).
- [`${CLAUDE_SKILL_DIR}/references/rocksdb-state-store-tuning.md`](references/rocksdb-state-store-tuning.md) — bounded off-heap state + changelog checkpointing (D05).
- [`${CLAUDE_SKILL_DIR}/references/autoloader-schema-evolution.md`](references/autoloader-schema-evolution.md) — the schema-evolution modes + schemaHints (D10).
- [`${CLAUDE_SKILL_DIR}/references/dlt-rebuild-safety.md`](references/dlt-rebuild-safety.md) — DLT thread race, full-refresh data loss, tier cost (D08/D09/D11).
- [`${CLAUDE_SKILL_DIR}/scripts/pre-optimize-check.sh`](scripts/pre-optimize-check.sh) — auto-compaction collision probe.
- [`${CLAUDE_SKILL_DIR}/scripts/recover-streaming-source.py`](scripts/recover-streaming-source.py) — 4-way recovery decision tree.
- [`${CLAUDE_SKILL_DIR}/hooks/streaming-guard-hook.py`](hooks/streaming-guard-hook.py) — the PreToolUse block for destructive ops on streamed-from tables.
- [`${CLAUDE_SKILL_DIR}/agents/merge-rewriter.md`](agents/merge-rewriter.md) — rewrites a MERGE predicate for Liquid Clustering.
- [Delta concurrency control](https://docs.databricks.com/aws/en/optimizations/isolation-level) · [Structured Streaming production](https://docs.databricks.com/aws/en/structured-streaming/query-recovery) · [Auto Loader schema evolution](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema)
