---
name: supabase-reference-architecture
description: "Implement enterprise Supabase reference architectures \u2014 monorepo\
  \ layout, multi-tenant RLS,\nmicroservices with cross-project access, framework\
  \ integration, edge functions, caching,\nqueue patterns, and audit logging.\nUse\
  \ when designing a new Supabase project from scratch, reviewing project structure\
  \ for\nproduction readiness, planning multi-tenant isolation, or establishing team\
  \ architecture standards.\nTrigger with phrases like \"supabase architecture\",\
  \ \"supabase project structure\",\n\"supabase monorepo\", \"supabase multi-tenant\"\
  , \"supabase reference design\",\n\"how to organize supabase at scale\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(supabase:*), Grep,
  Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- architecture
- patterns
- multi-tenant
- monorepo
compatibility: Designed for Claude Code
---
# Supabase Reference Architecture

## Overview

Production Supabase applications need more than a flat `lib/supabase.ts` file. This skill covers five enterprise architecture patterns: monorepo with shared types, multi-tenant RLS isolation, microservices with separate Supabase projects, framework integration (Next.js / SvelteKit), and operational patterns (edge functions, caching, queues, audit trails). Each pattern stands alone — pick the ones that match your scale.

For the full monorepo directory layout and microservices cross-project access, see [Project Structure](references/project-structure.md). For edge functions, caching, queue, and audit trail patterns, see [Operational Patterns](references/key-components.md).

## Prerequisites

- `@supabase/supabase-js` v2+ installed (`npm install @supabase/supabase-js`)
- Supabase CLI installed (`npm install --save-dev supabase`)
- A Supabase project at [supabase.com/dashboard](https://supabase.com/dashboard)
- Familiarity with `supabase-install-auth` (project URL, anon key, service role key)
- PostgreSQL basics (RLS policies, triggers, functions)

## Instructions

### Step 1: Browser Client and Isolated Admin Client

Share configuration and generated types, not request-bound server sessions. The singleton below is for standalone browser apps without SSR; SSR-backed browser components use the cookie-aware factory in Step 3. Create each SSR user client inside its request. Never cache authenticated responses or share a server user client across requests.

```typescript
// packages/supabase/src/client.ts — browser-only; never use as an SSR singleton
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

let client: SupabaseClient<Database> | null = null

export function getSupabaseClient(): SupabaseClient<Database> {
  if (!client) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? process.env.SUPABASE_ANON_KEY
    if (!url || !key) {
      throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables')
    }
    client = createClient<Database>(url, key)
  }
  return client
}

// Reset for testing
export function resetClient(): void {
  client = null
}
```

```typescript
// packages/supabase/src/admin.ts — isolated privileged module for Next.js
import 'server-only'
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

export function getSupabaseAdmin() {
  const url = process.env.SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !serviceKey) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY — server-only')
  }
  return createClient<Database>(url, serviceKey, {
    auth: { autoRefreshToken: false, persistSession: false }
  })
}
```

The admin client bypasses RLS. Never attach user cookies or a user session to it; invoke it only after application-owned authorization for a specific privileged operation. Keep it out of shared client exports. Other server runtimes need an equivalent build/import boundary.

### Step 2: Read-Only Multi-Tenant Membership Policies

This example authorizes reads through trusted membership rows, not user-editable metadata or a fabricated JWT claim. Only a separately authorized administrative process may provision tenants, memberships, or projects; no user write policies are supplied.

```sql
-- Migration: 20260101000000_create_tenants.sql

-- Tenants table
create table public.tenants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  plan text default 'free' check (plan in ('free', 'pro', 'enterprise')),
  created_at timestamptz default now()
);

-- Tenant membership
create table public.tenant_members (
  tenant_id uuid references public.tenants(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  role text default 'member' check (role in ('owner', 'admin', 'member', 'viewer')),
  primary key (tenant_id, user_id)
);

-- Example tenant-scoped table
create table public.projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.tenants(id) on delete cascade,
  name text not null,
  created_by uuid references auth.users(id),
  created_at timestamptz default now()
);

-- Enable RLS on every exposed table, including the authorization table.
alter table public.tenants enable row level security;
alter table public.tenant_members enable row level security;
alter table public.projects enable row level security;

-- Read-only application surface: remove existing direct role grants first.
revoke all privileges on public.tenants, public.tenant_members, public.projects
  from public, anon, authenticated;
grant select on public.tenants, public.tenant_members, public.projects
  to authenticated;

-- This policy reads only the current row; it does not query itself recursively.
create policy "Read own memberships" on public.tenant_members
  for select to authenticated
  using (user_id = (select auth.uid()));

create policy "Read member tenants" on public.tenants
  for select to authenticated
  using (exists (
    select 1 from public.tenant_members as membership
    where membership.tenant_id = tenants.id
      and membership.user_id = (select auth.uid())
  ));

create policy "Read member projects" on public.projects
  for select to authenticated
  using (exists (
    select 1 from public.tenant_members as membership
    where membership.tenant_id = projects.org_id
      and membership.user_id = (select auth.uid())
  ));
```

This is a new-table migration example. On existing tables, review other policies and inherited grants; a permissive policy can widen access. The table-local revocations above also remove grants inherited through `PUBLIC`, including configured defaults; they do not alter schema-wide defaults or privileges on other tables. Test as ordinary authenticated users, not the table owner or an RLS-bypassing admin. A query's tenant filter narrows results but never grants membership. Writes require a separate reviewed authorization design; do not add a blanket `for all` policy.

### Step 3: Framework Integration (Next.js)

User-facing SSR uses a request-scoped `@supabase/ssr` client with a publishable key (or legacy anon key) and cookie adapters. A plain `Cookie` header on a privileged client is not a user authorization boundary.

```typescript
// app/lib/supabase-server.ts — cookie-writable Route Handlers / Server Actions
import 'server-only'
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@my-platform/supabase'

export async function getSupabaseServer() {
  const cookieStore = await cookies()
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
    ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  if (!key) throw new Error('Missing Supabase publishable or anon key')

  return createServerClient<Database>(process.env.NEXT_PUBLIC_SUPABASE_URL!, key, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (updates) => {
        for (const { name, value, options } of updates) {
          cookieStore.set(name, value, options)
        }
      }
    }
  })
}

// app/api/projects/route.ts — read-only, user-authenticated request
import { getSupabaseServer } from '@/app/lib/supabase-server'

export async function GET() {
  const supabase = await getSupabaseServer()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) return Response.json({ error: 'Unauthorized' }, {
    status: 401, headers: { 'Cache-Control': 'private, no-store' }
  })

  const { data, error } = await supabase.from('projects')
    .select('id, name, created_at').order('created_at', { ascending: false }).limit(50)
  if (error) return Response.json({ error: 'Project query failed' }, {
    status: 500, headers: { 'Cache-Control': 'private, no-store' }
  })
  return Response.json(data, { headers: { 'Cache-Control': 'private, no-store' } })
}
```

Server Components cannot persist refreshed cookies. Configure the framework's Proxy/session-refresh route and its request/response cookie propagation before rendering; do not reuse the writable helper above in a read-only context or silently discard refresh writes. See the [SSR client guide](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=nextjs) for the framework-specific adapter. Never cache a response carrying another user's session.

```typescript
// app/lib/supabase-browser.ts — same cookie session as the SSR client
'use client'
import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '@my-platform/supabase'

let browserClient: ReturnType<typeof createBrowserClient<Database>> | null = null

export function getSupabaseBrowser() {
  if (!browserClient) {
    browserClient = createBrowserClient<Database>(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
        ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)!
    )
  }
  return browserClient
}
```

For SvelteKit integration and additional framework patterns, see [Examples](references/examples.md).

## Output

After applying these patterns you will have:

- Monorepo with shared Supabase client, typed database access, and centralized migrations
- Read-only tenant membership policies, with tenant filters used only for query scope
- Framework-specific integration for Next.js (server/client split) and SvelteKit (hooks)
- Edge Functions, caching layer, job queue, and audit trail (see [Operational Patterns](references/key-components.md))

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing SUPABASE_URL or SUPABASE_ANON_KEY` | Environment variables not set | Check `.env` file and ensure variables are loaded |
| `new row violates row-level security policy` | RLS blocks the operation | Check verified user identity, role grants, and the trusted membership row |
| Empty tenant result | No readable membership or no matching rows | Check the requested tenant and trusted membership; never bypass RLS |
| `TypeError: Cannot read properties of null` | Client singleton not initialized | Ensure env vars are available before first `getSupabaseClient()` call |
| `cron.schedule: permission denied` | `pg_cron` extension not enabled | Enable via dashboard: Database > Extensions > pg_cron |

For the full error reference including RLS debugging and cross-project troubleshooting, see [Error Handling Reference](references/errors.md).

## Examples

### Multi-Tenant Query Flow (TypeScript)

```typescript
// Use the current request's authenticated, non-admin client.
import { getSupabaseServer } from './supabase-server'

export async function readTenantProjects(tenantId: string) {
  const supabase = await getSupabaseServer()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) throw new Error('Authentication required')

  const { data, error } = await supabase.from('projects')
    .select('id, name, created_at')
    .eq('org_id', tenantId) // Query scope only; membership RLS authorizes access.
    .order('created_at', { ascending: false })
  if (error) throw new Error('Project query failed')
  return data
}
```

For the job queue consumer example and SvelteKit integration, see [Examples](references/examples.md).

## Resources

- [Supabase Architecture](https://supabase.com/docs/guides/getting-started/architecture)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [SSR Client Authentication](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=nextjs)
- [Edge Functions](https://supabase.com/docs/guides/functions)
- [TypeScript Support](https://supabase.com/docs/reference/javascript/typescript-support)
- [Generating Types](https://supabase.com/docs/guides/api/rest/generating-types)
- [pg_cron Extension](https://supabase.com/docs/guides/database/extensions/pg_cron)
- [Auth JWT Helper](https://supabase.com/docs/guides/auth/jwts)
- [createClient Reference](https://supabase.com/docs/reference/javascript/initializing)

## Next Steps

For performance optimization and indexing strategies, see `supabase-performance-tuning`. For deployment pipelines and CI integration, see `supabase-ci-integration`. For security hardening and policy guardrails, see `supabase-security-basics`.
