# Sample Rate Optimization

## Sample Rate Optimization

### Dynamic Sampling

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  tracesSampler: (samplingContext) => {
    const { transactionContext, parentSampled } = samplingContext;
    const name = transactionContext.name;

    // Always trace if parent was sampled (distributed tracing)
    if (parentSampled !== undefined) return parentSampled;

    // Skip health checks entirely
    if (name.includes('/health') || name.includes('/ready')) {
      return 0;
    }

    // Lower rate for high-volume endpoints
    if (name.includes('/api/events')) return 0.01;

    // Higher rate for critical paths
    if (name.includes('/checkout') || name.includes('/payment')) {
      return 0.5;
    }

    // Default rate
    return 0.1;
  },
});
```

### Environment-Based Rates

```typescript
const sampleRates: Record<string, number> = {
  development: 1.0,
  staging: 0.5,
  production: 0.1,
};

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: sampleRates[process.env.NODE_ENV] || 0.1,
});
```
