---
name: supabase-schema-from-requirements
description: 'Design Supabase Postgres schema from business requirements with migrations,
  RLS, and types.

  Use when translating specifications into database tables, creating migration files,

  adding Row Level Security policies, or generating TypeScript types from schema.

  Trigger with phrases like "supabase schema", "design database supabase",

  "schema from requirements", "supabase migration", "supabase tables from spec".

  '
allowed-tools: Read, Write, Bash(supabase:*), Bash(npx:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- database
- migration
- schema-design
- postgres
- rls
compatibility: Designed for Claude Code
---
# Supabase Schema from Requirements

## Overview

Translate business requirements into a production-ready Postgres schema inside Supabase, covering the full path from specification to applied migration: entity extraction, tables with proper types and constraints, Row Level Security policies, performance indexes, timestamp triggers, and TypeScript type generation. Getting this right early matters because every downstream feature — auth, storage, realtime, edge functions — depends on well-designed tables.

## Prerequisites

- Supabase CLI installed (`npm install --save-dev supabase`) and project linked (`supabase link`)
- `@supabase/supabase-js` v2+ installed in the project
- Business requirements, PRD, or specification document identifying entities and access rules
- Local Supabase running (`supabase start`) or a linked remote project

## Instructions

### Step 1: Parse Requirements and Create Migration

Read the requirements document and extract entities, attributes, relationships, and access control rules. Map each entity to a Postgres table.

**Entity extraction example** (project management app):

| Entity | Key Columns | Relationships |
| -------- | ------------ | --------------- |
| Organization | name, slug, plan | has many Projects, has many Members |
| Project | name, description, status | belongs to Organization, has many Tasks |
| Task | title, priority, status, due_date | belongs to Project, assigned to User |
| Member | role (owner/admin/member) | junction linking User to Organization |

Create the migration file:

```bash
npx supabase migration new create_tables
# Creates: supabase/migrations/TIMESTAMP_create_tables.sql
```

Write the migration SQL using standard Postgres data types (`uuid`, `text`, `integer`, `boolean`, `timestamptz`, `jsonb`):
Full worked migration (project-management app — tables, FKs, indexes, `moddatetime` triggers): [references/worked-schema-examples.md](references/worked-schema-examples.md).

**Data type selection guide:**

| Use case | Type | Notes |
| ---------- | ------ | ------- |
| Primary keys | `uuid` | Always with `uuid_generate_v4()` default |
| Names, titles | `text` | Prefer over `varchar` in Postgres |
| Counts, ranks | `integer` | Use `bigint` for sequences |
| Flags | `boolean` | Default explicitly to `true` or `false` |
| Timestamps | `timestamptz` | Never use `timestamp` without timezone |
| Flexible data | `jsonb` | Queryable JSON; use for settings, metadata |
| Lists | `text[]` | Postgres arrays for simple tags or labels |

### Step 2: Add Row Level Security Policies

Every table exposed to the client must have RLS enabled. Write reusable `security
definer` helper functions first, then write per-table policies that call them. The
skeleton for one table:

```sql
alter table public.organizations enable row level security;

create policy "Users read own orgs"
  on public.organizations for select
  using (public.is_org_member(id));
```

The full worked policy set — the `is_org_member` / `is_org_admin` helper functions and
every select/insert/update/delete policy across organizations, members, projects, and
tasks — is in [references/rls-policies.md](references/rls-policies.md). Name policies
after who and what action (`"Admins manage members"`, `"Assignee updates tasks"`).

### Step 3: Apply Migration and Generate Types

```bash
# Apply migration locally
npx supabase db reset

# Or push to a linked remote project
npx supabase db push

# Generate TypeScript types from the live schema
npx supabase gen types typescript --local > types/supabase.ts
```

Pass the generated `Database` type as the generic parameter to `createClient` (see
`import type { Database } from './types/supabase'`) for end-to-end type safety on every
query. Full typed-client walkthrough — typed inserts, foreign-key joins, nested multi-table
joins, and an RLS-enforcement check — is in
[references/typescript-client.md](references/typescript-client.md).

## Output

- SQL migration file under `supabase/migrations/` with all tables, constraints, and indexes
- RLS policies matching the access control rules from requirements
- Helper functions (`is_org_member`, `is_org_admin`) for reusable authorization checks
- `moddatetime` triggers for automatic `updated_at` management
- Generated TypeScript types at `types/supabase.ts` for type-safe client queries
- Partial indexes on frequently filtered columns (status, due_date)

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `42P07: relation already exists` | Table name collision in migration | Use `create table if not exists` or rename the table |
| `23503: foreign key violation` | Insert references a nonexistent parent row | Insert parent rows first, or check the UUID |
| `42501: insufficient privilege` | RLS helper function permissions | Add `security definer` to the function definition |
| `42883: function uuid_generate_v4() does not exist` | Extension not enabled | Add `create extension if not exists "uuid-ossp"` |
| `supabase db push` succeeds but tables missing | Migration was already recorded | Check `supabase_migrations.schema_migrations` and repair |
| `PGRST204: column not found` | TypeScript types out of sync | Re-run `npx supabase gen types typescript --local > types/supabase.ts` |
| `new row violates row-level security` | RLS policy blocks the operation | Verify `auth.uid()` matches expected value; check policy `using` clause |
| `moddatetime` trigger fails | Extension not enabled | Add `create extension if not exists "moddatetime"` at top of migration |

## Examples

**E-commerce schema** (different domain, same pattern). The complete e-commerce
migration SQL — stores, products, orders, order_items with FKs and indexes — is in
[references/worked-schema-examples.md](references/worked-schema-examples.md), and the
matching typed client queries are in
[references/typescript-client.md](references/typescript-client.md).

## Resources

- [Row Level Security Guide](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Database Migrations](https://supabase.com/docs/guides/deployment/database-migrations)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [JavaScript Client — Select](https://supabase.com/docs/reference/javascript/select)
- [TypeScript Support](https://supabase.com/docs/guides/api/rest/generating-types)
- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)

## Next Steps

For auth integration, file storage, and realtime subscriptions on top of this schema, proceed to `supabase-auth-storage-realtime-core`.
