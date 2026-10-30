---
name: supabase-sdk-patterns
description: |
  Use when implementing Supabase queries, auth, realtime, storage, or RPC calls
  with @supabase/supabase-js or supabase-py and you need production-ready,
  type-safe patterns that check each service's documented error contract.
  Trigger with phrases like "supabase SDK patterns", "supabase query",
  "supabase typescript", "supabase python", "supabase client setup",
  "supabase realtime", "supabase auth", "supabase storage".
allowed-tools: Read, Write, Edit, Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - supabase
  - typescript
  - python
  - sdk
  - patterns
compatibility: Designed for Claude Code
---

# Supabase SDK Patterns

## Overview

Production patterns for `@supabase/supabase-js` v2 and `supabase-py`, with explicit error handling for each service; database queries return `{ data, error }`. Covers client initialization, CRUD with filters, auth, realtime, storage, and RPC, with Python equivalents for the query patterns.

## Prerequisites

- Supabase project with URL and publishable/anon key; privileged admin keys isolated from normal request code
- `@supabase/supabase-js` v2 installed (TypeScript) or `supabase` pip package (Python)
- TypeScript projects: generated database types via `supabase gen types typescript`

## Instructions

### Step 1: Initialize a client scoped to the identity

Reuse a client within an appropriate browser context. Cookie-authenticated SSR
requires a request-scoped `@supabase/ssr` client; never share a mutable user session
across unrelated server requests. The HTTP SDK client is not a direct SQL pool.
The following example is browser-only and uses public build-time configuration,
not server secret/service-role credentials.

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

let supabase: ReturnType<typeof createClient<Database>>;

export function getSupabase() {
  if (!supabase) {
    supabase = createClient<Database>(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
      {
        auth: { autoRefreshToken: true, persistSession: true },
        db: { schema: 'public' },
        global: { headers: { 'x-app-name': 'my-app' } },
      },
    );
  }
  return supabase;
}
```

**Python:** use `create_client(url, key)` with the intended identity. Do not cache
mutable user-authenticated clients across unrelated requests; Python raises service-
specific exceptions and does not universally return a JavaScript-style error tuple.
See [Python initialization](https://supabase.com/docs/reference/python/initializing).

### Step 2: Query, filter, and mutate data

Destructure `{ data, error }` and check `error` before touching `data`. Chain
filters onto `.from(table).select(...)`; use `.select().single()` after an
insert/upsert to return the affected row. Skeleton:

```typescript
const { data, error } = await getSupabase()
  .from('users')
  .select('id, name, email')
  .eq('active', true)
  .order('name')
  .limit(10);

if (error) throw error;
```

For the full CRUD set (insert-with-select, upsert on conflict, update, delete,
RPC), the complete 12-filter reference table, and the Python equivalents, see
[queries and filters](references/queries-and-filters.md).

### Step 3: Auth, realtime, and storage

These APIs have distinct contracts: `onAuthStateChange` returns subscription data,
Realtime reports status through callbacks, and `getPublicUrl` builds a URL without
checking object existence. Check each documented result/callback rather than
assuming every call returns a database-query error tuple. Auth exposes `signUp` / `signInWithPassword` / `getSession` /
`onAuthStateChange`; realtime subscribes to `postgres_changes` on a channel and
requires `removeChannel` cleanup; storage does `upload` / `download` /
`getPublicUrl` / `createSignedUrl` per bucket. Full walkthroughs with code for
each: see [auth, realtime, and storage](references/auth-realtime-storage.md).

## Output

Applying these patterns yields:

- Identity-scoped client with `Database` generics
- CRUD operations using the full filter chain (eq, gt, in, ilike, etc.)
- Insert-with-select and upsert patterns that return the affected row
- Auth flows for sign-up, sign-in, session management, and state listeners
- Realtime subscriptions with row-level filtering and cleanup
- Storage upload/download with signed URLs for private buckets
- Python equivalents for the query patterns

## Error Handling

Database query results return `{ data, error }`. Check the returned error;
handle thrown transport/application exceptions at the appropriate caller boundary.

```typescript
const { data, error } = await getSupabase().from('users').select('*');

if (error) {
  // error is a PostgrestError with these fields:
  //   error.message  — human-readable description
  //   error.code     — Postgres error code (e.g., '23505')
  //   error.details  — additional context
  //   error.hint     — suggested fix from Postgres
  console.error(`Query failed [${error.code}]: ${error.message}`);
  throw error;
}

// Only safe to use data after the error check
```

| Error Code | Meaning                                                | What to Do                                                                   |
| ---------- | ------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `PGRST116` | Singular result expected, but zero or multiple rows    | Use `.maybeSingle()` for zero-or-one; multiple rows still require correction |
| `23505`    | Unique-constraint violation (Postgres duplicate key)   | Use `.upsert()` or show conflict error                                       |
| `42501`    | RLS policy violation (Postgres insufficient privilege) | Check auth state and RLS policies                                            |
| `PGRST000` | Connection error                                       | Retry with exponential backoff                                               |
| `42P01`    | Table does not exist                                   | Verify table name and run migrations                                         |
| `23503`    | Foreign key violation                                  | Ensure referenced row exists first                                           |
| `42703`    | Column does not exist                                  | Check column name, regenerate types                                          |

## Examples

The recommended production shape is a typed **service layer** that wraps the
client so callers never touch raw queries, plus a **pagination helper** that
returns a page of rows and the total count in one round trip. Both full,
copy-ready implementations are in [service patterns](references/service-patterns.md).

## Resources

- [Supabase JS Client Reference](https://supabase.com/docs/reference/javascript/initializing)
- [TypeScript Support & Type Generation](https://supabase.com/docs/reference/javascript/typescript-support)
- [Supabase Auth Reference](https://supabase.com/docs/reference/javascript/auth-signup)
- [Realtime Guide](https://supabase.com/docs/guides/realtime)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [Python Client Reference](https://supabase.com/docs/reference/python/initializing)

## Next Steps

For database schema design, see `supabase-schema-from-requirements`. For auth deep-dive with RLS policies, see `supabase-install-auth`. For realtime architecture patterns, see `supabase-auth-storage-realtime-core`.
