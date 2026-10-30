# Signature Verification for an Application-Owned Protocol

Supabase Database Webhooks let you configure an HTTP request; they do not implicitly
supply the signing protocol below. Use this example only when you own the sender
and receiver and deploy BOTH to the same byte-level contract. For another provider,
implement its actual signature, header, version and replay requirements instead.

## Exact Contract

- `x-app-timestamp`: canonical nonnegative integer Unix seconds.
- `x-app-signature`: 64-character hex HMAC-SHA256 over the UTF-8 bytes of
  `<timestamp>.` followed by the ORIGINAL body bytes, without text re-encoding.
- Reject timestamps more than 300 seconds in either the past or future relative to
  a trusted receiver clock. This is a freshness bound, not durable replay prevention.
- JSON body: producer-generated unique `eventId` UUID, `type: "order.created"`,
  and `orderId` UUID. Persist that event ID at the producer and reuse it on delivery
  retries; a new change gets a new ID, not just the row ID or table/event type.
- The receiver stores a unique durable inbox row before acknowledging acceptance.
  The producer must retain/reconcile the event ID when delivery times out.

## Shared Node/Deno Web Crypto Module

Place this code in an application-owned `custom-protocol.ts`, imported by both the
sender and [receiver](edge-function-receivers.md). Modern Node exposes Web Crypto;
Deno provides it natively. Do not replace request bytes with `req.text()` or parsed
JSON before verification. No provider requests occur in these helpers.

```typescript
const encoder = new TextEncoder();

export async function signOwnedWebhook(
  raw: Uint8Array,
  timestamp: string,
  secret: string,
): Promise<string> {
  if (
    !(raw instanceof Uint8Array) ||
    !/^(0|[1-9][0-9]{0,15})$/.test(timestamp) ||
    !Number.isSafeInteger(Number(timestamp)) ||
    typeof secret !== 'string' ||
    !secret
  ) {
    throw new Error('Invalid signing input');
  }
  const prefix = encoder.encode(`${timestamp}.`);
  const bytes = new Uint8Array(prefix.length + raw.length);
  bytes.set(prefix);
  bytes.set(raw, prefix.length);
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const digest = await crypto.subtle.sign('HMAC', key, bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export async function verifyOwnedWebhook(
  raw: unknown,
  signature: unknown,
  timestamp: unknown,
  secret: unknown,
  nowMs: number,
): Promise<boolean> {
  if (
    !(raw instanceof Uint8Array) ||
    typeof signature !== 'string' ||
    !/^[0-9a-fA-F]{64}$/.test(signature) ||
    typeof timestamp !== 'string' ||
    !/^(0|[1-9][0-9]{0,15})$/.test(timestamp) ||
    typeof secret !== 'string' ||
    !secret ||
    !Number.isFinite(nowMs)
  )
    return false;
  const seconds = Number(timestamp);
  if (
    !Number.isSafeInteger(seconds) ||
    !Number.isSafeInteger(seconds * 1000) ||
    Math.abs(nowMs - seconds * 1000) > 300_000
  )
    return false;
  const received = Uint8Array.from(signature.match(/../g)!, (pair) => parseInt(pair, 16));
  const prefix = encoder.encode(`${timestamp}.`);
  const bytes = new Uint8Array(prefix.length + raw.length);
  bytes.set(prefix);
  bytes.set(raw, prefix.length);
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['verify'],
  );
  // Delegate signature comparison to the cryptographic primitive, not string equality.
  return crypto.subtle.verify('HMAC', key, received, bytes);
}
```

Web Crypto verification recomputes the digest from the exact signed bytes. Keep sender and receiver using
the same algorithm and byte contract. Secret provisioning and rotation belong to the
application's secret store; do not paste real secrets into SQL, shell history, logs,
or committed examples.

## Sender: Construct Once, Send the Same Bytes

```typescript
import { signOwnedWebhook } from './custom-protocol.ts';

export async function buildOwnedDelivery(
  url: string,
  event: { eventId: string; type: 'order.created'; orderId: string },
  secret: string,
  nowMs: number,
): Promise<Request> {
  if (!Number.isFinite(nowMs) || nowMs < 0) throw new Error('Invalid clock');
  const destination = new URL(url);
  if (destination.protocol !== 'https:') throw new Error('HTTPS receiver required');
  const timestamp = String(Math.floor(nowMs / 1000));
  const raw = new TextEncoder().encode(JSON.stringify(event));
  const signature = await signOwnedWebhook(raw, timestamp, secret);
  return new Request(destination, {
    method: 'POST',
    body: raw,
    headers: {
      'content-type': 'application/json',
      'x-app-timestamp': timestamp,
      'x-app-signature': signature,
    },
  });
}
```

This builds a request without sending it. The actual producer needs a durable outbox,
retry/dead-letter policy and stable event ID. A Database Webhook trigger that signs
`jsonb::text` and then lets another transport serialize JSON again does not prove
byte identity; do not claim that such a trigger interoperates without a verified
raw-byte transport. Native webhook retry/delivery semantics must be assessed
separately, not inferred from these helpers.

[Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
[Web Crypto HMAC](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/verify)
