---
name: anima-webhooks-events
description: 'Use Figma webhooks to trigger automatic Anima code generation on design
  changes.

  Use when building event-driven design-to-code pipelines, auto-generating

  components when Figma files change, or integrating design updates into CI.

  Trigger with: "anima webhook", "figma webhook", "anima auto-generate on change".

  '
allowed-tools: Read, Write, Edit, Bash(curl:*)
version: 2.0.0
argument-hint: "[figma-team-id] [endpoint]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- webhooks
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Webhooks & Events

## Overview

Use **Figma Webhooks v2** to detect approved design changes and enqueue Anima
generation. Figma supplies the event contract; this workflow does not invent an
Anima webhook API.

## Prerequisites

- Team-level Figma webhook permission, a publicly reachable HTTPS endpoint,
  and a webhook passcode stored in a secret manager rather than source or
  request logs.
- An allowlist mapping approved file keys and component node IDs to their
  generated output directories and responsible owners.
- A durable event-id/version store, queue with retry and dead-letter handling,
  and a staging workspace containing synthetic design data.
- A rate-limit budget, replay/duplicate policy, and an explicit approval gate
  before generated code can be merged or deployed.

## Authentication

Register the webhook with an authorized Figma token and keep its passcode in the
receiver's secret manager. The queued backend worker separately uses managed
Anima and Figma credentials; neither credential belongs in the event payload.

## Instructions

### Step 1: Register Figma Webhook

```bash
# Figma Webhooks API (requires team-level access)
curl -X POST "https://api.figma.com/v2/webhooks" \
  -H "X-Figma-Token: ${FIGMA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "FILE_VERSION_UPDATE",
    "context": "team",
    "context_id": "YOUR_TEAM_ID",
    "endpoint": "https://your-server.com/webhooks/figma",
    "passcode": "your-webhook-secret",
    "description": "Trigger Anima code generation on design changes"
  }'
```

### Step 2: Webhook Handler

```typescript
// src/webhooks/figma-handler.ts
import express from 'express';
import crypto from 'node:crypto';

const router = express.Router();
declare const generationQueue: {
  enqueue(job: { fileKey: string; eventTimestamp: string }): Promise<void>;
};

interface FigmaWebhookEvent {
  event_type: 'FILE_VERSION_UPDATE' | 'FILE_UPDATE' | 'FILE_DELETE';
  file_key: string;
  timestamp: string;
  passcode: string;
}

router.post('/webhooks/figma', express.json(), async (req, res) => {
  const event = req.body as FigmaWebhookEvent;

  // Verify passcode
  const supplied = Buffer.from(event.passcode || '');
  const expected = Buffer.from(process.env.FIGMA_WEBHOOK_SECRET || '');
  if (supplied.length !== expected.length || !crypto.timingSafeEqual(supplied, expected)) {
    return res.status(400).json({ error: 'Invalid passcode' });
  }

  // Only process file version updates
  if (event.event_type !== 'FILE_VERSION_UPDATE') {
    return res.status(200).json({ skipped: true });
  }

  console.log({ eventType: event.event_type, fileKey: event.file_key });

  // Trigger async generation — respond immediately
  await generationQueue.enqueue({ fileKey: event.file_key, eventTimestamp: event.timestamp });
  res.status(200).json({ accepted: true });
});

export default router;
```

## Error Handling

| Failure | Required response |
|---------|-------------------|
| Passcode is missing or invalid | Return `400`, enqueue nothing, and record only a redacted rejection reason. |
| Event is malformed, duplicated, stale, or outside the file/node allowlist | Acknowledge safely where appropriate, discard the event, and retain a deduplicated audit receipt. |
| Generation or downstream quality checks fail | Retry with bounded backoff, then move the event to a dead-letter queue; do not open a merge or deploy automatically. |
| Figma or Anima rate limit is reached | Honor the provider response, apply queue backpressure, and preserve event order for the same file. |
| File is deleted or access is revoked | Disable further generation for that source and require owner confirmation before cleanup or re-registration. |

Verify the passcode before parsing or acting on design data, use an idempotency
key based on the webhook/version identity, and never log file contents,
triggerer handles, tokens, or full payloads. A failed regeneration must leave
the last known-good generated revision intact.

### Step 3: Figma Webhook Event Types

| Event Type | Trigger | Use Case |
|-----------|---------|----------|
| `FILE_VERSION_UPDATE` | New version saved | Regenerate components |
| `FILE_UPDATE` | File modified (real-time) | Too frequent — use version instead |
| `FILE_DELETE` | File deleted | Clean up generated code |
| `PING` | Webhook health check | Validate receipt without enqueuing generation |

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Figma webhook registration for design change detection
- Event handler triggering Anima code generation on file updates
- Rate-limited async regeneration pipeline

## Examples

Register a staging webhook with a managed passcode and an endpoint dedicated to
synthetic design fixtures:

```bash
curl -X POST "https://api.figma.com/v2/webhooks" \
  -H "X-Figma-Token: ${FIGMA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "FILE_VERSION_UPDATE",
    "context": "team",
    "context_id": "synthetic-team",
    "endpoint": "https://staging.example.invalid/webhooks/figma",
    "passcode": "'"${FIGMA_WEBHOOK_SECRET}"'",
    "description": "staging design sync"
  }'
```

Send one version-update fixture and confirm the endpoint returns immediately,
queues exactly one allowlisted generation, applies rate limiting, and produces
`contacts_exported=0` (or the equivalent no-external-write assertion). The
receipt should contain only the webhook/version identity, source allowlist
result, generation status, artifact digest, and cleanup/rollback result.

## Resources

- [Figma Webhooks API](https://www.figma.com/developers/api#webhooks-v2)
- [Anima API](https://docs.animaapp.com/docs/anima-api)
