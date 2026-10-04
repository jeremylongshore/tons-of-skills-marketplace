---
name: sentry-performance-tracing
description: 'Set up performance monitoring and distributed tracing with Sentry.

  Use when implementing performance tracking, tracing requests,

  or monitoring application performance.

  Trigger with phrases like "sentry performance", "sentry tracing",

  "sentry APM", "monitor performance sentry".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(node:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- monitoring
- performance
- tracing
- spans
compatibility: Designed for Claude Code
---
# Sentry Performance Tracing

## Overview

Sentry performance monitoring captures distributed traces across your application stack, measuring latency, identifying bottlenecks, and tracking Web Vitals. The v8 SDK uses a span-based API where `Sentry.startSpan()` replaces the deprecated `startTransaction()`. Auto-instrumentation covers HTTP, database queries, and framework routes out of the box. Manual spans let you measure business-critical operations. Combined with profiling (`profilesSampleRate`), you get function-level flamegraphs attached to traces.

## Prerequisites

- Sentry SDK v8+ installed (`@sentry/node` >= 8.0.0 or `sentry-sdk` >= 2.0.0)
- `tracesSampleRate > 0` set in `Sentry.init()` — performance data is not collected at zero
- Performance monitoring enabled in your Sentry project settings (Settings > Performance)
- For distributed tracing: all participating services must have Sentry SDK initialized

## Instructions

### Step 1 — Configure Tracing and Profiling in SDK Init

Set `tracesSampleRate` to control what percentage of requests generate traces. Use `tracesSampler` for dynamic, per-endpoint sampling. Add `profilesSampleRate` to attach function-level flamegraphs to sampled transactions.

**TypeScript (`@sentry/node`):**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2, // 20% of transactions in production

  // Profiling — profiles 10% of sampled transactions
  profilesSampleRate: 0.1,

  // Dynamic sampling overrides tracesSampleRate when defined
  tracesSampler: (samplingContext) => {
    const { name, attributes } = samplingContext;

    // Drop health checks entirely — no trace data
    if (name === 'GET /health') return 0;

    // Always trace payment flows
    if (name?.includes('/api/payment')) return 1.0;

    // Higher sampling for API routes
    if (name?.startsWith('GET /api/') || name?.startsWith('POST /api/')) return 0.2;

    // Default: 5% for everything else
    return 0.05;
  },
});
```

**Python (`sentry-sdk`):**

```python
import os
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    traces_sample_rate=0.2,       # 20% of transactions
    profiles_sample_rate=0.1,     # 10% of sampled transactions get profiled

    # Dynamic sampling via traces_sampler (overrides traces_sample_rate)
    traces_sampler=lambda ctx: (
        0.0 if ctx.get("transaction_context", {}).get("name") == "GET /health"
        else 1.0 if "/api/payment" in ctx.get("transaction_context", {}).get("name", "")
        else 0.2
    ),
)
```

**Key decisions:**

- Start at `tracesSampleRate: 0.2` and adjust based on volume and budget
- `tracesSampler` takes priority when defined — `tracesSampleRate` becomes the fallback
- `profilesSampleRate` is relative to sampled transactions (0.1 means 10% of the 20% that are sampled)
- Return `0` from `tracesSampler` to explicitly drop a transaction, not `false`

### Step 2 — Create Custom Spans for Business Logic

Auto-instrumentation covers HTTP and database calls, but business-critical operations need manual spans. The v8 API provides three span creation methods for different use cases.

**`Sentry.startSpan()` — auto-ending spans (most common):**

```typescript
import * as Sentry from '@sentry/node';

const result = await Sentry.startSpan(
  {
    name: 'order.process',
    op: 'task',
    attributes: {
      'order.id': orderId,
      'order.items': items.length,
    },
  },
  async (span) => {
    // Nested spans automatically become children of the parent
    const validated = await Sentry.startSpan(
      { name: 'order.validate', op: 'validation' },
      async () => validateOrder(order)
    );

    const charged = await Sentry.startSpan(
      { name: 'payment.charge', op: 'http.client' },
      async () => chargePayment(order.total)
    );

    // Set span status based on outcome
    if (!charged.success) {
      span.setStatus({ code: 2, message: 'payment_failed' });
    }

    // Add custom measurements visible in Performance dashboard
    Sentry.setMeasurement('order.item_count', items.length, 'none');
    Sentry.setMeasurement('order.total_cents', order.total, 'none');

    return { validated, charged };
  }
);
// Span automatically ends when callback resolves or rejects
```

**`Sentry.startSpanManual()` — for spans that cross callback boundaries:**

```typescript
Sentry.startSpanManual(
  { name: 'queue.process', op: 'queue.task' },
  (span) => {
    queue.on('message', async (msg) => {
      try {
        await processMessage(msg);
        span.setStatus({ code: 1 }); // OK
      } catch (error) {
        span.setStatus({ code: 2, message: 'processing_failed' });
        Sentry.captureException(error);
      } finally {
        span.end(); // REQUIRED — must call end() manually
      }
    });
  }
);
```

**`Sentry.startInactiveSpan()` — background work without changing active context:**

```typescript
const span = Sentry.startInactiveSpan({
  name: 'cache.warmup',
  op: 'cache',
});

await warmCache(); // Other spans created here won't be children of this span

span.end();
```

**Span attributes and measurements:**

```typescript
await Sentry.startSpan(
  { name: 'search.query', op: 'db.query' },
  async (span) => {
    const start = Date.now();
    const results = await searchIndex(query);

    // Attributes — appear in span details, filterable in Sentry UI
    span.setAttribute('search.query', query);
    span.setAttribute('search.results_count', results.length);
    span.setAttribute('search.index', indexName);

    // Measurements — appear in Performance dashboard charts
    Sentry.setMeasurement('search.duration_ms', Date.now() - start, 'millisecond');
    Sentry.setMeasurement('search.result_count', results.length, 'none');

    return results;
  }
);
```

**Python equivalent:**

```python
import sentry_sdk

with sentry_sdk.start_span(op="task", name="process_order") as span:
    span.set_data("order_id", order_id)
    span.set_data("item_count", len(items))

    with sentry_sdk.start_span(op="validation", name="validate_input"):
        validate(input_data)

    with sentry_sdk.start_span(op="http.client", name="charge_payment"):
        result = charge(payment)

    if not result.success:
        span.set_status("internal_error")
```

### Step 3 — Enable Auto-Instrumentation and Distributed Tracing

SDK v8 auto-instruments most I/O without configuration. For distributed tracing across services, Sentry propagates `sentry-trace` and `baggage` headers automatically on HTTP calls. Custom propagation is needed only for non-HTTP transports (message queues, gRPC, etc.).

**Auto-instrumented integrations (Node.js v8):**

| Integration | What it traces | Enabled by |
|-------------|---------------|------------|
| `httpIntegration()` | All outbound HTTP/HTTPS requests | Default |
| `expressIntegration()` | Express route handlers and middleware | Default with Express |
| `fastifyIntegration()` | Fastify routes | Default with Fastify |
| `graphqlIntegration()` | GraphQL resolvers | Default with graphql |
| `mongoIntegration()` | MongoDB queries | Default with mongodb driver |
| `postgresIntegration()` | PostgreSQL queries (pg driver) | Default with pg |
| `mysqlIntegration()` | MySQL queries | Default with mysql2 |
| `redisIntegration()` | Redis commands | Default with ioredis/redis |
| `prismaIntegration()` | Prisma ORM queries | Default with @prisma/client |

**Express with custom middleware spans:**

```typescript
import express from 'express';
import * as Sentry from '@sentry/node';

const app = express();

// Sentry auto-instruments all Express routes
// Add custom spans for specific middleware:
app.use('/api', async (req, res, next) => {
  await Sentry.startSpan(
    { name: 'middleware.auth', op: 'middleware' },
    async () => {
      req.user = await authenticateRequest(req);
    }
  );
  next();
});

// Parameterized route names prevent cardinality explosion
// Sentry automatically uses '/api/users/:id' not '/api/users/12345'
app.get('/api/users/:id', async (req, res) => {
  const user = await Sentry.startSpan(
    { name: 'db.getUser', op: 'db.query' },
    () => db.users.findById(req.params.id)
  );
  res.json(user);
});

// Must be after all routes
Sentry.setupExpressErrorHandler(app);
```

**Django/Flask auto-instrumentation (Python):**

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.2,
    profiles_sample_rate=0.1,
)
# All Django views, middleware, and template rendering are traced automatically
```

```python
# Flask equivalent
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.2,
)
```

```python
# FastAPI equivalent
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FastApiIntegration(), StarletteIntegration()],
    traces_sample_rate=0.2,
)
```

**Distributed tracing — custom header propagation:**

When Sentry cannot automatically propagate headers (non-HTTP transports, custom fetch wrappers), extract and inject manually:

```typescript
// Service A: Extract trace headers from the active span
const activeSpan = Sentry.getActiveSpan();
const traceHeaders = {
  'sentry-trace': Sentry.spanToTraceHeader(activeSpan),
  'baggage': Sentry.spanToBaggageHeader(activeSpan),
};

// Pass headers to downstream service via HTTP, message queue, etc.
await fetch('https://service-b.internal/api/process', {
  headers: { ...traceHeaders, 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});

// Service B: Sentry SDK automatically reads sentry-trace and baggage
// from incoming request headers and continues the same trace
```

**Browser Web Vitals (`@sentry/browser`):**

The browser SDK automatically captures Core Web Vitals when tracing is enabled:

- **LCP** (Largest Contentful Paint) — loading performance
- **INP** (Interaction to Next Paint) — responsiveness (replaced FID in 2024)
- **CLS** (Cumulative Layout Shift) — visual stability
- **TTFB** (Time to First Byte) — server response time

These appear in the **Web Vitals** tab of your Sentry Performance dashboard. No additional configuration beyond `tracesSampleRate > 0` in the browser SDK.

## Output

- Distributed traces visible in Sentry Performance > Trace View as span waterfalls
- Auto-instrumented spans for HTTP, database, and framework operations
- Custom spans with attributes measuring business-critical operations
- Profiling flamegraphs attached to sampled transactions
- Web Vitals (LCP, INP, CLS, TTFB) tracked for frontend performance
- Custom measurements charted in Performance dashboard
- Cross-service traces linked via `sentry-trace` and `baggage` headers

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No transactions in Performance tab | `tracesSampleRate` is `0` or not set | Set `tracesSampleRate > 0` in `Sentry.init()` or define `tracesSampler` |
| Spans not nested correctly | Child span created outside parent callback | Call `Sentry.startSpan()` inside the parent `startSpan` callback to establish parent-child |
| High cardinality warning in Sentry UI | Dynamic values in span/transaction names | Use parameterized names (`/api/users/:id`) not literal values (`/api/users/12345`) |
| Distributed trace broken between services | `sentry-trace`/`baggage` headers not forwarded | Verify both headers are propagated in inter-service HTTP calls |
| `startSpanManual` span never ends | Missing `span.end()` call | Always call `span.end()` in a `finally` block |
| Profiling data missing | `profilesSampleRate` not set or `@sentry/profiling-node` not installed | Set `profilesSampleRate > 0` and install the profiling package |
| `tracesSampler` errors silently | Sampler function throws | Wrap sampler logic in try/catch, return a fallback rate |
| Performance data but no Web Vitals | Browser SDK not initialized or `tracesSampleRate` is 0 on client | Ensure `@sentry/browser` or `@sentry/react` is initialized with tracing |

## Examples

### TypeScript — Full Express API with Profiling

```typescript
import * as Sentry from '@sentry/node';
import express from 'express';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2,
  profilesSampleRate: 0.1,
});

const app = express();

app.post('/api/orders', async (req, res) => {
  const order = await Sentry.startSpan(
    { name: 'order.create', op: 'task', attributes: { 'order.source': 'api' } },
    async (span) => {
      const validated = await Sentry.startSpan(
        { name: 'order.validate', op: 'validation' },
        () => validateOrder(req.body)
      );

      const saved = await Sentry.startSpan(
        { name: 'order.save', op: 'db.query' },
        () => db.orders.create(validated)
      );

      await Sentry.startSpan(
        { name: 'notification.send', op: 'http.client' },
        () => notifyWarehouse(saved.id)
      );

      Sentry.setMeasurement('order.total_cents', saved.total, 'none');
      return saved;
    }
  );

  res.status(201).json(order);
});

Sentry.setupExpressErrorHandler(app);
app.listen(3000);
```

### Python — FastAPI with Custom Spans

```python
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FastApiIntegration(), StarletteIntegration()],
    traces_sample_rate=0.2,
    profiles_sample_rate=0.1,
)

app = FastAPI()

@app.post("/api/orders")
async def create_order(payload: OrderRequest):
    with sentry_sdk.start_span(op="task", name="order.create") as span:
        span.set_data("order_source", "api")

        with sentry_sdk.start_span(op="validation", name="order.validate"):
            validated = validate_order(payload)

        with sentry_sdk.start_span(op="db.query", name="order.save"):
            saved = await db.orders.create(validated)

        with sentry_sdk.start_span(op="http.client", name="notification.send"):
            await notify_warehouse(saved.id)

    return {"id": saved.id, "status": "created"}
```

## Resources

- [Set Up Tracing — Node.js](https://docs.sentry.io/platforms/javascript/guides/node/tracing/)
- [Custom Instrumentation](https://docs.sentry.io/platforms/javascript/guides/node/tracing/instrumentation/custom-instrumentation/)
- [Distributed Tracing](https://docs.sentry.io/platforms/javascript/guides/node/tracing/distributed-tracing/)
- [Python Performance Monitoring](https://docs.sentry.io/platforms/python/tracing/)
- [Profiling — Node.js](https://docs.sentry.io/platforms/javascript/guides/node/profiling/)
- [Web Vitals](https://docs.sentry.io/product/insights/web-vitals/)
- [Performance Monitoring Product Guide](https://docs.sentry.io/product/performance/)

## Next Steps

- **Alerting on performance regressions**: Configure Performance Alerts in Sentry to trigger when p95 latency exceeds thresholds or throughput drops
- **Custom dashboards**: Build dashboards in Sentry using custom measurements (`Sentry.setMeasurement()`) to track business KPIs alongside latency
- **Span sampling in high-volume services**: Use `tracesSampler` to selectively trace slow endpoints at higher rates while keeping fast endpoints low
- **Connect to error tracking**: Errors captured with `Sentry.captureException()` inside a traced span automatically link to that trace in the Sentry UI
