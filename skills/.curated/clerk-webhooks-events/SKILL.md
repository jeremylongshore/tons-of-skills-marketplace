---
name: clerk-webhooks-events
description: 'Configure Clerk webhooks and handle authentication events.

  Use when setting up user sync, handling auth events,

  or integrating Clerk with external systems via Svix webhooks.

  Trigger with phrases like "clerk webhooks", "clerk events",

  "clerk user sync", "clerk svix", "clerk event handling".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- authentication
- webhooks
compatibility: Designed for Claude Code
---
# Clerk Webhooks & Events

## Overview

Configure and handle Clerk webhooks for user lifecycle events and data synchronization. Clerk uses Svix for webhook delivery with HMAC-SHA256 signature verification. As of 2025, Clerk provides a built-in `verifyWebhook()` helper in `@clerk/backend` alongside the manual Svix approach.

## Prerequisites

- Clerk account with webhook endpoint configured in Dashboard
- HTTPS endpoint (use `ngrok` for local dev)
- `CLERK_WEBHOOK_SECRET` environment variable (starts with `whsec_`)

## Instructions

### Step 1: Install Dependencies

```bash
# Option A: Use @clerk/backend's built-in verifyWebhook() (recommended)
# Already included with @clerk/nextjs — no extra install needed

# Option B: Manual Svix verification
npm install svix
```

### Step 2: Create Webhook Endpoint (verifyWebhook — Recommended)

```typescript
// app/api/webhooks/clerk/route.ts
import { verifyWebhook } from '@clerk/backend/webhooks'
import type { WebhookEvent } from '@clerk/nextjs/server'

export async function POST(req: Request) {
  let evt: WebhookEvent

  try {
    evt = await verifyWebhook(req)
  } catch (err) {
    console.error('Webhook verification failed:', err)
    return new Response('Invalid signature', { status: 400 })
  }

  return handleWebhookEvent(evt)
}
```

### Step 2 (Alternative): Manual Svix Verification

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix'
import { headers } from 'next/headers'
import type { WebhookEvent } from '@clerk/nextjs/server'

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET
  if (!WEBHOOK_SECRET) {
    throw new Error('Missing CLERK_WEBHOOK_SECRET env variable')
  }

  const headerPayload = await headers()
  const svixHeaders = {
    'svix-id': headerPayload.get('svix-id') || '',
    'svix-timestamp': headerPayload.get('svix-timestamp') || '',
    'svix-signature': headerPayload.get('svix-signature') || '',
  }

  if (!svixHeaders['svix-id'] || !svixHeaders['svix-signature']) {
    return new Response('Missing svix headers', { status: 400 })
  }

  // CRITICAL: Use req.text(), NOT req.json() — JSON parsing alters the payload
  // and breaks signature verification
  const body = await req.text()
  const wh = new Webhook(WEBHOOK_SECRET)
  let evt: WebhookEvent

  try {
    evt = wh.verify(body, svixHeaders) as WebhookEvent
  } catch (err) {
    console.error('Webhook verification failed:', err)
    return new Response('Invalid signature', { status: 400 })
  }

  return handleWebhookEvent(evt)
}
```

### Step 3: Implement Event Handlers

```typescript
async function handleWebhookEvent(evt: WebhookEvent) {
  const eventType = evt.type

  switch (eventType) {
    case 'user.created': {
      const { id, email_addresses, first_name, last_name, image_url } = evt.data
      const primaryEmail = email_addresses.find(e => e.id === evt.data.primary_email_address_id)

      await db.user.create({
        data: {
          clerkId: id,
          email: primaryEmail?.email_address || email_addresses[0]?.email_address,
          firstName: first_name,
          lastName: last_name,
          avatarUrl: image_url,
        },
      })
      console.log(`[Webhook] User created: ${id}`)
      break
    }

    case 'user.updated': {
      const { id, email_addresses, first_name, last_name, image_url } = evt.data
      const primaryEmail = email_addresses.find(e => e.id === evt.data.primary_email_address_id)

      await db.user.upsert({
        where: { clerkId: id },
        update: {
          email: primaryEmail?.email_address,
          firstName: first_name,
          lastName: last_name,
          avatarUrl: image_url,
        },
        create: {
          clerkId: id,
          email: primaryEmail?.email_address || '',
          firstName: first_name,
          lastName: last_name,
          avatarUrl: image_url,
        },
      })
      break
    }

    case 'user.deleted': {
      if (evt.data.id) {
        // Soft-delete or hard-delete based on your data retention policy
        await db.user.update({
          where: { clerkId: evt.data.id },
          data: { deletedAt: new Date() },
        })
      }
      break
    }

    case 'organization.created': {
      const { id, name, slug, created_by } = evt.data
      await db.organization.create({
        data: { clerkOrgId: id, name, slug: slug || '', createdBy: created_by },
      })
      break
    }

    case 'organizationMembership.created': {
      const { organization, public_user_data, role } = evt.data
      await db.orgMembership.create({
        data: {
          orgId: organization.id,
          userId: public_user_data.user_id,
          role,
        },
      })
      break
    }

    case 'session.created':
      console.log(`[Webhook] Session created for user: ${evt.data.user_id}`)
      break

    default:
      console.log(`[Webhook] Unhandled event: ${eventType}`)
  }

  return new Response('OK', { status: 200 })
}
```

### Step 4: Idempotency Protection

```typescript
// lib/webhook-idempotency.ts
// Clerk/Svix may retry failed deliveries — prevent duplicate processing

export async function processIdempotently(
  svixId: string,
  eventType: string,
  handler: () => Promise<void>
): Promise<{ processed: boolean; duplicate: boolean }> {
  // Check if already processed (use your DB or Redis)
  const existing = await db.webhookEvent.findUnique({
    where: { svixId },
  })

  if (existing) {
    console.log(`[Webhook] Duplicate event skipped: ${svixId} (${eventType})`)
    return { processed: false, duplicate: true }
  }

  // Mark as processing (before handler, to catch concurrent deliveries)
  await db.webhookEvent.create({
    data: { svixId, eventType, status: 'processing', receivedAt: new Date() },
  })

  try {
    await handler()
    await db.webhookEvent.update({
      where: { svixId },
      data: { status: 'completed', processedAt: new Date() },
    })
    return { processed: true, duplicate: false }
  } catch (error) {
    await db.webhookEvent.update({
      where: { svixId },
      data: { status: 'failed', error: String(error) },
    })
    throw error
  }
}
```

### Step 5: Configure Webhook in Clerk Dashboard

1. Navigate to **Clerk Dashboard > Webhooks > Add Endpoint**
2. Set endpoint URL: `https://yourdomain.com/api/webhooks/clerk`
3. Select events to subscribe to:
   - **User events:** `user.created`, `user.updated`, `user.deleted`
   - **Org events:** `organization.created`, `organizationMembership.created`
   - **Session events:** `session.created`, `session.ended` (optional, high volume)
4. Copy the **Signing Secret** (`whsec_...`) to your `.env.local`:

```bash
CLERK_WEBHOOK_SECRET=whsec_...
```

### Step 6: Express.js Webhook Endpoint

```typescript
import express from 'express'
import { Webhook } from 'svix'

const app = express()

// CRITICAL: Use express.raw(), NOT express.json() for webhook routes
app.post('/api/webhooks/clerk',
  express.raw({ type: 'application/json' }),
  (req, res) => {
    const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!)
    try {
      const evt = wh.verify(req.body, {
        'svix-id': req.headers['svix-id'] as string,
        'svix-timestamp': req.headers['svix-timestamp'] as string,
        'svix-signature': req.headers['svix-signature'] as string,
      })
      // Handle event...
      res.status(200).json({ received: true })
    } catch (err) {
      console.error('Webhook verification failed:', err)
      res.status(400).json({ error: 'Invalid signature' })
    }
  }
)
```

### Local Development with ngrok

```bash
# Start ngrok tunnel for local webhook testing
ngrok http 3000

# Copy the https://xxx.ngrok-free.app URL
# Add it as webhook endpoint in Clerk Dashboard > Webhooks
# URL: https://xxx.ngrok-free.app/api/webhooks/clerk
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid signature | Wrong `CLERK_WEBHOOK_SECRET` | Re-copy signing secret from Dashboard > Webhooks |
| Invalid signature | Body parsed with `json()` before verify | Use `req.text()` (Next.js) or `express.raw()` (Express) |
| Missing svix headers | Request not from Clerk/Svix | Verify endpoint URL; check sender |
| Duplicate processing | Clerk retried delivery | Implement idempotency with `svix-id` as unique key |
| Handler timeout | Slow DB operations | Offload heavy work to a background job queue |
| 404 on webhook URL | Route not matching | Ensure `/api/webhooks` is in middleware's `isPublicRoute` |

## Enterprise Considerations

- Treat `CLERK_WEBHOOK_SECRET` like a password -- rotate it if compromised (Dashboard > Webhooks > Signing Secret > Rotate)
- Svix headers include `svix-timestamp` for replay attack protection (rejects events older than 5 minutes by default)
- For high-volume apps, offload webhook processing to a queue (BullMQ, Inngest, Trigger.dev) and return 200 immediately
- Monitor webhook delivery in Dashboard > Webhooks > Message Logs -- failed messages auto-retry with exponential backoff
- Use `verifyWebhook()` from `@clerk/backend/webhooks` when possible -- it handles header extraction and secret key resolution automatically

## Output

Record the verified Svix event ID, event type, tenant/user scope when needed,
timestamp/replay decision, idempotency result, queued work status, and redacted
failure reason. A 2xx response is issued only after durable idempotency state
is recorded; do not log signing secrets, raw event bodies, or unnecessary user
attributes.

## Examples

For a `user.created` event, verify the raw request, persist the `svix-id` with
the allowed event metadata, enqueue one provisioning job, and return 200. If
the same delivery retries, return a safe acknowledgement without provisioning
again; reject invalid or expired signatures without echoing their contents.

## Resources

- [Webhooks Overview](https://clerk.com/docs/guides/development/webhooks/overview)
- [verifyWebhook() Reference](https://clerk.com/docs/reference/backend/verify-webhook)
- [Sync Data with Webhooks](https://clerk.com/docs/webhooks/sync-data)
- [Debug Webhooks](https://clerk.com/docs/guides/development/webhooks/debugging)

## Next Steps

Proceed to `clerk-performance-tuning` for optimization strategies.
