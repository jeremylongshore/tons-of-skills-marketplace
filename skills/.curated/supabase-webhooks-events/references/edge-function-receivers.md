# Verified Durable Inbox Receiver

This is an application-owned HMAC protocol, NOT implicit native Supabase Database
Webhook signing. Deploy the exact shared module in [signature verification](signature-verification.md)
as `custom-protocol.ts`. Configure the sender to use that module's headers and
raw-byte contract. If using an Edge Function with external HMAC rather than Supabase
JWT authentication, its gateway authentication settings must deliberately permit
the intended sender; the in-function verifier below is then mandatory. Do not
turn off gateway checks for unrelated functions or treat HMAC as user authorization.

## Explicit Inbox Schema

Apply this migration only in a reviewed application. The example stores no full
webhook payload or user profile, only the accepted event and order IDs. Public
clients cannot read/write this inbox. The isolated receiver uses the server-only
service-role key solely after authenticating the configured producer. The table's
primary key makes one insert atomic with respect to duplicate event IDs; it does
not make business processing exactly once.

```sql
create table public.order_event_inbox (
  event_id uuid primary key,
  event_type text not null check (event_type = 'order.created'),
  order_id uuid not null,
  received_at timestamptz not null default now()
);
alter table public.order_event_inbox enable row level security;
revoke all on public.order_event_inbox from public, anon, authenticated;
grant insert on public.order_event_inbox to service_role;
```

## Edge Function Handler

Copy the shared verifier alongside this function and pin the SDK through the
application's reviewed dependency lock. `handleOwnedWebhook` is separate from
`Deno.serve` so isolated tests can inject a fake inbox without creating a server.
No business action or notification is executed on acceptance.

```typescript
import { createClient } from 'npm:@supabase/supabase-js@2';
import { verifyOwnedWebhook } from './custom-protocol.ts';

type Inbox = {
  insert: (row: {
    event_id: string;
    event_type: string;
    order_id: string;
  }) => Promise<{ error: { code?: string } | null }>;
};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function handleOwnedWebhook(
  req: Request,
  secret: string | undefined,
  inbox: Inbox,
  nowMs: number,
): Promise<Response> {
  if (!secret) return new Response('Receiver configuration missing', { status: 503 });
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });
  const reader = req.body?.getReader();
  if (!reader) return new Response('Body required', { status: 400 });
  const chunks: Uint8Array[] = [];
  let length = 0;
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      length += value.byteLength;
      if (length > 262_144) {
        await reader.cancel();
        return new Response('Body too large', { status: 413 });
      }
      chunks.push(value);
    }
  } catch {
    return new Response('Body read failed', { status: 400 });
  } finally {
    reader.releaseLock();
  }
  const raw = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    raw.set(chunk, offset);
    offset += chunk.length;
  }
  if (
    !(await verifyOwnedWebhook(
      raw,
      req.headers.get('x-app-signature'),
      req.headers.get('x-app-timestamp'),
      secret,
      nowMs,
    ))
  ) {
    return new Response('Unauthorized', { status: 401 });
  }
  let event: unknown;
  try {
    event = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(raw));
  } catch {
    return new Response('Invalid JSON', { status: 400 });
  }
  if (!event || typeof event !== 'object' || Array.isArray(event)) {
    return new Response('Invalid event', { status: 400 });
  }
  const e = event as Record<string, unknown>;
  if (
    Object.keys(e).sort().join(',') !== 'eventId,orderId,type' ||
    e.type !== 'order.created' ||
    typeof e.eventId !== 'string' ||
    !UUID.test(e.eventId) ||
    typeof e.orderId !== 'string' ||
    !UUID.test(e.orderId)
  ) {
    return new Response('Invalid event', { status: 400 });
  }
  try {
    const { error } = await inbox.insert({
      event_id: e.eventId,
      event_type: e.type,
      order_id: e.orderId,
    });
    if (error?.code === '23505') {
      // Do not assert that a reused ID has identical content or completed processing.
      return new Response('Event ID already present; reconcile producer receipt', { status: 409 });
    }
    if (error) return new Response('Inbox unavailable', { status: 503 });
    return Response.json(
      { accepted: true, eventId: e.eventId, processingComplete: false },
      { status: 202 },
    );
  } catch {
    return new Response('Inbox unavailable', { status: 503 });
  }
}

Deno.serve(async (req) => {
  const secret = Deno.env.get('WEBHOOK_SECRET');
  const url = Deno.env.get('SUPABASE_URL');
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!secret || !url || !key)
    return new Response('Receiver configuration missing', { status: 503 });
  const client = createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false, detectSessionInUrl: false },
  });
  return handleOwnedWebhook(
    req,
    secret,
    {
      insert: async (row) => await client.from('order_event_inbox').insert(row),
    },
    Date.now(),
  );
});
```

## Acknowledgment and Processing Boundary

202 means only that the inbox insert returned success. 409 requires the producer or
an authorized reconciler to compare its durable event receipt with the stored ID;
it is not proof that matching business effects completed. If the database committed
but the response was lost, retrying the same ID cannot create a second inbox row.
Do not generate a new event ID to evade that conflict.

A worker is deliberately not implemented here. Before enabling business effects,
design durable claim/lease transitions, bounded retries, crash recovery, dead-letter
handling, authorization at processing time, and effect-specific idempotency or an
appropriate transaction. Keep an independently checked outcome receipt. Do not use
SELECT-then-side-effect-INSERT, a row-ID-derived event key, or inbox acceptance as a
claim of exactly-once delivery. Retain deduplication records for the reviewed replay
horizon; arbitrary seven-day deletion can re-enable old effects.

Apply request/connection deadlines and ingress rate limits as well as the body cap;
this cap does not bound a slow sender's elapsed read time. Do not log payloads,
headers, keys, personal data or raw SDK errors. Monitor aggregate accepted/rejected
counts and protected operational receipts instead.

[Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
[Database insert](https://supabase.com/docs/reference/javascript/insert)
