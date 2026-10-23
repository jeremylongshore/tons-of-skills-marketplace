---
name: supabase-incident-runbook
description: >-
  Execute Supabase incident response: dashboard health checks, connection pool
  status, pg_stat_activity queries, RLS debugging, Edge Function logs, storage
  health, and escalation. Use when responding to Supabase outages, investigating
  production errors, debugging connection issues, or preparing evidence for
  Supabase support escalation. Trigger with "supabase incident", "supabase
  outage", "supabase down", "supabase on-call", "supabase emergency", "supabase
  broken", or "supabase connection issues".
allowed-tools: Read, Grep, Bash(npx supabase:*), Bash(supabase:*), Bash(curl:*), Bash(psql:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- incident-response
- debugging
- operations
- runbook
compatibility: Designed for Claude Code
---
# Supabase Incident Runbook

## Overview

A structured response for Supabase-backed application failures. Work three
layers in order: triage platform vs. application, run `pg_stat_activity`
database diagnostics, then debug RLS, Edge Functions, and storage — ending with
an evidence bundle for support escalation.

**When to use:** Production errors involving Supabase, degraded API response times, connection pool exhaustion, silent data filtering from RLS, Edge Function cold start failures, or storage upload/download errors.

Each step below gives the workflow plus a first command. The complete
copy-paste blocks for every step live in
[references/diagnostics.md](references/diagnostics.md).

## Prerequisites

- Supabase project with dashboard access at [supabase.com/dashboard](https://supabase.com/dashboard)
- `@supabase/supabase-js` v2+ installed in your project
- Supabase Dashboard access for remote Edge Function logs; an installed CLI for local diagnostics
- Direct database connection string (for `psql` diagnostics)
- Access to [status.supabase.com](https://status.supabase.com) for platform health

## Instructions

### Step 1: Triage — Platform vs. Application

Determine whether the issue is a Supabase platform incident or an application-level bug. Check the official status page first, then verify SDK client connectivity. Use `Read` to inspect the app's Supabase env config and `Grep` to scan application logs for HTTP error codes (401=auth, 429=rate limit, 500=server).

```bash
# Check official status page — is this a platform-wide incident?
curl -sf https://status.supabase.com/api/v2/status.json | jq '.status'
# Expected: { "indicator": "none", "description": "All Systems Operational" }
```

If the status page is green, run the SDK `healthCheck()` (a `select 1` against a
small `_health_check` table) to measure latency and confirm connectivity. A
green platform plus a failing health check points at your queries, RLS, or Edge
Functions — the SDK block, incident-check query, and full decision tree are in
[references/diagnostics.md](references/diagnostics.md).

### Step 2: Database Diagnostics with pg_stat_activity

Connect directly via `psql` (or the Supabase SQL Editor) to inspect connections, find stuck queries, and detect leaks.

```sql
-- Current connections grouped by state — the first thing to run
SELECT state, count(*) AS connections,
       max(extract(epoch FROM age(now(), state_change)))::int AS max_idle_seconds
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state ORDER BY connections DESC;
-- WARNING: If idle > 20 or idle_in_transaction > 0, you have a leak
```

From there, drill into long-running queries, connection-limit headroom
(`pct_used > 80%` means enable Supavisor pooling), the `pg_cancel_backend` /
`pg_terminate_backend` kill switches, and an app-side `get_connection_stats()`
RPC — all in
[references/diagnostics.md](references/diagnostics.md).

### Step 3: RLS Debugging, Edge Functions, and Storage

Debug silent data filtering from Row Level Security, inspect Edge Function execution, and verify storage. The classic RLS tell is an anon query returning fewer rows than the same query under the service role.

```sql
-- List every RLS policy on the affected table
SELECT policyname, cmd, permissive, roles, qual AS using_expression
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'your_table_name';
```

Continue with JWT-claim simulation in the SQL Editor, the anon-vs-service-role
SDK diff (`debugRLS`), remote Edge Function log inspection in the Dashboard, cold-start detection, and a storage bucket upload/download check — full
blocks in
[references/diagnostics.md](references/diagnostics.md).

## Output

After running this incident runbook, you will have:

- **Platform status assessment** — confirmed whether the issue is Supabase-side or application-side
- **SDK health check** — latency measurement and connectivity verification via `createClient`
- **Connection pool analysis** — `pg_stat_activity` showing active, idle, and leaked connections
- **Long-running query identification** — stuck queries with PIDs ready for cancellation
- **RLS policy diagnosis** — side-by-side comparison of anon vs. service role query results
- **Edge Function status** — deployment status, cold start detection, and log inspection
- **Storage health report** — bucket accessibility and upload/download verification
- **Evidence bundle** — complete diagnostic data for Supabase support escalation

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `FetchError: request failed` | Supabase API unreachable | Check status.supabase.com; verify network/DNS |
| `connection refused` on port 5432 | Direct DB access blocked or wrong credentials | Use pooler URL (port 6543) or check dashboard connection strings |
| `too many clients already` | Connection pool exhausted | Kill idle-in-transaction connections; enable Supavisor pooling |
| `permission denied for table` | RLS blocking or wrong role | Check policies with `pg_policies`; verify JWT claims |
| `WORKER_LIMIT` in Edge Function | Memory/CPU exceeded | Reduce function payload size; optimize imports |
| `JWT expired` | Token not refreshing | Verify `autoRefreshToken: true` in `createClient` options |
| `storage/object-not-found` | File deleted or wrong path | Check bucket policies; verify path with service role client |
| `rate limit exceeded` (429) | Too many API requests | Implement exponential backoff; contact Supabase for limit increase |

## Examples

**Example 1 — Quick triage script.** A single async function that pings database, auth, storage, and realtime in sequence and prints an OK/ERROR line per service — the fastest "what's actually down?" check.

```typescript
// One-line database probe (the first check in the full triage script)
const { error } = await supabase.from('_health_check').select('id').limit(1);
console.log('Database:', error ? `ERROR: ${error.message}` : 'OK');
```

Two more worked examples — a connection-leak detector SQL query that labels each
connection `LEAK`/`STALE`/`OK`, and an escalation evidence-bundle builder that
assembles diagnostics into JSON for Supabase support — are in
[references/examples.md](references/examples.md).

## Resources

- [Supabase Status Page](https://status.supabase.com)
- Supabase Support Portal
- [Database Health — Supabase Docs](https://supabase.com/docs/guides/database/inspect)
- [RLS Debugging — Supabase Docs](https://supabase.com/docs/guides/troubleshooting/rls-simplified-BJTcS8)
- [Edge Functions Logs — Supabase Docs](https://supabase.com/docs/guides/functions/logging)
- [Connection Pooling with Supavisor](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [pg_stat_activity — PostgreSQL Docs](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW)

## Next Steps

- For GDPR compliance and data handling, see `supabase-data-handling`
- For performance tuning and query optimization, see `supabase-performance-tuning`
- For observability and monitoring setup, see `supabase-observability`
- For common error patterns and fixes, see `supabase-common-errors`
