---
name: supabase-policy-guardrails
description: 'Enforce organizational governance for Supabase projects: shared RLS
  policy

  library with reusable templates, table and column naming conventions,

  migration review process with CI checks, cost alert thresholds,

  and security audit scripts scanning for common misconfigurations.

  Use when establishing Supabase standards across teams, creating RLS

  policy templates, setting up migration review workflows, or auditing

  existing projects for security and cost issues.

  Trigger with phrases like "supabase governance", "supabase policy library",

  "supabase naming convention", "supabase migration review",

  "supabase cost alert", "supabase security audit", "supabase RLS template".

  '
allowed-tools: Read, Write, Edit, Bash(supabase:*), Bash(psql:*), Bash(npx:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- governance
- security
- rls
- naming-conventions
- cost-management
compatibility: Designed for Claude Code
---
# Supabase Policy Guardrails

## Overview

Organizational governance for Supabase at scale: a **shared RLS policy library** (reusable templates for common access patterns), **naming conventions** (tables, columns, functions, policies), **migration review process** (CI checks ensuring RLS, preventing destructive operations, enforcing naming), **cost alert configuration** (billing thresholds and usage monitoring), and **security audit scripts** (scanning for exposed keys, missing RLS, overly permissive policies). All patterns use real `createClient` from `@supabase/supabase-js` and Supabase CLI commands.

## Prerequisites

- Supabase project with `supabase` CLI installed and linked
- `@supabase/supabase-js` v2+ installed
- CI/CD pipeline (GitHub Actions recommended)
- Database access via `psql` or Supabase SQL Editor
- Pro plan recommended for cost alerts and usage API

## Instructions

### Step 1 — Shared RLS Policy Library and Naming Conventions

#### RLS Policy Templates

Create reusable RLS policy templates that teams apply to new tables. This prevents each developer from writing ad-hoc policies and ensures consistent access control.

```sql
-- supabase/migrations/00000000000000_rls_policy_library.sql
-- Shared RLS policy library — apply these templates to new tables

-- ============================================================
-- Template 1: Owner-only access (user owns the row)
-- Usage: tables with a user_id column (todos, profiles, settings)
-- ============================================================
CREATE OR REPLACE FUNCTION public.rls_owner_only(table_name text, user_column text DEFAULT 'user_id')
RETURNS void AS $$
BEGIN
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);

  EXECUTE format(
    'CREATE POLICY "owner_select" ON public.%I FOR SELECT USING (%I = auth.uid())',
    table_name, user_column
  );
  EXECUTE format(
    'CREATE POLICY "owner_insert" ON public.%I FOR INSERT WITH CHECK (%I = auth.uid())',
    table_name, user_column
  );
  EXECUTE format(
    'CREATE POLICY "owner_update" ON public.%I FOR UPDATE USING (%I = auth.uid())',
    table_name, user_column
  );
  EXECUTE format(
    'CREATE POLICY "owner_delete" ON public.%I FOR DELETE USING (%I = auth.uid())',
    table_name, user_column
  );
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Template 2: Organization-scoped access (user is member of org)
-- Usage: tables with org_id referencing org_members
-- ============================================================
CREATE OR REPLACE FUNCTION public.rls_org_scoped(
  table_name text,
  org_column text DEFAULT 'org_id',
  allow_delete boolean DEFAULT false
)
RETURNS void AS $$
BEGIN
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);

  EXECUTE format(
    'CREATE POLICY "org_select" ON public.%I FOR SELECT USING (
      %I IN (SELECT org_id FROM public.org_members WHERE user_id = auth.uid())
    )', table_name, org_column
  );
  EXECUTE format(
    'CREATE POLICY "org_insert" ON public.%I FOR INSERT WITH CHECK (
      %I IN (SELECT org_id FROM public.org_members WHERE user_id = auth.uid())
    )', table_name, org_column
  );
  EXECUTE format(
    'CREATE POLICY "org_update" ON public.%I FOR UPDATE USING (
      %I IN (SELECT org_id FROM public.org_members WHERE user_id = auth.uid() AND role IN (''admin'', ''editor''))
    )', table_name, org_column
  );

  IF allow_delete THEN
    EXECUTE format(
      'CREATE POLICY "org_delete" ON public.%I FOR DELETE USING (
        %I IN (SELECT org_id FROM public.org_members WHERE user_id = auth.uid() AND role = ''admin'')
      )', table_name, org_column
    );
  END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Template 3: Public read, authenticated write
-- Usage: blog posts, product listings, public content
-- ============================================================
CREATE OR REPLACE FUNCTION public.rls_public_read_auth_write(
  table_name text,
  owner_column text DEFAULT 'created_by'
)
RETURNS void AS $$
BEGIN
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);

  EXECUTE format(
    'CREATE POLICY "public_select" ON public.%I FOR SELECT USING (true)',
    table_name
  );
  EXECUTE format(
    'CREATE POLICY "auth_insert" ON public.%I FOR INSERT WITH CHECK (auth.uid() IS NOT NULL)',
    table_name
  );
  EXECUTE format(
    'CREATE POLICY "owner_update" ON public.%I FOR UPDATE USING (%I = auth.uid())',
    table_name, owner_column
  );
  EXECUTE format(
    'CREATE POLICY "owner_delete" ON public.%I FOR DELETE USING (%I = auth.uid())',
    table_name, owner_column
  );
END;
$$ LANGUAGE plpgsql;

-- Apply templates to tables:
-- SELECT public.rls_owner_only('todos');
-- SELECT public.rls_org_scoped('projects', 'org_id', true);
-- SELECT public.rls_public_read_auth_write('blog_posts', 'author_id');
```

#### Naming Conventions

```sql
-- supabase/migrations/00000000000001_naming_convention_check.sql
-- Validation function that checks naming conventions at migration time

CREATE OR REPLACE FUNCTION public.validate_naming_conventions()
RETURNS TABLE(issue text, object_name text, suggestion text) AS $$
BEGIN
  -- Tables must be snake_case, plural
  RETURN QUERY
  SELECT
    'Table name should be plural snake_case'::text,
    t.tablename::text,
    regexp_replace(t.tablename, '([A-Z])', '_\1', 'g')::text
  FROM pg_tables t
  WHERE t.schemaname = 'public'
  AND (
    t.tablename ~ '[A-Z]'           -- contains uppercase
    OR t.tablename ~ '-'             -- contains hyphens
    OR t.tablename !~ 's$'           -- not plural (heuristic)
  )
  AND t.tablename NOT LIKE '\_%';   -- skip internal tables

  -- Columns must be snake_case
  RETURN QUERY
  SELECT
    'Column name should be snake_case'::text,
    (c.table_name || '.' || c.column_name)::text,
    regexp_replace(c.column_name, '([A-Z])', '_\1', 'g')::text
  FROM information_schema.columns c
  WHERE c.table_schema = 'public'
  AND (c.column_name ~ '[A-Z]' OR c.column_name ~ '-');

  -- Foreign key columns should end with _id
  RETURN QUERY
  SELECT
    'Foreign key column should end with _id'::text,
    (tc.table_name || '.' || kcu.column_name)::text,
    (kcu.column_name || '_id')::text
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND kcu.column_name NOT LIKE '%_id';

  -- Boolean columns should start with is_ or has_
  RETURN QUERY
  SELECT
    'Boolean column should start with is_ or has_'::text,
    (c.table_name || '.' || c.column_name)::text,
    ('is_' || c.column_name)::text
  FROM information_schema.columns c
  WHERE c.table_schema = 'public'
  AND c.data_type = 'boolean'
  AND c.column_name NOT LIKE 'is_%'
  AND c.column_name NOT LIKE 'has_%';
END;
$$ LANGUAGE plpgsql;

-- Run: SELECT * FROM public.validate_naming_conventions();
```

#### Naming Convention Reference

| Object | Convention | Example |
|--------|-----------|---------|
| Tables | Plural snake_case | `user_profiles`, `order_items` |
| Columns | snake_case | `created_at`, `full_name` |
| Foreign keys | `{referenced_table_singular}_id` | `user_id`, `order_id` |
| Booleans | `is_` or `has_` prefix | `is_active`, `has_verified_email` |
| Timestamps | `_at` suffix | `created_at`, `updated_at`, `deleted_at` |
| RLS policies | `{scope}_{operation}` | `owner_select`, `org_insert` |
| Functions | `verb_noun` | `create_user`, `get_dashboard_metrics` |
| Indexes | `idx_{table}_{columns}` | `idx_orders_user_id_created_at` |
| Migrations | `{timestamp}_{verb}_{description}` | `20250322000000_create_orders_table.sql` |

### Step 2 — Migration Review Process with CI Checks

See [CI checks, cost alerts, and security audits](references/ci-cost-security.md) for GitHub Actions migration guardrails (RLS enforcement, naming checks, destructive operation blocks), pre-commit hooks, cost monitoring with Slack alerts, security audit scripts, and scheduled Edge Function audits.

## Output

- Shared RLS policy library with owner-only, org-scoped, and public-read templates
- Naming convention validation function checking tables, columns, FKs, and booleans
- CI pipeline enforcing RLS, naming, and destructive operation controls
- Pre-commit hook blocking hardcoded secrets and tables without RLS
- Cost monitoring script with configurable thresholds and Slack alerting
- Security audit script detecting missing RLS, permissive policies, and missing indexes
- Scheduled Edge Function for continuous security monitoring

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| CI RLS check fails on new table | Migration missing `ENABLE ROW LEVEL SECURITY` | Add `ALTER TABLE` after `CREATE TABLE` in same migration |
| Naming convention false positive | Table is intentionally singular (e.g., `config`) | Add to exclusion list in validation function |
| Cost alert not firing | Missing `SUPABASE_ACCESS_TOKEN` | Generate token at supabase.com/dashboard/account/tokens |
| Security audit times out | Too many tables to scan | Run audit on specific schemas or paginate results |
| Pre-commit blocks legitimate JWT in test | Test fixture contains JWT-like string | Add test file path to exclusion pattern |
| RLS template function not found | Migration not applied | Run `supabase db reset` or apply migration manually |

## Examples

See [CI, cost, and security reference](references/ci-cost-security.md) for full examples including applying RLS templates, running security audits, and checking naming conventions.

## Resources

- [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase CLI Migrations](https://supabase.com/docs/guides/cli/managing-environments)
- [Supabase Management API](https://supabase.com/docs/reference/api/introduction)
- [Supabase Pricing](https://supabase.com/pricing)
- [PostgreSQL Naming Conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS)

## Next Steps

For architecture patterns across different app types, see `supabase-architecture-variants`.
