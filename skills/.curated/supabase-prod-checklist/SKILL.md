---
name: supabase-prod-checklist
description: |
  Execute a Supabase production deployment checklist covering RLS, key hygiene,
  connection pooling, backups, monitoring, Edge Functions, and Storage policies.
  Use when deploying to production, preparing for launch, or auditing a live
  Supabase project for security and performance gaps. Trigger with "supabase
  production", "supabase go-live", "supabase launch checklist", "supabase prod
  ready", "deploy supabase", "supabase production readiness".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(curl:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- deployment
- production
- security
- rls
compatibility: Designed for Claude Code
---
# Supabase Production Deployment Checklist

## Overview

Actionable 14-step checklist for taking a Supabase project to production, based
on Supabase's official [production guide](https://supabase.com/docs/guides/deployment/going-into-prod).
Each step below carries its verification checklist inline; the full SQL,
TypeScript, and CLI commands for every step live in
[references/step-commands.md](references/step-commands.md).

## Prerequisites

- Supabase project on Pro plan or higher (required for PITR, network restrictions)
- Separate production project (never share dev/prod)
- `@supabase/supabase-js` v2+ installed
- Supabase CLI installed (`npx supabase --version`)
- Domain and DNS configured for custom domain
- Deployment platform ready (Vercel, Netlify, Cloudflare, etc.)

## Instructions

Work top to bottom. Every checkbox must be satisfied before go-live. Each step
names the commands to run; copy them from
[references/step-commands.md](references/step-commands.md).

### Step 1: Enforce Row Level Security on ALL Tables

RLS is the single most critical production requirement. Without it, any client
with your anon key can read/write every row. Start with the audit query — it
**must return zero rows** before going live:

```sql
-- Find tables WITHOUT RLS enabled (must return zero rows before launch)
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = false;
```

Then `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and add per-command policies —
full `CREATE POLICY` patterns in [step-commands.md](references/step-commands.md).

- [ ] RLS enabled on every public table (zero rows from audit query above)
- [ ] SELECT, INSERT, UPDATE, DELETE policies defined for each table
- [ ] Policies tested with both authenticated and anonymous roles
- [ ] No tables use `USING (true)` without intent (public read tables only)

### Step 2: Enforce Key Separation — Anon vs Service Role

The `anon` key is safe for client-side code. The `service_role` key bypasses RLS
entirely and must never leave server-side environments. See the two-client setup
in [step-commands.md](references/step-commands.md).

- [ ] Anon key used in all client-side code (`NEXT_PUBLIC_` prefix)
- [ ] Service role key used only in server-side code (API routes, Edge Functions)
- [ ] Service role key not in any client bundle (verify with `grep -r "service_role" dist/`)
- [ ] Database password changed from the auto-generated default

### Step 3: Configure Connection Pooling (Supavisor)

Supabase uses Supavisor for pooling. Serverless functions (Vercel, Netlify,
Cloudflare Workers) MUST use the pooled connection string (port 6543) to avoid
exhausting the database connection limit — direct connections (port 5432) are for
migrations and admin tasks only. Connection strings and client config in
[step-commands.md](references/step-commands.md).

- [ ] Application code uses pooled connection string (port 6543)
- [ ] Direct connection reserved for migrations and admin tasks only
- [ ] Connection string in deployment platform env vars (not hardcoded)
- [ ] Verified pool mode: `transaction` for serverless, `session` for long-lived connections

### Step 4: Enable Database Backups

Supabase provides automatic daily backups on Pro plan. Point-in-time recovery
(PITR) enables granular restores.

- [ ] Automatic daily backups enabled (Pro plan — verify in Dashboard > Database > Backups)
- [ ] Point-in-time recovery configured (Dashboard > Database > Backups > PITR)
- [ ] Tested restore procedure on a staging project (do not skip this)
- [ ] Migration files committed to version control (`supabase/migrations/` directory)
- [ ] `npx supabase db push` tested against a fresh project to verify migrations replay cleanly

### Step 5: Configure Network Restrictions

Restrict database access to known IP addresses. This prevents unauthorized direct
database connections even if credentials leak.

- [ ] IP allowlist configured (Dashboard > Database > Network Restrictions)
- [ ] Only deployment platform IPs and team office IPs are allowed
- [ ] Verified that application still connects after restrictions applied
- [ ] Documented which IPs are allowed and why

### Step 6: Configure Custom Domain

A custom domain replaces the default `*.supabase.co` URLs with your brand domain
for API and auth endpoints.

- [ ] Custom domain configured (Dashboard > Settings > Custom Domains)
- [ ] DNS CNAME record added and verified
- [ ] SSL certificate provisioned and active
- [ ] Application code updated to use custom domain URL
- [ ] OAuth redirect URLs updated to use custom domain

### Step 7: Customize Auth Email Templates

Default Supabase auth emails show generic branding. Customize them so users see
your domain and brand.

- [ ] Confirmation email template customized (Dashboard > Auth > Email Templates)
- [ ] Password reset email template customized
- [ ] Magic link email template customized
- [ ] Invite email template customized
- [ ] Custom SMTP configured (Dashboard > Auth > SMTP Settings) — avoids rate limits and improves deliverability
- [ ] Email confirmation enabled (Dashboard > Auth > Settings)
- [ ] OAuth redirect URLs restricted to production domains only
- [ ] Unused auth providers disabled

### Step 8: Understand Rate Limits Per Tier

Supabase enforces rate limits that vary by plan. Hitting these in production
causes 429 errors.

| Resource | Free | Pro | Team |
| ---------- | ------ | ----- | ------ |
| API requests | 500/min | 1,000/min | 5,000/min |
| Auth emails | 4/hour | 30/hour | 100/hour |
| Realtime connections | 200 concurrent | 500 concurrent | 2,000 concurrent |
| Edge Function invocations | 500K/month | 2M/month | 5M/month |
| Storage bandwidth | 2GB/month | 250GB/month | Custom |
| Database size | 500MB | 8GB | 50GB |

- [ ] Rate limits documented for your plan tier
- [ ] Client-side retry logic with exponential backoff for 429 responses
- [ ] Auth email rate limits understood (use custom SMTP to increase)
- [ ] Realtime connection limits planned for expected concurrent users

### Step 9: Review Monitoring Dashboards

Supabase provides built-in monitoring. Review these before launch to establish
baselines, and deploy a health check endpoint (full route handler in
[step-commands.md](references/step-commands.md)).

- [ ] Dashboard > Reports reviewed (API requests, auth, storage, realtime)
- [ ] Dashboard > Logs > API checked for error patterns
- [ ] Dashboard > Database > Performance Advisor reviewed and recommendations applied
- [ ] Health check endpoint deployed and monitored (uptime service)
- [ ] Error tracking configured (Sentry, LogRocket, etc.)
- [ ] Alerts set for: error rate spikes, high latency, connection pool exhaustion

### Step 10: Deploy Edge Functions with Proper Env Vars

Edge Functions run on Deno Deploy. Set environment variables via the Supabase CLI
or Dashboard, not hardcoded. Secret commands and a webhook function template in
[step-commands.md](references/step-commands.md).

- [ ] All Edge Functions deployed to production (`npx supabase functions deploy`)
- [ ] Environment secrets set via `npx supabase secrets set` (not hardcoded)
- [ ] `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` available automatically (no need to set)
- [ ] Edge Functions tested with `npx supabase functions serve` locally before deploying
- [ ] CORS headers configured for Edge Functions that receive browser requests

### Step 11: Verify Storage Bucket Policies

Storage buckets need explicit policies, similar to RLS on tables. Without
policies, buckets are inaccessible (default deny). Inspection queries and example
policies in [step-commands.md](references/step-commands.md).

- [ ] Each bucket has explicit SELECT/INSERT/UPDATE/DELETE policies
- [ ] Public buckets are intentionally public (not accidentally open)
- [ ] File size limits set per bucket (`file_size_limit` in bucket config)
- [ ] Allowed MIME types restricted per bucket (`allowed_mime_types`)
- [ ] User upload paths scoped to `auth.uid()` to prevent overwrites

### Step 12: Add Database Indexes on Frequently Queried Columns

Missing indexes are the leading cause of slow queries after launch. Add indexes on
foreign keys, filter columns, and sort columns. Diagnostic queries (missing-index,
slow-query, table-bloat) and index DDL in
[step-commands.md](references/step-commands.md).

- [ ] Indexes on all foreign key columns
- [ ] Indexes on columns used in WHERE, ORDER BY, and JOIN clauses
- [ ] `pg_stat_statements` enabled for ongoing query monitoring
- [ ] Performance Advisor reviewed (Dashboard > Database > Performance)
- [ ] `statement_timeout` set for authenticated role to prevent runaway queries
- [ ] Table bloat checked — VACUUM if dead tuple percentage > 10%

### Step 13: Apply Migrations with `npx supabase db push`

All schema changes must go through migration files, never manual Dashboard edits
in production. Migration commands in
[step-commands.md](references/step-commands.md).

- [ ] All schema changes in `supabase/migrations/` directory (version controlled)
- [ ] `npx supabase db push` tested against a fresh project
- [ ] Migration history matches between local and remote (`npx supabase migration list`)
- [ ] Rollback migration prepared for risky schema changes
- [ ] No manual schema edits in production Dashboard

### Step 14: Pre-Launch Final Verification

Run the final linked-project verification commands in
[step-commands.md](references/step-commands.md),
then confirm:

- [ ] CORS settings match production domain (Dashboard > API > CORS)
- [ ] Environment variables set correctly in deployment platform
- [ ] Realtime enabled only on tables that need it (reduces connection usage)
- [ ] Webhook endpoints registered and tested
- [ ] Load test completed on staging (see `supabase-load-scale`)
- [ ] SSL enforcement enabled (Dashboard > Database > Settings > SSL)
- [ ] DNS and custom domain verified end-to-end

## Output

- All 14 checklist sections verified with zero unchecked items
- RLS enforced on every public table with tested policies
- Key separation verified (anon client-side, service_role server-side only)
- Connection pooling via Supavisor (port 6543) for all application code
- Backups, PITR, monitoring, Edge Functions, Storage policies, indexes all verified
- Migrations applied cleanly via `npx supabase db push`

## Error Handling

Common go-live failures and their fixes. Full catalog (with HTTP status codes,
alert thresholds, and a Supabase error-code `switch` handler) in
[references/errors.md](references/errors.md).

| Issue | Cause | Solution |
| ------- | ------- | ---------- |
| `403 Forbidden` on all API calls | RLS enabled but no policies created | Add SELECT/INSERT/UPDATE/DELETE policies for each role |
| `429 Too Many Requests` | Plan rate limit exceeded | Upgrade plan or implement client-side backoff with retry |
| Connection timeout under load | Using direct connection in serverless | Switch to pooled connection string (port 6543) |
| Auth emails not delivered | Default SMTP rate-limited | Configure custom SMTP provider (SendGrid, Resend, Postmark) |
| `PGRST301` permission denied | Service role key used where anon expected | Check client initialization — use anon key for client-side |
| Storage upload fails | Missing bucket policy or size limit exceeded | Add INSERT policy and check `file_size_limit` on bucket |
| Slow queries after launch | Missing indexes on filter/join columns | Run Performance Advisor and add indexes per Step 12 |
| Migration conflicts | Manual Dashboard edits diverged from migration files | Run `npx supabase db diff` to capture drift, then commit |

## Examples

Lean patterns below; complete, copy-paste versions (Next.js client setup, health
check endpoint, full RLS policy set, storage policies, Edge Functions, rollback)
in [references/examples.md](references/examples.md).

### RLS Policy Pattern

```sql
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read published" ON public.posts
  FOR SELECT USING (status = 'published');
CREATE POLICY "Authors manage own" ON public.posts
  FOR ALL USING (auth.uid() = author_id)
  WITH CHECK (auth.uid() = author_id);
```

### Rollback

```bash
npx supabase migration new rollback_bad_change  # Create reversal SQL
npx supabase db push                             # Apply rollback
# For data: Dashboard > Database > Backups > PITR
# For app: vercel rollback / netlify deploy --prod
```

## Resources

- [references/step-commands.md](references/step-commands.md) — Full SQL/TypeScript/CLI for every step
- [references/examples.md](references/examples.md) — Complete copy-paste code patterns
- [references/errors.md](references/errors.md) — Error catalog + alert thresholds
- [references/implementation.md](references/implementation.md) — Pre-deploy config + post-launch monitoring
- [Going to Production](https://supabase.com/docs/guides/deployment/going-into-prod) — Official production checklist
- [Maturity Model](https://supabase.com/docs/guides/deployment/maturity-model) — Project lifecycle stages
- [Shared Responsibility Model](https://supabase.com/docs/guides/deployment/shared-responsibility-model) — What Supabase manages vs. what you manage
- [Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler) — Supavisor configuration
- [RLS Guide](https://supabase.com/docs/guides/database/postgres/row-level-security) — Policy patterns and examples
- [Edge Functions](https://supabase.com/docs/guides/functions) — Serverless Deno functions
- [Storage](https://supabase.com/docs/guides/storage) — File storage with policies

## Next Steps

- For SDK version upgrades, see `supabase-upgrade-migration`
- For load testing before launch, see `supabase-load-scale`
- For monitoring in production, see `supabase-monitoring`
- For Edge Function patterns, see `supabase-edge-functions`
