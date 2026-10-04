# Best Practices

## Best Practices

### Sample Rate Guidelines

```typescript
const environment = process.env.NODE_ENV;

const sampleRates = {
  development: 1.0,   // 100% - capture everything
  staging: 0.5,       // 50% - good balance
  production: 0.1,    // 10% - cost efficient
};

Sentry.init({
  tracesSampleRate: sampleRates[environment] || 0.1,
});
```

### Custom Instrumentation

```typescript
// Wrap database operations
function instrumentedQuery<T>(sql: string, fn: () => Promise<T>): Promise<T> {
  const span = Sentry.getCurrentHub().getScope()?.getSpan();
  const child = span?.startChild({
    op: 'db.query',
    description: sql.substring(0, 100),
  });

  return fn()
    .then((result) => {
      child?.setStatus('ok');
      return result;
    })
    .catch((error) => {
      child?.setStatus('internal_error');
      throw error;
    })
    .finally(() => child?.finish());
}
```
