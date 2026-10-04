# High-Volume Sampling Strategies

## High-Volume Sampling Strategies

### Adaptive Sampling

```typescript
import * as Sentry from '@sentry/node';

// Track recent error counts
const errorCounts = new Map<string, number>();
const WINDOW_MS = 60000; // 1 minute window

function getAdaptiveSampleRate(errorType: string): number {
  const count = errorCounts.get(errorType) || 0;

  // High volume = low sample rate
  if (count > 1000) return 0.001; // 0.1%
  if (count > 100) return 0.01;   // 1%
  if (count > 10) return 0.1;     // 10%
  return 1.0;                      // 100%
}

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event) {
    const errorType = event.exception?.values?.[0]?.type || 'unknown';

    // Update counter
    errorCounts.set(errorType, (errorCounts.get(errorType) || 0) + 1);

    // Sample based on frequency
    const sampleRate = getAdaptiveSampleRate(errorType);
    if (Math.random() > sampleRate) {
      return null; // Drop event
    }

    return event;
  },
});

// Reset counters periodically
setInterval(() => errorCounts.clear(), WINDOW_MS);
```

### Tiered Transaction Sampling

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  tracesSampler: (ctx) => {
    const name = ctx.transactionContext.name;

    // Critical paths: higher sampling
    if (name.includes('/checkout')) return 0.1;
    if (name.includes('/payment')) return 0.1;

    // High-volume endpoints: very low sampling
    if (name.includes('/api/events')) return 0.0001; // 0.01%
    if (name.includes('/health')) return 0;

    // Default: low sampling
    return 0.001; // 0.1%
  },
});
```
