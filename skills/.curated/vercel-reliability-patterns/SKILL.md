---
name: vercel-reliability-patterns
description: 'Implement reliability patterns for Vercel deployments including circuit
  breakers, retry logic, and graceful degradation.

  Use when building fault-tolerant serverless functions, implementing retry strategies,

  or adding resilience to production Vercel services.

  Trigger with phrases like "vercel reliability", "vercel circuit breaker",

  "vercel resilience", "vercel fallback", "vercel graceful degradation".

  '
allowed-tools: Read, Write, Edit
version: 1.18.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- vercel
- reliability
- resilience
- patterns
compatibility: Designed for Claude Code
---
# Vercel Reliability Patterns

## Overview

Build fault-tolerant Vercel deployments with circuit breakers, retry logic, graceful degradation, and instant rollback integration. Addresses reliability at two levels: function-level resilience (protecting against dependency failures) and deployment-level resilience (protecting against bad deploys).

## Prerequisites

- Vercel project deployed to production
- Understanding of failure modes in serverless
- External dependencies (databases, APIs) identified

## Instructions

### Step 1: Circuit Breaker for External Dependencies

```typescript
// lib/circuit-breaker.ts
type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

class CircuitBreaker {
  private state: CircuitState = 'CLOSED';
  private failures = 0;
  private lastFailure = 0;
  private readonly threshold: number;
  private readonly resetTimeMs: number;

  constructor(threshold = 5, resetTimeMs = 30000) {
    this.threshold = threshold;
    this.resetTimeMs = resetTimeMs;
  }

  async call<T>(fn: () => Promise<T>, fallback: () => T): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure > this.resetTimeMs) {
        this.state = 'HALF_OPEN';
      } else {
        console.warn('Circuit OPEN — returning fallback');
        return fallback();
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      console.error('Circuit breaker caught error:', error);
      return fallback();
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailure = Date.now();
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      console.warn(`Circuit OPENED after ${this.failures} failures`);
    }
  }
}

// Usage in a serverless function:
const dbCircuit = new CircuitBreaker(3, 30000);

export default async function handler(req, res) {
  const users = await dbCircuit.call(
    () => db.user.findMany({ take: 10 }),
    () => [] // Fallback: empty array when DB is down
  );
  res.json({ users, degraded: users.length === 0 });
}
```

**Important for serverless:** Circuit breaker state lives in a single function instance. Different instances have independent circuits. For global circuit state, use a shared store such as Upstash Redis.

### Step 2: Retry with Exponential Backoff

```typescript
// lib/retry.ts
interface RetryOptions {
  maxRetries?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  retryOn?: (error: unknown) => boolean;
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const { maxRetries = 3, baseDelayMs = 200, maxDelayMs = 5000, retryOn } = options;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      if (retryOn && !retryOn(error)) throw error;

      const delay = Math.min(
        baseDelayMs * Math.pow(2, attempt) + Math.random() * 200,
        maxDelayMs
      );
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error('Unreachable');
}

// Usage:
const data = await withRetry(
  () => fetch('https://api.example.com/data').then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }),
  {
    maxRetries: 3,
    retryOn: (err) => {
      // Only retry on network errors and 5xx, not 4xx
      if (err instanceof TypeError) return true; // network error
      return err.message?.includes('5');
    },
  }
);
```

### Step 3: Graceful Degradation with Stale Cache

```typescript
// api/products.ts — serve stale data when primary source is down
import { Redis } from '@upstash/redis';

const redis = Redis.fromEnv();

export default async function handler(req, res) {
  const cacheKey = 'products:latest';

  try {
    // Try primary data source
    const freshData = await fetchProductsFromDB();

    // Update cache with fresh data
    await redis.set(cacheKey, freshData, { ex: 3600 }); // values are JSON-serialized automatically

    res.setHeader('x-data-source', 'live');
    res.json(freshData);
  } catch (error) {
    // Primary failed — serve stale cache
    const cachedData = await redis.get(cacheKey);

    if (cachedData) {
      console.warn('Serving stale cache — primary source unavailable');
      res.setHeader('x-data-source', 'cache-stale');
      res.json(cachedData);
    } else {
      // No cache available — return degraded response
      res.setHeader('x-data-source', 'degraded');
      res.status(503).json({
        error: 'Service temporarily unavailable',
        degraded: true,
      });
    }
  }
}
```

### Step 4: Idempotency Keys for Mutations

```typescript
// api/orders/route.ts — idempotent order creation
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function POST(request: NextRequest) {
  const idempotencyKey = request.headers.get('idempotency-key');
  if (!idempotencyKey) {
    return NextResponse.json(
      { error: 'idempotency-key header required' },
      { status: 400 }
    );
  }

  // Check if this request was already processed
  const existing = await db.idempotencyRecord.findUnique({
    where: { key: idempotencyKey },
  });

  if (existing) {
    // Return the cached response — same status and body
    return NextResponse.json(JSON.parse(existing.responseBody), {
      status: existing.responseStatus,
      headers: { 'x-idempotent-replay': 'true' },
    });
  }

  // Process the order
  const body = await request.json();
  const order = await db.order.create({ data: body });

  // Cache the response for idempotency
  const responseBody = JSON.stringify({ order });
  await db.idempotencyRecord.create({
    data: { key: idempotencyKey, responseStatus: 201, responseBody },
  });

  return NextResponse.json({ order }, { status: 201 });
}
```

### Step 5: Health Check with Dependency Status

```typescript
// api/health/route.ts
export const dynamic = 'force-dynamic';

interface HealthCheck {
  name: string;
  check: () => Promise<boolean>;
}

const checks: HealthCheck[] = [
  {
    name: 'database',
    check: async () => {
      await db.$queryRaw`SELECT 1`;
      return true;
    },
  },
  {
    name: 'cache',
    check: async () => {
      await kv.ping();
      return true;
    },
  },
  {
    name: 'external-api',
    check: async () => {
      const r = await fetch('https://api.example.com/health', { signal: AbortSignal.timeout(3000) });
      return r.ok;
    },
  },
];

export async function GET() {
  const results: Record<string, 'ok' | 'error'> = {};

  await Promise.all(
    checks.map(async ({ name, check }) => {
      try {
        await check();
        results[name] = 'ok';
      } catch {
        results[name] = 'error';
      }
    })
  );

  const healthy = Object.values(results).every(v => v === 'ok');
  return Response.json(
    { status: healthy ? 'healthy' : 'degraded', checks: results },
    { status: healthy ? 200 : 503 }
  );
}
```

### Step 6: Deployment-Level Resilience

```bash
# Instant rollback on health check failure (CI integration)
DEPLOY_URL=$(vercel --prod)
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOY_URL/api/health")

if [ "$HEALTH" != "200" ]; then
  echo "Health check failed ($HEALTH) — rolling back"
  vercel rollback
  exit 1
fi
echo "Deployment healthy"
```

## Reliability Patterns Summary

| Pattern | Protects Against | Vercel Implementation |
|---------|-----------------|----------------------|
| Circuit breaker | Dependency degradation | In-function state or Edge Config |
| Retry + backoff | Transient failures | withRetry wrapper |
| Stale cache | Primary source outage | Upstash Redis with TTL |
| Idempotency | Duplicate mutations | Database record per request |
| Health checks | Bad deployments | `/api/health` + rollback automation |
| Instant rollback | Deployment regression | `vercel rollback` in CI |

## Output

- Circuit breaker protecting all external dependency calls
- Retry logic with exponential backoff for transient failures
- Graceful degradation serving stale data when primary fails
- Idempotency preventing duplicate mutations
- Automated health check + rollback pipeline

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Circuit opens too aggressively | Threshold too low | Increase failure threshold (e.g., 5 → 10) |
| Retry causes duplicate side effects | No idempotency | Add idempotency-key to mutation endpoints |
| Stale cache expired | TTL too short or never populated | Increase TTL, seed cache on deploy |
| Health check false positive | Timeout too short | Increase AbortSignal timeout to 5s |
| Rollback reverts good deployment | Flaky health check | Add retry to health check before rollback |

## Examples

### Protect a payment mutation from retries and rollback safely

Require a client-supplied idempotency key for the mutation, store the key and outcome in the authoritative data store, and retry only transient upstream failures with bounded backoff. Exercise a synthetic duplicate request in preview and confirm that it returns the original outcome without creating a second charge or record. Pair health-check rollback with multiple checks and an explicit deployment ID so a noisy probe cannot revert a healthy release.

## Resources

- [Vercel Instant Rollback](https://vercel.com/docs/instant-rollback)
- [Upstash Redis TypeScript SDK](https://upstash.com/docs/redis/sdks/ts/overview)
- [Edge Config](https://vercel.com/docs/edge-config)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## Next Steps

For policy guardrails, see `vercel-policy-guardrails`.
