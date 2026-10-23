---
name: supabase-security-basics
description: 'Apply Supabase security best practices: anon vs service_role key separation,

  RLS enforcement, policy patterns, JWT verification, and API hardening.

  Use when securing a Supabase project, auditing API key usage,

  implementing Row Level Security, or running a production security checklist.

  Trigger with phrases like "supabase security", "supabase RLS",

  "secure supabase", "supabase API key", "supabase hardening",

  "row level security", "service role key".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(supabase:*), Bash(npx supabase:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- security
- rls
- jwt
- api-keys
compatibility: Designed for Claude Code
---
# Supabase Security Basics

## Overview

The Data API exposes configured schemas through PostgREST. Access depends on schema exposure, the requesting role’s object grants, and RLS policies; a non-RLS table is not automatically readable and writable without grants. This skill covers the three pillars of Supabase security: key separation (anon vs service_role), RLS policy enforcement, and API surface hardening.

## Prerequisites

- Supabase project created (local or hosted) with Dashboard access
- `@supabase/supabase-js` installed (`npm install @supabase/supabase-js`)
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` environment variables configured
- Basic understanding of SQL and Postgres

## Instructions

### Step 1 — Understand the Two API Keys

Distinguish public and privileged keys. The table below describes legacy JWT-based keys; current projects also support publishable and secret keys, with different rotation and verification behavior:

| Key | Environment Variable | Exposed to Client? | RLS Behavior |
|-----|---------------------|-------------------|--------------|
| **Anon key** | `SUPABASE_ANON_KEY` | Yes — browser-safe | Respects all RLS policies |
| **Service role key** | `SUPABASE_SERVICE_ROLE_KEY` | **NEVER** expose | Bypasses ALL RLS |

The anon key is a JWT that PostgREST uses to determine which RLS policies apply. It may be included in client-side bundles; the effective role still needs appropriate grants and RLS on exposed tables. A public key does not identify a signed-in user. The service role key bypasses every RLS policy and should only ever exist in server-side code (API routes, Edge Functions, cron jobs, migration scripts).

```typescript
// CORRECT: anon key on the client
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

```typescript
// CORRECT: service role key ONLY in server-side code
// e.g., app/api/admin/route.ts (Next.js server route)
import { createClient } from '@supabase/supabase-js'

const supabaseAdmin = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { autoRefreshToken: false, persistSession: false } }
)
```

```typescript
// WRONG — service role key in client-side code
// This bypasses ALL RLS and leaks your admin key to every user
const supabase = createClient(url, process.env.NEXT_PUBLIC_SERVICE_ROLE_KEY!)  // NEVER DO THIS
```

**Key rotation:** Inventory legacy JWT keys, publishable/secret API keys, and Auth signing keys separately. Follow the current [API-key migration](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys) and signing-key procedures for the actual key type. Stage and verify consumer cutover, then explicitly revoke/deactivate the retired credential as supported. Coexistence, caching, signing-key grace periods, and already-issued JWT lifetime differ; do not promise universal immediate invalidation or zero grace. Never print keys during verification.

### Step 2 — Enforce Row Level Security on Every Table

Audit configured exposed schemas and grants as well as RLS. Non-RLS tables can expose rows to roles granted access; enabling RLS constrains ordinary roles but does not constrain a superuser, BYPASSRLS role, or normally the table owner. Test the actual request role and identity.

```sql
-- Audit: find tables missing RLS
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Enable RLS on every public table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- With no applicable policies, ordinary RLS-constrained roles are denied.
-- Grant and add policies ONLY for reviewed required operations. SELECT-only
-- access does not require INSERT/UPDATE/DELETE policies; keep writes denied.
```

**Policy patterns — independently reviewed operations:**

The following policies are alternatives to adopt only for required operations, not a mandate to enable every write. Review existing permissive policies and grants first; a policy alone does not grant table privileges.

```sql
-- SELECT: user can only read their own rows
CREATE POLICY "Users read own data"
  ON public.todos FOR SELECT
  USING (auth.uid() = user_id);

-- INSERT: user can only insert rows for themselves
CREATE POLICY "Users insert own data"
  ON public.todos FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- UPDATE: user can only update their own rows
CREATE POLICY "Users update own data"
  ON public.todos FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- DELETE: user can only delete their own rows
CREATE POLICY "Users delete own data"
  ON public.todos FOR DELETE
  USING (auth.uid() = user_id);
```

**Policy pattern — public read, authenticated write:**

```sql
CREATE POLICY "Anyone can read posts"
  ON public.posts FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can insert"
  ON public.posts FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);
```

**Policy pattern — role-based access via custom JWT claims:**

```sql
-- Admin-only policy using app_metadata
CREATE POLICY "Admins have full access"
  ON public.settings FOR ALL
  USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  );
```

To set custom claims server-side:

```typescript
// Server-side only — requires service role key
const { error } = await supabaseAdmin.auth.admin.updateUserById(userId, {
  app_metadata: { role: 'admin' }
})
```

**Policy pattern — organization-scoped access:**

```sql
CREATE POLICY "Org members can read projects"
  ON public.projects FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.members
      WHERE members.organization_id = projects.organization_id
      AND members.user_id = auth.uid()
    )
  );
```

**Key distinction — USING vs WITH CHECK:**

- `USING (expr)` — filters which existing rows the user can see (SELECT, UPDATE, DELETE)
- `WITH CHECK (expr)` — validates new/modified row data (INSERT, UPDATE)
- For UPDATE, you need both: USING controls which rows can be targeted, WITH CHECK controls what the new values can be

### Step 3 — Harden the API Surface

**JWT verification:** Supabase verifies JWTs server-side automatically. The `auth.uid()` function in RLS policies extracts the authenticated user's ID from the verified JWT. You do not need to verify tokens manually in RLS policies — Supabase handles this.

**SQL injection prevention:** The Supabase JS SDK uses parameterized queries internally. Never build raw SQL strings from user input — always use the SDK query builder:

```typescript
// SAFE: SDK parameterizes automatically
const { data } = await supabase
  .from('posts')
  .select('*')
  .eq('author_id', userId)
  .ilike('title', `%${searchTerm}%`)

// DANGEROUS: raw SQL with string interpolation
// Only use supabase.rpc() with parameterized functions, never template literals
```

**Network restrictions:** Restrict direct database connections to known IP ranges in Dashboard > Settings > Database > Network Restrictions. This does not affect the REST API (which goes through PostgREST) but protects direct Postgres connections.

**CORS boundary:** For browser calls to an Edge Function, implement the documented [function CORS/preflight handling](https://supabase.com/docs/guides/functions/cors) and the application’s reviewed origin policy. This is not a universal Data API Dashboard CORS setting. Auth redirect allowlists are a separate control. Origins and preflight responses are not authentication or row authorization; retain verified identity, grants, and RLS.

**Disable unused auth providers:** Dashboard > Authentication > Providers. Disable any provider you are not actively using (email, phone, Google, GitHub, etc.) to reduce attack surface.

**SSL enforcement:** Dashboard > Settings > Database > SSL Configuration. Enforce SSL for all direct database connections.

**Statement timeouts:** Prevent long-running queries from exhausting database resources:

```sql
ALTER ROLE authenticated SET statement_timeout = '10s';
ALTER ROLE anon SET statement_timeout = '5s';
```

**Revoke default schema grants (verify only):**

```sql
-- Supabase handles this by default, but verify:
-- anon and authenticated roles should only access data through RLS policies
SELECT grantee, privilege_type, table_name
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
AND grantee IN ('anon', 'authenticated')
ORDER BY table_name, grantee;
```

## Output

After completing these steps you will have:

- Anon key used exclusively in client-side code, service role key restricted to server-side
- RLS enabled on every public table with explicit policies per operation
- Custom JWT claims configured for role-based access patterns
- Network restrictions, CORS, SSL, and statement timeouts hardened
- Unused auth providers disabled

### Security Audit Checklist

- [ ] RLS enabled on ALL public tables (`SELECT rowsecurity FROM pg_tables WHERE schemaname='public'`)
- [ ] Every table has at least one RLS policy per needed operation
- [ ] Service role key is NOT in any client-side or `NEXT_PUBLIC_*` environment variables
- [ ] `.env` files are in `.gitignore`
- [ ] Email confirmation enabled (Dashboard > Authentication > Settings)
- [ ] OAuth redirect URLs restricted to your domains
- [ ] Unused auth providers disabled
- [ ] SSL enforcement enabled (Dashboard > Database > SSL)
- [ ] Database password changed from default
- [ ] Network restrictions configured for direct DB connections
- [ ] `statement_timeout` set for `authenticated` and `anon` roles
- [ ] MFA enabled for sensitive user operations
- [ ] Point-in-time recovery (PITR) enabled for production
- [ ] API keys rotated after any suspected exposure

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `42501: new row violates row-level security policy` | RLS policy missing or `WITH CHECK` condition fails | Add or fix the RLS policy for that operation; verify `auth.uid()` matches the row's user column |
| Query returns empty `data` with no error | RLS `USING` clause filters out all rows | Verify `auth.uid()` in the policy matches the authenticated user; check JWT claims |
| `PGRST301: JWSError` | Invalid or expired JWT token | Re-authenticate the user; verify `SUPABASE_ANON_KEY` matches the project |
| `PGRST302: anonymous access disabled` | Anon key not provided in client init | Pass the anon key to `createClient()`; check environment variable is set |
| `permission denied for table X` | RLS enabled but no matching policy | Create a policy for the specific operation (SELECT/INSERT/UPDATE/DELETE) |
| `Could not find the function auth.uid()` | Running SQL outside PostgREST context | `auth.uid()` only works in RLS policies evaluated by PostgREST; use explicit user IDs in migrations |

## Examples

**Minimal secure setup for a new table:**

```sql
-- 1. Create table
CREATE TABLE public.notes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL DEFAULT auth.uid(),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Enable RLS immediately
ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;

-- 3. Add policies
CREATE POLICY "Users manage own notes" ON public.notes
  FOR ALL USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**Client-side query (anon key — RLS enforced):**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// This only returns notes belonging to the authenticated user
// because the RLS policy filters by auth.uid()
const { data: notes, error } = await supabase
  .from('notes')
  .select('*')
  .order('created_at', { ascending: false })
```

## Resources

- [Row Level Security Guide](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Securing Your API](https://supabase.com/docs/guides/api/securing-your-api)
- [Security Overview](https://supabase.com/docs/guides/security)
- [Production Checklist](https://supabase.com/docs/guides/deployment/going-into-prod)
- [Custom Claims & RBAC](https://supabase.com/docs/guides/auth/custom-claims-and-role-based-access-control-rbac)
- [@supabase/supabase-js Reference](https://supabase.com/docs/reference/javascript/introduction)

## Next Steps

- Apply production hardening with `supabase-prod-checklist`
- Set up auth flows with `supabase-auth-flows`
- Configure database migrations with `supabase-migrations`
