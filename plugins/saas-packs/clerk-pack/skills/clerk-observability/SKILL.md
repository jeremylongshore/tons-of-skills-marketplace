---
name: clerk-observability
description: 'Implement monitoring, logging, and observability for Clerk authentication.

  Use when setting up monitoring, debugging auth issues in production,

  or implementing audit logging.

  Trigger with phrases like "clerk monitoring", "clerk logging",

  "clerk observability", "clerk metrics", "clerk audit log".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- monitoring
- observability
- debugging
compatibility: Designed for Claude Code
---
# Clerk Observability

## Overview

Implement monitoring, logging, and observability for Clerk authentication. Covers structured auth logging, middleware performance tracking, webhook event monitoring, Sentry integration, and health check endpoints.

## Prerequisites

- Clerk integration working
- Monitoring platform (Sentry, DataDog, or Pino logger at minimum)
- Logging infrastructure (structured JSON logs recommended)

## Instructions

### Step 1: Structured Authentication Event Logging

```typescript
// lib/auth-logger.ts
import pino from 'pino'

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development' ? { target: 'pino-pretty' } : undefined,
})

export function logAuthEvent(event: {
  type: 'sign_in' | 'sign_out' | 'sign_up' | 'permission_denied' | 'session_expired'
  userId?: string | null
  orgId?: string | null
  path: string
  metadata?: Record<string, any>
}) {
  logger.info({
    category: 'auth',
    ...event,
    timestamp: new Date().toISOString(),
  })
}

export function logAuthError(error: Error, context: { userId?: string; path: string }) {
  logger.error({
    category: 'auth',
    error: error.message,
    stack: error.stack,
    ...context,
    timestamp: new Date().toISOString(),
  })
}
```

### Step 2: Middleware Performance Monitoring

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)'])

export default clerkMiddleware(async (auth, req) => {
  const start = Date.now()

  if (!isPublicRoute(req)) {
    await auth.protect()
  }

  const duration = Date.now() - start
  const { userId } = await auth()

  // Log slow auth checks
  if (duration > 100) {
    console.warn(`[Auth Perf] ${req.nextUrl.pathname} took ${duration}ms`, {
      userId: userId || 'anonymous',
      method: req.method,
    })
  }

  // Add timing header for debugging
  const response = new Response(null, { status: 200 })
  response.headers.set('X-Auth-Duration', `${duration}ms`)
})
```

### Step 3: Webhook Event Tracking

```typescript
// app/api/webhooks/clerk/route.ts
import { logAuthEvent } from '@/lib/auth-logger'

async function handleWebhookEvent(evt: WebhookEvent) {
  const startTime = Date.now()

  // Track webhook processing metrics
  const metrics = {
    eventType: evt.type,
    receivedAt: new Date().toISOString(),
    processingTimeMs: 0,
  }

  switch (evt.type) {
    case 'user.created':
      logAuthEvent({
        type: 'sign_up',
        userId: evt.data.id,
        path: '/webhooks/clerk',
        metadata: { email: evt.data.email_addresses[0]?.email_address },
      })
      await db.user.create({ data: { clerkId: evt.data.id } })
      break

    case 'session.created':
      logAuthEvent({
        type: 'sign_in',
        userId: evt.data.user_id,
        path: '/webhooks/clerk',
      })
      break

    case 'session.ended':
      logAuthEvent({
        type: 'sign_out',
        userId: evt.data.user_id,
        path: '/webhooks/clerk',
      })
      break
  }

  metrics.processingTimeMs = Date.now() - startTime

  // Alert on slow webhook processing
  if (metrics.processingTimeMs > 5000) {
    console.error('[Webhook] Slow processing:', metrics)
  }

  return Response.json({ received: true })
}
```

### Step 4: Sentry Error Tracking Integration

```typescript
// lib/sentry-clerk.ts
import * as Sentry from '@sentry/nextjs'
import { auth, currentUser } from '@clerk/nextjs/server'

export async function initSentryUser() {
  const { userId, orgId } = await auth()

  if (userId) {
    const user = await currentUser()
    Sentry.setUser({
      id: userId,
      email: user?.emailAddresses[0]?.emailAddress,
      username: user?.username || undefined,
    })
    Sentry.setTag('org_id', orgId || 'personal')
  }
}

// Wrap API routes with Sentry + Clerk context
export function withAuthSentry(handler: Function) {
  return async (...args: any[]) => {
    await initSentryUser()
    try {
      return await handler(...args)
    } catch (error) {
      Sentry.captureException(error)
      throw error
    }
  }
}
```

```typescript
// sentry.server.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Scrub Clerk secret key if accidentally logged
    if (event.extra) {
      delete event.extra['CLERK_SECRET_KEY']
    }
    return event
  },
})
```

### Step 5: Health Check Endpoint

```typescript
// app/api/health/route.ts
import { clerkClient } from '@clerk/nextjs/server'

export async function GET() {
  const checks: Record<string, { status: string; latencyMs: number; detail?: string }> = {}

  // Check Clerk Backend API
  const clerkStart = Date.now()
  try {
    const client = await clerkClient()
    await client.users.getUserList({ limit: 1 })
    checks.clerk = { status: 'healthy', latencyMs: Date.now() - clerkStart }
  } catch (err: any) {
    checks.clerk = { status: 'unhealthy', latencyMs: Date.now() - clerkStart, detail: err.message }
  }

  // Check database
  const dbStart = Date.now()
  try {
    await db.$queryRaw`SELECT 1`
    checks.database = { status: 'healthy', latencyMs: Date.now() - dbStart }
  } catch (err: any) {
    checks.database = { status: 'unhealthy', latencyMs: Date.now() - dbStart, detail: err.message }
  }

  const allHealthy = Object.values(checks).every((c) => c.status === 'healthy')
  return Response.json(
    { status: allHealthy ? 'healthy' : 'degraded', checks, timestamp: new Date().toISOString() },
    { status: allHealthy ? 200 : 503 }
  )
}
```

### Step 6: Dashboard Metrics Query

```typescript
// app/api/admin/auth-metrics/route.ts
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { has } = await auth()
  if (!has({ role: 'org:admin' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  const now = new Date()
  const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)

  const metrics = {
    signIns24h: await db.auditLog.count({
      where: { action: 'sign_in', timestamp: { gte: dayAgo } },
    }),
    signUps24h: await db.auditLog.count({
      where: { action: 'sign_up', timestamp: { gte: dayAgo } },
    }),
    authErrors24h: await db.auditLog.count({
      where: { action: 'permission_denied', timestamp: { gte: dayAgo } },
    }),
    webhookEvents24h: await db.webhookEvent.count({
      where: { processedAt: { gte: dayAgo } },
    }),
  }

  return Response.json(metrics)
}
```

## Output

- Structured auth event logging with Pino (sign-in, sign-out, sign-up, errors)
- Middleware performance tracking with slow-request alerts
- Webhook event monitoring with processing time metrics
- Sentry integration with Clerk user context
- Health check endpoint monitoring Clerk API and database
- Admin metrics endpoint for auth dashboard

## Error Handling

| Issue | Monitoring Action |
|-------|-------------------|
| High auth latency (p95 > 200ms) | Alert via middleware timing logs, investigate caching |
| Webhook failure rate > 1% | Alert on processing errors, check endpoint health |
| Session anomalies | Track unusual sign-in patterns via audit log |
| Clerk API errors | Capture with Sentry context, check status.clerk.com |

## Examples

### Quick Monitoring One-Liner

```bash
# Watch auth events in real-time (development)
LOG_LEVEL=debug npm run dev 2>&1 | grep '"category":"auth"'
```

## Resources

- Clerk Dashboard Analytics
- [Sentry Next.js Integration](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Pino Logger](https://getpino.io/)

## Next Steps

Proceed to `clerk-incident-runbook` for incident response procedures.
