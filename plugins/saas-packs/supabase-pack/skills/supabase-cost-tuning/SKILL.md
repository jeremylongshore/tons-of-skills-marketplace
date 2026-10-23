---
name: supabase-cost-tuning
description: 'Optimize Supabase costs through plan selection, database tuning, storage
  cleanup,

  connection pooling, and Edge Function optimization.

  Use when analyzing Supabase billing, reducing costs, right-sizing compute,

  or implementing usage tracking and budget alerts.

  Trigger with phrases like "supabase cost", "supabase billing",

  "reduce supabase costs", "supabase pricing", "supabase expensive", "supabase budget".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(supabase:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - supabase
  - cost-optimization
compatibility: Designed for Claude Code
---

# Supabase Cost Tuning

## Overview

Reduce Supabase spend by auditing usage against plan limits, eliminating database and storage waste, and right-sizing compute resources. The three biggest levers: database optimization (vacuum, index cleanup, archival), storage lifecycle management (compress before upload, orphan cleanup), and connection pooling to reduce compute add-on requirements.

Work the three steps below in order — audit first to find where the money goes, then optimize the biggest offenders, then right-size compute. Each step keeps a representative snippet inline; the full query and script sets live in `references/` so this file stays scannable.

## Prerequisites

- Supabase project with Dashboard access (Settings > Billing)
- `@supabase/supabase-js` installed: `npm install @supabase/supabase-js`
- Service role key for admin operations (storage audit, cleanup scripts)
- SQL editor access (Dashboard > SQL Editor or `psql` connection)

## Pricing Reference

Reviewed 2026-10-22: use [current pricing](https://supabase.com/pricing) and the
project's actual billing dashboard rather than a universal hard-coded plan table.
Compute is billed hourly; paid organizations receive $10 of compute credits per
month, shared across projects, not a free compute instance for every project.
The [compute usage reference](https://supabase.com/docs/guides/platform/manage-your-usage/compute)
lists Small at $0.0206/hour (about $15 for 730 hours), Medium at $0.0822/hour
(about $60), and Large at $0.1517/hour (about $111), before plan fees, credits and
other usage. These dated estimates are not a billing quote or fixed monthly cap.

Read replicas have their own compute and usage costs, not a universal $25/month
price. Model the selected size, active hours, disk, egress, region and current plan
allowances before changing topology. Pooling can reduce connection overhead but
does not guarantee that a smaller compute size will satisfy the workload.

## Instructions

### Step 1: Audit current usage and identify cost drivers

Find where the database budget is going before changing anything. Run the audit queries in the SQL Editor to surface the biggest tables, unused indexes, dead-tuple bloat, and connection count. Start with total size:

```sql
select pg_size_pretty(pg_database_size(current_database())) as total_db_size;
```

Then audit storage per bucket with a service-role client, and read current spend under **Dashboard > Settings > Billing**. See [full audit queries and storage script](references/audit-queries.md) for the complete SQL set (table sizes, zero-scan indexes, dead-tuple ratio, connection count) and the per-bucket usage script.

### Step 2: Optimize database, storage, and bandwidth

Attack the biggest offenders from Step 1. Archive old rows before deleting, then VACUUM ANALYZE to make dead-tuple space reusable and refresh planner stats; ordinary VACUUM does not generally shrink the on-disk allocation:

```sql
vacuum (verbose, analyze) public.events;
```

For storage, compress images client-side before upload and schedule an orphan-cleanup job. For bandwidth, replace `select('*')` with explicit column lists, use `head: true` count queries for totals, and paginate with `.range()`. See [full optimization code](references/optimization.md) for the archival + VACUUM SQL, the compress/clean-orphans scripts, and the bandwidth-reduction patterns.

### Step 3: Right-size compute and distinguish invocation cost from latency

Prefer pooling and code fixes over a compute upgrade. Choose the appropriate direct or Supavisor session/transaction connection mode for the client. Migrations may require direct/session semantics; do not send every workflow to transaction pooling:

```typescript
// Copy the actual direct/session/transaction connection string from Dashboard.
// Do not derive the pooler hostname by changing only the port.
// Transaction pooling constraints (including prepared statements) need review.
```

Smaller imports and warm-instance caching can improve latency/resource use, but do
not themselves reduce hosted Edge Function invocation charges. Current
[invocation billing](https://supabase.com/docs/guides/platform/manage-your-usage/edge-function-invocations)
is based on invocation count (excluding preflight OPTIONS), with package rounding
for billable overage. Avoid unnecessary invocations and retry storms within the
application's correctness requirements; do not skip required work to reduce counts.
Treat historical optimization examples as resource/latency patterns, not evidence
of invocation savings. Use actual billing usage rather than a custom event table
as invoice authority.

## Output

After completing all three steps, the project has:

- Database size audit with table-level breakdown and dead tuple analysis
- Candidate unused indexes reviewed against representative workloads before any approved drop
- Approved archival and vacuum outcomes measured without promising physical disk shrinkage
- Storage orphans cleaned and upload compression implemented
- Bandwidth reduced through column selection and pagination
- Connection pooling configured to avoid unnecessary compute upgrades
- Edge Function cold starts minimized with dynamic imports and caching
- Usage monitoring table and daily summary view for spend visibility

## Error Handling

| Issue                                            | Cause                                        | Solution                                                                                                       |
| ------------------------------------------------ | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Database approaching 500 MB (Free) or 8 GB (Pro) | Data growth without archival                 | Archive old records, VACUUM, drop unused indexes                                                               |
| Storage costs climbing monthly                   | Orphaned uploads accumulating                | Schedule cleanup job for files not linked to records                                                           |
| Unexpected bandwidth spike                       | `select('*')` on large tables                | Use specific column lists; add `.range()` pagination                                                           |
| Edge Function billing spike                      | Excess invocations or retry loops            | Inspect invocation counts and correctness-preserving admission/retry budgets; import size is a latency concern |
| Connection limit errors                          | Too many direct connections                  | Switch to pooler URL (port 6543); reduce client pool size                                                      |
| Spend cap reached                                | A capped usage surface reached its allowance | Review the current spend-cap coverage and response; it does not cap every charge                               |
| VACUUM not reclaiming space                      | Long-running transactions holding locks      | Check `pg_stat_activity` for idle-in-transaction; terminate stale sessions                                     |

## Examples

**Quick cost check** — inspect actual billing usage and an authorized database-size query; bucket count is not stored bytes.

**Cost estimation** — supply reviewed quantities, units, current rates, eligible credits and source/date to an explicitly scoped calculator. No universal Pro-tier total is supplied.

The [explicit-input examples](references/examples.md) validate arithmetic without embedding provider rates. Reconcile every included allowance, package/tier rounding, compute hour, credit and excluded charge against the current billing surface before using an estimate for a decision.

## Resources

- [Supabase Pricing](https://supabase.com/pricing) — plan comparison and calculator
- [Compute Add-ons](https://supabase.com/docs/guides/platform/compute-add-ons) — instance sizing guide
- [Spend Cap](https://supabase.com/docs/guides/platform/spend-cap) — prevent unexpected overage charges
- [Database Disk Usage](https://supabase.com/docs/guides/platform/database-size) — monitoring and management
- [Connection Pooling (Supavisor)](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler) — reduce connection overhead
- [Edge Functions Best Practices](https://supabase.com/docs/guides/functions/best-practices) — cold start and performance tips
- [supabase-js Reference](https://supabase.com/docs/reference/javascript/introduction) — `createClient` and SDK patterns

## Next Steps

For architecture patterns, see `supabase-reference-architecture`.
For performance tuning beyond cost, see `supabase-performance-tuning`.
