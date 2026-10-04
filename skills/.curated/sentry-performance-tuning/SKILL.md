---
name: sentry-performance-tuning
description: 'Optimize Sentry performance monitoring for lower overhead and higher
  signal.

  Use when tuning tracesSampleRate vs tracesSampler, configuring continuous profiling,

  fixing high-cardinality transaction names, adding custom span measurements,

  reducing SDK overhead, or setting Web Vitals thresholds.

  Trigger: "sentry performance optimize", "tune sentry sampling",

  "reduce sentry overhead", "sentry web vitals", "sentry profiling setup".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm:*), Bash(npx:*), Bash(node:*),
  Bash(sentry-cli:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- monitoring
- performance
- optimization
- profiling
- web-vitals
compatibility: Designed for Claude Code
---
# Sentry Performance Tuning

## Overview

Optimize Sentry's performance monitoring pipeline to maximize signal quality while minimizing SDK overhead and event volume costs. Covers the v8 SDK API for `@sentry/node`, `@sentry/browser`, and `sentry-sdk` (Python), targeting `sentry.io` or self-hosted Sentry 24.1+.

## Prerequisites

- Sentry SDK v8+ installed (`@sentry/node` >= 8.0.0 or `sentry-sdk` >= 2.0.0)
- `Sentry.init()` called with a valid DSN before any application code runs
- Performance monitoring enabled (`tracesSampleRate > 0` or a `tracesSampler` function)
- Access to the Sentry Performance dashboard to verify changes

## Instructions

### Step 1 — Replace Static `tracesSampleRate` with Dynamic `tracesSampler`

A flat `tracesSampleRate: 0.1` samples all routes equally. The `tracesSampler` callback makes per-transaction decisions based on route, operation type, and upstream trace context.

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  // tracesSampler replaces tracesSampleRate — do not set both
  tracesSampler: (samplingContext) => {
    const { name, attributes, parentSampled } = samplingContext;

    // Honor parent sampling for distributed trace consistency
    if (parentSampled !== undefined) return parentSampled ? 1.0 : 0;

    // Drop noise — health probes, static assets
    if (name?.match(/\/(health|ready|alive|ping|metrics)$/)) return 0;
    if (name?.match(/\.(js|css|png|jpg|svg|woff2?|ico)$/)) return 0;

    // Always sample business-critical paths
    if (name?.includes('/checkout') || name?.includes('/payment')) return 1.0;

    // Higher sampling for write operations (mutations are riskier)
    if (name?.startsWith('POST ') || name?.startsWith('PUT ')) return 0.25;

    // Moderate sampling for read APIs
    if (name?.startsWith('GET /api/')) return 0.1;

    // Low sampling for background work
    if (name?.startsWith('job:') || name?.startsWith('queue:')) return 0.05;

    // User-tier sampling (via custom attributes from middleware)
    if (attributes?.['user.plan'] === 'enterprise') return 0.5;

    return 0.05; // Default: 5%
  },
});
```

### Step 2 — Configure Profiling with `profilesSampleRate`

The `profilesSampleRate` controls what fraction of *traced* transactions get profiled. Setting it to 1.0 with a 5% `tracesSampler` means 5% of traffic is profiled.

```typescript
import { nodeProfilingIntegration } from '@sentry/profiling-node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [nodeProfilingIntegration()],
  tracesSampler: (ctx) => { /* ... from Step 1 ... */ },

  // Effective rate = tracesSampler rate * profilesSampleRate
  profilesSampleRate: 1.0,

  // Alternative: Continuous profiling (v8.7.0+) — profiles the entire process
  // profileSessionSampleRate: 0.1,  // 10% of server instances
});
```

**Tuning:** Start at `profilesSampleRate: 0.1` in production. Profiling adds ~3-5% CPU overhead per profiled transaction. Continuous profiling (`profileSessionSampleRate`) has lower per-transaction cost but runs on sampled instances continuously.

### Step 3 — Fix Transaction Naming (Prevent Cardinality Explosion)

Names with dynamic IDs (`/api/users/12345`) create thousands of unique entries, degrading dashboard performance and inflating quota. **Route templates go in the name, dynamic values go in attributes.**

```typescript
// BAD — creates thousands of unique transaction entries
// GET /api/users/12345, GET /api/users/67890, ...

// GOOD — Sentry auto-parameterizes Express/Koa/Fastify routes
// GET /api/users/:userId

// For custom spans, always parameterize:
Sentry.startSpan(
  {
    name: 'order.process',           // No dynamic IDs in name
    op: 'task',
    attributes: {
      'order.id': orderId,           // Filterable in Discover queries
      'order.total_cents': totalCents,
      'customer.tier': customerTier,
    },
  },
  async (span) => {
    const result = await processOrder(orderId);
    span.setAttribute('order.status', result.status);
    return result;
  }
);
```

**Detect cardinality issues** with a Discover query:

```
SELECT count(), transaction FROM transactions GROUP BY transaction ORDER BY count() DESC
```

### Step 4 — Add Custom Measurements

Custom measurements appear in the Performance dashboard and can be charted, alerted on, and queried in Discover. Unit types: `'millisecond'`, `'byte'`, `'none'` (count), `'percent'`.

```typescript
await Sentry.startSpan(
  { name: 'search.execute', op: 'function' },
  async (span) => {
    const start = performance.now();
    const results = await searchService.query(term);

    Sentry.setMeasurement('search.latency', performance.now() - start, 'millisecond');
    Sentry.setMeasurement('search.result_count', results.length, 'none');
    Sentry.setMeasurement('search.memory_delta',
      process.memoryUsage().heapUsed - memBefore, 'byte');

    span.setAttribute('search.cache_hit', results.fromCache);
    return results;
  }
);
```

| Measurement | Unit | Use case |
|-------------|------|----------|
| `cart.total_cents` | `none` | Revenue correlation with latency |
| `query.rows_scanned` | `none` | Database query efficiency |
| `cache.hit_rate` | `percent` | Cache performance per route |
| `upload.file_size` | `byte` | File upload impact on response time |

### Step 5 — Reduce SDK Overhead

For high-throughput services (>1000 req/s), every integration and breadcrumb counts.

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  maxBreadcrumbs: 20,           // Default: 100. Each ~0.5-2KB.
  maxValueLength: 500,          // Truncate long string values
  maxAttachmentSize: 5_242_880, // 5MB (default: 20MB)

  // Remove noisy integrations
  integrations: (defaults) => defaults.filter(
    (i) => i.name !== 'Console'
  ),

  // Trim oversized stack traces
  beforeSend: (event) => {
    if (event.exception?.values) {
      for (const exc of event.exception.values) {
        if (exc.stacktrace?.frames && exc.stacktrace.frames.length > 30) {
          exc.stacktrace.frames = [
            ...exc.stacktrace.frames.slice(0, 10),
            ...exc.stacktrace.frames.slice(-20),
          ];
        }
      }
    }
    return event;
  },

  // Drop internal/noise spans
  beforeSendSpan: (span) => {
    if (span.description?.startsWith('internal.')) return null;
    return span;
  },
});
```

**Browser SDK lazy loading** (saves ~30KB gzipped from critical path):

```typescript
async function initSentry() {
  const Sentry = await import('@sentry/browser');
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
  });
}
window.addEventListener('load', initSentry, { once: true });
```

### Step 6 — Span Best Practices (Avoid Span Explosion)

Only wrap operations with measurable latency (>1ms). Never span synchronous lookups or individual loop iterations.

```typescript
// BAD — sub-microsecond config read; span overhead exceeds operation cost
function getConfig(key: string) {
  return Sentry.startSpan({ name: 'config.get', op: 'function' }, () => config[key]);
}

// BAD — N spans per request from loop iterations
for (const item of items) {
  await Sentry.startSpan({ name: 'process.item', op: 'function' }, () => processItem(item));
}

// GOOD — span the batch, count in attributes
await Sentry.startSpan(
  { name: 'process.batch', op: 'function', attributes: { 'batch.size': items.length } },
  async () => Promise.all(items.map(processItem))
);

// GOOD — span external I/O with real latency
async function fetchUserProfile(userId: string) {
  return Sentry.startSpan(
    { name: 'user.fetch_profile', op: 'http.client', attributes: { 'user.id': userId } },
    async () => fetch(`${USER_SERVICE_URL}/users/${userId}`).then(r => r.json())
  );
}
```

### Step 7 — Web Vitals Monitoring

The Browser SDK auto-captures Core Web Vitals. Filter span creation to avoid noise from third-party scripts.

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    Sentry.browserTracingIntegration({
      shouldCreateSpanForRequest: (url) =>
        !url.includes('googleapis.com') && !url.includes('analytics'),
    }),
  ],
  tracesSampleRate: 0.1,
});
```

| Metric | Good | Poor | Measures |
|--------|------|------|----------|
| **LCP** | < 2.5s | > 4.0s | Visual load completion |
| **INP** | < 200ms | > 500ms | Input responsiveness (replaced FID) |
| **CLS** | < 0.1 | > 0.25 | Visual stability |
| **TTFB** | < 800ms | > 1800ms | Server response time |

**Alert thresholds:** LCP p75 > 2.5s (5 min), INP p75 > 200ms (5 min), CLS p75 > 0.1 (15 min).

### Step 8 — Dashboard Queries for Performance Trends

```
-- Slowest transactions (p95)
SELECT transaction, p95(transaction.duration), count()
FROM transactions WHERE transaction.duration:>1000
ORDER BY p95(transaction.duration) DESC

-- Regression detection (20%+ slower vs last week)
SELECT transaction, p75(transaction.duration),
       compare(p75(transaction.duration), -7d) as vs_last_week
FROM transactions GROUP BY transaction
HAVING compare(p75(transaction.duration), -7d) > 1.2

-- Span breakdown for a route
SELECT span.op, span.description, p75(span.duration), count()
FROM spans WHERE transaction:/api/checkout
ORDER BY p75(span.duration) DESC
```

## Output

- **Dynamic sampling** active — health checks at 0%, payments at 100%, defaults at 5%
- **Profiling** enabled with `profilesSampleRate` or continuous `profileSessionSampleRate`
- **Transaction names** parameterized — cardinality under 500 unique names
- **Custom measurements** tracking business KPIs alongside latency
- **SDK overhead** reduced — fewer breadcrumbs, filtered integrations, trimmed payloads
- **Web Vitals** monitored with alerts at Google's recommended thresholds

Verify at Sentry Stats (Settings > Stats) — volume should drop while data quality improves.

## Error Handling

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Performance tab empty | `tracesSampler` returns 0 for all routes | Log sampler decisions; check default return |
| "Too many unique transaction names" | Dynamic IDs in names | Parameterize names; IDs in `attributes` (Step 3) |
| SDK adds >50ms latency | Too many integrations/breadcrumbs | Reduce `maxBreadcrumbs` to 20; disable `Console` |
| Profiling tab empty | Missing `@sentry/profiling-node` | Install package; set `profilesSampleRate: 1.0` |
| Incomplete distributed traces | Independent sampling decisions | Check `parentSampled` first in sampler (Step 1) |
| `setMeasurement` values missing | Called outside active span | Call inside `Sentry.startSpan()` callback |
| Web Vitals null | Missing `browserTracingIntegration` | Add integration; set `tracesSampleRate > 0` |

## Examples

### TypeScript — Express Production Setup

```typescript
import * as Sentry from '@sentry/node';
import { nodeProfilingIntegration } from '@sentry/profiling-node';
import express from 'express';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.SENTRY_RELEASE,
  integrations: [nodeProfilingIntegration()],
  tracesSampler: (ctx) => {
    const { name, parentSampled } = ctx;
    if (parentSampled !== undefined) return parentSampled ? 1.0 : 0;
    if (name?.match(/\/(health|ready|ping)$/)) return 0;
    if (name?.includes('/checkout')) return 1.0;
    if (name?.startsWith('POST ')) return 0.25;
    if (name?.startsWith('GET /api/')) return 0.1;
    return 0.05;
  },
  profilesSampleRate: 1.0,
  maxBreadcrumbs: 20,
  beforeSendSpan: (span) =>
    span.description?.includes('health') ? null : span,
});

const app = express();
Sentry.setupExpressErrorHandler(app);

app.get('/api/search', async (req, res) => {
  const results = await Sentry.startSpan(
    { name: 'search.execute', op: 'function' },
    async () => {
      const data = await searchService.query(req.query.q as string);
      Sentry.setMeasurement('search.result_count', data.length, 'none');
      return data;
    }
  );
  res.json(results);
});
```

### Python — FastAPI Production Setup

```python
import os, re, sentry_sdk
from fastapi import FastAPI

def traces_sampler(ctx: dict) -> float:
    tx = ctx.get("transaction_context", {})
    name = tx.get("name", "")
    parent = ctx.get("parent_sampled")
    if parent is not None:
        return 1.0 if parent else 0.0
    if re.search(r"/(health|ready|ping)$", name):
        return 0.0
    if "/checkout" in name or "/payment" in name:
        return 1.0
    if name.startswith(("POST ", "PUT ")):
        return 0.25
    if name.startswith("GET /api/"):
        return 0.1
    if tx.get("op") == "task":
        return 0.05
    return 0.05

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    environment=os.environ.get("ENVIRONMENT", "development"),
    release=os.environ.get("SENTRY_RELEASE"),
    traces_sampler=traces_sampler,
    profiles_sample_rate=1.0,
    max_breadcrumbs=20,
    before_send_transaction=lambda event, hint: (
        None if event.get("transaction", "").endswith("/health") else event
    ),
)

app = FastAPI()

@app.get("/api/search")
async def search(q: str):
    with sentry_sdk.start_span(op="function", name="search.execute") as span:
        results = await search_service.query(q)
        sentry_sdk.set_measurement("search.result_count", len(results), "none")
        span.set_data("search.query_length", len(q))
        return {"results": results}
```

## Resources

- [Performance Monitoring](https://docs.sentry.io/product/performance/) — Dashboard overview and configuration
- [Sampling Configuration](https://docs.sentry.io/platforms/javascript/configuration/sampling/) — `tracesSampler` deep dive
- [Profiling (Node.js)](https://docs.sentry.io/platforms/javascript/guides/node/profiling/) — Setup and tuning
- [Profiling (Python)](https://docs.sentry.io/platforms/python/profiling/) — `sentry-sdk[profiling]` setup
- [Web Vitals](https://docs.sentry.io/product/insights/web-vitals/) — LCP, INP, CLS dashboards
- [Custom Instrumentation](https://docs.sentry.io/platforms/javascript/performance/instrumentation/custom-instrumentation/) — `setMeasurement()` API
- [Discover Queries](https://docs.sentry.io/product/explore/discover-queries/) — SQL-like query builder
- [Span Operations](https://develop.sentry.dev/sdk/performance/span-operations/) — Naming conventions for `op` field

## Next Steps

1. **Validate sampling** — Check Sentry Stats (Settings > Stats) to confirm volume dropped while critical route coverage is maintained
2. **Set up alerts** — Create metric alerts for LCP p75 > 2.5s and INP p75 > 200ms
3. **Review flamegraphs** — Navigate to a sampled transaction and examine the Profile tab for CPU hotspots
4. **Audit cardinality** — Run the Discover query from Step 3 to find remaining high-cardinality names
5. **Add business measurements** — Identify 3-5 KPIs (cart value, search latency) and add `setMeasurement()` calls
6. **Server-side sampling** — Use Sentry's Dynamic Sampling UI (Settings > Performance) for rules without code deploys
