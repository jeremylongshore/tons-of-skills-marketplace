# Reduce Transaction Volume

## Reduce Transaction Volume

### Aggressive Sampling

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Low sample rate in production
  tracesSampleRate: 0.01, // 1%

  // Or dynamic sampling
  tracesSampler: (ctx) => {
    // Never trace health checks
    if (ctx.transactionContext.name.includes('health')) return 0;

    // Very low rate for common endpoints
    if (ctx.transactionContext.name.includes('/api/')) return 0.001;

    return 0.01;
  },
});
```

### Skip Unimportant Transactions

```typescript
tracesSampler: (ctx) => {
  const name = ctx.transactionContext.name;

  // Skip static assets
  if (/\.(js|css|png|jpg|svg)$/.test(name)) return 0;

  // Skip bots
  const userAgent = ctx.request?.headers?.['user-agent'];
  if (userAgent?.includes('bot')) return 0;

  return 0.05;
},
```
