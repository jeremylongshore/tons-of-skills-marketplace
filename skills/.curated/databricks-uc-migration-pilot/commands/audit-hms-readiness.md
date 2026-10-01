---
name: audit-hms-readiness
description: Audit a Hive Metastore schema and classify tables for UC migration readiness
aliases: [hms-audit, uc-readiness]
---

# /audit-hms-readiness

Runs the `databricks-uc-migration-pilot` skill's readiness audit against a Hive
Metastore schema and reports which tables can move to Unity Catalog and which
cannot (and why).

## Usage

```
/audit-hms-readiness <schema>
```

- `<schema>` — the `hive_metastore` schema to audit (e.g. `sales`). If omitted,
  ask which schema, or offer to audit every schema in `hive_metastore`.

## What it does

1. Confirms the role chain first (metastore-admin + system schemas enabled) — Step
   1 of the skill. Stops with the missing grant if the principal cannot read
   `system.information_schema`.
2. Runs `scripts/audit-hms-readiness.py --live <schema> --summary` to enumerate the
   schema's tables and classify each by storage URI:
   **READY** (cloud-native, `SYNC`-able), **BLOCKED** (named condition), **ORPHAN**
   (dangling entry).
3. Writes the readiness CSV to the working dir and prints the
   READY/BLOCKED/ORPHAN tally.
4. **If any BLOCKED class appears**, opens
   `references/uc-migration-blockers.md` for that class — its canonical error, the
   physical relocation procedure, and the per-cloud variant — and reminds you of
   the `DEEP CLONE`-not-shallow-clone history gotcha.

## Next step

Hand the CSV to the `migration-planner` subagent for a dependency-ordered
execution plan (`SYNC` the ready tables, relocate the blocked ones, order views
last).
