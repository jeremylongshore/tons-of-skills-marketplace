# RLS Conflicts, Edge Function Cold Starts, and Realtime Drops

Diagnose RLS policy conflicts that cause unexpected access patterns, profile Edge Function cold starts, and investigate Realtime connection drops.

**RLS policy conflict analysis:**

```sql
-- List ALL policies on a table to find conflicts
SELECT
  pol.polname AS policy_name,
  CASE pol.polcmd
    WHEN 'r' THEN 'SELECT'
    WHEN 'a' THEN 'INSERT'
    WHEN 'w' THEN 'UPDATE'
    WHEN 'd' THEN 'DELETE'
    WHEN '*' THEN 'ALL'
  END AS command,
  CASE pol.polpermissive
    WHEN true THEN 'PERMISSIVE'
    ELSE 'RESTRICTIVE'
  END AS type,
  pg_get_expr(pol.polqual, pol.polrelid) AS using_clause,
  pg_get_expr(pol.polwithcheck, pol.polrelid) AS with_check_clause,
  ARRAY(SELECT rolname FROM pg_roles WHERE oid = ANY(pol.polroles)) AS applies_to_roles
FROM pg_policy pol
JOIN pg_class cls ON cls.oid = pol.polrelid
WHERE cls.relname = 'your_table_name'
ORDER BY pol.polcmd, pol.polpermissive DESC;

-- Common conflict: PERMISSIVE policies are OR'd together
-- If you have two SELECT policies, a row is visible if EITHER matches
-- RESTRICTIVE policies are AND'd — all must pass

-- Test a specific user's access
SET request.jwt.claim.sub = 'user-uuid';
SET request.jwt.claim.role = 'authenticated';
SET request.jwt.claims = '{"sub": "user-uuid", "role": "authenticated", "app_metadata": {"role": "editor", "org_id": "org-123"}}';

-- Check what they can see
SELECT count(*) FROM your_table_name;

-- Check the auth functions
SELECT auth.uid(), auth.jwt(), auth.role();

RESET ALL;
```

**RLS conflict debugging from the SDK:**

```typescript
import { createClient } from '@supabase/supabase-js';

// Compare results across permission levels
async function debugRLSConflict(table: string, filters: Record<string, string>) {
  const anonClient = createClient(url, anonKey);
  const authedClient = createClient(url, anonKey);
  const adminClient = createClient(url, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  // Sign in as a test user
  await authedClient.auth.signInWithPassword({
    email: 'test@example.com',
    password: 'test-password',
  });

  let query = (client: any) => {
    let q = client.from(table).select('*', { count: 'exact' });
    for (const [key, value] of Object.entries(filters)) {
      q = q.eq(key, value);
    }
    return q;
  };

  const [anonResult, authedResult, adminResult] = await Promise.all([
    query(anonClient),
    query(authedClient),
    query(adminClient),
  ]);

  console.log(`RLS debug for "${table}":`, {
    anon: { count: anonResult.count, error: anonResult.error?.message },
    authenticated: { count: authedResult.count, error: authedResult.error?.message },
    admin: { count: adminResult.count, error: adminResult.error?.message },
  });

  if (adminResult.count !== authedResult.count) {
    console.warn(
      `RLS filtering: admin sees ${adminResult.count} rows, user sees ${authedResult.count}`
    );
  }
}
```

**Edge Function cold start profiling:**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, anonKey);

// Measure cold start vs warm invocation times
async function profileEdgeFunction(
  functionName: string,
  iterations = 5,
  coldStartDelayMs = 60000
) {
  const results: { iteration: number; durationMs: number; isColdStart: boolean }[] = [];

  for (let i = 0; i < iterations; i++) {
    // Wait before first call to ensure cold start
    if (i === 0) {
      console.log(`Waiting ${coldStartDelayMs / 1000}s for cold start...`);
      await new Promise((r) => setTimeout(r, coldStartDelayMs));
    }

    const start = performance.now();
    const { data, error } = await supabase.functions.invoke(functionName, {
      body: { action: 'ping', timestamp: Date.now() },
    });
    const duration = Math.round(performance.now() - start);

    results.push({
      iteration: i + 1,
      durationMs: duration,
      isColdStart: i === 0 || duration > 1000,
    });

    console.log(`Invocation ${i + 1}: ${duration}ms ${i === 0 ? '(cold start)' : '(warm)'}`);
  }

  const coldStarts = results.filter((r) => r.isColdStart);
  const warmStarts = results.filter((r) => !r.isColdStart);

  console.log('Summary:', {
    coldStartAvgMs: coldStarts.length > 0
      ? Math.round(coldStarts.reduce((s, r) => s + r.durationMs, 0) / coldStarts.length)
      : 'N/A',
    warmStartAvgMs: warmStarts.length > 0
      ? Math.round(warmStarts.reduce((s, r) => s + r.durationMs, 0) / warmStarts.length)
      : 'N/A',
  });
}
```

```bash
# Inspect the selected function in the project Dashboard: Logs and Invocations.
# Match timestamps and execution metadata to the approved test invocation.

# Look for patterns:
# - First invocation after deploy: high latency
# - "Worker booted" or "Isolate created" messages
# - Memory/CPU spikes on first request

# Reduce cold starts:
# 1. Minimize imports (lazy-load heavy dependencies)
# 2. Keep function payload small
# 3. Use scheduled warm-up pings via pg_cron
```

**Realtime connection drop investigation:**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(url, anonKey);

// Debug Realtime connection stability
function monitorRealtimeChannel(table: string) {
  const channel = supabase
    .channel(`debug-${table}`)
    .on('system', {}, (payload) => {
      console.log(`[SYSTEM] ${new Date().toISOString()}:`, payload);
      // Watch for: CHANNEL_ERROR, TIMED_OUT, TOKEN_EXPIRED
    })
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table },
      (payload) => {
        console.log(`[CHANGE] ${payload.eventType}:`, payload.new);
      }
    )
    .subscribe((status, err) => {
      console.log(`[STATUS] ${new Date().toISOString()}: ${status}`, err ?? '');

      if (status === 'CHANNEL_ERROR') {
        console.error('Channel error — will auto-reconnect');
      }
      if (status === 'TIMED_OUT') {
        console.error('Connection timed out — check network/firewall');
      }
    });

  // Monitor connection health periodically
  const healthInterval = setInterval(() => {
    const state = channel.state;
    console.log(`[HEALTH] Channel state: ${state}`);
    if (state !== 'joined') {
      console.warn(`[HEALTH] Channel not joined, current state: ${state}`);
    }
  }, 30000);

  return {
    channel,
    stop: () => {
      clearInterval(healthInterval);
      channel.unsubscribe();
    },
  };
}
```

```sql
-- Verify table is in the Realtime publication
SELECT schemaname, tablename
FROM pg_publication_tables
WHERE pubname = 'supabase_realtime'
ORDER BY tablename;

-- Add a missing table to the publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.your_table;

-- Check Realtime connection limits
-- Supabase free plan: 200 concurrent connections
-- Pro plan: 500 concurrent connections
-- You can check current count in the Supabase dashboard → Realtime → Connections
```

## Output

After completing this skill, you will have:

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
|-------|-------|----------|
| `pg_stat_statements` not available | Extension not enabled | Run `CREATE EXTENSION pg_stat_statements;` |
| Seq Scan on large table | Missing index on filter column | Create index with `CREATE INDEX CONCURRENTLY` |
| `deadlock detected` | Circular lock dependency | Ensure consistent lock ordering across transactions |
| All connections in `idle in transaction` | Application not closing transactions | Add connection timeout; review ORM connection pool settings |
| RLS returns empty for authenticated user | JWT claims don't match policy | Check `auth.jwt()` output; verify `app_metadata` is set |
| Edge Function > 2s cold start | Large dependency bundle | Lazy-import heavy modules; reduce function size |
| Realtime `TIMED_OUT` | Network/firewall blocking WebSocket | Check port 443 is open; verify no proxy strips `Upgrade` header |
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
