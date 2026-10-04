# Performance Data Missing

## Performance Data Missing

### Check Transaction Creation

```typescript
// Verify transactions are being created
const transaction = Sentry.startTransaction({
  name: 'test-transaction',
  op: 'test',
});

console.log('Transaction created:', transaction.traceId);

// Don't forget to finish!
transaction.finish();
console.log('Transaction finished');
```

### Check Trace Sampling

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Ensure traces are sampled
  tracesSampleRate: 1.0,

  // Or debug sampler
  tracesSampler: (ctx) => {
    console.log('Trace sampler called:', ctx.transactionContext);
    return 1.0;
  },
});
```

### Verify Integration Setup

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,

  integrations: [
    // HTTP tracing
    new Sentry.Integrations.Http({ tracing: true }),

    // Express tracing
    new Sentry.Integrations.Express({ app }),
  ],
});

// Verify integrations loaded
const client = Sentry.getCurrentHub().getClient();
console.log('Integrations:', client?.getIntegration);
```
