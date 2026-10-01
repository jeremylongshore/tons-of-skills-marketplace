---
name: databricks-uc-migration-pilot
description: |
  Pilot a Databricks Hive Metastore (HMS) → Unity Catalog (UC) migration before
  the deadline — audit every table's migratability, produce a dependency-ordered
  migration plan, trace UC's two-level permission model, and pick an environment
  isolation pattern. Use when a user asks how to migrate off the Hive metastore,
  move to Unity Catalog, which tables are UC-ready, why a table won't migrate, why
  a user lacks access after migration, or how to isolate dev/test/prod under UC.
  Trigger with "migrate to unity catalog", "hive metastore migration", "uc
  migration", "which tables can migrate", "unity catalog permission".
allowed-tools: Read, Write, Edit, Bash(databricks:*), Bash(jq:*), Bash(aws:*), Bash(python3:*), Glob
version: 2.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, databricks, unity-catalog, migration, identity]
---

# Databricks Unity Catalog Migration Pilot

Pilots a Hive Metastore → Unity Catalog migration end to end: it audits which
tables can migrate (and why the rest cannot), turns that audit into a
dependency-ordered execution plan, traces UC's two-level permission model when
access breaks, and picks an environment-isolation pattern for the
one-metastore-per-region constraint.

## Overview

**The September 30, 2026 forcing function.** Databricks is deprecating the legacy
Hive Metastore. On the cutover date the `hive_metastore` catalog goes
**read-only** — no new writes, no schema changes — and stays available only for
read-through while you migrate. Everything that writes to HMS (jobs, DLT
pipelines, dashboards, external BI) must be pointed at a Unity Catalog table
before then, or it breaks. This is not optional and it is not fast: the blockers
below (legacy storage schemes, DBFS-root managed data, DENY-based ACLs) each
require a physical data move or a grant rewrite, so the work is measured in weeks,
not an afternoon.

> ⚠️ **Verify the exact date and scope against your workspace's current
> deprecation notice** (Databricks account console → *Previews / Announcements*).
> Deprecation dates move; this skill's job is to get you *ready* well ahead of
> whatever the live date is — treat 2026-09-30 as the planning deadline, not an
> excuse to wait for it.

This skill does four things, in order, and each is deterministic where it can be:

1. **Detect** — `scripts/audit-hms-readiness.py` classifies every HMS table by its
   storage URI into **READY** (cloud-native, UC-governable), **BLOCKED** (a named
   un-migratable condition), or **ORPHAN** (a dangling HMS row pointing at deleted
   storage). The LLM never eyeballs a URI; the script owns the verdict.
2. **Plan** — the `migration-planner` subagent turns the readiness CSV into a
   per-table plan (`SYNC` / `DEEP CLONE` / rewrite / skip) **ordered by
   dependencies** so a view never migrates before its base tables.
3. **Trace** — the `uc-permission-tracer` subagent walks UC's two-level access
   model to answer "why can't user X read this?" in one pass — replacing ~90
   minutes of doc-spelunking per ticket.
4. **Isolate** — `/uc-env-pattern-picker` recommends one of four dev/test/prod
   isolation patterns under the single-metastore-per-region limit.

It is architecturally distinct from the v1 `databricks-upgrade-migration` and
`databricks-migration-deep-dive` skills: those narrate migration in prose. This
one runs a real readiness audit, emits a dependency-ordered plan, and traces live
permissions. Deep, load-on-demand knowledge lives in `references/`; the
arithmetic-and-classification lives in `scripts/`.

## Prerequisites

The three role grants below are the hard dependencies and the most common reason
the pilot stalls mid-flow. The skill checks the role chain **first** (Step 1) and
reports exactly what is missing before doing any work.

- **Account-admin** — required to enable the UC **system schemas**
  (`system.information_schema`, `system.access`) the audit reads, and to create
  the metastore/assign it to workspaces. Enable at the account level, not per
  workspace.
- **Metastore-admin** — required to `CREATE CATALOG`, run `GRANT` on UC objects,
  and create **external locations + storage credentials**. Migration *is* a
  sequence of metastore-admin operations.
- **Cloud IAM read access** (AWS `s3`/IAM, Azure, or GCP) — required to diagnose a
  storage-credential failure (the D2 case: a table is cloud-native but the UC
  storage credential's IAM role cannot assume the bucket). `Bash(aws:*)` is
  allowed for read-only IAM inspection; the skill never mutates cloud IAM.
- **Databricks CLI** authenticated (`databricks auth login`, or the
  `DATABRICKS_HOST` + `DATABRICKS_TOKEN` env pair) and `jq` for parsing.
  Enumeration and grant SQL run through the **CLI Statement Execution API**.
- **`DATABRICKS_WAREHOUSE_ID`** set to a running SQL warehouse — every
  statement-execution call requires it.

**Authentication.** All auth comes from the environment: the CLI's
`DATABRICKS_HOST` + `DATABRICKS_TOKEN` (or `databricks auth login`), and read-only
cloud credentials from the standard provider chain (`aws sts get-caller-identity`
to confirm). No secrets are hardcoded.

## Instructions

The pipeline is **verify role chain → detect readiness → plan → migrate →
trace access → isolate envs**. Do them in order; Step 1 is a hard gate.

### Step 1: Verify the Role Chain (hard gate — fail fast, not mid-migration)

Before touching data, confirm the running principal holds the roles the migration
needs. A missing role surfaces here, not three tables into a `SYNC`.

```bash
# Am I authenticated, and as whom?
databricks current-user me | jq -r '.userName'

# Metastore-admin check: only a metastore admin can read every grant. If this
# errors with PERMISSION_DENIED, the principal is not metastore-admin.
databricks api post /api/2.0/sql/statements --json "$(jq -n --arg wh "$DATABRICKS_WAREHOUSE_ID" \
  '{warehouse_id:$wh, wait_timeout:"30s",
    statement:"SELECT 1 FROM system.information_schema.catalog_privileges LIMIT 1"}')" \
  | jq -r '.status.state, (.status.error.message // "ok")'
```

Report the role chain status plainly: **account-admin** (needed to enable system
schemas), **metastore-admin** (needed for grants + external locations), **cloud
IAM read** (`aws sts get-caller-identity`). If any is missing, name who must grant
it and STOP — do not start an audit you cannot finish.

### Step 2: Enable & Confirm the System Schemas

The readiness audit reads `system.information_schema`; permission tracing reads
`system.access`. Those schemas are **individually gated** — enabling one does not
enable the others — behind an account-level flag AND a metastore-admin grant
chain. If they are not enabled, run the bundled idempotent enabler (account-admin
auth; a workspace PAT is rejected up front) to enable each schema and grant a
group `USE CATALOG system` + `USE SCHEMA` + `SELECT` in one pass:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/enable-system-schemas.py" \
  --account-id "$DATABRICKS_ACCOUNT_ID" --metastore-id "$METASTORE_ID" \
  --grant-to data-governance --dry-run   # drop --dry-run to apply
```

Then confirm a UC metastore is attached to this workspace
(`databricks metastores current`) — without one there is nowhere to migrate *to*.
The full two-layer access model (account-admin enables, metastore-admin grants,
neither inherits `SELECT`) is in
[`${CLAUDE_SKILL_DIR}/references/system-tables-access-model.md`](references/system-tables-access-model.md).

### Step 3: Detect — Run the Readiness Audit

Enumerate the HMS schema(s) and classify every table. The script owns the
verdict; feed it either live (`--live SCHEMA`) or the enumerated rows as JSON.

```bash
OUT="${OUT:-$(pwd)/uc-migration-out}" && mkdir -p "$OUT"

# Live enumeration (needs DATABRICKS_WAREHOUSE_ID + an authenticated CLI):
python3 "${CLAUDE_SKILL_DIR}/scripts/audit-hms-readiness.py" \
  --live sales --summary --out "$OUT/readiness-sales.csv"
```

Every row lands in one of three buckets — **READY** (cloud-native path, `SYNC`-able),
**BLOCKED** (a named condition), **ORPHAN** (dangling HMS entry, cleanup not
migration). When a BLOCKED class appears, load
[`${CLAUDE_SKILL_DIR}/references/uc-migration-blockers.md`](references/uc-migration-blockers.md)
for that class's canonical error, the physical relocation procedure, and the
per-cloud variant. **Do not skip the CLONE-drops-history gotcha in that file** — a
shallow `CREATE TABLE ... CLONE` breaks time travel post-migration; use `DEEP CLONE`.

### Step 4: Plan — Dependency-Ordered Migration Plan

Hand the readiness CSV to the **`migration-planner`** subagent (see
`agents/migration-planner.md`) with the org's catalog naming convention. It emits
a numbered execution order with per-step rationale and the right verb per table
(`SYNC` for ready Delta externals, `DEEP CLONE`/rewrite for blocked, `CREATE
VIEW` after base tables, skip for orphans). Dependency ordering is the point:
**a view never migrates before the tables it reads.**

Invoke it via `/audit-hms-readiness` (which runs Step 3 then routes here) or
directly by handing the subagent the CSV path.

### Step 5: Migrate — Execute the Plan

Walk the plan top to bottom:

- **READY (Delta external, cloud path):** `SYNC TABLE <uc_cat>.<schema>.<table>
  FROM hive_metastore.<schema>.<table>` — metadata-only, no data copy. `SYNC
  SCHEMA` does a whole schema when every table is ready.
- **BLOCKED (legacy scheme / DBFS root):** relocate the data first (`DEEP CLONE`
  for Delta, `CREATE TABLE AS SELECT` for non-Delta) to a UC-governed cloud path,
  register an **external location + storage credential**, then create the UC
  table at the new path. Full procedure per class in `uc-migration-blockers.md`.
- **LEGACY_TABLE_ACL:** the data may be ready, but the DENY-based grants cannot
  auto-map to UC's allow-only model — re-author them (Step 6 traces them).

Re-run Step 3 after a batch to confirm the migrated tables drop out of BLOCKED.

### Step 6: Trace — Diagnose Access After Migration

When a user hits `PERMISSION_DENIED` or `AccessDenied on s3://…` post-migration,
route to the **`uc-permission-tracer`** subagent (`/trace-uc-permission <user>
<error>`). It walks UC's two levels — account-admin/metastore-admin status →
group membership (including nested-group caveats) → catalog/schema/table grants →
the external-location/storage-credential grant for a cloud `AccessDenied` — and
returns a single actionable line: *"user X needs group Y membership AND `GRANT
SELECT ON <obj>` run by metastore admin W."*

When the fix is "add the user to group Y" but the grant still does not apply, the
cause is usually the Entra→Databricks SCIM bridge silently dropping nested-group
membership — see
[`${CLAUDE_SKILL_DIR}/references/scim-bridge-patterns.md`](references/scim-bridge-patterns.md)
for the connector's direct-members-only limitation and the three workarounds.

### Step 7: Isolate — Pick an Environment Pattern

For a fresh UC layout, run `/uc-env-pattern-picker`. It asks compliance, cost, and
BI-tool questions and recommends one of four patterns for the
**one-UC-metastore-per-region** constraint, emitting a matching Databricks Asset
Bundle `target` stub. The four patterns, their cost models, and tradeoffs live in
[`${CLAUDE_SKILL_DIR}/references/uc-environment-isolation-patterns.md`](references/uc-environment-isolation-patterns.md).

## Output

- **A readiness CSV** (`$OUT/readiness-<schema>.csv`, in the working dir) — one row
  per HMS table: `table_name, storage_uri, scheme, migration_blocker,
  suggested_action`, each table bucketed READY / BLOCKED / ORPHAN with a
  READY/BLOCKED/ORPHAN tally.
- **A dependency-ordered migration plan** (markdown from `migration-planner`) — a
  numbered execution order, the verb per table (`SYNC`/`DEEP CLONE`/rewrite/skip),
  per-step rationale, and views ordered after their base tables.
- **A permission trace** (from `uc-permission-tracer`) — the exact missing group
  membership + grant + who must run it, for a specific user + error.
- **An environment-isolation recommendation** — the chosen pattern, its cost model,
  and a ready-to-paste DAB `target` stub.
- **A role-chain status** up front — account-admin / metastore-admin / cloud-IAM,
  with the exact grant and grantor for anything missing.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `PERMISSION_DENIED` on `system.information_schema` | Principal is not metastore-admin, or system schemas not enabled | Step 1/2: report the missing role; an account admin enables system schemas, a metastore admin grants access. Stop until resolved. |
| No metastore attached to the workspace | UC not set up for this workspace | `databricks metastores current`; if empty, an account admin must create/assign a metastore before any migration. |
| `SYNC` fails with an unsupported-location error | Table is on a legacy scheme (`wasbs://`/`adl://`/`dbfs:/`) | It is BLOCKED, not READY — relocate per `uc-migration-blockers.md` (DEEP CLONE to a cloud path), then create the UC table. |
| Time travel broken after migration | Shallow `CREATE TABLE ... CLONE` was used | Use `DEEP CLONE` — shallow clone copies metadata only and drops Delta history. Re-clone with `DEEP CLONE`. See the gotcha in `uc-migration-blockers.md`. |
| `AccessDenied on s3://…` after a READY table migrates | UC storage credential's IAM role cannot assume the bucket | Trace with `/trace-uc-permission`; verify the external location's storage credential role and the bucket trust policy with read-only `aws` calls (D2). |
| DESCRIBE DETAIL returns no location | Orphaned HMS entry (deleted storage) or a view | The audit marks it ORPHAN — clean up or skip; never report it as a migration blocker. |
| `DATABRICKS_WAREHOUSE_ID` unset | No SQL warehouse for statement execution | Set it to a running warehouse before Step 1. |

## Examples

### Example 1: "How do I migrate off the Hive metastore?"

Runs the full pipeline. Step 1 confirms metastore-admin, Step 3 audits the schema
(`12 READY, 5 BLOCKED, 2 ORPHAN`), the planner emits a numbered order (`SYNC` the
12 ready Delta tables first, `DEEP CLONE` the 3 `dbfs:/user/hive` managed tables
to `s3://`, re-CREATE the 2 Parquet externals, skip the 2 orphans, then the 4
views), and the skill walks the plan — surfacing the Sept-30-2026 deadline and
the CLONE-history gotcha inline.

### Example 2: "Which of my tables can't migrate, and why?"

Step 3 only. The audit CSV lists each BLOCKED table with its scheme and the
one-line reason; the skill loads `uc-migration-blockers.md` for each class and
gives the physical relocation procedure per cloud.

### Example 3: "User can't read a table after we migrated it."

Routes straight to `/trace-uc-permission alice@corp.com "PERMISSION_DENIED:
SELECT on main.sales.orders"`. The tracer returns: *"alice@corp.com is in no group
with a grant; add her to `data-analysts` AND run `GRANT SELECT ON TABLE
main.sales.orders TO data-analysts` as metastore admin — she is not
account-admin, so the grant will not inherit."*

### Example 4: "How do I keep dev/test/prod separate under Unity Catalog?"

`/uc-env-pattern-picker` asks the compliance/cost/BI questions and, for a
cost-sensitive team that accepts shared lineage, recommends
single-metastore-catalog-per-env (`bronze_dev`/`bronze_prod`) with a DAB
`var.env`-parameterized target stub — noting the lineage-cleanliness tradeoff and
the multi-account alternative for hard isolation.

## Resources

- [`${CLAUDE_SKILL_DIR}/references/uc-migration-blockers.md`](references/uc-migration-blockers.md) — the taxonomy of un-migratable HMS conditions: canonical error, physical relocation procedure, per-cloud variant, and the CLONE-drops-history gotcha.
- [`${CLAUDE_SKILL_DIR}/references/uc-environment-isolation-patterns.md`](references/uc-environment-isolation-patterns.md) — the four dev/test/prod isolation patterns under one-metastore-per-region, with cost models and a DAB target stub.
- [`${CLAUDE_SKILL_DIR}/references/system-tables-access-model.md`](references/system-tables-access-model.md) — the two-layer access model (account-admin enables, metastore-admin grants), per-schema enablement, and the manual permission traversal.
- [`${CLAUDE_SKILL_DIR}/references/scim-bridge-patterns.md`](references/scim-bridge-patterns.md) — the Entra→Databricks SCIM nested-group limitation and the three workarounds.
- [`${CLAUDE_SKILL_DIR}/scripts/audit-hms-readiness.py`](scripts/audit-hms-readiness.py) — deterministic HMS-table readiness classifier (READY/BLOCKED/ORPHAN → CSV).
- [`${CLAUDE_SKILL_DIR}/scripts/enable-system-schemas.py`](scripts/enable-system-schemas.py) — idempotent system-schema enabler + group grant chain (account-admin auth precheck).
- [`${CLAUDE_SKILL_DIR}/agents/migration-planner.md`](agents/migration-planner.md) — turns the readiness CSV into a dependency-ordered plan.
- [`${CLAUDE_SKILL_DIR}/agents/uc-permission-tracer.md`](agents/uc-permission-tracer.md) — traces UC's two-level access model for a user + error.
- [Databricks: Upgrade to Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/migrate) · [`SYNC` command](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-sync) · [UCX (Databricks Labs)](https://github.com/databrickslabs/ucx)
