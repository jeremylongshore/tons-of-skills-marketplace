---
name: supabase-architecture-variants
description: |
  Use when choosing how to integrate Supabase into a specific stack — setting up
  Next.js SSR auth flows, wiring an SPA or React Native client, configuring mobile
  deep links, or designing multi-tenant data isolation. Covers where the client runs
  (browser vs server) and which key it uses (anon respects RLS, service_role bypasses it).
  Trigger with phrases like "supabase next.js", "supabase SSR", "supabase react native",
  "supabase SPA", "supabase serverless", "supabase multi-tenant", "supabase server component",
  "supabase architecture", "supabase service_role server".
allowed-tools: Read, Write, Edit, Bash(supabase:*), Bash(npx:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- architecture
- nextjs
- ssr
- spa
- mobile
- multi-tenant
- serverless
compatibility: Designed for Claude Code
---
# Supabase Architecture Variants

## Overview

Every Supabase `createClient` configuration turns on two questions: **where the client runs** (browser vs server) and **which key it uses** (`anon` respects RLS; `service_role` bypasses it). This skill supplies production-ready patterns for five architectures — Next.js SSR, SPA, Mobile, Serverless Edge Functions, and Multi-tenant isolation.

## Prerequisites

- `@supabase/supabase-js` v2+ installed
- `@supabase/ssr` package for Next.js SSR (v0.5+)
- Supabase project with URL, `anon` key, and `service_role` key
- TypeScript project with generated database types (`supabase gen types typescript`)
- For mobile: React Native with Expo or bare workflow

## Instructions

Pick the architecture that matches the target stack, then follow the linked walkthrough for the full, copy-ready client setup.

| Architecture | Client(s) | Key | Session storage |
| -------------- | ----------- | ----- | ----------------- |
| Next.js SSR | Server (cookies) + browser + admin | `anon` in-request, `service_role` server-only | HTTP cookies |
| SPA (React/Vue) | Single browser client | `anon` only | `localStorage` |
| Mobile (React Native) | Single native client | `anon` only | `AsyncStorage` |
| Serverless (Edge Functions) | Per-request client | `anon` (forwarded JWT) or `service_role` | none (stateless) |
| Multi-tenant | Any of the above | `anon` + RLS, or schema-per-tenant | per host pattern |

### Step 1 — Next.js SSR (App Router)

Next.js App Router needs **two separate clients**: a server client that reads/writes auth cookies via `@supabase/ssr`, and a browser client for client components. A third `service_role` admin client is used only in Server Actions/Route Handlers and must **never** reach the browser. The browser client is the minimal skeleton:

```typescript
// lib/supabase/client.ts
'use client'
import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '../database.types'

export function createSupabaseBrowser() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!  // anon key only — respects RLS
  )
}
```

Full walkthrough — server client, admin client, middleware session refresh, server component usage, Server Actions, and the OAuth callback route: [Next.js SSR patterns](references/nextjs-ssr.md).

### Step 2 — SPA (React/Vue) and Mobile (React Native)

SPAs and mobile apps both use a **single browser/native client with the `anon` key**; all authorization is enforced by RLS and the `service_role` key is never bundled. They differ only in session storage (`localStorage` for SPA, `AsyncStorage` for mobile) and OAuth handling (URL detection for SPA, deep links for mobile). Minimal SPA skeleton:

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

export const supabase = createClient<Database>(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
  { auth: { autoRefreshToken: true, persistSession: true, detectSessionInUrl: true } }
)
```

Full walkthrough — SPA singleton + auth-state listener, React Query hooks, React Native `AsyncStorage` client, mobile OAuth with deep links, and Expo `app.json` config: [SPA and mobile patterns](references/spa-and-mobile.md).

### Step 3 — Serverless (Edge Functions) and Multi-Tenant

Edge Functions create a **per-request** client from the forwarded JWT (stateless, no session persistence), escalating to `service_role` only for privileged operations. Multi-tenant isolation is either RLS-based (a `tenant_members` lookup gates every row) or schema-per-tenant.

Full walkthrough — Edge Function per-request clients, admin escalation, RLS multi-tenant isolation, and tenant-scoped SDK queries: [serverless and multi-tenant patterns](references/serverless-and-multi-tenant.md).

## Output

- Next.js SSR setup with server client (cookies-based auth), browser client, and middleware
- Server Actions using admin client with `service_role` for privileged operations
- SPA pattern with singleton client, React Query integration, and auth state listener
- React Native setup with `AsyncStorage`, deep link OAuth, and in-app browser
- Edge Function patterns for per-request auth and admin escalation
- Multi-tenant RLS isolation with `tenant_members` lookup and scoped queries
- Decision matrix for choosing the right architecture per stack

## Error Handling

| Issue | Cause | Solution |
| ------- | ------- | ---------- |
| `AuthSessionMissingError` in Server Component | Cookies not passed to Supabase client | Use `createServerClient` from `@supabase/ssr` with cookie handlers |
| OAuth redirect fails in React Native | Missing deep link scheme | Add `scheme` to app.json and configure Supabase redirect URL |
| `service_role` key in client bundle | Wrong env var prefix (`NEXT_PUBLIC_`) | Remove `NEXT_PUBLIC_` prefix; only server code should access it |
| Multi-tenant data leak | Missing RLS policy or missing `tenant_id` filter | Verify RLS is enabled and policies check `tenant_members` |
| Edge Function `auth.getUser()` returns null | Missing Authorization header | Forward user's JWT from the client call |
| Session not persisting on mobile | `AsyncStorage` not configured | Pass `AsyncStorage` in auth config; ensure package is installed |

## Examples

Verify tenant isolation by impersonating a JWT and confirming RLS scopes the result:

```sql
-- Test that RLS properly isolates tenants
SET request.jwt.claims = '{"sub": "user-uuid-1"}';

-- Should only return projects for user-uuid-1's tenant
SELECT * FROM public.projects;
```

More runnable examples — the Next.js OAuth callback route and further end-to-end flows: [Next.js SSR patterns](references/nextjs-ssr.md) and [examples](references/examples.md).

## Resources

- [Supabase SSR (Next.js)](https://supabase.com/docs/guides/auth/server-side/nextjs)
- [Supabase React Native](https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Multi-Tenant with RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Auth Deep Linking](https://supabase.com/docs/guides/auth/native-mobile-deep-linking)
- [@supabase/ssr Package](https://supabase.com/docs/guides/auth/server-side/overview)

## Next Steps

After wiring the client for your architecture, review `supabase-known-pitfalls` for common mistakes and anti-patterns to avoid, then generate database types with `supabase gen types typescript` and enable RLS on every table before shipping.
