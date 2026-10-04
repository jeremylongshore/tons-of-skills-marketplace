# APM Tool Integration Reference

## Datadog + Sentry Cross-Linking

Add Datadog trace IDs to Sentry events so you can click from a Sentry error directly to the Datadog trace:

```typescript
import tracer from 'dd-trace';
import * as Sentry from '@sentry/node';

// dd-trace MUST be initialized before @sentry/node
tracer.init();

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event) {
    const span = tracer.scope().active();
    if (span) {
      const traceId = span.context().toTraceId();
      const spanId = span.context().toSpanId();
      event.tags = {
        ...event.tags,
        'dd.trace_id': traceId,
        'dd.span_id': spanId,
      };
      event.contexts = {
        ...event.contexts,
        datadog: {
          trace_url: `https://app.datadoghq.com/apm/trace/${traceId}`,
          trace_id: traceId,
          span_id: spanId,
        },
      };
    }
    return event;
  },
});
```

## New Relic + Sentry Cross-Linking

```typescript
import newrelic from 'newrelic';
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event) {
    const txn = newrelic.getTransaction();
    const traceId = txn?.traceId;
    if (traceId) {
      event.tags = {
        ...event.tags,
        'newrelic.trace_id': traceId,
      };
      event.contexts = {
        ...event.contexts,
        newrelic: {
          trace_url: `https://one.newrelic.com/distributed-tracing?traceId=${traceId}`,
          trace_id: traceId,
        },
      };
    }
    return event;
  },
});
```

## When Sentry Performance Is Enough

| Scenario | Recommendation |
|----------|---------------|
| < 5 services, frontend + backend | Sentry Performance only |
| Need infrastructure metrics (CPU, mem) | Add Datadog/New Relic agent |
| 10+ microservices with complex traces | Datadog/New Relic for tracing, Sentry for errors |
| Budget-constrained, error-focused | Sentry Performance only |
| Existing Datadog/NR investment | Keep both, cross-link via beforeSend |

## OpenTelemetry Bridge (SDK v8)

Sentry SDK v8 uses OpenTelemetry internally. Custom OTel spans are visible in Sentry automatically:

```typescript
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('my-app');
const span = tracer.startSpan('custom-operation');
// This span appears in Sentry — no extra configuration
span.end();
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
