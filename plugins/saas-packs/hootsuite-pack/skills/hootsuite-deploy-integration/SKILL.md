---
name: hootsuite-deploy-integration
description: 'Deploy Hootsuite integrations to Vercel, Fly.io, and Cloud Run platforms.

  Use when deploying Hootsuite-powered applications to production,

  configuring platform-specific secrets, or setting up deployment pipelines.

  Trigger with phrases like "deploy hootsuite", "hootsuite Vercel",

  "hootsuite production deploy", "hootsuite Cloud Run", "hootsuite Fly.io".

  '
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(fly:*), Bash(gcloud:*)
version: 1.6.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- hootsuite
- social-media
compatibility: Designed for Claude Code
---
# Hootsuite Deploy Integration

## Overview

Deploy Hootsuite social media management backends. Key consideration: OAuth refresh tokens must persist across deployments — use a database or key-value store, not environment variables.

## Instructions

### Step 1: Vercel Deployment

```typescript
// api/schedule.ts — Vercel serverless
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') return res.status(405).end();

  // Get token from persistent store (not env var — tokens rotate)
  const token = await getStoredToken();

  const response = await fetch('https://platform.hootsuite.com/v1/messages', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body),
  });

  const result = await response.json();
  res.json(result);
}
```

```bash
vercel env add HOOTSUITE_CLIENT_ID production
vercel env add HOOTSUITE_CLIENT_SECRET production
vercel --prod
```

### Step 2: Token Persistence

```typescript
// Use Redis, database, or KV store for token persistence
// Tokens refresh every ~1 hour and refresh_token changes each time
import { Redis } from '@upstash/redis';

const kv = Redis.fromEnv();

async function getStoredToken(): Promise<string> {
  let token = await kv.get<string>('hootsuite:access_token');
  const expiresAt = (await kv.get<number>('hootsuite:expires_at')) ?? 0;

  if (!token || Date.now() > expiresAt - 60000) {
    const refreshToken = (await kv.get<string>('hootsuite:refresh_token')) as string;
    const newTokens = await refreshHootsuiteToken(refreshToken);
    await kv.set('hootsuite:access_token', newTokens.access_token);
    await kv.set('hootsuite:refresh_token', newTokens.refresh_token);
    await kv.set('hootsuite:expires_at', Date.now() + newTokens.expires_in * 1000);
    token = newTokens.access_token;
  }
  return token as string;
}
```

## Prerequisites

- An approved deployment change, secret references, profile/destination allowlist, and pinned client/configuration revision.
- A draft-only canary profile, baselines for health/quota/schedule behavior, and tested rollback/cancel procedures.

## Output

Produce a deployment receipt with artifact digest, environment, canary profile, health/quota/draft assertions, owner approval, rollout state, and rollback reference. Exclude post copy, media, handles, and secrets.

## Error Handling

Halt for unknown profile/destination, missing approval, public-post path in a canary, unbounded retry, or leaked copy in telemetry. Cancel/revert the schedule and restore the previous revision.

## Examples

`artifact=sha256:opaque; env=staging; canary=sandbox-brand; health=pass; draft=pass; public_posts=0; rollback=release-r31` supports controlled promotion.

## Resources

- [Upstash Redis TypeScript SDK](https://upstash.com/docs/redis/sdks/ts/overview)
- [Hootsuite OAuth](https://developer.hootsuite.com/docs/using-rest-apis)

## Next Steps

For webhooks, see `hootsuite-webhooks-events`.
