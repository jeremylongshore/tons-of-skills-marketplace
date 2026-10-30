---
name: supabase-migration-deep-dive
description: |
  Database migration patterns with the Supabase CLI: npx supabase migration new,
  zero-downtime migrations, data backfill strategies, schema versioning, rollback
  strategies, and TypeScript type generation.
  Use when creating database migrations, performing zero-downtime schema changes,
  backfilling data in production, managing schema versions, or planning rollback
  strategies.
  Trigger with "supabase migration", "supabase schema change", "supabase zero
  downtime", "supabase rollback", "supabase db push", "supabase migration new".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(supabase:*), Bash(psql:*),
  Grep, Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- migration
- database
- schema
- zero-downtime
- rollback
compatibility: Designed for Claude Code
---
# Supabase Migration Deep Dive

## Overview

Supabase migrations are timestamped SQL files managed by the CLI that track schema changes across environments. This skill covers the full lifecycle — creating migrations, zero-downtime schema changes, batch backfills, versioning, rollback, and TypeScript type generation — using real CLI commands and `createClient` from `@supabase/supabase-js`.

**When to use:** Creating new database migrations, modifying production schemas without downtime, backfilling existing data after adding columns, managing migration history across dev/staging/production, rolling back failed migrations, or regenerating TypeScript types.

## Prerequisites

- Supabase CLI installed: `npm install --save-dev supabase` or `npx supabase --version`
- `@supabase/supabase-js` v2+ installed in your project
- Local Supabase running: `npx supabase start`
- Understanding of PostgreSQL DDL and transaction behavior

## Instructions

### Step 1: Create and Manage Migrations

Create each migration as a timestamped SQL file, write the DDL, test it against a local reset, then promote it through environments with `db push`:

```bash
npx supabase migration new add_profiles_table   # create timestamped SQL file
npx supabase migration list                      # show applied/pending status
npx supabase db reset                            # apply + seed locally (destructive)
npx supabase gen types typescript --local > lib/database.types.ts
npx supabase link --project-ref "<ref>" && npx supabase db push   # promote to remote
```

Write DDL that enables RLS, adds policies, indexes, and triggers in the same file so the schema is complete when applied. For the full worked migration (a `profiles` table with RLS policies, an email index, a signup trigger, and an `updated_at` trigger) plus the local-test and staging/production promotion commands, see [creating migrations](references/creating-migrations.md).

### Step 2: Zero-Downtime Migration Patterns

Production schema changes must avoid locking tables. The core rules: adding a nullable column with a default is lock-free on Postgres 11+; build indexes with `CREATE INDEX CONCURRENTLY` in a `-- supabase:disable-transaction` migration; rename or retype a column in two phases (add new column, backfill, sync trigger, then drop the old one) rather than an in-place `ALTER COLUMN`. Example of the safe column-add:

```sql
-- Nullable column with a default does NOT lock the table in Postgres 11+
ALTER TABLE public.orders ADD COLUMN status text DEFAULT 'pending';
-- Then, in a separate -- supabase:disable-transaction migration:
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status ON public.orders(status);
```

For the complete set — two-phase column rename with a sync trigger, safe type change via add-backfill-swap, and an SDK health-check that samples query latency during the migration — see [zero-downtime patterns](references/zero-downtime-patterns.md).

### Step 3: Data Backfill, Versioning, and Rollback

See [data backfill, versioning, and rollback](references/backfill-versioning-rollback.md) for batch backfill patterns with the SDK, schema versioning across environments, three rollback strategies (compensating migration, repair, feature flags), and type regeneration after migrations.

## Output

This skill produces:

- **Migration creation workflow** — `npx supabase migration new` with descriptive SQL files and local testing
- **Zero-downtime patterns** — safe column additions, two-phase renames, concurrent index creation
- **Batch backfill** — SDK-based row-by-row updates with progress logging and rate limiting
- **Schema versioning** — `supabase migration list` and `db diff` for comparing environments
- **Rollback strategies** — compensating migrations, `migration repair`, and feature-flagged schema changes
- **Type regeneration** — `supabase gen types typescript` after every schema change
- **Migration promotion** — `db push` workflow from local to staging to production

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `migration has already been applied` | Re-running existing migration | Use `supabase migration list` to check status; never modify applied migrations |
| `cannot run inside a transaction block` | `CREATE INDEX CONCURRENTLY` in transaction | Add `-- supabase:disable-transaction` comment at top of migration file |
| `column does not exist` after migration | Migration not applied or types stale | Run `supabase db push` then `supabase gen types typescript` |
| `deadlock detected` during backfill | Concurrent updates on same rows | Reduce batch size; add retry logic with exponential backoff |
| `statement timeout` on large table | Migration takes longer than timeout | Increase `statement_timeout` in migration: `SET statement_timeout = '300s';` |
| `migration repair` failed | Wrong version number | Use exact version from `supabase migration list` (the timestamp prefix) |
| `db diff` shows unexpected changes | Schema drift from manual SQL Editor changes | Run `supabase db pull` to capture manual changes as a migration |
| Type mismatch after migration | Generated types don't match new schema | Delete `database.types.ts` and regenerate from `--local` or `--linked` |

## Examples

The create-write-test-push workflow for a real column addition:

```text
npx supabase migration new add_tags_to_projects
cat > supabase/migrations/20260322150000_add_tags_to_projects.sql << 'SQL'
ALTER TABLE public.projects ADD COLUMN tags text[] DEFAULT '{}';
CREATE INDEX idx_projects_tags ON public.projects USING GIN(tags);
SQL
npx supabase db reset
npx supabase gen types typescript --local > lib/database.types.ts
npx supabase link --project-ref <staging-ref> && npx supabase db push
```

See [examples](references/examples.md) for three full worked examples: the complete local-to-production migration workflow, a batch backfill with progress tracking from the SDK, and a safe enum migration using a `CHECK` constraint instead of `ALTER TYPE`.

## Resources

- [Database Migrations — Supabase Docs](https://supabase.com/docs/guides/deployment/database-migrations)
- [Supabase CLI Migration Commands](https://supabase.com/docs/reference/cli/supabase-migration)
- [supabase db push — Supabase Docs](https://supabase.com/docs/reference/cli/supabase-db-push)
- [supabase gen types — Supabase Docs](https://supabase.com/docs/reference/cli/supabase-gen-types)
- [Zero-Downtime PostgreSQL Migrations](https://www.postgresql.org/docs/current/sql-altertable.html)
- [supabase db diff — Supabase Docs](https://supabase.com/docs/reference/cli/supabase-db-diff)

## Next Steps

- For advanced troubleshooting after migrations, see `supabase-advanced-troubleshooting`
- For multi-environment migration promotion, see `supabase-multi-env-setup`
- For performance tuning after schema changes, see `supabase-performance-tuning`
