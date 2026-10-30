---
name: supabase-observability
description: |
  Set up monitoring and observability for Supabase projects using Dashboard
  reports, CLI inspect commands, pg_stat_statements, log drains, and alerting.
  Use when implementing monitoring, diagnosing slow queries, forwarding logs,
  or configuring alerts for Supabase project health.
  Trigger with phrases like "supabase monitoring", "supabase metrics",
  "supabase observability", "supabase logs", "supabase alerts",
  "supabase inspect", "supabase log drain".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(supabase:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- monitoring
- observability
compatibility: Designed for Claude Code
---
# Supabase Observability

## Overview

Monitor Supabase projects end-to-end: Dashboard reports for API/database/auth metrics, `supabase inspect db` CLI for deep Postgres diagnostics, `pg_stat_statements` for query analytics, log drains for external aggregation, Edge Functions for custom metrics, and alerting on quota thresholds.

Follow the three steps below from this file for the high-level workflow, then drill into the linked `references/` files for the full commands, SQL, and function source.

## Prerequisites

- Supabase CLI installed (`npx supabase --version`)
- Supabase project linked (`supabase link --project-ref <ref>`)
- Pro plan or higher for log drain support and extended log retention
- `@supabase/supabase-js` v2+ installed for application-level monitoring

## Instructions

### Step 1: Dashboard Reports and CLI Inspect Commands

Start with the built-in **Dashboard > Reports** (API Requests, Database, Auth Usage, Storage, Realtime) for high-level metrics. For deeper Postgres diagnostics, use the `supabase inspect db` subcommands — begin with cache hit ratio and sequential scans:

```bash
# Cache hit ratio — should be > 99% (below 95% means upgrade compute)
npx supabase inspect db cache-hit --linked

# Sequential scans — tables needing indexes
npx supabase inspect db seq-scans --linked
```

The full report table plus all nine inspect subcommands (table sizes, index usage, long-running queries, bloat, blocking, replication slots, and more) are in [references/cli-inspect-commands.md](references/cli-inspect-commands.md).

### Step 2: Query Analytics with pg_stat_statements and Log Drains

Enable `pg_stat_statements` for query-level metrics, then rank queries by execution time:

```sql
create extension if not exists pg_stat_statements;

-- Top slowest queries by average execution time
select substring(query, 1, 80) as query_preview, calls,
  round(mean_exec_time::numeric, 2) as avg_ms
from pg_stat_statements
where mean_exec_time > 50
order by mean_exec_time desc limit 20;
```

Forward logs to external aggregation with a log drain:

Configure an approved destination under **Project Settings > Log Drains** in the Dashboard. Review exported data, retention, credentials, and destination region before enabling forwarding; confirm arrival using synthetic events.

The complete slow-query / high-frequency / connection-monitoring SQL set and the Dashboard log-drain configuration and verification workflow are in [references/query-analytics-and-log-drains.md](references/query-analytics-and-log-drains.md).

### Step 3: Custom Metrics, Alerting, and Health Checks

Emit business-level metrics from a scheduled Edge Function, alert on quota thresholds, and expose a health endpoint for uptime monitors. The skeleton of the metrics collector:

```typescript
// supabase/functions/collect-metrics/index.ts — see reference for full source
const DB_LIMIT_MB = 8000; // 8GB Pro plan limit
if (dbSize > DB_LIMIT_MB * 0.85) {
  console.warn(`[QUOTA_ALERT] Database at ${Math.round(dbSize / DB_LIMIT_MB * 100)}% capacity`);
}
```

Schedule approved invocations with `pg_cron` and `pg_net`, retrieving the URL and appropriate function credential from Vault; a function TOML schedule field is not supported. The complete collector, the multi-service health-check endpoint, and Realtime connection monitoring are in [references/custom-metrics-and-health-checks.md](references/custom-metrics-and-health-checks.md). For external alert rules, see the Prometheus AlertManager set in [references/alert-configuration.md](references/alert-configuration.md).

## Output

- Dashboard reports configured for API, database, and auth monitoring
- CLI inspect commands available for Postgres diagnostics (table sizes, index usage, cache hits, sequential scans, long-running queries)
- `pg_stat_statements` enabled with slow-query and high-frequency-query views
- Log drains forwarding to external tools (Datadog, Logflare, or webhook)
- Custom metrics Edge Function collecting quota-relevant data on a schedule
- Health check endpoint returning per-service status with latency
- Alerting on quota thresholds (database size, user count)

## Error Handling

| Issue | Cause | Solution |
| ------- | ------- | ---------- |
| `pg_stat_statements` returns no rows | Extension not enabled | Enable via Dashboard > Database > Extensions |
| `supabase inspect db` fails | CLI not linked to project | Run `supabase link --project-ref <ref>` |
| Log drain not receiving events | API key invalid or region mismatch | Verify the destination and drain status in Project Settings > Log Drains |
| Cache hit ratio below 95% | Working set exceeds RAM | Upgrade compute add-on or optimize queries |
| Health check returns 503 | One or more services degraded | Check `detail` field in response; verify service role key |
| Edge Function cron not firing | Cron job or HTTP/authentication failure | Inspect the reviewed cron job and invocation logs; verify Vault references and the function auth mode |
| Long-running queries growing | Missing indexes or lock contention | Run `inspect db seq-scans` and `inspect db blocking` |

## Examples

A one-shot diagnostic bash script that runs every inspect command in sequence, plus the `app_metrics` backing table schema with a 90-day retention policy, are in [references/diagnostic-scripts.md](references/diagnostic-scripts.md). For application-level Prometheus instrumentation of the Supabase client, see [references/metrics-collection.md](references/metrics-collection.md).

## Resources

- [Supabase Logs & Analytics](https://supabase.com/docs/guides/platform/logs)
- [Database Inspect Commands](https://supabase.com/docs/guides/database/inspect)
- [Log Drains](https://supabase.com/docs/guides/platform/log-drains)
- [Edge Functions Scheduling](https://supabase.com/docs/guides/functions/schedule-functions)
- [pg_stat_statements](https://supabase.com/docs/guides/database/extensions/pg_stat_statements)
- [Supabase JS Client](https://supabase.com/docs/reference/javascript/introduction)

## Next Steps

For incident response procedures, see `supabase-incident-runbook`.
For performance optimization, see `supabase-performance-tuning`.
