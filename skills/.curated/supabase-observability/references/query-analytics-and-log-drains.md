# Query Analytics and Log Drains

## pg_stat_statements

Enable `pg_stat_statements` for detailed query-level metrics:

```sql
-- Enable the extension (Dashboard > Database > Extensions, or SQL)
create extension if not exists pg_stat_statements;

-- Top 20 slowest queries by average execution time
select
  substring(query, 1, 80) as query_preview,
  calls,
  round(mean_exec_time::numeric, 2) as avg_ms,
  round(max_exec_time::numeric, 2) as max_ms,
  round(total_exec_time::numeric, 2) as total_ms,
  rows
from pg_stat_statements
where mean_exec_time > 50
order by mean_exec_time desc
limit 20;

-- Most-called queries (high call count may indicate N+1 problems)
select
  substring(query, 1, 80) as query_preview,
  calls,
  round(mean_exec_time::numeric, 2) as avg_ms,
  rows
from pg_stat_statements
order by calls desc
limit 20;

-- Real-time connection monitoring
select
  state,
  count(*) as connections,
  max(age(now(), state_change))::text as longest_duration
from pg_stat_activity
where datname = current_database()
group by state
order by connections desc;

-- Reset stats after optimization (to measure improvement)
select pg_stat_statements_reset();
```

## Log Drains

**Log drains** forward Supabase logs to external aggregation tools:

1. In the project Dashboard, open **Project Settings > Log Drains**.
2. Choose a supported destination and provision its credentials through the approved secret-management flow.
3. Review source data, destination region, retention, cost, and access before enabling the drain.
4. Send a synthetic event and verify arrival and parsing at the destination; inspect status in the Dashboard.
5. Disable or remove the drain in the Dashboard when no longer required, then verify forwarding stopped.

See the [current log-drain guide](https://supabase.com/docs/guides/observability/log-drains) for supported integrations and eligibility. No CLI log-drain subcommand is assumed.

Log drain events include API requests, Auth events, Postgres logs, Storage
operations, and Edge Function invocations.
