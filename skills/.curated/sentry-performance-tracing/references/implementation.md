## Implementation Guide

### Step 1: Enable Performance Monitoring

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Enable performance monitoring
  tracesSampleRate: 1.0, // 100% in dev, lower in prod

  // Or use sampling function
  tracesSampler: (samplingContext) => {
    if (samplingContext.transactionContext.name.includes('health')) {
      return 0; // Don't trace health checks
    }
    return 0.1; // 10% sample rate
  },

  // Enable profiling (optional)
  profilesSampleRate: 0.1,
});
```

### Step 2: Create Transactions

```typescript
// Automatic transactions for HTTP (enabled by default)
// Manual transactions for custom operations

const transaction = Sentry.startTransaction({
  name: 'processOrder',
  op: 'task',
  data: { orderId: order.id },
});

try {
  await processOrder(order);
} finally {
  transaction.finish();
}
```

### Step 3: Add Spans

```typescript
const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();

if (transaction) {
  const span = transaction.startChild({
    op: 'db.query',
    description: 'SELECT * FROM users',
  });

  try {
    const result = await db.query('SELECT * FROM users');
    span.setData('row_count', result.length);
  } finally {
    span.finish();
  }
}
```

### Step 4: Distributed Tracing

```typescript
// Client side - include trace headers
const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();
const traceHeaders = transaction?.toTraceparent();

fetch('/api/endpoint', {
  headers: {
    'sentry-trace': traceHeaders,
    'baggage': Sentry.getBaggage(),
  },
});

// Server side - continue trace
const transaction = Sentry.continueTrace(
  { sentryTrace: req.headers['sentry-trace'], baggage: req.headers['baggage'] },
  (ctx) => Sentry.startTransaction({ ...ctx, name: 'api.endpoint', op: 'http.server' })
);
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
