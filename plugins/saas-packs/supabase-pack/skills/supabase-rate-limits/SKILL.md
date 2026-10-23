---
name: supabase-rate-limits
description: |
  Manage Supabase rate limits and quotas across all plan tiers.
  Use when hitting 429 errors, configuring connection pooling, optimizing
  API throughput, or understanding tier-specific quotas for Auth, Storage,
  Realtime, and Edge Functions.
  Trigger with "supabase rate limit", "supabase 429", "supabase throttle",
  "supabase quota", "supabase connection pool", "supabase too many requests".
allowed-tools: Read, Write, Edit, Bash(supabase:*), Bash(node:*), Bash(npx:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- rate-limiting
- reliability
- quotas
compatibility: Designed for Claude Code
---
# Supabase Rate Limits

## Overview

Supabase limits differ across PostgREST, Auth, Storage, Realtime, and Edge Functions. Use the current surface-specific documentation and project configuration rather than a universal requests-per-minute or requests-per-day table. Review pooling, bounded retries, pagination, and monitoring for the actual workload.

## Prerequisites

- Active Supabase project (any tier)
- `@supabase/supabase-js` v2+ installed
- Project URL and anon/service-role key available
- Node.js 22+ for current SDK releases, or another supported SDK runtime

## Instructions

### Step 1 — Know your tier limits

Record the relevant endpoint, project configuration, plan, observation date, and current provider documentation. Auth, Storage, Realtime, Edge Functions, and database connections have different controls; a plan name alone does not establish one universal API request budget. See [rate-limit-tiers.md](references/rate-limit-tiers.md) for the per-surface review.

### Step 2 — Pool connections with Supavisor

Supavisor is Supabase's built-in connection pooler (replaced PgBouncer). Pick the mode by workload:

| Use case | Mode | Port |
| ---------- | ------ | ------ |
| Serverless / Edge Functions | Transaction | 6543 |
| Next.js API routes | Transaction | 6543 |
| Long-running workers | Session | 5432 |
| Realtime subscriptions | Direct (no pooler) | 5432 |
| Prisma / Drizzle ORM | Transaction + `?pgbouncer=true` | 6543 |

Transaction mode (port 6543) returns a connection to the pool after each transaction — the right default for serverless. Session mode (port 5432) holds a dedicated connection for LISTEN/NOTIFY and prepared statements. Full client setup and connection-string formats are in [implementation.md](references/implementation.md).

### Step 3 — Retry, paginate, and batch

Wrap queries in an exponential-backoff retry that recognizes 429s and pool exhaustion:

```typescript
// Retryable when the error is a rate limit, "too many requests",
// code 429, or PGRST000 (connection pool exhausted). Delay doubles
// per attempt with jitter, capped at maxDelayMs, honoring Retry-After.
const users = await withRetry(() =>
  supabase.from('users').select('id, email, created_at').eq('active', true)
)
```

Then cut request volume two ways: paginate large reads with `.range(from, to)` so responses stay small and avoid timeouts, and combine compatible writes using bounded batch `upsert` requests (choose chunk sizes for the actual payload and API behavior). The full `withRetry`, `fetchPaginated`, and batch/`chunk` helpers — plus dashboard monitoring steps — are in [implementation.md](references/implementation.md).

## Output

After applying this skill you will have:

- Dated, per-surface limit evidence and project-specific operating budgets
- Connection pooling configured via Supavisor (port 6543 transaction mode for serverless)
- Retry wrapper with exponential backoff handling 429 errors
- Paginated queries using `.range(0, 99)` to reduce payload size
- Batch upsert pattern reducing N requests to 1
- Dashboard monitoring configured for API usage alerts

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `429 Too Many Requests` | Endpoint-specific rate control or workload saturation | Apply `withRetry` backoff; reduce concurrency; upgrade tier |
| `PGRST000: could not connect` | Connection pool exhausted | Switch to Supavisor transaction mode (port 6543); reduce concurrent queries |
| Auth `over_request_rate_limit` | Too many signups/logins from one IP | Add CAPTCHA; configure custom auth rate limits in Dashboard |
| Storage `413 Payload Too Large` | File exceeds tier limit | Use TUS resumable upload; check tier file size limit |
| Realtime `too_many_connections` | Concurrent connection limit reached | Unsubscribe unused channels; review the current project connection allowance |
| Edge Function `BOOT_ERROR` | Cold start timeout or memory exceeded | Reduce bundle size; avoid large imports at top level |
| `pgbouncer=true` errors with Prisma | Missing connection string parameter | Append `?pgbouncer=true` to pooler connection string on port 6543 |

Use response headers only where the endpoint documents them; honor `Retry-After` when supplied. Endpoint-specific error handling is in [errors.md](references/errors.md).

## Examples

- **Serverless Edge Function with a batch-inserting, rate-limit-safe client** — see [examples.md](references/examples.md)
- **Connection-string selection per runtime** (serverless vs long-running vs direct) — see [examples.md](references/examples.md)
- **Queue-based throttling and client-side header monitoring** — see [examples.md](references/examples.md)

## Resources

- [Supabase Platform Limits & Quotas](https://supabase.com/docs/guides/platform/going-into-prod#rate-limiting)
- [Supavisor Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Edge Functions Limits](https://supabase.com/docs/guides/functions/limits)
- [Storage Limits](https://supabase.com/docs/guides/storage#limits)
- [@supabase/supabase-js Reference](https://supabase.com/docs/reference/javascript/introduction)

## Next Steps

For securing your Supabase project with RLS policies and API key management, see `supabase-security-basics`. For optimizing database queries and indexing, see `supabase-performance-tuning`.
