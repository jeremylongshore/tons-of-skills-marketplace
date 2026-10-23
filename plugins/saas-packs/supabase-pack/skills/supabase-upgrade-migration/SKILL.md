---
name: supabase-upgrade-migration
description: "Upgrade Supabase SDK and CLI versions with breaking-change detection\
  \ and automated code migration.\nUse when upgrading @supabase/supabase-js (v1\u2192\
  v2 or minor bumps), migrating auth/realtime/storage\nAPIs, or updating the Supabase\
  \ CLI. Trigger with phrases like \"upgrade supabase\",\n\"supabase breaking changes\"\
  , \"migrate supabase v2\", \"update supabase SDK\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(pip:*), Bash(supabase:*),
  Bash(git:*), Grep, Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- migration
- upgrade
- sdk
compatibility: Designed for Claude Code
---
# Supabase Upgrade Migration

## Overview

Upgrade `@supabase/supabase-js` and the Supabase CLI with breaking-change detection, automated code migration, and rollback planning. Covers the v1-to-v2 migration path (auth method renames, `data`/`error` destructuring, realtime API overhaul), minor version bumps, `@supabase/ssr` adoption, and Python SDK upgrades via `pip install --upgrade supabase`.

## Manual Version Diagnostics

Inspect the installed versions only when requested; this skill does not run these commands on load.

```text
npm list @supabase/supabase-js
npx supabase --version
pip show supabase
```

## Prerequisites

- `@supabase/supabase-js` or the Python `supabase` package installed in the project
- Git with a clean working tree (no uncommitted changes)
- Test suite available for post-upgrade verification
- Node.js 22+ for current JS SDK releases, or Python 3.9+ for the Python SDK

## Instructions

### Step 1: Audit Versions, Scan Usage, and Review Breaking Changes

Check every installed Supabase package and find all import sites in the codebase.

```bash
# Check current SDK version
npm list @supabase/supabase-js

# Check CLI version
supabase --version

# Check Python SDK version
pip show supabase | grep Version

# Find all JS/TS Supabase imports
grep -rn "from '@supabase/supabase-js'" --include="*.ts" --include="*.tsx" --include="*.js" src/ lib/ app/ 2>/dev/null
grep -rn "createClient" --include="*.ts" --include="*.tsx" --include="*.js" src/ lib/ app/ 2>/dev/null

# Find all Python Supabase imports
grep -rn "from supabase" --include="*.py" src/ app/ 2>/dev/null
```

**supabase-js v1 → v2 breaking changes:**

| v1 Pattern | v2 Replacement | Notes |
|-----------|---------------|-------|
| `createClient(url, key)` | `createClient(url, key)` | Signature unchanged, but return type differs |
| `supabase.auth.session()` | `supabase.auth.getSession()` | Sync → async, returns `{ data: { session } }` |
| `supabase.auth.user()` | `supabase.auth.getUser()` | Sync → async, returns `{ data: { user } }` |
| `supabase.auth.signIn({ email, password })` | `supabase.auth.signInWithPassword({ email, password })` | Method split by auth type |
| `supabase.auth.signIn({ provider: 'google' })` | `supabase.auth.signInWithOAuth({ provider: 'google' })` | OAuth separated |
| `supabase.auth.signIn({ email })` | `supabase.auth.signInWithOtp({ email })` | Magic link separated |
| `supabase.auth.api.resetPasswordForEmail(e)` | `supabase.auth.resetPasswordForEmail(e)` | `.api` namespace removed |
| `{ data: subscription }` from `onAuthStateChange` | `{ data: { subscription } }` | Extra destructuring level |
| `error.message` string parsing | `error.code` enum (`PGRST116`, etc.) | Reliable error matching |
| `.single()` returns error on 0 rows | `.maybeSingle()` for optional rows | New method for nullable results |
| `supabase.from('t').on('INSERT', cb).subscribe()` | `supabase.channel('c').on('postgres_changes', ...).subscribe()` | Realtime v2 channel API |
| `supabase.storage.from('b').download('path')` | Same, but returns `{ data: Blob, error }` | Consistent error/data tuple |

**Realtime v2 migration detail:**

```typescript
// v1 realtime
supabase
  .from('messages')
  .on('INSERT', (payload) => console.log(payload.new))
  .subscribe()

// v2 realtime — channel-based API
supabase
  .channel('messages-insert')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' },
    (payload) => console.log(payload.new))
  .subscribe()
```

### Step 2: Run the Upgrade and Apply Code Migrations

Create a branch, install new packages, and transform code to match v2 APIs.

```bash
# Create upgrade branch
git checkout -b upgrade-supabase-sdk

# Upgrade JS/TS SDK
npm install @supabase/supabase-js@latest

# Upgrade SSR helper (if used with Next.js/SvelteKit/Nuxt)
npm install @supabase/ssr@latest

# Upgrade CLI
npm install --save-dev supabase@latest

# Upgrade Python SDK
pip install --upgrade supabase

# Regenerate TypeScript types from linked project
npx supabase gen types typescript --linked > lib/database.types.ts

# Generate a database migration if schema drifted
npx supabase db diff --use-migra -f upgrade_check
```

Apply auth code migrations:

```typescript
// BEFORE (v1 auth patterns)
const session = supabase.auth.session()
const user = supabase.auth.user()
const { error } = await supabase.auth.signIn({ email, password })
const { data: subscription } = supabase.auth.onAuthStateChange(callback)

// AFTER (v2 auth patterns)
const { data: { session } } = await supabase.auth.getSession()
const { data: { user } } = await supabase.auth.getUser()
const { error } = await supabase.auth.signInWithPassword({ email, password })
const { data: { subscription } } = supabase.auth.onAuthStateChange(callback)
```

Apply error handling migration:

```typescript
// Classify the actual returned error; do not translate "not found" text blindly.
if (error?.code === 'PGRST116') {
  throw new Error('Expected exactly one visible row; review query cardinality')
}
```

### Step 3: Verify, Test, and Prepare Rollback

```bash
# Run in Bash; any failed check stops this verification sequence.
set -euo pipefail

# Type check the configured project; not proof of complete migration correctness.
npx tsc --noEmit

# Run test suite
npm test

# Python tests
python -m pytest tests/ -v

# Manual smoke test critical auth flows:
# 1. Sign up → confirm email → sign in with password
# 2. OAuth sign in → callback handling
# 3. Password reset → email → reset form
# 4. Session refresh across page navigations
# 5. Realtime subscription connect/disconnect
# 6. Storage upload/download round-trip
```

**Rollback procedure** (if upgrade causes issues):

```text
# Option A: Pin to previous version
npm install @supabase/supabase-js@<previous-version>
pip install supabase==<previous-version>

# Option B: Revert the branch
git stash && git checkout main
```

## Output

- `@supabase/supabase-js` upgraded to latest version with `npm list` confirmation
- All `supabase.auth.signIn()` calls migrated to `signInWithPassword` / `signInWithOAuth` / `signInWithOtp`
- Sync auth methods (`session()`, `user()`) replaced with async `getSession()` / `getUser()`
- Realtime subscriptions migrated from `.on()` to channel-based API
- `data`/`error` destructuring updated where return shapes changed
- TypeScript types regenerated from current schema
- Test suite passing, type checking clean
- Rollback branch or version pin documented

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Property 'session' does not exist` | v1 sync `.session()` removed in v2 | Replace with `await supabase.auth.getSession()` |
| `Property 'signIn' does not exist` | `signIn` split into multiple methods in v2 | Use `signInWithPassword`, `signInWithOAuth`, or `signInWithOtp` |
| `supabase.auth.api` is undefined | `.api` namespace removed in v2 | Call methods directly on `supabase.auth.*` |
| `TypeError: supabase.from(...).on is not a function` | Realtime API replaced in v2 | Use `supabase.channel().on('postgres_changes', ...)` |
| Type errors after `gen types` | Database schema changed between versions | Update application code to match new generated types |
| `PGRST116` from `.single()` | Singular response requested but zero or multiple rows returned; inspect the returned `error` | Use `.maybeSingle()` only for intended zero-or-one results; duplicates still return an error |
| `ERR_REQUIRE_ESM` after upgrade | Installed dependency/runtime/bundler ESM–CommonJS resolution mismatch | Inspect the exact installed dependency exports and runtime/bundler configuration; the published Supabase SDK supports both import and require, so do not apply a blanket module-setting fix |
| `AuthSessionMissingError` | `getSession()` called before auth initialized | Wrap in `onAuthStateChange` listener or check `session !== null` |

## Examples

**Full v1 → v2 auth migration (Next.js):**

```typescript
// lib/supabase.ts — client initialization (unchanged API)
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

```typescript
// app/login/page.tsx — v2 auth flow
export async function login(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  if (error) {
    // v2: use error.code instead of parsing error.message
    if (error.code === 'invalid_credentials') {
      return { success: false, message: 'Invalid email or password' }
    }
    throw error
  }
  return { success: true, session: data.session }
}
```

```typescript
// hooks/useAuth.ts — v2 session listener
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import type { Session } from '@supabase/supabase-js'

export function useAuth() {
  const [session, setSession] = useState<Session | null>(null)

  useEffect(() => {
    // v2: getSession is async, returns nested { data: { session } }
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })

    // v2: subscription nested one level deeper
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => setSession(session)
    )

    return () => subscription.unsubscribe()
  }, [])

  return session
}
```

**Python SDK upgrade:**

```python
# Before (supabase-py < 2.0)
from supabase import create_client
supabase = create_client(url, key)
data = supabase.table("users").select("*").execute()
users = data["data"]

# After (supabase-py >= 2.0)
from supabase import create_client, Client
supabase: Client = create_client(url, key)
response = supabase.table("users").select("*").execute()
users = response.data  # attribute access, not dict
```

## Resources

- supabase-js v2 Migration Guide — official step-by-step
- [supabase-js Releases](https://github.com/supabase/supabase-js/releases) — changelog for every version
- [Supabase CLI Releases](https://github.com/supabase/cli/releases) — CLI changelog
- Auth Helpers Migration — `@supabase/auth-helpers` → `@supabase/ssr`
- [Realtime v2 Guide](https://supabase.com/docs/guides/realtime) — channel-based API reference
- [supabase-py Releases](https://github.com/supabase-community/supabase-py/releases) — Python SDK changelog

## Next Steps

For CI integration with the upgraded SDK, see `supabase-ci-integration`. For database migration workflows after schema changes, see `supabase-migration-deep-dive`.
