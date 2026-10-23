# Supabase Skill Pack

> 30 Claude Code skills covering Supabase SDKs, PostgreSQL RLS, Edge Functions, and documented operator workflows.

## Installation

```bash
/plugin install supabase-pack@claude-code-plugins-plus
```

## What Makes This Different

The pack includes worked SDK and SQL examples plus manual Dashboard procedures. Adapt application types, tables, and authorization before use; skill invocation does not authorize provider access, deployments, destructive actions, or secret handling.

## Skills (30)

### Getting Started (S01-S06)

| Skill | What It Does |
|-------|-------------|
| `supabase-install-auth` | Install `@supabase/supabase-js`, CLI, configure keys, generate TypeScript types |
| `supabase-hello-world` | First table migration with RLS, INSERT/SELECT/UPDATE/DELETE, filtering, joins |
| `supabase-local-dev-loop` | `supabase start`, migrations, seeds, `db diff`, Edge Function hot reload, Vitest |
| `supabase-sdk-patterns` | Typed singleton, service layer, custom errors, retry with backoff, Zod validation |
| `supabase-schema-from-requirements` | Requirements to SQL migration: tables, FKs, indexes, RLS helper functions |
| `supabase-auth-storage-realtime-core` | Auth (signup, OAuth, MFA), Storage (upload, signed URLs, bucket RLS), Realtime (Postgres changes, broadcast, presence) |

### Operations (S07-S12)

| Skill | What It Does |
|-------|-------------|
| `supabase-common-errors` | PGRST error codes, PostgreSQL errors, Auth/Storage/Realtime diagnostics, RLS debugging |
| `supabase-debug-bundle` | Collect redacted debug bundle: env info, `pg_stat_statements`, connection health |
| `supabase-rate-limits` | Supabase limits by tier, retry with backoff, request queue, batch operations, idempotency |
| `supabase-security-basics` | Anon vs service role keys, RLS policy patterns, security audit checklist |
| `supabase-prod-checklist` | Full production checklist: RLS, SSL, indexes, PITR, health checks, rollback |
| `supabase-upgrade-migration` | v1-to-v2 breaking changes, auth method renames, code migration steps |

### DevOps (P13-P18)

| Skill | What It Does |
|-------|-------------|
| `supabase-ci-integration` | GitHub Actions: local Supabase in CI, migration deploy, pgTAP tests, type drift |
| `supabase-deploy-integration` | Edge Functions (Deno), Vercel/Fly.io/Cloud Run deploy, Supavisor connection pooling |
| `supabase-webhooks-events` | Database webhooks, `pg_net` async HTTP from triggers, Edge Function handlers, Auth hooks |
| `supabase-performance-tuning` | `EXPLAIN ANALYZE`, index optimization, RLS performance, caching, N+1 elimination |
| `supabase-cost-tuning` | Pricing breakdown, database size audit, storage cleanup, bandwidth reduction |
| `supabase-reference-architecture` | Layered project structure: client layer, service layer, hooks, error handling, health check |

### Enterprise (F19-F24)

| Skill | What It Does |
|-------|-------------|
| `supabase-multi-env-setup` | Dev/staging/prod with separate Supabase projects, migration promotion, env guards |
| `supabase-observability` | `pg_stat_statements`, structured logging, instrumented client, health checks, alerting |
| `supabase-incident-runbook` | 5-minute triage, platform vs app isolation, mitigation, communication, postmortem |
| `supabase-data-handling` | PII classification, GDPR deletion, data export, retention policies with pg_cron, audit log |
| `supabase-enterprise-rbac` | Custom roles, JWT custom claims via Auth Hooks, org-scoped RLS, SAML SSO |
| `supabase-migration-deep-dive` | Firebase/MongoDB to Supabase, strangler fig pattern, data migration scripts, auth migration |

### Advanced (X25-X30)

| Skill | What It Does |
|-------|-------------|
| `supabase-advanced-troubleshooting` | `EXPLAIN ANALYZE`, RLS step-by-step debug, connection leaks, lock contention, Realtime debug |
| `supabase-load-scale` | k6 load test scripts, connection pool sizing, read replicas, capacity planning |
| `supabase-reliability-patterns` | Circuit breaker, idempotent writes, bulkhead isolation, graceful degradation, DLQ |
| `supabase-policy-guardrails` | ESLint rules, pre-commit secret scanning, CI RLS checks, runtime safety guards |
| `supabase-architecture-variants` | Monolith vs modular monolith vs service layer decision matrix with migration paths |
| `supabase-known-pitfalls` | 12 anti-patterns ranked by severity with fix + detection for each |

## Key Technologies Covered

- **SDK**: `@supabase/supabase-js` v2, `@supabase/ssr`, TypeScript generics
- **Database**: PostgreSQL, PostgREST, Row Level Security, `pg_stat_statements`, `pg_net`, `pg_cron`
- **Auth**: Email/password, OAuth (Google, GitHub), Magic Links, MFA, SAML SSO, Auth Hooks, JWT custom claims
- **Storage**: Uploads, signed URLs, public URLs, bucket RLS policies, TUS resumable uploads
- **Realtime**: Postgres Changes, Broadcast, Presence
- **Edge Functions**: Deno runtime, `supabase functions deploy`, local serve with hot reload
- **CLI**: `supabase start`, `supabase db push`, `supabase db diff`, `supabase gen types`, `supabase migration new`
- **Deployment**: Vercel, Fly.io, Cloud Run, Supavisor connection pooling

## Runtime and CLI Setup

Current JavaScript SDK releases require Node.js 22+ ([SDK support policy](https://github.com/supabase/supabase-js#nodejs)); the Python SDK requires Python 3.9+ ([package metadata](https://pypi.org/project/supabase/)). The npm CLI has its own Node.js 20+ floor: install it as a project dev dependency (`npm install --save-dev supabase`) and run `npx supabase`. Homebrew or Scoop provide supported global installations. See the [official CLI setup](https://supabase.com/docs/guides/local-development/cli/getting-started).

Pack homepage: https://tonsofskills.com/learn/supabase/

## Usage

Skills auto-activate based on context. Examples:

- "Help me set up Supabase" activates `supabase-install-auth`
- "My Supabase query is slow" activates `supabase-performance-tuning`
- "Set up RLS for my tables" activates `supabase-security-basics`
- "Deploy my Edge Function" activates `supabase-deploy-integration`
- "Migrate from Firebase to Supabase" activates `supabase-migration-deep-dive`

## License

MIT
