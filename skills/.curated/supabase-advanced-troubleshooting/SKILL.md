---
name: supabase-advanced-troubleshooting
description: |
  Deep Supabase diagnostics: pg_stat_statements for slow queries, lock debugging
  with pg_locks, connection leak detection, RLS policy conflicts, Edge Function
  cold starts, and Realtime connection drop analysis.
  Use when standard troubleshooting fails, when investigating performance
  regressions, when debugging race conditions, or when building evidence for a
  Supabase support escalation.
  Trigger with "supabase deep debug", "supabase slow query", "supabase lock
  contention", "supabase connection leak", "supabase RLS conflict", "supabase
  cold start".
allowed-tools: Read, Grep, Bash(npx supabase:*), Bash(supabase:*), Bash(curl:*), Bash(psql:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- debugging
- advanced
- performance
- troubleshooting
compatibility: Designed for Claude Code
---
# Supabase Advanced Troubleshooting

## Overview

When basic debugging does not reveal the root cause, you need deep PostgreSQL diagnostics: `pg_stat_statements` to find the slowest queries by cumulative execution time, `pg_locks` to detect lock contention and deadlocks, `pg_stat_activity` to find connection leaks, RLS policy conflict analysis to diagnose silent data filtering, Edge Function cold start profiling, and Realtime channel drop investigation. This skill covers every advanced diagnostic technique with real SQL queries and `createClient` from `@supabase/supabase-js`.

**When to use:** Slow query investigation, lock contention causing timeouts, connection pool exhaustion from leaks, RLS policies that silently filter or conflict, Edge Functions with unpredictable latency, or Realtime subscriptions that disconnect intermittently.

## Prerequisites

- Supabase project with `pg_stat_statements` extension enabled
- Direct database access via SQL Editor or `psql`
- `@supabase/supabase-js` v2+ installed in your project
- Dashboard access to the selected Edge Function’s Logs and Invocations panels
- Familiarity with PostgreSQL system catalogs

## Authentication

Every technique here runs against your own project's Postgres, so authenticate with
project-scoped credentials, never a shared key:

- **`psql` / SQL Editor** — connect with the project's direct connection string or
  pooled Supavisor URI from Dashboard → Settings → Database. Keep the database
  password in an env var (`PGPASSWORD` / `.pgpass`), never inline in a command.
- **SDK (`createClient`)** — pass the **service-role key** (`SUPABASE_SERVICE_ROLE_KEY`)
  for the diagnostic RPCs below, since they read `pg_stat_activity` and system
  catalogs that the anon key cannot. Load it from the environment; never commit it.
- **Remote Edge Function logs** — use the selected project’s Dashboard Logs and
  Invocations panels with approved project access. The CLI has no remote
  `functions logs` command; local `functions serve` output is not remote evidence.

## Instructions

Work the three diagnostic tracks in the order the symptom points to. Each track's
full query set and SDK helper lives in a reference file — SKILL.md carries the
skeleton so you can start immediately, then drill in for the complete toolkit.

### Step 1: pg_stat_statements and slow query analysis

Enable `pg_stat_statements`, then rank queries by total execution time, call
frequency, and cache-hit ratio to find the real cost centers. Follow up with
`EXPLAIN (ANALYZE, BUFFERS)` on the worst offenders and add targeted indexes with
`CREATE INDEX CONCURRENTLY`. The starter query:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT queryid, calls,
  round(total_exec_time::numeric, 2) AS total_ms,
  round(mean_exec_time::numeric, 2)  AS avg_ms,
  left(query, 150) AS query_preview
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

The full toolkit — frequency and cache-hit-ratio rankings, the `EXPLAIN ANALYZE`
reading guide, and a `timedQuery` SDK wrapper that flags any call over 500 ms — is
in [slow query analysis](references/slow-query-analysis.md).

### Step 2: lock debugging and connection leak detection

Find blocked/blocking query pairs via `pg_locks` joined to `pg_stat_activity`,
then hunt connection leaks — especially `idle in transaction` backends, which hold
locks and exhaust the pool. The starter query surfaces who is blocked and who holds
the lock:

```sql
SELECT blocked.pid AS blocked_pid, blocking.pid AS blocking_pid,
  bl.mode AS lock_mode, left(blocked.query, 80) AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks kl ON kl.relation = bl.relation AND kl.granted AND kl.pid != bl.pid
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE blocked.state = 'active';
```

The full toolkit — deadlock detection, idle/idle-in-transaction leak queries with
`pg_terminate_backend` cleanup, and a `get_connection_health` RPC with utilization
alerts — is in [lock and connection diagnostics](references/lock-connection-diagnostics.md).

### Step 3: RLS conflicts, Edge Function cold starts, and Realtime drops

Diagnose silent RLS data filtering, profile Edge Function cold-vs-warm latency, and
trace Realtime channel drops. The full walkthrough — RLS policy conflict analysis
(SQL and SDK), cold start profiling, channel-state monitoring, and publication
configuration — is in [RLS, Edge Functions, and Realtime](references/rls-edge-functions-realtime.md).

## Output

This skill produces the following diagnostic artifacts:

- **Slow query identification** — `pg_stat_statements` queries ranking by total time, frequency, and cache hit ratio
- **EXPLAIN ANALYZE proficiency** — reading execution plans and creating targeted indexes
- **Lock contention diagnosis** — blocked/blocking query pairs with lock modes
- **Connection leak detection** — idle and idle-in-transaction connections with kill commands
- **Connection pool monitoring** — SDK-based health check RPC with utilization alerts
- **RLS conflict analysis** — policy listing with permissive/restrictive classification and multi-level comparison
- **Edge Function profiling** — cold start vs warm invocation measurement
- **Realtime debugging** — channel state monitoring with system event logging

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `pg_stat_statements` not available | Extension not enabled | Run `CREATE EXTENSION pg_stat_statements;` |
| Seq Scan on large table | Missing index on filter column | Create index with `CREATE INDEX CONCURRENTLY` |
| `deadlock detected` | Circular lock dependency | Ensure consistent lock ordering across transactions |
| All connections in `idle in transaction` | Application not closing transactions | Add connection timeout; review ORM connection pool settings |
| RLS returns empty for authenticated user | JWT claims don't match policy | Check `auth.jwt()` output; verify `app_metadata` is set |
| Edge Function > 2s cold start | Large dependency bundle | Lazy-import heavy modules; reduce function size |
| Realtime `TIMED_OUT` | Network/firewall blocking WebSocket | Check port 443 (HTTPS/WSS) is open outbound; verify no proxy strips the `Upgrade` header |
| `CHANNEL_ERROR` on subscribe | Table not in Realtime publication | Run `ALTER PUBLICATION supabase_realtime ADD TABLE ...` |

## Examples

**Example 1 — Quick performance audit:**

```sql
-- Run this query to get a snapshot of database health
SELECT
  'Connections' AS metric,
  count(*)::text AS value
FROM pg_stat_activity WHERE datname = current_database()
UNION ALL
SELECT 'Cache hit ratio',
  round(100.0 * sum(heap_blks_hit) / nullif(sum(heap_blks_hit + heap_blks_read), 0), 2)::text || '%'
FROM pg_statio_user_tables
UNION ALL
SELECT 'Table bloat (dead tuples)',
  sum(n_dead_tup)::text
FROM pg_stat_user_tables
UNION ALL
SELECT 'Longest running query',
  coalesce(max(age(now(), query_start))::text, 'none')
FROM pg_stat_activity WHERE state = 'active' AND query NOT LIKE '%pg_stat%';
```

**Example 2 — Build a diagnostic bundle for support:**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function buildDiagnosticBundle() {
  const bundle: Record<string, any> = {
    timestamp: new Date().toISOString(),
    projectRef: process.env.SUPABASE_PROJECT_REF,
  };

  // Connection stats
  const { data: connHealth } = await supabase.rpc('get_connection_health');
  bundle.connections = connHealth;

  // Table sizes
  const { data: tableSizes } = await supabase.rpc('get_table_sizes');
  bundle.tableSizes = tableSizes;

  // Recent errors from application logs
  const { data: recentErrors } = await supabase
    .from('error_logs')
    .select('message, count, last_seen')
    .order('last_seen', { ascending: false })
    .limit(10);
  bundle.recentErrors = recentErrors;

  console.log(JSON.stringify(bundle, null, 2));
  // Submit with your support ticket at https://supabase.com/dashboard/support
}
```

**Example 3 — Automated slow query alert:**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function checkSlowQueries(thresholdMs = 1000) {
  const { data: slowQueries } = await supabase.rpc('get_slow_queries', {
    threshold_ms: thresholdMs,
  });

  if (slowQueries && slowQueries.length > 0) {
    console.warn(`Found ${slowQueries.length} queries averaging > ${thresholdMs}ms`);
    for (const q of slowQueries) {
      console.warn(`  [${q.avg_ms}ms avg, ${q.calls} calls] ${q.query_preview}`);
    }
  }
}

// Database function:
// CREATE OR REPLACE FUNCTION get_slow_queries(threshold_ms numeric DEFAULT 1000)
// RETURNS TABLE(queryid bigint, avg_ms numeric, calls bigint, query_preview text) AS $$
//   SELECT queryid, round(mean_exec_time::numeric, 2), calls, left(query, 150)
//   FROM pg_stat_statements
//   WHERE mean_exec_time > threshold_ms AND calls > 10
//   ORDER BY mean_exec_time DESC LIMIT 10;
// $$ LANGUAGE sql SECURITY DEFINER;
```

## Resources

- [pg_stat_statements — PostgreSQL Docs](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [EXPLAIN ANALYZE — PostgreSQL Docs](https://www.postgresql.org/docs/current/sql-explain.html)
- [Supabase Performance Advisor](https://supabase.com/docs/guides/database/inspect)
- [RLS Debugging — Supabase Docs](https://supabase.com/docs/guides/troubleshooting/rls-simplified-BJTcS8)
- [Edge Functions Logging — Supabase Docs](https://supabase.com/docs/guides/functions/logging)
- Realtime Debugging — Supabase Docs
- [pg_locks — PostgreSQL Docs](https://www.postgresql.org/docs/current/view-pg-locks.html)
- [Connection Pooling with Supavisor](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)

## Next Steps

- For load testing and scaling patterns, see `supabase-load-scale`
- For incident response procedures, see `supabase-incident-runbook`
- For performance tuning and index optimization, see `supabase-performance-tuning`
- For common error patterns and quick fixes, see `supabase-common-errors`
