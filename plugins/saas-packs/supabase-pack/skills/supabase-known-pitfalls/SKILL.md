---
name: supabase-known-pitfalls
description: |
  Use when reviewing Supabase code, onboarding developers, auditing an existing
  project, or debugging unexpected behavior — catches the twelve most common
  Supabase mistakes: exposing the service_role key in client bundles, forgetting
  to enable RLS, skipping connection pooling in serverless, .single() throwing on
  empty results, missing .select() after insert/update, ignoring { data, error },
  creating multiple client instances, and not using generated types.
  Trigger with phrases like "supabase mistakes", "supabase anti-patterns",
  "supabase pitfalls", "supabase code review", "supabase gotchas",
  "supabase debugging", "what not to do supabase", "supabase common errors".
allowed-tools: Read, Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- anti-patterns
- code-review
- debugging
- security
- pitfalls
compatibility: Designed for Claude Code
---
# Supabase Known Pitfalls

## Overview

The twelve most common Supabase mistakes, ranked by severity: **security** (service_role exposure, missing RLS, permissive policies, no connection pooling), **data integrity** (ignoring `{ data, error }`, missing `.select()` after mutations, `.single()` on optional results), and **performance / maintainability** (`select('*')`, N+1 queries, missing FK indexes, multiple client instances, no generated types). Each pitfall shows the broken code, why it fails, and the correct pattern using `createClient` from `@supabase/supabase-js`.

This SKILL.md carries the full pitfall table plus one representative fix per category. The verbatim broken-vs-correct code and detection queries for all twelve live in **[references/pitfalls.md](references/pitfalls.md)** — drill in there for depth.

## Prerequisites

- Access to a Supabase project codebase for review
- `@supabase/supabase-js` v2+ installed
- Basic understanding of Row Level Security (RLS)

## Instructions

Work the pitfalls top-down by severity. Fix every **Critical** finding before moving on — a single security miss can expose the whole database.

| # | Pitfall | Severity | Fix |
| --- | --------- | ---------- | ----- |
| 1 | service_role key in client bundle | Critical | anon key on client; service_role server-only, no `NEXT_PUBLIC_` |
| 2 | Table without RLS | Critical | `ALTER TABLE … ENABLE ROW LEVEL SECURITY` right after `CREATE TABLE` |
| 3 | Overly permissive RLS policy | Critical | scope `USING (…)` to `auth.uid()`, never `USING (true)` for writes |
| 4 | No connection pooling in serverless | Critical | pooled string (Supavisor, port 6543), not the direct 5432 URL |
| 5 | Ignoring `{ data, error }` | High | destructure both; check `error` before touching `data` |
| 6 | Missing `.select()` after mutation | High | chain `.select('cols')` — mutations return `null` otherwise |
| 7 | `.single()` on optional result | High | use `.maybeSingle()` for 0-or-1; `.single()` only for guaranteed 1 |
| 8 | `select('*')` everywhere | Medium | name the columns — smaller payload, typed, no leakage |
| 9 | N+1 query loop | Medium | PostgREST embedded join, or batch with `.in()` |
| 10 | FK column without index | Medium | `CREATE INDEX` on every foreign-key column |
| 11 | Multiple client instances | Low | singleton in `lib/supabase.ts`, imported everywhere |
| 12 | Hand-written DB types | Low | `supabase gen types typescript --linked` |

### Step 1 — Security (Critical, pitfalls 1-4)

The service_role key bypasses all RLS, so it must never reach a browser bundle. Split the client by trust boundary:

```typescript
// Client (browser): anon key — respects RLS
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)

// Server only (API routes, server actions): service_role, NO NEXT_PUBLIC_ prefix
const supabaseAdmin = createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { autoRefreshToken: false, persistSession: false } })
```

Then confirm RLS is enabled on every table, tighten any `USING (true)` policy to `auth.uid()`, and use the pooled connection string in serverless. Full broken-vs-correct code and the SQL detection queries for pitfalls 1-4 are in the Security section of [references/pitfalls.md](references/pitfalls.md).

### Step 2 — Data Integrity (High, pitfalls 5-7)

Supabase returns `{ data, error }` and mutations return `null` unless you ask for the row back:

```typescript
const { data, error } = await supabase
  .from('orders').insert(order)
  .select('id, status')   // without .select(), data is null
  .maybeSingle()          // .single() throws PGRST116 on 0 rows
if (error) throw new Error(`Order failed: ${error.message}`)
```

See the Data Integrity section of [references/pitfalls.md](references/pitfalls.md) for the `.single()` vs `.maybeSingle()` rule of thumb and each failure mode.

### Step 3 — Performance & Maintainability (Medium/Low, pitfalls 8-12)

Name your columns, collapse N+1 loops into a single embedded join, index foreign keys, share one client instance, and use generated types:

```typescript
// One query instead of 1 + N — PostgREST embeds the FK relation
const { data } = await supabase
  .from('projects')
  .select('id, name, tasks (id, title, status)')
```

The full singleton pattern, the FK-index detection query, and the `supabase gen types` workflow are in the Performance and Maintainability section of [references/pitfalls.md](references/pitfalls.md).

## Output

- Security pitfalls identified: service_role exposure, missing RLS, permissive policies, no connection pooling
- Data integrity pitfalls fixed: `{ data, error }` handling, `.select()` after mutations, `.maybeSingle()` usage
- Performance pitfalls resolved: column-specific selects, JOIN queries, FK indexes
- Maintainability improved: singleton client, generated types
- Detection commands for automated scanning of each pitfall

## Error Handling

| Issue | Cause | Solution |
| ------- | ------- | ---------- |
| `PGRST116: JSON object requested, multiple (or no) rows returned` | Used `.single()` when 0 or 2+ rows match | Use `.maybeSingle()` for optional lookups |
| `data` is `null` after insert | Missing `.select()` chain | Add `.select('column1, column2')` after `.insert()` |
| `TypeError: Cannot read property of null` | Destructured only `data`, ignoring `error` | Always destructure `{ data, error }` and check error first |
| `too many connections for role` | Direct connection from serverless | Use pooled connection string (port 6543) |
| `permission denied for table` | RLS blocking access, no matching policy | Check RLS policies match the authenticated user's JWT claims |
| `relation does not exist` | Table name typo, not caught at compile time | Use generated types for compile-time validation |

More operator-facing failure modes (legacy codebases, false positives, fixes that break tests): [references/errors.md](references/errors.md).

## Examples

### Quick Security Audit

```bash
# Check for the three critical code-level security pitfalls in one pass
echo "=== Pitfall 1: Service role in client code ==="
grep -rn 'SERVICE_ROLE' --include="*.tsx" --include="*.ts" src/ app/ components/ 2>/dev/null || echo "Clean"

echo "=== Pitfall 2: Tables without RLS (run in SQL Editor) ==="
echo "SELECT tablename FROM pg_tables WHERE schemaname='public' AND rowsecurity=false;"

echo "=== Pitfall 3: Overly permissive policies (run in SQL Editor) ==="
echo "SELECT tablename, policyname FROM pg_policies WHERE qual='true' AND cmd!='r';"
```

### Code Review Checklist

```markdown
### Security
- [ ] No SERVICE_ROLE_KEY in client-side code or NEXT_PUBLIC_* vars
- [ ] RLS enabled on all new tables; policies scope to auth.uid() (no USING(true) writes)
### Data Integrity
- [ ] All calls destructure { data, error } and check error
- [ ] .select() chained after insert/update/upsert; .maybeSingle() for optional lookups
### Performance & Maintainability
- [ ] Columns named in .select() (no select('*')); no N+1; FK columns indexed
- [ ] Single createClient instance; generated types; pooled connection string in serverless
```

More detection one-liners: [references/examples.md](references/examples.md). Every pitfall's full before/after code: [references/pitfalls.md](references/pitfalls.md).

## Resources

- [Supabase Auth: Securing Your Data](https://supabase.com/docs/guides/auth#securing-your-data)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [TypeScript Support](https://supabase.com/docs/reference/javascript/typescript-support)
- [Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Supabase JavaScript Client Reference](https://supabase.com/docs/reference/javascript/select)
- [PostgREST Error Codes](https://postgrest.org/en/stable/references/errors.html)

## Next Steps

This completes the Supabase pitfalls reference. To start a new project with best practices from day one, see `supabase-hello-world`.
