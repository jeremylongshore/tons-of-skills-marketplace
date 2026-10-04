# Distributed Tracing Architecture

## Distributed Tracing Architecture

### Service-to-Service

```typescript
// Outgoing request (client)
async function callService(url: string, data: unknown) {
  const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Propagate trace context
  if (transaction) {
    headers['sentry-trace'] = transaction.toTraceparent();
    headers['baggage'] = Sentry.getBaggage()?.toString() || '';
  }

  return fetch(url, { method: 'POST', headers, body: JSON.stringify(data) });
}

// Incoming request (server)
app.use((req, res, next) => {
  const transaction = Sentry.continueTrace(
    {
      sentryTrace: req.headers['sentry-trace'],
      baggage: req.headers['baggage'],
    },
    (ctx) =>
      Sentry.startTransaction({
        ...ctx,
        name: `${req.method} ${req.path}`,
        op: 'http.server',
      })
  );

  Sentry.getCurrentHub().configureScope((scope) => {
    scope.setSpan(transaction);
  });

  res.on('finish', () => transaction.finish());
  next();
});
```
