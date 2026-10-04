---
name: sentry-observability
description: "Integrate Sentry with your observability stack \u2014 logging, metrics,\
  \ APM, and dashboards.\nUse when connecting Sentry to winston/pino/structlog, correlating\
  \ errors with business\nmetrics, deciding between Sentry performance and Datadog/New\
  \ Relic, building Sentry\nDiscover dashboards, or linking events to external tools\
  \ via extra context.\nTrigger: \"sentry observability\", \"sentry logging\", \"\
  sentry metrics\", \"sentry grafana\",\n\"sentry datadog correlation\", \"sentry\
  \ discover dashboard\".\n"
allowed-tools: Read, Write, Edit, Grep, Bash(node:*), Bash(npx:*), Bash(pip:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- observability
- logging
- metrics
- apm
- grafana
- opentelemetry
compatibility: Designed for Claude Code
---
# Sentry Observability Integration

## Overview

Wire Sentry into your logging, metrics, APM, and dashboard toolchain so every error carries full context and every metric correlates back to root-cause events. This skill covers three integration layers: structured logging (winston, pino, structlog) with Sentry event ID correlation, business metrics with error-rate tracking, and cross-tool linking via Sentry Discover, Grafana webhooks, and APM tools.

See also: [Logging integration details](references/logging-integration.md) | [Metrics patterns](references/metrics-integration.md) | [APM tool cross-linking](references/apm-tool-integration.md)

## Prerequisites

- Sentry SDK v8+ installed (`@sentry/node` for Node.js, `sentry-sdk` for Python)
- At least one structured logger configured (winston, pino, or structlog)
- Sentry project DSN available in environment (`SENTRY_DSN`)
- Dashboard platform accessible (Sentry Discover, Grafana, or Datadog)
- Alert routing strategy decided (who gets paged, where warnings go)

## Instructions

### Step 1 — Attach Sentry Event IDs to Structured Logs

The core pattern: every log line that triggers a Sentry event carries the event ID, and every Sentry event carries the log context. This creates a two-way link between your log aggregator and Sentry.

**Winston (Node.js) — custom transport:**

```typescript
import winston from 'winston';
import * as Sentry from '@sentry/node';

class SentryTransport extends winston.Transport {
  log(info: any, callback: () => void) {
    setImmediate(callback);

    if (info.level === 'error' || info.level === 'fatal') {
      const error = info.error instanceof Error
        ? info.error
        : new Error(info.message);

      Sentry.withScope((scope) => {
        scope.setTag('logger', 'winston');
        scope.setContext('log_entry', {
          level: info.level,
          timestamp: info.timestamp,
          service: info.service,
        });
        const eventId = Sentry.captureException(error);
        info.sentry_event_id = eventId;
        info.sentry_url = `https://${process.env.SENTRY_ORG}.sentry.io/issues/?query=${eventId}`;
      });
    }
  }
}

const logger = winston.createLogger({
  defaultMeta: { service: 'api-gateway' },
  transports: [
    new winston.transports.Console({ format: winston.format.json() }),
    new SentryTransport(),
  ],
});
```

**Pino (Node.js) — hooks pattern:**

```typescript
import pino from 'pino';
import * as Sentry from '@sentry/node';

const logger = pino({
  hooks: {
    logMethod(inputArgs, method, level) {
      if (level >= 50) { // 50 = error, 60 = fatal
        const [obj, msg] = typeof inputArgs[0] === 'object'
          ? [inputArgs[0], inputArgs[1]]
          : [{}, inputArgs[0]];

        Sentry.withScope((scope) => {
          scope.setTag('logger', 'pino');
          const eventId = Sentry.captureException(
            obj.err instanceof Error ? obj.err : new Error(String(msg))
          );
          if (typeof inputArgs[0] === 'object') {
            inputArgs[0].sentry_event_id = eventId;
          }
        });
      }
      return method.apply(this, inputArgs);
    },
  },
});
```

For Python structlog integration, see [logging-integration.md](references/logging-integration.md).

**Request ID correlation middleware:**

```typescript
import { randomUUID } from 'crypto';
import * as Sentry from '@sentry/node';

app.use((req, res, next) => {
  const requestId = (req.headers['x-request-id'] as string) || randomUUID();
  req.requestId = requestId;
  res.setHeader('x-request-id', requestId);
  Sentry.setTag('request_id', requestId);
  req.log = logger.child({ requestId, path: req.path });
  next();
});
```

### Step 2 — Correlate Errors with Business Metrics and APM

Connect Sentry events to your metrics pipeline and decide when Sentry performance monitoring is sufficient versus when to add Datadog or New Relic.

**Sentry custom metrics (built-in, no extra tools):**

```typescript
import * as Sentry from '@sentry/node';

// Counter — track error rates alongside business events
Sentry.metrics.increment('checkout.attempted', 1, {
  tags: { payment_provider: 'stripe', plan: 'enterprise' },
});

Sentry.metrics.increment('checkout.failed', 1, {
  tags: { payment_provider: 'stripe', failure_reason: 'timeout' },
});

// Distribution — track latency with error correlation
Sentry.metrics.distribution('api.response_time', responseTimeMs, {
  tags: { endpoint: '/api/orders', status_code: String(res.statusCode) },
  unit: 'millisecond',
});

// Gauge — track queue depth, connection pool size
Sentry.metrics.gauge('db.pool.active', pool.activeCount, {
  tags: { database: 'primary' },
});

// Set — track unique affected users during incidents
Sentry.metrics.set('incident.affected_users', userId, {
  tags: { incident: 'payment-outage-2026-03' },
});
```

For Prometheus dual-write patterns, see [metrics-integration.md](references/metrics-integration.md).

**When to use Sentry performance vs Datadog/New Relic:**

| Scenario | Use Sentry Performance | Use Datadog/New Relic |
|----------|----------------------|----------------------|
| Frontend + backend in one view | Yes — unified error + perf traces | Overkill if Sentry covers your stack |
| Infrastructure metrics (CPU, memory) | No — Sentry does not collect infra | Yes — native host agent collection |
| 100+ custom metric series | Limited query constraints | Yes — built for high-cardinality |
| Budget-constrained, < 5 services | Yes — one tool, one bill | Unnecessary cost |

**Datadog + Sentry cross-linking via `beforeSend`:**

```typescript
import tracer from 'dd-trace';
import * as Sentry from '@sentry/node';

// dd-trace MUST be initialized before @sentry/node
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event) {
    const span = tracer.scope().active();
    if (span) {
      const traceId = span.context().toTraceId();
      event.tags = { ...event.tags, 'dd.trace_id': traceId };
      event.contexts = {
        ...event.contexts,
        datadog: {
          trace_url: `https://app.datadoghq.com/apm/trace/${traceId}`,
          trace_id: traceId,
        },
      };
    }
    return event;
  },
});
```

For New Relic correlation patterns, see [apm-tool-integration.md](references/apm-tool-integration.md).

### Step 3 — Build Dashboards and Connect External Tools

Use Sentry Discover for error analytics, set up Grafana webhooks for unified dashboards, and link Sentry events to external tools via `setContext`.

**Linking all tools via `Sentry.setContext('monitoring', ...)`:**

```typescript
import * as Sentry from '@sentry/node';

function setMonitoringContext(req: Request) {
  const traceId = Sentry.getActiveSpan()?.spanContext().traceId;
  const spanId = Sentry.getActiveSpan()?.spanContext().spanId;
  const requestId = req.headers['x-request-id'] as string || crypto.randomUUID();

  // setContext creates a named section in the Sentry event sidebar
  Sentry.setContext('monitoring', {
    traceId,
    spanId,
    requestId,
    grafana_dashboard: `https://grafana.example.com/d/abc123?var-trace_id=${traceId}`,
    kibana_logs: `https://kibana.example.com/app/logs?query=request_id:${requestId}`,
    datadog_trace: traceId
      ? `https://app.datadoghq.com/apm/trace/${traceId}`
      : undefined,
  });

  Sentry.setTag('request_id', requestId);
  Sentry.setTag('trace_id', traceId || 'none');
  Sentry.setTag('deployment', process.env.DEPLOYMENT_ID || 'unknown');
}

app.use((req, res, next) => {
  setMonitoringContext(req);
  next();
});
```

**Grafana integration via Sentry webhooks:**

Configure in Settings > Integrations > Internal Integrations. Point the webhook URL at a receiver that transforms Sentry events into Grafana annotations:

```typescript
// Receive Sentry webhook, create Grafana annotation
app.post('/sentry-to-grafana', async (req, res) => {
  const { event } = req.body;
  if (!event) return res.status(200).send('ignored');

  await fetch(`${process.env.GRAFANA_URL}/api/annotations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.GRAFANA_API_KEY}`,
    },
    body: JSON.stringify({
      dashboardUID: process.env.GRAFANA_DASHBOARD_UID,
      panelId: 1,
      time: new Date(event.datetime).getTime(),
      tags: ['sentry', event.level, event.project],
      text: `**${event.title}**\nLevel: ${event.level}\nView in Sentry`,
    }),
  });

  res.status(201).json({ status: 'annotation_created' });
});
```

**Alert routing across tools:**

```
Issue Alert: "Critical Production Error"
  When: An event is first seen
  If: level is fatal AND environment is production
  Then: PagerDuty (Critical) + #alerts-critical Slack + Grafana annotation
  Frequency: Once per issue

Metric Alert: "Error Rate Spike"
  When: Error count > 50 in 5 minutes
  Then: PagerDuty (High) + #alerts-production Slack + webhook to Grafana
  Resolve: Error count < 5 for 10 minutes

Metric Alert: "Latency Regression"
  When: p95(transaction.duration) for /api/* > 2000ms for 10 minutes
  Then: #alerts-performance Slack + JIRA ticket via webhook
  Resolve: p95 < 1000ms for 15 minutes
```

## Output

After completing these steps you will have:

- Winston/pino/structlog forwarding errors to Sentry with event IDs stamped into log lines
- Sentry custom metrics (counters, gauges, distributions, sets) tracking business KPIs
- `beforeSend` hooks linking Sentry events to Datadog traces and New Relic transactions
- `Sentry.setContext('monitoring', { traceId, spanId })` linking every event to external tool URLs
- Grafana annotations created from Sentry webhooks on infrastructure dashboards
- Tiered alert routing: fatal errors page on-call, warnings go to Slack, latency issues create tickets

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Sentry event IDs missing from logs | Transport/processor not wired up | Verify `SentryTransport` is in Winston transports or `sentry_processor` is in structlog chain |
| `beforeSend` silently dropping events | Handler throws or returns `undefined` | Wrap `beforeSend` in try/catch, always return `event` on error paths |
| Grafana annotations not appearing | Webhook URL wrong or API key expired | Test webhook with `curl -X POST` first; check Grafana API key has annotation write |
| Datadog trace IDs not matching | `dd-trace` not initialized before Sentry | Import and init `dd-trace` before `@sentry/node` |
| Sentry metrics not visible | Feature not enabled on plan | Custom metrics require Business plan or higher |
| Duplicate events from logger | SDK auto-capture and transport both fire | Use `beforeSend` to deduplicate, or disable auto-capture for handled errors |
| Webhook payload format changed | Sentry API version upgrade | Pin webhook to API v0; validate payload shape in receiver |

## Examples

**Example 1 — Full-stack request tracing with log correlation**

Request: "Every error in our Express API should show up in both our log aggregator and Sentry with cross-links."

```typescript
import express from 'express';
import pino from 'pino';
import * as Sentry from '@sentry/node';
import { randomUUID } from 'crypto';

Sentry.init({ dsn: process.env.SENTRY_DSN, tracesSampleRate: 0.1 });
const logger = pino({ level: 'info' });
const app = express();

app.use((req, res, next) => {
  const requestId = (req.headers['x-request-id'] as string) || randomUUID();
  req.requestId = requestId;
  res.setHeader('x-request-id', requestId);
  Sentry.setTag('request_id', requestId);
  req.log = logger.child({ requestId, path: req.path, method: req.method });
  next();
});

app.get('/api/orders/:id', async (req, res) => {
  try {
    const order = await db.orders.findById(req.params.id);
    if (!order) {
      req.log.warn({ orderId: req.params.id }, 'Order not found');
      return res.status(404).json({ error: 'Not found' });
    }
    res.json(order);
  } catch (error) {
    Sentry.withScope((scope) => {
      scope.setContext('request', { params: req.params, requestId: req.requestId });
      const eventId = Sentry.captureException(error);
      req.log.error({
        err: error,
        sentry_event_id: eventId,
        sentry_url: `https://sentry.io/issues/?query=${eventId}`,
      }, 'Order fetch failed');
    });
    res.status(500).json({ error: 'Internal error', request_id: req.requestId });
  }
});

Sentry.setupExpressErrorHandler(app);
```

**Example 2 — Grafana dashboard with Sentry error annotations**

Request: "Show Sentry errors as annotations on our Grafana latency dashboard."

Result: Create a Sentry internal integration (Settings > Integrations > Internal Integrations) with a webhook URL pointing to your annotation receiver. The receiver transforms Sentry event payloads into Grafana annotation API calls. Error events appear as vertical markers on latency graphs with clickable links back to the Sentry issue.

See [examples.md](references/examples.md) for additional integration patterns.

## Resources

- [Sentry + OpenTelemetry](https://docs.sentry.io/platforms/javascript/guides/node/tracing/instrumentation/opentelemetry/) — SDK v8 OTel bridge
- [Custom Metrics](https://docs.sentry.io/product/explore/metrics/) — counters, gauges, distributions, sets
- [Sentry Discover Queries](https://docs.sentry.io/product/explore/discover-queries/) — custom event analytics
- [Webhooks Integration](https://docs.sentry.io/organization/integrations/integration-platform/webhooks/) — outbound event webhooks
- [PagerDuty Integration](https://docs.sentry.io/organization/integrations/notification-incidents/pagerduty/) — incident routing
- [Slack Integration](https://docs.sentry.io/organization/integrations/notification-incidents/slack/) — alert channels

## Next Steps

- Configure sentry-performance-tracing for transaction-level instrumentation
- Set up sentry-release-management to correlate deploys with error regressions
- Add sentry-ci-integration to catch regressions before they reach production
- Review sentry-cost-tuning to manage event volume as observability coverage expands
