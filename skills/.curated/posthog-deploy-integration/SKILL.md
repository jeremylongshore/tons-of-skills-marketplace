---
name: posthog-deploy-integration
description: |
  Deploy a PostHog application integration with correct regional hosts, reverse-proxy coverage, server lifecycle, and rollback checks. Use when shipping PostHog instrumentation to a hosted application. Trigger with "deploy PostHog", "PostHog Vercel", or "PostHog reverse proxy".
argument-hint: "[project-path] [deployment-platform]"
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(fly:*), Bash(gcloud:*)
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- deployment
compatibility: Designed for Claude Code
---
# PostHog Deploy Integration

## Overview

Ship an application's PostHog integration with regional routing, a supported reverse proxy, server-side flushing, validation evidence, and an instrumentation rollback. This workflow deploys the application integration; it does not present open-source self-hosting as a supported production PostHog service.

## Prerequisites

- PostHog project API key (`phc_...`)
- A feature flags secure API key only when server-side local evaluation is required
- A scoped private-API credential only when deployment annotations are required
- Platform CLI installed (`vercel`, `fly`, or `gcloud`)

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass. Use the `vercel`, `fly`, or `gcloud` Bash allowance only for the deployment platform actually selected by the user.

### Step 1: Next.js + Vercel Deployment

```bash
set -euo pipefail
# Set environment variables in Vercel
vercel env add NEXT_PUBLIC_POSTHOG_KEY production     # phc_... (public)
vercel env add NEXT_PUBLIC_POSTHOG_HOST production    # /ingest (if using proxy)
vercel env add POSTHOG_FEATURE_FLAGS_SECURE_API_KEY production # only for local evaluation
vercel env add POSTHOG_PERSONAL_API_KEY production    # only for scoped private API automation
vercel env add POSTHOG_PROJECT_ID production          # Project ID number
```

```typescript
// next.config.js — Reverse proxy to bypass ad blockers
module.exports = {
  async rewrites() {
    return [
      {
        source: '/ingest/static/:path*',
        destination: 'https://us-assets.i.posthog.com/static/:path*',
      },
      {
        source: '/ingest/:path*',
        destination: 'https://us.i.posthog.com/:path*',
      },
    ];
  },
};
```

```typescript
// app/providers.tsx — Client-side PostHog with proxy
'use client';
import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';
import { useEffect } from 'react';

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: '/ingest', // Routes through your domain's reverse proxy
      capture_pageview: false, // Handle manually in App Router
      capture_pageleave: true,
    });
  }, []);

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}
```

### Step 2: Server-Side Capture in Vercel Edge Functions

```typescript
// app/api/track/route.ts — Server-side event capture
import { PostHog } from 'posthog-node';
import { NextResponse } from 'next/server';

export const runtime = 'edge';

export async function POST(request: Request) {
  const body = await request.json();
  const { userId, event, properties } = body;

  const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    host: 'https://us.i.posthog.com',
    flushAt: 1,       // Immediate flush in serverless
    flushInterval: 0,
  });

  try {
    posthog.capture({ distinctId: userId, event, properties });
    await posthog.shutdown(); // CRITICAL: flush before function exits
    return NextResponse.json({ status: 'ok' });
  } catch (error) {
    return NextResponse.json({ error: 'capture failed' }, { status: 500 });
  }
}
```

### Step 3: Validate the Proxy and Rollback Boundary

```bash
set -euo pipefail
# Use the deployed application URL; do not test against a guessed region.
: "${APPLICATION_URL:?Set the deployed application URL}"
: "${NEXT_PUBLIC_POSTHOG_KEY:?Set the public project token}"

# Static asset and flag routes should traverse the same proxy configuration.
curl -fsSI "$APPLICATION_URL/ingest/static/array.js" | head -n 1
curl -fsS -X POST "$APPLICATION_URL/ingest/flags/?v=2" \
  -H 'Content-Type: application/json' \
  -d "{\"api_key\":\"$NEXT_PUBLIC_POSTHOG_KEY\",\"distinct_id\":\"deployment-proxy-check\"}" \
  | jq '{errorsParsingFlags, flags}'
```

The rollback must disable the new SDK initialization or restore the previous proxy mapping without blocking the application. PostHog's open-source self-hosted distribution is explicitly a hobbyist, single-machine option with limited support and no recovery guarantee; evaluate it as a separate infrastructure project, not as a step in this application-deployment workflow.

### Step 4: Google Cloud Run Deployment

```bash
set -euo pipefail
# Reference secrets that were created through the organization's approved secret workflow.
gcloud secrets describe posthog-project-token >/dev/null
gcloud secrets describe posthog-feature-flags-secure-key >/dev/null

# Deploy with PostHog secrets
gcloud run deploy my-app \
  --image gcr.io/my-project/my-app:latest \
  --set-secrets "NEXT_PUBLIC_POSTHOG_KEY=posthog-project-token:latest" \
  --set-secrets "POSTHOG_FEATURE_FLAGS_SECURE_API_KEY=posthog-feature-flags-secure-key:latest" \
  --set-env-vars "POSTHOG_HOST=https://us.i.posthog.com" \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 5: Deploy Annotation (Mark Deployments in PostHog)

```bash
set -euo pipefail
# Create annotation on each deploy so you can correlate metric changes with releases
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/annotations/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Deploy: $(git rev-parse --short HEAD) — $(git log -1 --pretty=%s)\",
    \"date_marker\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"scope\": \"project\"
  }"
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Events not appearing | Wrong `api_host` | Use `us.i.posthog.com` (not `app.posthog.com`) |
| Ad blocker blocks events | Direct PostHog requests | Set up reverse proxy via Next.js rewrites |
| Edge function events lost | No `shutdown()` call | Always `await posthog.shutdown()` in serverless |
| Proxy assets load but flags fail | Proxy does not cover `/flags` | Compare all proxy paths with the official platform guide |
| Cloud Run cold start lag | Client initialized per request | Reuse a module-scoped client where the runtime permits it and flush at lifecycle boundaries |

## Output

- Application integration deployed to the chosen platform with credential boundaries documented
- Reverse proxy enabled for ad blocker bypass (Vercel/Next.js)
- Server-side event capture with proper shutdown hooks
- Deployment annotations marking releases in PostHog timeline

## Examples

For a Vercel-hosted Next.js app, verify the region-specific ingest and asset routes, keep private keys server-only, test capture and flags through the proxy, and record a rollback that disables instrumentation without blocking the application.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Next.js Integration](https://posthog.com/docs/libraries/next-js)
- [PostHog open-source self-hosting disclaimer](https://posthog.com/docs/self-host/open-source/disclaimer)
- [PostHog Vercel Integration](https://posthog.com/docs/libraries/vercel)
- [PostHog Annotations API](https://posthog.com/docs/api/annotations)

## Next Steps

For webhook handling, see `posthog-webhooks-events`.
