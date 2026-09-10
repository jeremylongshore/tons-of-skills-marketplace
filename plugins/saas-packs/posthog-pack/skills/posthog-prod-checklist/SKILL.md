---
name: posthog-prod-checklist
description: |
  Run a fail-safe production-readiness review for PostHog instrumentation, flags, secrets, privacy, delivery, and rollback. Use when enabling a new production integration or major SDK change. Trigger with "PostHog production checklist", "PostHog go-live", or "review PostHog launch".
argument-hint: "[project-path] [release-ref]"
allowed-tools: Read, Bash(kubectl:*), Bash(curl:*), Grep
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- deployment
compatibility: Designed for Claude Code
---
# PostHog Production Checklist

## Overview

Production readiness verification for PostHog integrations. Covers SDK configuration hardening, graceful degradation when PostHog is unavailable, health check endpoints, proper shutdown hooks for serverless, and rollback procedures.

## Prerequisites

- PostHog integration tested in staging
- Production PostHog project with `phc_` key
- Least-privilege private API credential only for the private operations the integration actually performs
- Deployment pipeline configured

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries.

### Pre-Deployment Checklist

**SDK Configuration:**

- [ ] `api_host` set to correct region (`us.i.posthog.com` or `eu.i.posthog.com`)
- [ ] `capture_pageview: false` if using SPA with manual pageview tracking
- [ ] `capture_pageleave: true` for session duration accuracy
- [ ] Reverse proxy configured to bypass ad blockers (see `posthog-sdk-patterns`)
- [ ] `posthog.debug()` disabled in production (guarded by `NODE_ENV`)
- [ ] `autocapture` configured to exclude noisy elements

**Server-Side:**

- [ ] `posthog.shutdown()` called in SIGTERM handler and serverless function cleanup
- [ ] Feature flags secure API key is passed through `personalApiKey` for server-side local evaluation
- [ ] `flushAt` and `flushInterval` tuned (default 20/10s is fine for most apps)

**Security:**

- [ ] Personal API key (`phx_`) never in client bundles or NEXT_PUBLIC_ vars
- [ ] `.env` files in `.gitignore`
- [ ] Separate PostHog project per environment

### Step 1: Production SDK Configuration

```typescript
// lib/posthog-production.ts
import { PostHog } from 'posthog-node';

const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
  personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
  flushAt: 20,
  flushInterval: 10000,
  requestTimeout: 10000,
  maxRetries: 3,
});

// Graceful shutdown
async function shutdown() {
  await posthog.shutdown();
  process.exit(0);
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

### Step 2: Graceful Degradation

```typescript
// PostHog should never break your app — wrap all calls
function safeCapture(distinctId: string, event: string, properties?: Record<string, any>) {
  try {
    posthog.capture({ distinctId, event, properties });
  } catch (error) {
    // Log but never throw — analytics should not crash your app
    console.error('[PostHog] Capture failed:', (error as Error).message);
  }
}

async function safeGetFlag(flagKey: string, userId: string, defaultValue: boolean = false): Promise<boolean> {
  try {
    const result = await posthog.isFeatureEnabled(flagKey, userId);
    return result ?? defaultValue;
  } catch (error) {
    console.error('[PostHog] Flag evaluation failed:', (error as Error).message);
    return defaultValue; // Always return safe default
  }
}
```

### Step 3: Health Check Endpoint

```typescript
// api/health.ts (Next.js API route or Express handler)
// getPostHogDeliverySnapshot() reads application-owned counters maintained by
// the capture wrapper; it does not send a synthetic event on every health check.
export async function GET() {
  const delivery = getPostHogDeliverySnapshot();
  const degraded = delivery.errorRatio > delivery.reviewedErrorRatio
    || delivery.oldestQueuedEventMs > delivery.reviewedQueueAgeMs
    || delivery.flagFallbackRatio > delivery.reviewedFlagFallbackRatio;

  return Response.json({
    status: degraded ? 'degraded' : 'healthy',
    checks: {
      capture_delivery: delivery.captureStatus,
      queue_age_ms: delivery.oldestQueuedEventMs,
      flag_fallback_ratio: delivery.flagFallbackRatio,
      last_success_at: delivery.lastSuccessAt,
    },
  }, { status: degraded ? 503 : 200 });
}
```

### Step 4: Serverless Function Pattern

```typescript
// For Vercel Edge Functions, AWS Lambda, etc.
import { PostHog } from 'posthog-node';

export async function handler(request: Request) {
  // Create client per invocation in serverless (or use module-level singleton)
  const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    host: 'https://us.i.posthog.com',
    flushAt: 1,       // Flush immediately in serverless
    flushInterval: 0,  // Don't wait
  });

  try {
    posthog.capture({
      distinctId: getUserId(request),
      event: 'api_called',
      properties: { endpoint: new URL(request.url).pathname },
    });

    const result = await doWork(request);
    return Response.json(result);
  } finally {
    // CRITICAL: Always flush before function exits
    await posthog.shutdown();
  }
}
```

### Step 5: Pre-Flight Verification

```bash
set -euo pipefail
: "${POSTHOG_PUBLIC_HOST:?Set the project's regional ingestion host}"
: "${POSTHOG_PRIVATE_HOST:?Set the matching private API host}"

# 1. Verify PostHog is reachable from the release environment.
curl -sf "$POSTHOG_PUBLIC_HOST/healthz" && echo "PostHog: OK" || echo "PostHog: UNREACHABLE"

# 2. Verify the public project token through the non-capture flags endpoint.
curl -s -X POST "$POSTHOG_PUBLIC_HOST/flags?v=2" \
  -H 'Content-Type: application/json' \
  -d "{\"api_key\":\"$NEXT_PUBLIC_POSTHOG_KEY\",\"distinct_id\":\"deploy-check\"}" | jq '{flags, errorsParsingFlags}'

# 3. Verify private API access only when the integration requires it.
curl -sf "$POSTHOG_PRIVATE_HOST/api/projects/$POSTHOG_PROJECT_ID/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | jq '.name' && echo "Admin API: OK"
```

Verify event delivery in a dedicated test project or with an explicitly approved synthetic production event. A 200 response confirms receipt and payload shape, not final ingestion; inspect `quota_limited`, ingestion warnings, and the resulting named event.

## Error Handling

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| PostHog capture failing | Application delivery error SLO breached | P3 | Check API host, queue, flush, and ingestion warnings |
| Flag evaluation breaches the service SLO | Reviewed service threshold | P2 | Inspect local evaluation, cache state, and remote fallback |
| Events not appearing | Expected event freshness SLO breached | P2 | Check `shutdown()` is called, verify flush and warnings |
| Admin API 401 | Personal key rejected | P1 | Rotate key in PostHog settings |

## Rollback Procedure

```bash
set -euo pipefail
# Quick rollback if PostHog causes issues
# Option 1: Disable PostHog via env var
kubectl set env deployment/app POSTHOG_ENABLED=false
kubectl rollout restart deployment/app

# Option 2: Roll back deployment
kubectl rollout undo deployment/app
kubectl rollout status deployment/app
```

## Output

- Production-hardened PostHog SDK configuration
- Graceful degradation wrappers (never crash on analytics failure)
- Read-only health endpoint based on application-owned delivery and fallback telemetry
- Serverless shutdown pattern
- Pre-flight verification commands

## Examples

Before enabling production capture, verify the regional host, project-token scope, consent behavior, server lifecycle, flag defaults, proxy routes, release owner, and kill switch. Use a controlled test identity and report each check as pass, fail, or not applicable with evidence.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Node.js SDK](https://posthog.com/docs/libraries/node)
- [PostHog Status Page](https://status.posthog.com)
- [PostHog Support](https://posthog.com/docs/support)

## Next Steps

For version upgrades, see `posthog-upgrade-migration`.
