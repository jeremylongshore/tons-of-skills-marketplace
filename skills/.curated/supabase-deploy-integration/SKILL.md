---
name: supabase-deploy-integration
description: 'Deploy and manage Supabase projects in production. Covers database migrations,

  Edge Functions deployment, secrets management, zero-downtime rollouts,

  blue/green branching, rollback procedures, and post-deploy health checks.

  Use when deploying Supabase to production, running migrations, deploying

  Edge Functions, managing secrets, or implementing zero-downtime deployments.

  Trigger: "deploy supabase", "supabase migration push", "deploy edge function",

  "supabase rollback", "supabase blue green", "supabase health check".

  '
allowed-tools: Read, Write, Edit, Bash(npx:supabase), Bash(supabase:*), Bash(curl:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- deployment
- migrations
- edge-functions
- devops
compatibility: Designed for Claude Code
---
# Supabase Deploy Integration

## Overview

Deploy and manage Supabase projects in production with confidence. This skill covers the full deployment lifecycle: pushing database migrations, deploying Edge Functions, managing secrets, executing zero-downtime rollouts with blue/green database branching, rolling back failed migrations, and verifying deployment health. Verify the approved project and working directory before remote work. Link-based database commands use `--linked`; only commands that document a project-ref flag use it directly.

**SDK**: `@supabase/supabase-js` — [supabase.com/docs](https://supabase.com/docs)

## Prerequisites

- Supabase CLI installed (`npm install --save-dev supabase` or `npx supabase`)
- Supabase project linked (`npx supabase link --project-ref <your-ref>`)
- Database migrations in `supabase/migrations/` directory
- Edge Functions in `supabase/functions/` directory (if deploying functions)
- `SUPABASE_ACCESS_TOKEN` set for CI/non-interactive environments

## Instructions

### Step 1 — Push Database Migrations and Deploy Edge Functions

Apply pending database migrations to your production project, then deploy Edge Functions with their required secrets.

**Database migrations:**

```bash
# Link only the approved target; inspect the CLI confirmation against the Dashboard.
npx supabase link --project-ref "$PROJECT_REF"

# Confirm migration history in this same working directory and approved project.
npx supabase migration list --linked
npx supabase db push --linked --dry-run

# Apply only after target, migration review, and deployment approval.
npx supabase db push --linked
```

Each migration file in `supabase/migrations/` is applied in timestamp order. The CLI tracks which migrations have already been applied and only runs new ones.

**Edge Functions deployment:**

```bash
# Deploy a single Edge Function
npx supabase functions deploy process-webhook --project-ref $PROJECT_REF

# Deploy all Edge Functions at once
npx supabase functions deploy --project-ref $PROJECT_REF
```

**Secrets management — set environment variables for Edge Functions:**

```bash
# Set individual secrets
npx supabase secrets set STRIPE_KEY=sk_live_xxx --project-ref $PROJECT_REF
npx supabase secrets set WEBHOOK_SECRET=whsec_xxx --project-ref $PROJECT_REF

# Set multiple secrets at once
npx supabase secrets set API_KEY=value1 SIGNING_KEY=value2 --project-ref $PROJECT_REF

# List current secrets (names only, values hidden)
npx supabase secrets list --project-ref $PROJECT_REF

# Remove a secret
npx supabase secrets unset OLD_KEY --project-ref $PROJECT_REF
```

### Step 2 — Zero-Downtime Deployments and Blue/Green Branching

Use Supabase database branching to test migrations against a production-like environment before cutting over.

**Blue/green deployment via database branching:**

```bash
# Create a preview branch (clones schema, not data)
npx supabase branches create staging-v2 --project-ref $PROJECT_REF

# The branch gets its own connection string and API URL
# Test your migrations against the branch first
npx supabase link --project-ref "$BRANCH_REF"
# Verify the linked branch target before applying.
npx supabase db push --linked

# Verify the branch works with your application
# Point a staging instance at the branch's connection string

# When satisfied, merge branch changes into production
# Apply the same migrations to the main project
npx supabase link --project-ref "$PROJECT_REF"
# Verify the approved main project target again; linking is per working directory.
npx supabase db push --linked

# Delete the branch after successful cutover
npx supabase branches delete staging-v2 --project-ref $PROJECT_REF
```

**Rolling deployment pattern for zero downtime:**

1. Deploy backward-compatible migration first (additive schema changes only)
2. Deploy application code that works with both old and new schema
3. Run data backfill if needed
4. Deploy cleanup migration (drop old columns/tables) after all instances updated

```sql
-- Migration 1: Add new column (backward compatible)
ALTER TABLE orders ADD COLUMN status_v2 text;

-- Migration 2: Backfill (run separately, can be done in batches)
UPDATE orders SET status_v2 = status WHERE status_v2 IS NULL;

-- Migration 3: Cleanup (only after all app instances use status_v2)
ALTER TABLE orders DROP COLUMN status;
ALTER TABLE orders RENAME COLUMN status_v2 TO status;
```

### Step 3 — Rollback, Health Checks, and Monitoring

When a migration fails or causes issues, roll it back. Then verify deployment health.

**Recovery and migration-history repair are different operations:**

First verify the approved project, inspect the actual schema/data effects, and review a compensating migration or a tested backup-recovery plan. A failed migration is not automatically reversible, and a history edit does not restore business data.

```bash
# In the explicitly linked, verified target working directory:
npx supabase migration list --linked
# Author and review the actual compensating SQL before any remote apply.
npx supabase migration new reviewed_compensation
```

Only if the history itself needs repair, use the exact reviewed migration version with the documented command:

```text
npx supabase migration repair <reviewed-version> --status reverted --linked
```

That command changes migration-history metadata; it does not execute a down migration or undo data changes. Do not choose a version by parsing the last line of CLI output. Recheck history, schema, and application/data recovery independently after the approved operation.

**Post-deploy health check:**

```typescript
import { createClient } from '@supabase/supabase-js'

async function healthCheck() {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )

  const checks = {
    database: false,
    auth: false,
    storage: false,
    functions: false,
  }

  // Database connectivity
  const dbStart = Date.now()
  const { error: dbErr } = await supabase.from('_health').select('id', { head: true }).limit(1)
  checks.database = !dbErr // Every returned error remains a failed scoped query
  const dbLatency = Date.now() - dbStart

  // Fresh user verification, not a standalone Auth-platform availability test.
  const { data: { user }, error: authErr } = await supabase.auth.getUser()
  checks.auth = !authErr && !!user

  // Storage service
  const { error: storageErr } = await supabase.storage.listBuckets()
  checks.storage = !storageErr

  // Edge Function ping (replace with your function name)
  try {
    const { error: fnErr } = await supabase.functions.invoke('health-ping')
    checks.functions = !fnErr
  } catch {
    checks.functions = false
  }

  const allHealthy = Object.values(checks).every(Boolean)

  console.log({
    status: allHealthy ? 'probes_succeeded' : 'probe_failed_or_not_authorized',
    checks,
    db_latency_ms: dbLatency,
    timestamp: new Date().toISOString(),
  })

  return allHealthy
}
```

Use an approved existing `_health` table and independently reviewed user session for these probes. A missing table, absent user, or authorization error cannot be counted as healthy. `PGRST116` is HTTP 406 for zero/multiple rows in a singular response, not a missing-table condition. These checks do not certify whole-platform availability.

**Monitoring via Supabase Dashboard:**

- Navigate to **Dashboard > Reports** for database performance metrics
- Check **Dashboard > Logs > Postgres** for slow queries and errors
- Review **Dashboard > Logs > Edge Functions** for function invocation logs
- Set up **Dashboard > Database > Webhooks** for change notifications
- Monitor **Dashboard > Settings > Infrastructure** for resource utilization

## Output

After completing these steps, you will have:

- All pending database migrations applied to production via `supabase db push`
- Edge Functions deployed to Supabase's global edge network
- Secrets configured for Edge Functions without exposing values in code
- A zero-downtime deployment strategy using database branching or rolling migrations
- Reviewed recovery plan with migration-history repair kept separate from schema/data rollback
- Health check endpoint verifying database, auth, storage, and function connectivity
- Monitoring configured through the Supabase Dashboard Reports

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `migration already applied` | Re-running a migration that succeeded | Check `npx supabase migration list` — skip if already applied |
| `permission denied for schema` | Migration modifies a protected schema | Use `ALTER DEFAULT PRIVILEGES` or run via dashboard SQL editor |
| `functions deploy: not linked` | Project not linked locally | Run `npx supabase link --project-ref $PROJECT_REF` first |
| `secret already exists` | Setting a secret that exists | `supabase secrets set` overwrites by default — this is safe |
| `branch limit reached` | Too many active branches | Delete unused branches with `supabase branches delete` |
| `migration repair` has no effect | Wrong version number | Run `supabase migration list` to find the exact version string |
| `connection refused` on db push | IP not allowlisted | Add your IP in Dashboard > Settings > Database > Network Bans |
| Edge Function 500 after deploy | Missing secret or import error | Inspect the function Logs and Invocations in the project Dashboard |

## Examples

**CI/CD pipeline — GitHub Actions:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Supabase
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Link project
        run: npx supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Push migrations
        run: npx supabase db push --linked
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Deploy Edge Functions
        run: npx supabase functions deploy --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

**Recovery review checklist:**

1. Verify the linked project against the approved target and inspect migration history with `npx supabase migration list --linked`.
2. Determine what schema and business-data changes actually occurred; choose a reviewed compensating migration or tested backup recovery.
3. Treat `migration repair` solely as an explicitly reviewed history correction, never an automatic rollback.
4. Verify data reconciliation and application behavior before declaring recovery complete.

## Resources

- [Database Migrations Guide](https://supabase.com/docs/guides/deployment/database-migrations)
- [Edge Functions Deployment](https://supabase.com/docs/guides/functions/deploy)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [Database Branching](https://supabase.com/docs/guides/deployment/branching)
- [Secrets Management](https://supabase.com/docs/guides/functions/secrets)
- Supabase Dashboard Reports

## Next Steps

- For schema design from requirements, see `supabase-schema-from-requirements`
- For RLS policy configuration, see `supabase-policy-guardrails`
- For webhook and event handling, see `supabase-webhooks-events`
- For production readiness checklist, see `supabase-prod-checklist`
- For multi-environment setup, see `supabase-multi-env-setup`
