---
name: supabase-auth-storage-realtime-core
description: 'Implement Supabase Auth (signUp, signIn, OAuth, session management),
  Storage
  (upload, download, signed URLs, bucket policies), and Realtime (Postgres changes,
  broadcast, presence). Use when building user auth flows, file upload features,
  or live-updating UIs with Supabase. Trigger with phrases like "supabase auth",
  "supabase storage upload", "supabase realtime subscribe", "supabase oauth",
  "supabase file upload", "supabase presence", "supabase rls storage".
  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(supabase:*), Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- auth
- storage
- realtime
- rls
compatibility: Designed for Claude Code
---
# Supabase Auth + Storage + Realtime Core

## Overview

Implement the three pillars that turn a Supabase database into a full application backend: user authentication (email/password, OAuth, magic links, session lifecycle), file storage (uploads, downloads, signed URLs, bucket-level RLS policies), and real-time subscriptions (Postgres change events, client-to-client broadcast, presence tracking). Every operation integrates with Row-Level Security through `auth.uid()`.

Each pillar below carries a lean skeleton in this file; the full, copy-paste walkthroughs live in `references/` so this file stays scannable.

## Prerequisites

- Supabase project created at [supabase.com/dashboard](https://supabase.com/dashboard)
- `@supabase/supabase-js` v2 installed (`npm install @supabase/supabase-js`)
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` available from project Settings > API
- For Python: `pip install supabase` (wraps `postgrest-py`, `gotrue-py`, `storage3`, `realtime-py`)

## Instructions

Read the file (Read), edit or create the client and route/component code (Write, Edit), and grep the project (Grep) to reuse an existing Supabase client before creating a new one. Use `Bash(npm:*)` to install the SDK and `Bash(supabase:*)` to run migrations/policies.

### Step 1: Auth — registration, login, OAuth

Initialize the client once, then wire the flows your app needs. The skeleton:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!)

// Email/password
await supabase.auth.signUp({ email, password })
await supabase.auth.signInWithPassword({ email, password })

// OAuth — redirect the user to data.url
const { data } = await supabase.auth.signInWithOAuth({ provider: 'google' })

// React to session changes (SIGNED_IN / SIGNED_OUT / TOKEN_REFRESHED)
supabase.auth.onAuthStateChange((event, session) => { /* update UI */ })
```

Full auth walkthrough — OAuth callback, magic link, session lifecycle, password reset: [references/auth.md](references/auth.md). Python: [references/python-examples.md](references/python-examples.md).

### Step 2: Storage — upload, download, secure with bucket policies

Public buckets serve via CDN URLs; private buckets require signed URLs. The skeleton:

```typescript
// Upload to the signed-in user's own folder (RLS enforces ownership)
await supabase.storage.from('avatars').upload(`${userId}/avatar.png`, file, { upsert: true })

// Public URL (public bucket) vs. time-limited signed URL (private bucket)
supabase.storage.from('avatars').getPublicUrl(`${userId}/avatar.png`)
await supabase.storage.from('documents').createSignedUrl('reports/q4.pdf', 3600)
```

Full storage walkthrough — download, list, delete, and the bucket RLS policies that enforce per-user access: [references/storage.md](references/storage.md). Python: [references/python-examples.md](references/python-examples.md).

### Step 3: Realtime — Postgres changes, broadcast, presence

Three channel types: database change listeners, client-to-client broadcast, and presence. The skeleton:

```typescript
const channel = supabase
  .channel('chat-room')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'messages' },
    (payload) => console.log('New:', payload.new))
  .subscribe()
// One-time table setup: ALTER PUBLICATION supabase_realtime ADD TABLE messages;
supabase.removeChannel(channel)  // clean up
```

Full realtime walkthrough — UPDATE/DELETE filters, RLS-scoped subscriptions, broadcast, and presence tracking: [references/realtime.md](references/realtime.md). Python: [references/python-examples.md](references/python-examples.md).

## Output

- Auth: user registration, password login, OAuth flow (Google/GitHub), magic link, session lifecycle with `onAuthStateChange`, password reset
- Storage: file upload/download, public URLs for CDN-served assets, time-limited signed URLs for private files, bucket-level RLS policies using `auth.uid()` and `storage.foldername()`
- Realtime: Postgres change subscriptions with server-side filters, broadcast channels for client-to-client messaging, presence tracking for online status

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `AuthApiError: User already registered` | Duplicate email signup | Use `signInWithPassword` or check existence first |
| `AuthApiError: Invalid login credentials` | Wrong email or password | Verify credentials; check email confirmation status |
| `AuthApiError: Email not confirmed` | User has not clicked confirmation link | Resend with `resend({ type: 'signup', email })` |
| `StorageApiError: Bucket not found` | Bucket does not exist | Create via dashboard or `INSERT INTO storage.buckets` |
| `StorageApiError: new row violates row-level security` | RLS policy blocking the operation | Verify `storage.objects` policies match the user and bucket |
| `StorageApiError: The resource already exists` | File exists and `upsert: false` | Set `upsert: true` to overwrite or use a unique path |
| `Realtime: channel error` or `TIMED_OUT` | Network issues or Realtime not enabled | Check `ALTER PUBLICATION supabase_realtime ADD TABLE` for the target table |
| `Realtime: too many channels` | Exceeded concurrent channel limit | Unsubscribe unused channels with `removeChannel()` |

## Examples

The end-to-end flow — sign in, upload an avatar to the user's RLS-guarded folder, resolve its public URL, and subscribe to live profile updates — is in [references/examples.md](references/examples.md). Each step composes the three skeletons above with no new API surface.

## Resources

- [Auth Guide](https://supabase.com/docs/guides/auth)
- [Auth API Reference](https://supabase.com/docs/reference/javascript/auth-signup)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [Storage Access Control](https://supabase.com/docs/guides/storage/security/access-control)
- [Realtime Guide](https://supabase.com/docs/guides/realtime)
- [Realtime Postgres Changes](https://supabase.com/docs/guides/realtime/postgres-changes)
- [Realtime Broadcast](https://supabase.com/docs/guides/realtime/broadcast)
- [Realtime Presence](https://supabase.com/docs/guides/realtime/presence)

## Next Steps

For common Supabase errors and debugging, see `supabase-common-errors`.
For database queries and CRUD operations, see `supabase-crud-core`.
