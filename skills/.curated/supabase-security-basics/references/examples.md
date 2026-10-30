# Security Examples

## Public Clients and Explicit Admin Authority

Initialize normal application clients with the project's publishable key (or
supported legacy anon key). Key names such as `SUPABASE_READ_KEY` and
`SUPABASE_WRITE_KEY` do not create read/write scopes; grants, RLS, and the user's
identity determine access. Keep secret/service-role credentials out of browser
bundles. Use privileged clients only in isolated server-only code AFTER explicit
caller authentication and operation authorization, not to bypass a failing policy.

## HMAC for an Application-Owned Protocol Only

Supabase Database Webhooks do not implicitly implement this protocol. Use it only
when you own BOTH the sender and receiver and have configured them to sign the
same raw bytes with a shared secret. For a third-party provider, use that provider's
actual signature/header/version/replay contract instead. This hex HMAC comparison
alone supplies no timestamp validation or replay prevention.

```typescript
import { createHmac, timingSafeEqual } from 'node:crypto';

export function verifyOwnedHmac(payload: unknown, signature: unknown, secret: unknown): boolean {
  if (
    !(payload instanceof Uint8Array) ||
    typeof signature !== 'string' ||
    typeof secret !== 'string' ||
    secret.length === 0
  )
    return false;
  if (!/^[a-fA-F0-9]{64}$/.test(signature)) return false;
  const received = Buffer.from(signature, 'hex');
  const expected = createHmac('sha256', secret).update(payload).digest();
  if (received.length !== expected.length) return false;
  return timingSafeEqual(received, expected);
}
```

Pass the original Buffer or Uint8Array request bytes without decoding/re-encoding
them as text. Obtain these bytes before JSON parsing, reject missing configuration, and
apply the explicitly designed freshness/event-ID policy before side effects. Do
not treat TLS, possession of an anon key, or a client-supplied user ID as admin
authorization.

## Application Audit Table

Supabase JS has no `track('audit', ...)` analytics method. An application can define
its own table and an authenticated insert policy. This SQL lets an authenticated
user append only their own event; it does not make the event a trusted compliance
record or permit callers to impersonate other users. Table ownership, retention,
admin access and tamper resistance need a separate audit design.

```sql
create table public.app_audit_events (
  id bigint generated always as identity primary key,
  actor_id uuid not null references auth.users(id),
  action text not null check (length(action) between 1 and 100),
  created_at timestamptz not null default now()
);
alter table public.app_audit_events enable row level security;
revoke all on public.app_audit_events from public, anon, authenticated;
grant insert (actor_id, action) on public.app_audit_events to authenticated;
revoke all on sequence public.app_audit_events_id_seq from public, anon, authenticated;
grant usage on sequence public.app_audit_events_id_seq to authenticated;
create policy own_event_insert on public.app_audit_events
  for insert to authenticated with check ((select auth.uid()) = actor_id);
```

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';

export async function recordOwnEvent(client: SupabaseClient, action: string) {
  const {
    data: { user },
    error: userError,
  } = await client.auth.getUser();
  if (userError || !user) throw new Error('Authenticated user required');
  const { error } = await client.from('app_audit_events').insert({ actor_id: user.id, action });
  if (error) throw error;
}
```

Do not log keys, tokens, arbitrary request bodies, or private user data to stdout.

[Supabase API keys](https://supabase.com/docs/guides/api/api-keys)
[Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
