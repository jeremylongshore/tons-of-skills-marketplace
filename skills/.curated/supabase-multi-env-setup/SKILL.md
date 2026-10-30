---
name: supabase-multi-env-setup
description: |
  Configure Supabase across development, staging, and production with separate projects,
  environment-specific secrets, and safe migration promotion.
  Use when setting up multi-environment deployments, isolating dev from prod data,
  configuring per-environment Supabase projects, or promoting migrations through environments.
  Trigger with "supabase environments", "supabase staging", "supabase dev prod",
  "supabase multi-project", "supabase env config", "database branching".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(supabase:*), Bash(vercel:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- deployment
- environments
- multi-env
- devops
compatibility: Designed for Claude Code
---
# Supabase Multi-Environment Setup

## Overview

Production Supabase deployments require a separate project per environment — each with its
own URL, API keys, database, and RLS policies. This skill configures a three-tier
architecture (local dev, staging, production) with safe migration promotion via
`supabase db push`, environment-aware `createClient` initialization, database branching
for preview deployments, and CI/CD that prevents accidental cross-environment operations.

**When to use:** setting up a new project with multiple environments, migrating from a
single-project setup, adding staging to an existing dev/prod split, or configuring preview
environments with database branching.

## Prerequisites

- Three separate Supabase projects created at [supabase.com/dashboard](https://supabase.com/dashboard) (dev, staging, production)
- Supabase CLI installed: `npm install --save-dev supabase` or `npx supabase --version`
- `@supabase/supabase-js` v2+ installed in your project
- Node.js 22+ for current SDK releases, with a framework that supports `.env` files (Next.js, Nuxt, SvelteKit, etc.)
- A secret management solution for CI (GitHub Actions Secrets, Vercel env vars, etc.)

## Instructions

The workflow is three steps. Each step below gives the shape and the one command that
matters; the [full implementation walkthrough](references/implementation.md) carries the
complete env files, TypeScript client factory, RLS policies, CI/CD workflow, and seed data
verbatim.

### Step 1: Environment Files and Project Layout

Keep one Supabase CLI project with **shared migrations** and one `.env.*` file per
environment. Credential-bearing files, including `.env.local`, stay gitignored. Commit only a reviewed `.env.example` containing placeholders, never real local or hosted credentials.

```
supabase/migrations/   # shared schema — every env applies the same migrations
.env.local             # local credentials (gitignored)
.env.staging           # staging project creds  (gitignored)
.env.production        # production project creds (gitignored — NEVER commit)
.env.example           # reviewed placeholders only (may be committed)
```

The CLI links **one project at a time**. Before any `db push` or `functions deploy`,
re-link to the target:

```text
npx supabase link --project-ref <target-ref>
```

See the [implementation walkthrough](references/implementation.md) (Step 1)
for full `.env.*` contents, the `.gitignore` block, and the local-port reference.

### Step 2: Environment-Aware Client and Safeguards

Detect the active environment once, then build browser (anon key, respects RLS) and server
(service-role key, bypasses RLS) clients from it. Gate every destructive helper behind a
production guard so seeds and resets can never fire against prod:

```typescript
export function requireNonProduction(operation: string): void {
  if (isProduction()) {
    throw new Error(`[BLOCKED] "${operation}" is not allowed in production.`);
  }
}
```

The [implementation walkthrough](references/implementation.md) (Step 2)
has the full `lib/env.ts` detection, the `createBrowserClient` / `createServerClient`
factory, the `seedTestData` / `resetDatabase` guards, and environment-scoped RLS policies.

### Step 3: Migration Promotion and Database Branching

Promote schema changes strictly local → staging → production. `db reset` applies
everything plus `seed.sql` locally; `db push` applies only new migrations to a linked
remote:

```text
npx supabase db reset                              # local: all migrations + seed
npx supabase link --project-ref <staging-ref> && npx supabase db push   # then staging
npx supabase link --project-ref <prod-ref>    && npx supabase db push   # then production
```

For preview deployments, `supabase branches create` (Pro plan) gives each feature its own
isolated database, URL, and keys. Full migration workflow, branching commands, the
GitHub Actions deploy workflow (with a production approval gate), and seed data live in the
[implementation walkthrough](references/implementation.md) (Step 3).

## Output

Completing this skill produces:

- **Three isolated Supabase projects** — each with its own URL, API keys, database, and storage
- **Environment-specific `.env` files** — `.env.local`, `.env.staging`, `.env.production` with correct credentials
- **Environment-aware `createClient`** — browser and server clients auto-configured from env vars with `x-environment` header tracking
- **Production safeguards** — `requireNonProduction()` blocks destructive operations outside local/staging
- **Migration promotion pipeline** — `supabase db push` promotes schema changes local → staging → production
- **Database branching** — preview environments get isolated database branches (Pro plan)
- **CI/CD workflows** — GitHub Actions deploys migrations and Edge Functions per environment with approval gates for production
- **Generated TypeScript types** — `database.types.ts` generated from local or linked project schema

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `Cannot find project ref` | CLI not linked to a project | Run `npx supabase link --project-ref <ref>` before `db push` |
| `Migration has already been applied` | Re-running an existing migration | Check `supabase_migrations.schema_migrations` table; migrations are idempotent by ref |
| `Permission denied for schema public` | Wrong database password | Verify `SUPABASE_DB_PASSWORD` matches the project's database password in dashboard |
| `Seed data appeared in production` | Ran `supabase db reset` on prod | `seed.sql` only runs on `db reset` — never reset production; use `db push` instead |
| `Wrong environment keys in client` | `.env` file mismatch | Check `SUPABASE_ENV` var and verify URL matches expected project ref |
| `Branch creation failed` | Free plan or branching not enabled | Database branching requires Supabase Pro plan; enable in project settings |
| `Migration drift between envs` | Skipped staging promotion | Always promote through staging first; compare with `supabase migration list` per project |
| `Type generation mismatch` | Types generated from wrong env | Regenerate from local (`--local`) or re-link to the canonical environment |

## Examples

Three worked examples live in [references/examples.md](references/examples.md). The fastest
path — a full three-env bootstrap from `supabase init` to a production `db push` — is:

```bash
npx supabase init && npx supabase start        # local, copy keys to .env.local
npx supabase migration new create_users        # author schema, then:
npx supabase db reset                           # verify locally
npx supabase link --project-ref "<staging-ref>" && npx supabase db push
npx supabase link --project-ref "<prod-ref>"    && npx supabase db push
```

Examples 2 and 3 ([full file](references/examples.md)) show a Next.js middleware that
stamps and gates on `x-supabase-env`, and an admin handler that calls `requireNonProduction`
before a destructive RPC.

## Resources

- [Managing Environments — Supabase Docs](https://supabase.com/docs/guides/deployment/managing-environments)
- [Database Migrations — Supabase Docs](https://supabase.com/docs/guides/deployment/database-migrations)
- [Database Branching — Supabase Docs](https://supabase.com/docs/guides/deployment/branching)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli/introduction)
- [createClient — @supabase/supabase-js](https://supabase.com/docs/reference/javascript/initializing)
- [GitHub Actions with Supabase](https://supabase.com/docs/guides/deployment/managing-environments#using-github-actions)
- [12-Factor App — Config](https://12factor.net/config)
- [Full implementation walkthrough](references/implementation.md) · [Examples](references/examples.md)

## Next Steps

- For authentication patterns across environments, see `supabase-auth-storage-realtime-core`
- For RLS policy testing and validation, see `supabase-policy-guardrails`
- For local development workflow optimization, see `supabase-local-dev-loop`
- For monitoring and observability across environments, see `supabase-observability`
