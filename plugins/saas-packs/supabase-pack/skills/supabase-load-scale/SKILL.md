---
name: supabase-load-scale
description: >-
  Use when preparing a Supabase project for production load — traffic spikes,
  connection-limit tuning, read replicas for analytics queries, CDN caching for
  Storage, regional Edge Function deployment, or partitioning large tables.
  Covers read replicas, Supavisor connection pooling, compute-size upgrades,
  Storage CDN, Edge Function regions, and table partitioning. Trigger with
  phrases like "supabase scale", "supabase read replica", "supabase connection
  pooling", "supabase compute upgrade", "supabase CDN storage", "supabase edge
  function regions", "supabase partitioning", "supavisor", "supabase pool mode".
allowed-tools: Read, Write, Edit, Bash(supabase:*), Bash(psql:*), Bash(curl:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- scaling
- performance
- connection-pooling
- read-replicas
- partitioning
compatibility: Designed for Claude Code
---
# Supabase Load & Scale

## Overview

Supabase scaling operates at six layers: **read replicas** (offload analytics
and reporting queries), **connection pooling** (Supavisor, the pgBouncer
replacement, with transaction/session modes), **compute upgrades** (vCPU/RAM
tiers), **CDN for Storage** (cache public bucket assets at the edge), **Edge
Function regions** (deploy functions closer to users), and **table
partitioning** (split billion-row tables for query performance). This skill
gives the high-level workflow inline and links to `references/` for the full
`createClient` config, SQL, and CLI for each layer.

## Prerequisites

- Supabase project on a Pro plan or higher (read replicas require Pro+)
- `@supabase/supabase-js` v2+ installed
- `supabase` CLI installed and linked to your project
- Database access via `psql` or Supabase SQL Editor
- TypeScript project with generated database types

## Instructions

### Step 1 — Read Replicas and Connection Pooling

Route read-heavy queries (dashboards, reports, search) to a read replica while
keeping writes on the primary. Supavisor pools connections in two modes:
**transaction** (default, port 6543 — shares connections, no prepared
statements) and **session** (port 5432 — one connection per client, needed for
prepared statements and `LISTEN`/`NOTIFY`). Configure two clients — a primary
and a read-only replica pointed at the `-ro` URL:

```typescript
// lib/supabase.ts
export const supabase = createClient<Database>(
  process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!)       // writes + realtime
export const supabaseReadOnly = createClient<Database>(
  process.env.SUPABASE_READ_REPLICA_URL!, process.env.SUPABASE_ANON_KEY!) // analytics
```

Then send analytics queries to `supabaseReadOnly` and all writes to `supabase`.
Replicas lag slightly (typically <100ms), so never read-after-write on a
replica. Full client config, pooled `psql` connection strings, query-routing
services, and a pool-usage monitoring query:
[read replicas and connection pooling](references/connection-pooling.md).

### Step 2 — Compute Upgrades, CDN for Storage, and Edge Function Regions

Match the current project compute configuration to measured traffic, serve public
Storage buckets through the CDN with long `cacheControl` headers plus
content-addressed paths for cache busting, and deploy Edge Functions to the
appropriate execution region:

1. Review and change database compute in the project Dashboard, including cost and connection limits.
2. Deploy with the documented `supabase functions deploy my-function` workflow.
3. Choose execution routing at invocation time where appropriate; deploying does not accept a region-selection flag. See [regional invocations](https://supabase.com/docs/guides/functions/regional-invocation).

Compute selection workflow, CDN upload/transform patterns, versioned-asset
cache busting, and the regional geo-router Edge Function:
[compute, CDN, and edge regions](references/cdn-and-edge.md).

### Step 3 — Database Table Partitioning

Split large append-heavy tables (events, logs, metrics) by date range so
queries scan only the relevant partitions and old data drops cheaply. See
[table partitioning patterns](references/table-partitioning.md) for range
partitioning by date, automated partition creation via `pg_cron`, SDK query
patterns with partition-key filters, and partition drop for data retention.

## Output

- Read replica client configured for analytics/dashboard queries, primary for writes
- Connection pooling mode selected (transaction vs session) with correct port
- Compute tier matched to traffic requirements
- Storage uploads optimized with CDN cache headers and image transforms
- Edge Function invocation routing reviewed for application and database latency
- Large tables partitioned by date range with automated partition management
- Data retention policy via partition drops

## Error Handling

| Issue | Cause | Solution |
| ------- | ------- | ---------- |
| `too many connections for role` | Exceeded Supavisor pool limit | Use transaction mode (port 6543), reduce idle connections, upgrade compute |
| Read replica returns stale data | Replication lag (typically <100ms) | Do not read-after-write on replica; use primary for consistency-critical reads |
| `no partition of relation "events" found for row` | Insert date outside any partition range | Create a DEFAULT partition or pre-create future partitions |
| Storage CDN returns old file | Cached at edge | Use content-addressed paths (`hash.ext`) or set shorter `cacheControl` |
| Edge Function cold start | First request to a region | Use `keep-alive` cron ping or accept ~200ms cold start |
| `prepared statement already exists` | Transaction mode doesn't support prepared statements | Switch to session mode (port 5432) or disable prepared statements in your ORM |

## Examples

### Quick Connection Pool Check

```bash
# Check how many connections are in use right now
psql "$DATABASE_URL" -c "SELECT count(*) AS active_connections FROM pg_stat_activity WHERE state = 'active';"
```

For deeper worked examples — swapping an existing table to a partitioned one
(create/migrate/rename in a transaction) and measuring live read-replica lag —
see [advanced scaling examples](references/advanced-examples.md).

## Resources

- [Supabase Read Replicas](https://supabase.com/docs/guides/platform/read-replicas)
- [Supabase Connection Pooling (Supavisor)](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Supabase Compute Add-ons](https://supabase.com/docs/guides/platform/compute-add-ons)
- [Supabase Storage CDN](https://supabase.com/docs/guides/storage/cdn/fundamentals)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [PostgreSQL Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)

## Next Steps

For reliability patterns (circuit breakers, offline queues, graceful degradation), see `supabase-reliability-patterns`.
