# Metrics Integration Reference

## Sentry Custom Metrics (SDK v8)

Four metric types available:

```typescript
import * as Sentry from '@sentry/node';

// Counter — track occurrences, error rates, throughput
Sentry.metrics.increment('checkout.attempted', 1, {
  tags: { payment_provider: 'stripe', plan: 'enterprise' },
});

// Distribution — latency, response sizes (supports percentiles)
Sentry.metrics.distribution('api.response_time', responseTimeMs, {
  tags: { endpoint: '/api/orders', status_code: '200' },
  unit: 'millisecond',
});

// Gauge — current values (pool sizes, queue depth)
Sentry.metrics.gauge('db.pool.active', pool.activeCount, {
  tags: { database: 'primary' },
});

// Set — unique counts (affected users, unique errors)
Sentry.metrics.set('incident.affected_users', userId, {
  tags: { incident: 'payment-outage-2026-03' },
});
```

## Prometheus Dual-Write

Write to both Prometheus and Sentry for infrastructure + error correlation:

```typescript
import { Counter, Histogram } from 'prom-client';
import * as Sentry from '@sentry/node';

const httpErrors = new Counter({
  name: 'http_errors_total',
  help: 'HTTP errors with Sentry correlation',
  labelNames: ['method', 'path', 'status'],
});

const requestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Request duration',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
});

// Middleware captures both Prometheus metrics and Sentry events
app.use((req, res, next) => {
  const end = requestDuration.startTimer();
  res.on('finish', () => {
    const labels = {
      method: req.method,
      path: req.route?.path || req.path,
      status: String(res.statusCode),
    };
    end(labels);
    if (res.statusCode >= 500) {
      httpErrors.inc(labels);
    }
  });
  next();
});
```

## When to Use Sentry Metrics vs External Tools

| Sentry Metrics | Prometheus/Grafana | Datadog Metrics |
|----------------|-------------------|-----------------|
| Error-correlated business metrics | Infrastructure (CPU, memory, disk) | Full-stack with APM correlation |
| Small metric cardinality (< 100 series) | High cardinality (1000s of series) | High cardinality with auto-tagging |
| No extra infrastructure needed | Requires Prometheus server | Requires Datadog agent |
| Integrated with Sentry alerts | Grafana alerting | Datadog monitors |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
