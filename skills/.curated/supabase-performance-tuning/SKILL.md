---
name: supabase-performance-tuning
description: 'Optimize Supabase query performance with indexes, EXPLAIN ANALYZE, connection
  pooling,

  column selection, pagination, RPC functions, materialized views, and diagnostics.

  Use when queries are slow, connections are exhausted, response payloads are bloated,

  or when preparing a Supabase project for production-scale traffic.

  Trigger with phrases like "supabase performance", "supabase slow queries",

  "optimize supabase", "supabase index", "supabase connection pool",

  "supabase pagination", "supabase explain analyze".

  '
allowed-tools: Read, Write, Edit, Bash(npx:supabase), Bash(supabase:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- performance
- optimization
- postgres
compatibility: Designed for Claude Code
---
# Supabase Performance Tuning

## Overview

Systematically improve Supabase query and database performance across three layers: PostgreSQL engine (indexes, query plans, materialized views), Supabase infrastructure (Supavisor connection pooling, Edge Functions, read replicas), and client SDK patterns (column selection, pagination, RPC functions). Every technique here is measurable — run `EXPLAIN ANALYZE` before and after to confirm the improvement.

## Prerequisites

- Supabase project (local or hosted) with `@supabase/supabase-js` v2+ installed
- Supabase CLI installed (`npx supabase --version` to verify)
- Access to the SQL Editor in the Supabase Dashboard or a direct Postgres connection
- `pg_stat_statements` extension enabled (Step 1 covers this)

## Instructions

### Step 1: Diagnose — Find What Is Slow

Start every performance effort with data. Enable `pg_stat_statements` and run the Supabase CLI diagnostics to identify bottlenecks before optimizing.

**Enable the stats extension:**

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**Find the slowest queries by average execution time:**

```sql
SELECT
  query,
  calls,
  mean_exec_time::numeric(10,2) AS avg_ms,
  total_exec_time::numeric(10,2) AS total_ms,
  rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Check index usage and cache hit rates with the Supabase CLI:**

```bash
# Which indexes are actually being used?
npx supabase inspect db index-usage

# What percentage of queries are served from cache vs disk?
npx supabase inspect db cache-hit

# Tables consuming the most space
npx supabase inspect db table-sizes
```

**Inspect active connections for pooling issues:**

```sql
SELECT state, count(*), max(age(now(), state_change)) AS max_age
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;
```

If `idle` connections exceed your plan's limit or `active` queries show high `max_age`, connection pooling (Step 2) and query optimization (Step 3) are the priority.

### Step 2: Indexes and Query Plans

Indexes are the single highest-impact optimization. Use `EXPLAIN ANALYZE` to read query plans, then create targeted indexes.

**Read a query plan:**

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email = 'alice@example.com';
```

Look for `Seq Scan` on large tables — that means no index is being used. After adding an index, the plan should show `Index Scan` or `Index Only Scan`.

**Create a basic index:**

```sql
CREATE INDEX idx_users_email ON users(email);
```

**Create a composite index for multi-column filters:**

```sql
-- Optimizes: WHERE user_id = ? AND created_at > ? ORDER BY created_at DESC
CREATE INDEX idx_orders_user_created
  ON orders(user_id, created_at DESC);
```

**Create a partial index to cover a common filter pattern:**

```sql
-- Only indexes incomplete todos — much smaller and faster than full-table index
CREATE INDEX idx_todos_user_incomplete
  ON todos(user_id, inserted_at DESC)
  WHERE is_complete = false;
```

**Find missing indexes on foreign keys (common source of slow JOINs):**

```sql
SELECT
  tc.table_name,
  kcu.column_name AS fk_column,
  'CREATE INDEX idx_' || tc.table_name || '_' || kcu.column_name
    || ' ON public.' || tc.table_name || '(' || kcu.column_name || ');' AS fix
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
LEFT JOIN pg_indexes i
  ON i.tablename = tc.table_name
  AND i.indexdef LIKE '%' || kcu.column_name || '%'
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND i.indexname IS NULL;
```

**Find unused indexes (candidates for removal to reduce write overhead):**

```sql
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

Always use `CREATE INDEX CONCURRENTLY` on production tables to avoid locking writes during index creation.

### Step 3: Client SDK and Infrastructure Optimization

Optimize the Supabase JS client calls, then leverage infrastructure features for scale.

**Select only needed columns — avoid `select('*')`:**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

// BAD: fetches every column, large payloads
const { data } = await supabase.from('users').select('*')

// GOOD: only the columns you need
const { data } = await supabase.from('users').select('id, name, avatar_url')
```

**Paginate with `.range()` instead of loading all rows:**

```typescript
// Page 1: rows 0-49
const { data: page1 } = await supabase
  .from('products')
  .select('id, name, price')
  .order('created_at', { ascending: false })
  .range(0, 49)

// Page 2: rows 50-99
const { data: page2 } = await supabase
  .from('products')
  .select('id, name, price')
  .order('created_at', { ascending: false })
  .range(50, 99)
```

**Use RPC functions to push complex logic to Postgres:**

```sql
-- Create a server-side function for an expensive aggregation
CREATE OR REPLACE FUNCTION get_dashboard_stats(org_id uuid)
RETURNS json AS $$
  SELECT json_build_object(
    'total_users', (SELECT count(*) FROM users WHERE organization_id = org_id),
    'active_projects', (SELECT count(*) FROM projects WHERE organization_id = org_id AND status = 'active'),
    'tasks_completed_30d', (SELECT count(*) FROM tasks t
      JOIN projects p ON p.id = t.project_id
      WHERE p.organization_id = org_id
      AND t.completed_at > now() - interval '30 days')
  );
$$ LANGUAGE sql STABLE;
```

```typescript
// One network call instead of three separate queries
const { data } = await supabase.rpc('get_dashboard_stats', {
  org_id: 'your-org-uuid'
})
```

**Create materialized views for expensive aggregations:**

```sql
-- Precompute a leaderboard instead of recalculating on every request
CREATE MATERIALIZED VIEW leaderboard AS
SELECT
  u.id,
  u.username,
  count(t.id) AS tasks_completed,
  rank() OVER (ORDER BY count(t.id) DESC) AS rank
FROM users u
LEFT JOIN tasks t ON t.assignee_id = u.id AND t.status = 'done'
GROUP BY u.id, u.username;

-- Create an index on the materialized view
CREATE UNIQUE INDEX idx_leaderboard_user ON leaderboard(id);

-- Refresh on a schedule (e.g., via pg_cron or a cron Edge Function)
REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard;
```

**Configure connection pooling with Supavisor:**

```typescript
// For serverless environments (Vercel, Netlify, Cloudflare Workers):
// Use the pooled connection string with transaction mode
// Dashboard → Settings → Database → Connection string → "Transaction mode"

// The JS SDK uses PostgREST (HTTP) which has its own pooling — no config needed.
// Direct Postgres clients (Prisma, Drizzle, pg) need the pooled string:
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.SUPABASE_DATABASE_URL,
  max: 5,  // Keep low in serverless — Supavisor manages the upstream pool
  idleTimeoutMillis: 10000,
})
```

**Use Edge Functions for compute-heavy operations close to data:**

```typescript
// supabase/functions/generate-report/index.ts
// Edge Functions run in the same region as your database — low latency
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Heavy aggregation runs next to the database, not in the user's browser
  const { data } = await supabase.rpc('get_dashboard_stats', {
    org_id: (await req.json()).org_id
  })

  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' }
  })
})
```

**Enable read replicas on Pro+ plans** for read-heavy workloads — route analytics and reporting queries to the replica to offload the primary.

## Output

After completing these steps, you will have:

- Diagnostic baseline from `pg_stat_statements`, `index-usage`, and `cache-hit`
- Targeted indexes on slow query columns, foreign keys, and common filter patterns
- Query plans verified with `EXPLAIN ANALYZE` showing Index Scan instead of Seq Scan
- Client queries optimized with column selection, pagination, and joined queries
- RPC functions and materialized views for expensive server-side aggregations
- Connection pooling configured via Supavisor for serverless deployments
- Edge Functions deployed for compute-heavy operations near the database

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Seq Scan` in EXPLAIN output on large table | Missing index on filtered/sorted column | `CREATE INDEX` on the column(s) in the WHERE/ORDER BY clause |
| `PGRST000: could not connect to server` | Connection pool exhausted | Switch to Supavisor pooled connection string; reduce `max` pool size in serverless |
| Slow RLS policies (visible in `pg_stat_statements`) | Subquery in policy evaluates per row | Refactor to `security definer` function or use `EXISTS` instead of `IN` |
| Response payloads > 1MB | `select('*')` returning all columns/rows | Use `.select('col1, col2')` and `.range()` for pagination |
| Stale materialized view data | View not refreshed after writes | Set up `pg_cron` or a cron Edge Function to run `REFRESH MATERIALIZED VIEW CONCURRENTLY` |
| `cache-hit` ratio below 99% | Working set exceeds RAM (shared_buffers) | Upgrade compute add-on or optimize queries to access fewer pages |
| High latency on aggregation endpoints | Aggregation computed live on every request | Move to materialized view or RPC function; cache at the Edge Function layer |

## Examples

**Before/after index optimization:**

```sql
-- Before: 450ms, Seq Scan
EXPLAIN (ANALYZE) SELECT * FROM orders WHERE customer_id = 'abc-123';
-- Seq Scan on orders  (cost=0.00..15234.00 rows=50 width=128) (actual time=0.015..450.123 rows=50 loops=1)

CREATE INDEX idx_orders_customer ON orders(customer_id);

-- After: 0.8ms, Index Scan
EXPLAIN (ANALYZE) SELECT * FROM orders WHERE customer_id = 'abc-123';
-- Index Scan using idx_orders_customer on orders  (cost=0.42..8.44 rows=50 width=128) (actual time=0.025..0.812 rows=50 loops=1)
```

**Client query optimization — eliminating N+1:**

```typescript
// BAD: N+1 — one query per project (10 projects = 11 queries)
const { data: projects } = await supabase.from('projects').select('id, name')
for (const project of projects!) {
  const { data: tasks } = await supabase
    .from('tasks').select('*').eq('project_id', project.id)
}

// GOOD: Single query with embedded join (1 query total)
const { data } = await supabase
  .from('projects')
  .select('id, name, tasks(id, title, status)')
  .eq('organization_id', orgId)
```

## Resources

- [Supabase Performance Advisor](https://supabase.com/docs/guides/database/inspect) — built-in CLI diagnostics
- [PostgreSQL Index Types](https://supabase.com/docs/guides/database/postgres/indexes) — B-tree, GIN, GiST, and when to use each
- [Connection Pooling with Supavisor](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler) — transaction vs session mode
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions) — deploy serverless functions next to your database
- [Read Replicas](https://supabase.com/docs/guides/platform/read-replicas) — offload read-heavy queries on Pro+ plans
- [RLS Performance Best Practices](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv) — avoid per-row subqueries

## Next Steps

- For RLS policy design, see `supabase-rls-policies`
- For cost optimization, see `supabase-cost-tuning`
- For real-time subscriptions, see `supabase-realtime`
