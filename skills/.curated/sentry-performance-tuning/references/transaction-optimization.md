# Transaction Optimization

## Transaction Optimization

### Meaningful Transaction Names

```typescript
// Bad: Creates too many unique transactions
app.get('/users/:id', (req, res) => {
  // Transaction name: /users/123, /users/456, etc.
});

// Good: Parameterized names
app.get('/users/:id', (req, res) => {
  const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();
  if (transaction) {
    transaction.setName('/users/:id'); // Single transaction type
  }
});
```

### Skip Unnecessary Spans

```typescript
// Only create spans for meaningful operations
function processData(data: Data[]) {
  // Skip span for fast operations
  if (data.length < 10) {
    return quickProcess(data);
  }

  // Create span for slow operations
  const span = Sentry.getCurrentHub().getScope()?.getSpan()?.startChild({
    op: 'process',
    description: 'Process large dataset',
  });

  try {
    return slowProcess(data);
  } finally {
    span?.finish();
  }
}
```
