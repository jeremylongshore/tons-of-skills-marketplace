---
name: sentry-load-scale
description: 'Scale Sentry for high-traffic applications handling millions of events
  per day.

  Use when optimizing SDK performance at high volume, implementing adaptive sampling,

  managing quotas and costs at scale, or deploying Sentry across multi-region infrastructure.

  Trigger with phrases like "sentry high traffic", "scale sentry", "sentry millions
  events",

  "sentry high volume", "sentry quota management", "sentry load test".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(node:*), Bash(npx:*), Bash(k6:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- performance
- scaling
- high-traffic
- enterprise
compatibility: Designed for Claude Code
---
# Sentry Load & Scale

## Overview

Configure Sentry for applications processing 1M+ requests/day without sacrificing error visibility, burning through quota, or adding measurable SDK overhead. Covers adaptive sampling, connection pooling, multi-region tagging, quota management, SDK benchmarking, batch submission, load testing, and self-hosted deployment considerations.

## Prerequisites

- Application handling sustained high traffic (>10K requests/min or >1M events/day)
- Sentry organization with quota and billing access (Settings > Subscription)
- `@sentry/node` v8+ installed (`npm ls @sentry/node`)
- Performance baseline established (p50/p95/p99 latency without Sentry)
- Event volume estimates calculated per category (errors, transactions, replays, attachments)

## Instructions

### Step 1 — Implement Adaptive Sampling

Static `tracesSampleRate` wastes quota at scale because it treats a health check the same as a checkout. Replace it with a traffic-aware `tracesSampler` that adjusts rates based on endpoint criticality and current load.

**Traffic-aware tracesSampler:**

```typescript
import * as Sentry from '@sentry/node';

// Track request volume per endpoint for adaptive rate adjustment
const endpointVolume = new Map<string, { count: number; resetAt: number }>();
const WINDOW_MS = 60_000;

function getAdaptiveRate(name: string, baseRate: number): number {
  const now = Date.now();
  let entry = endpointVolume.get(name);

  if (!entry || now > entry.resetAt) {
    entry = { count: 0, resetAt: now + WINDOW_MS };
    endpointVolume.set(name, entry);
  }
  entry.count++;

  // Scale down sampling as volume increases within window
  // 0-100 req/min: full base rate
  // 100-1000: halve it
  // 1000+: quarter it
  if (entry.count > 1000) return baseRate * 0.25;
  if (entry.count > 100) return baseRate * 0.5;
  return baseRate;
}

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  tracesSampler: (samplingContext) => {
    const { name, parentSampled } = samplingContext;

    // Always respect parent decision for distributed tracing consistency
    if (parentSampled !== undefined) return parentSampled ? 1.0 : 0;

    // Tier 0: Never sample — high-frequency, zero diagnostic value
    if (name?.match(/\/(health|ready|alive|ping|metrics|favicon)/)) return 0;
    if (name?.match(/\.(css|js|png|jpg|svg|woff2?|ico)$/)) return 0;

    // Tier 1: Always sample — business-critical, low volume
    if (name?.includes('/payment') || name?.includes('/checkout')) return 1.0;
    if (name?.includes('/auth/login')) return getAdaptiveRate('auth', 0.5);

    // Tier 2: Moderate sampling — API mutations (higher signal)
    if (name?.startsWith('POST /api/')) return getAdaptiveRate(name, 0.05);
    if (name?.startsWith('PUT /api/'))  return getAdaptiveRate(name, 0.05);
    if (name?.startsWith('DELETE /api/')) return getAdaptiveRate(name, 0.05);

    // Tier 3: Light sampling — API reads
    if (name?.startsWith('GET /api/')) return getAdaptiveRate(name, 0.02);

    // Tier 4: Background jobs — sample sparingly
    if (name?.startsWith('job:') || name?.startsWith('queue:')) {
      return getAdaptiveRate(name, 0.01);
    }

    // Tier 5: Everything else — minimal baseline
    return getAdaptiveRate(name || 'default', 0.005);
  },
});
```

**Adaptive error deduplication with `beforeSend`:**

```typescript
// Reduce duplicate error volume by 90%+ while preserving first-occurrence fidelity
const errorCounts = new Map<string, number>();
const ERROR_WINDOW_MS = 60_000;

setInterval(() => errorCounts.clear(), ERROR_WINDOW_MS);

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event, hint) {
    const error = hint?.originalException;
    const key = error instanceof Error
      ? `${error.name}:${error.message?.substring(0, 100)}`
      : `unknown:${String(event.message || '').substring(0, 100)}`;

    const count = (errorCounts.get(key) || 0) + 1;
    errorCounts.set(key, count);

    // First occurrence: always send with full context
    if (count === 1) return event;

    // 2-10: send every 5th (capture ramp-up pattern)
    if (count <= 10) return count % 5 === 0 ? event : null;

    // 11-100: send every 25th (confirm still happening)
    if (count <= 100) return count % 25 === 0 ? event : null;

    // 100+: send every 100th (volume indicator only)
    return count % 100 === 0 ? event : null;
  },
});
```

### Step 2 — Optimize SDK for Minimal Overhead

At high throughput, every byte and every millisecond of SDK processing matters. This configuration reduces memory footprint, payload size, and CPU time.

**Lean SDK initialization:**

```typescript
import * as Sentry from '@sentry/node';
import os from 'node:os';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'production',
  release: `${process.env.SERVICE_NAME}@${process.env.VERSION || 'unknown'}`,

  // --- Memory reduction ---
  maxBreadcrumbs: 15,          // Down from 100 default; saves ~85KB/scope
  maxValueLength: 200,         // Truncate long string values

  // --- Disable high-overhead integrations ---
  integrations: (defaults) => defaults.filter(i =>
    !['Console', 'ContextLines'].includes(i.name)
  ),

  // --- No profiling at high scale (use dedicated APM if needed) ---
  profilesSampleRate: 0,

  // --- Transport tuning for high-throughput ---
  transportOptions: {
    bufferSize: 100,           // Default 64; absorbs traffic spikes
  },

  // --- Context size limiter ---
  beforeSend(event) {
    // Truncate oversized contexts to prevent payload bloat
    if (event.contexts) {
      for (const [key, ctx] of Object.entries(event.contexts)) {
        const str = JSON.stringify(ctx);
        if (str.length > 2000) {
          event.contexts[key] = { _truncated: true, originalSize: str.length };
        }
      }
    }

    // Strip headers that add bulk without diagnostic value
    if (event.request?.headers) {
      const keep = ['content-type', 'accept', 'user-agent', 'x-request-id'];
      event.request.headers = Object.fromEntries(
        Object.entries(event.request.headers)
          .filter(([k]) => keep.includes(k.toLowerCase()))
      );
    }

    return event;
  },

  // --- Multi-region tags for infrastructure visibility ---
  serverName: process.env.HOSTNAME || process.env.POD_NAME || os.hostname(),
  initialScope: {
    tags: {
      region: process.env.AWS_REGION || process.env.GCP_REGION || 'unknown',
      cluster: process.env.K8S_CLUSTER || 'default',
      pod: process.env.POD_NAME || 'unknown',
      service: process.env.SERVICE_NAME || 'unknown',
    },
  },
});
```

**Graceful shutdown ensuring event delivery:**

```typescript
import * as Sentry from '@sentry/node';

async function shutdown(signal: string) {
  console.log(`${signal} received — flushing Sentry events`);

  // Stop accepting new requests
  server.close();

  // Flush all pending events (2s timeout prevents hanging deploys)
  const flushed = await Sentry.close(2000);
  if (!flushed) {
    console.warn('Sentry flush timed out — some events may be lost');
  }

  process.exit(0);
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT',  () => shutdown('SIGINT'));
```

### Step 3 — Manage Quotas, Test Under Load, and Plan for Scale

**Quota management and reserved volume pricing:**

```
Application: 10M requests/day, 0.1% error rate, @sentry/node v8

Error events (with adaptive beforeSend):
  Raw errors:     10M x 0.001 = 10,000/day
  After dedup:    ~1,000/day (90% reduction)        = 30K/month

Transaction events (with tiered tracesSampler):
  Health/static:  0% of 4M    = 0
  Payment (T1):   100% of 5K  = 5,000/day
  POST API (T2):  5% of 500K  = 25,000/day
  GET API (T3):   2% of 5M    = 100,000/day
  Other (T5):     0.5% of 500K = 2,500/day
  Total:                        ~132K/day            = 4M/month

Sentry Business plan ($26/mo base):
  Errors:       30K included in base plan
  Transactions: 100K included, overage 3.9M x $0.000025 = ~$97/mo
  Estimated total: ~$123/month for 10M requests/day

Reserved volume (if predictable traffic):
  5M txns/mo reserved = $80/mo (vs $97 on-demand)
  Saves ~$17/mo, locks in price for 12 months
  → Total: ~$106/month
```

**SDK overhead benchmarks:**

```typescript
// Measure SDK initialization cost
const initStart = performance.now();
Sentry.init({ /* ... */ });
const initMs = performance.now() - initStart;
console.log(`Sentry.init: ${initMs.toFixed(1)}ms`);
// Expected: 5-15ms (Node.js), acceptable <50ms

// Measure per-request overhead with Sentry vs without
import { performance, PerformanceObserver } from 'node:perf_hooks';

async function benchmarkOverhead(iterations: number = 1000) {
  // Baseline: request without Sentry instrumentation
  const baseStart = performance.now();
  for (let i = 0; i < iterations; i++) {
    await handleRequest({ path: '/api/test', method: 'GET' });
  }
  const baseMs = (performance.now() - baseStart) / iterations;

  // Instrumented: request with Sentry span
  const sentryStart = performance.now();
  for (let i = 0; i < iterations; i++) {
    await Sentry.startSpan(
      { name: 'GET /api/test', op: 'http.server' },
      () => handleRequest({ path: '/api/test', method: 'GET' })
    );
  }
  const sentryMs = (performance.now() - sentryStart) / iterations;

  console.log(`Baseline: ${baseMs.toFixed(3)}ms/req`);
  console.log(`With Sentry: ${sentryMs.toFixed(3)}ms/req`);
  console.log(`Overhead: ${(sentryMs - baseMs).toFixed(3)}ms (${(((sentryMs - baseMs) / baseMs) * 100).toFixed(1)}%)`);
  // Healthy: <0.5ms overhead per request, <2% CPU impact
}
```

**Load testing Sentry integration with k6:**

```javascript
// k6-sentry-load-test.js
// Run: k6 run --vus 100 --duration 5m k6-sentry-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('sentry_errors_captured');
const latencyOverhead = new Trend('sentry_latency_overhead_ms');

export const options = {
  stages: [
    { duration: '1m', target: 50 },    // Ramp up
    { duration: '3m', target: 200 },   // Sustained load
    { duration: '1m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // p95 under 500ms with Sentry
    sentry_latency_overhead_ms: ['p(95)<5'], // Sentry adds <5ms at p95
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  // Normal traffic: API reads (high volume, low sample rate)
  const readRes = http.get(`${BASE_URL}/api/products`);
  check(readRes, { 'GET 200': (r) => r.status === 200 });

  // Track overhead via server timing header (if exposed)
  const sentryMs = readRes.headers['Server-Timing']?.match(/sentry;dur=(\d+\.?\d*)/);
  if (sentryMs) latencyOverhead.add(parseFloat(sentryMs[1]));

  // Occasional writes (lower volume, higher sample rate)
  if (Math.random() < 0.1) {
    const writeRes = http.post(`${BASE_URL}/api/orders`, JSON.stringify({
      items: [{ sku: 'TEST-001', qty: 1 }],
    }), { headers: { 'Content-Type': 'application/json' } });
    check(writeRes, { 'POST 201': (r) => r.status === 201 });
  }

  // Trigger errors (verify Sentry captures under load)
  if (Math.random() < 0.01) {
    const errRes = http.get(`${BASE_URL}/api/nonexistent-route`);
    errorRate.add(errRes.status === 404);
  }

  sleep(0.1);
}
```

**Background worker batch patterns:**

```typescript
import * as Sentry from '@sentry/node';

// For queue workers processing millions of jobs/day
async function processJobBatch(jobs: Job[]) {
  // Group jobs for batch-level tracing instead of per-job spans
  return Sentry.startSpan(
    {
      name: `batch.${jobs[0]?.type || 'unknown'}`,
      op: 'queue.batch',
      attributes: { 'batch.size': jobs.length },
    },
    async () => {
      const results = { success: 0, failed: 0 };

      for (const job of jobs) {
        try {
          await Sentry.withScope(async (scope) => {
            scope.setTag('job.type', job.type);
            scope.setTag('job.queue', job.queue);
            scope.setContext('job', {
              id: job.id,
              attempts: job.attempts,
            });
            await executeJob(job);
            results.success++;
          });
        } catch (error) {
          results.failed++;
          Sentry.captureException(error, {
            tags: { 'job.id': job.id, 'job.type': job.type },
            level: job.attempts >= 3 ? 'error' : 'warning',
          });
        }
      }

      Sentry.setMeasurement('batch.success_rate',
        results.success / jobs.length, 'ratio');
      return results;
    }
  );
}

// Periodic flush for long-running workers (don't rely on process exit)
setInterval(async () => {
  await Sentry.flush(2000);
}, 30_000);
```

**Self-hosted Sentry for enterprise (>100M events/month):**

Key tuning for self-hosted (`docker-compose.override.yml` on top of [getsentry/self-hosted](https://github.com/getsentry/self-hosted)):

- Relay: `RELAY_PROCESSING_MAX_RATE: 50000`, `RELAY_UPSTREAM_MAX_CONNECTIONS: 200`
- Kafka: `KAFKA_NUM_PARTITIONS: 32` (match to consumer count)
- Snuba: 4+ consumer replicas for Clickhouse ingestion parallelism
- Clickhouse: 16G+ RAM, dedicated SSD volumes

```
Self-hosted vs SaaS break-even:
  SaaS at 100M events/month:     ~$2,500/mo (Business plan + overage)
  Self-hosted (3x r6g.2xlarge):  ~$1,200/mo infra + $800/mo ops (0.25 FTE)
  Break-even: ~50M events/month
  → Use SaaS up to 50M events; evaluate self-hosted above that
```

## Output

- Adaptive sampling reducing duplicate error volume by 90%+ while preserving first-occurrence fidelity
- Traffic-aware `tracesSampler` with 5 tiers adjusting dynamically based on endpoint volume
- SDK memory and CPU footprint minimized (15 breadcrumbs, truncated contexts, filtered headers)
- Connection pooling via persistent HTTPS agent for efficient event submission
- Multi-region infrastructure tags for filtering by region/cluster/pod in Sentry dashboard
- Cost model with reserved volume pricing showing $106/month for 10M requests/day
- k6 load test script validating Sentry overhead stays under 5ms at p95
- Batch job processing pattern with scope isolation and periodic flush
- Self-hosted vs SaaS break-even analysis for enterprise decision-making

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Events silently dropped | SDK buffer full during traffic spike | Increase `transportOptions.bufferSize` to 200+, verify network to Sentry ingest |
| 429 rate limit from Sentry | Quota exhausted or spike protection triggered | Enable spike protection in Settings > Subscription, reduce sample rates |
| Memory growing linearly over time | Breadcrumb or scope accumulation | Reduce `maxBreadcrumbs`, verify `withScope` is used (not `configureScope`) |
| Lost events on deploy/restart | No `Sentry.close()` in shutdown handler | Add SIGTERM/SIGINT handlers calling `Sentry.close(2000)` |
| Distributed traces broken at scale | Mixed sampling decisions across services | Always check `parentSampled` first in `tracesSampler` |
| Clickhouse OOM on self-hosted | Insufficient memory for event volume | Allocate 16G+ RAM, increase Snuba consumer replicas |
| k6 shows >5ms Sentry overhead | Too many integrations or large payloads | Disable Console/ContextLines integrations, reduce `maxValueLength` |
| Quota burn from replay/attachments | Replays not rate-limited separately | Set `replaysSessionSampleRate: 0.01` and `replaysOnErrorSampleRate: 0.1` |

## Examples

**Minimal high-scale init (copy-paste ready):**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: `${process.env.SERVICE_NAME}@${process.env.VERSION}`,
  maxBreadcrumbs: 15,
  maxValueLength: 200,
  profilesSampleRate: 0,
  tracesSampler: ({ name, parentSampled }) => {
    if (parentSampled !== undefined) return parentSampled ? 1.0 : 0;
    if (name?.match(/\/(health|ping|metrics)/)) return 0;
    if (name?.includes('/payment')) return 1.0;
    if (name?.startsWith('POST /api/')) return 0.05;
    return 0.005;
  },
});
```

**Verify sampling is working as expected:**

```typescript
// Add to non-production environments temporarily
Sentry.init({
  // ... config ...
  tracesSampler: (ctx) => {
    const rate = calculateRate(ctx); // your logic
    if (process.env.DEBUG_SENTRY === 'true') {
      console.log(`[sentry] ${ctx.name} → rate=${rate}`);
    }
    return rate;
  },
});
```

## Resources

- [Quota Management](https://docs.sentry.io/pricing/quotas/) — spike protection, rate limits, reserved volume
- [Sampling Configuration](https://docs.sentry.io/platforms/javascript/configuration/sampling/) — tracesSampler API reference
- [Transport Configuration](https://docs.sentry.io/platforms/javascript/configuration/transports/) — custom transport, buffer size
- [Self-Hosted Sentry](https://develop.sentry.dev/self-hosted/) — installation and scaling guide
- [Pricing Calculator](https://sentry.io/pricing/) — estimate costs by event volume
- [SDK Performance Overhead](https://docs.sentry.io/platforms/javascript/performance/) — benchmarks and best practices

## Next Steps

- Run the k6 load test against staging to establish your baseline Sentry overhead
- Set up Sentry Spike Protection (Settings > Subscription > Spike Protection) before going to production
- Configure server-side sampling rules in Sentry Dynamic Sampling (Project Settings > Performance) to complement client-side `tracesSampler`
- Create a Sentry dashboard with widgets for: events/hour by category, quota usage %, p95 SDK overhead
- Review the `sentry-cost-tuning` skill for detailed quota optimization strategies
