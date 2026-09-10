---
name: posthog-webhooks-events
description: |
  Build and verify PostHog realtime webhook destinations and bounded private-API or HogQL event queries. Use when delivering selected events to another system or investigating event data. Trigger with "PostHog webhook", "PostHog destination", or "PostHog HogQL query".
argument-hint: "[project] [destination-or-query]"
allowed-tools: Read, Write, Edit, Bash(curl:*)
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- webhooks
compatibility: Designed for Claude Code
---
# PostHog Webhooks & Events

## Overview

PostHog sends webhooks via its CDP (Customer Data Platform) Destinations feature. You configure a Destination that fires when matching events are captured, sending an HTTP POST to your endpoint. This skill covers webhook destination setup, receiving and processing webhook payloads, querying events via the API, and using HogQL for custom event analysis.

## Prerequisites

- PostHog project with personal API key (`phx_...`)
- HTTPS endpoint to receive webhooks
- Events being captured in PostHog

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Create a Webhook Destination via API

```bash
set -euo pipefail
# Create a webhook destination that fires on specific events
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/pipeline_destinations/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Signup Notifications",
    "description": "Send webhook when user signs up",
    "config": {
      "url": "https://your-app.com/webhooks/posthog",
      "method": "POST",
      "headers": {
        "X-Webhook-Secret": "your-webhook-secret"
      },
      "body": {
        "event": "{event}",
        "distinct_id": "{distinct_id}",
        "person": "{person}",
        "properties": "{properties}",
        "timestamp": "{timestamp}"
      }
    },
    "filters": {
      "events": [
        {"id": "user_signed_up", "type": "events"},
        {"id": "subscription_started", "type": "events"}
      ]
    }
  }'
```

### Step 2: Receive and Process Webhooks

```typescript
// api/webhooks/posthog.ts
import { NextResponse } from 'next/server';
import crypto from 'crypto';

const WEBHOOK_SECRET = process.env.POSTHOG_WEBHOOK_SECRET!;

// Verify webhook authenticity
function verifySignature(payload: string, signature: string): boolean {
  const expected = crypto.createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
}

interface PostHogWebhookPayload {
  event: string;
  distinct_id: string;
  properties: Record<string, any>;
  person: {
    properties: Record<string, any>;
  };
  timestamp: string;
}

export async function POST(request: Request) {
  const body = await request.text();
  const signature = request.headers.get('x-webhook-secret') || '';

  // Verify webhook is from PostHog
  if (WEBHOOK_SECRET && signature !== WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
  }

  const payload: PostHogWebhookPayload = JSON.parse(body);

  // Route to handlers based on event type
  switch (payload.event) {
    case 'user_signed_up':
      await onUserSignup(payload);
      break;
    case 'subscription_started':
      await onSubscriptionStarted(payload);
      break;
    case 'subscription_canceled':
      await onSubscriptionCanceled(payload);
      break;
    default:
      console.log(`Unhandled PostHog event: ${payload.event}`);
  }

  return NextResponse.json({ received: true });
}

async function onUserSignup(payload: PostHogWebhookPayload) {
  const { distinct_id, properties, person } = payload;
  console.log(`New signup: ${distinct_id}`);

  // Sync to CRM
  await fetch('https://api.hubspot.com/contacts/v1/contact/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.HUBSPOT_KEY}` },
    body: JSON.stringify({
      properties: [
        { property: 'email', value: person.properties.email },
        { property: 'posthog_id', value: distinct_id },
      ],
    }),
  });

  // Notify Slack
  await fetch(process.env.SLACK_WEBHOOK_URL!, {
    method: 'POST',
    body: JSON.stringify({
      text: `New signup: ${person.properties.email || distinct_id} (${properties.source || 'unknown'})`,
    }),
  });
}

async function onSubscriptionStarted(payload: PostHogWebhookPayload) {
  console.log(`New subscription: ${payload.distinct_id}, plan: ${payload.properties.plan}`);
}

async function onSubscriptionCanceled(payload: PostHogWebhookPayload) {
  console.log(`Cancellation: ${payload.distinct_id}`);
}
```

### Step 3: Query Events via the API

```bash
set -euo pipefail
# List recent events by type
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/events/?event=user_signed_up&limit=10&orderBy=-timestamp" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.results[] | {
    distinct_id,
    event,
    timestamp,
    properties: (.properties | {source, plan, referrer: ."$referrer"})
  }'

# Get events for a specific person
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/events/?distinct_id=user-123&limit=20" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.results[] | {event, timestamp}'
```

### Step 4: Query Events with HogQL

```typescript
// Complex event analysis with HogQL (PostHog's SQL dialect)
async function queryPostHog(hogql: string) {
  const response = await fetch(
    `https://us.posthog.com/api/projects/${process.env.POSTHOG_PROJECT_ID}/query/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.POSTHOG_PERSONAL_API_KEY}`,
      },
      body: JSON.stringify({
        query: { kind: 'HogQLQuery', query: hogql },
      }),
    }
  );
  return response.json();
}

// Example: Signup funnel analysis
const funnelData = await queryPostHog(`
  SELECT
    properties.$referrer AS referrer,
    count() AS signups,
    uniq(distinct_id) AS unique_users
  FROM events
  WHERE event = 'user_signed_up'
    AND timestamp > now() - interval 30 day
  GROUP BY referrer
  ORDER BY signups DESC
  LIMIT 20
`);

// Example: Feature adoption by plan
const adoptionData = await queryPostHog(`
  SELECT
    person.properties.plan AS plan,
    properties.feature_name AS feature,
    count() AS usage_count,
    uniq(distinct_id) AS unique_users
  FROM events
  WHERE event = 'feature_used'
    AND timestamp > now() - interval 7 day
  GROUP BY plan, feature
  ORDER BY usage_count DESC
  LIMIT 50
`);
```

### Step 5: Set Up Slack Webhook Destination (UI)

PostHog has built-in Slack integration via Data Pipelines > Destinations:

1. Go to Data Pipelines > Destinations > New Destination
2. Select "Slack" or "Webhook"
3. Configure event filters (which events trigger the notification)
4. Set the webhook URL and message template
5. Test with a sample event

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Webhook not firing | No matching destination filter | Check event name matches filter exactly |
| Duplicate webhooks | Event matches multiple destinations | Narrow destination filters |
| Webhook timeout | Handler too slow | Acknowledge with 200 immediately, process async |
| HogQL query timeout | Unfiltered table scan | Add `timestamp >` filter and `LIMIT` |
| 429 on events API | Too many queries | Cache results, reduce polling frequency |

## Output

- Webhook destination configured for specific events
- Express/Next.js webhook handler with event routing
- Event queries via REST API and HogQL
- Slack/CRM integration on user lifecycle events

## Examples

For a webhook destination, define the filtered event set, minimal payload, receiver authentication, idempotency key, retry behavior, and response logging; then use the built-in test flow before enabling it. For queries, use the regional private API with a scoped credential and a bounded time range.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog CDP Destinations](https://posthog.com/docs/cdp/destinations)
- [PostHog Webhook Destination](https://posthog.com/docs/cdp/destinations/webhook)
- [PostHog Events API](https://posthog.com/docs/api/events)
- [HogQL Documentation](https://posthog.com/docs/sql)

## Next Steps

For deployment setup, see `posthog-deploy-integration`.
