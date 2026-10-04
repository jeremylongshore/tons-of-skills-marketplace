# Reduce Sdk Overhead

## Reduce SDK Overhead

### Minimal Integrations

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Only include needed integrations
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    // Remove unused integrations to reduce overhead
  ],

  // Disable automatic breadcrumbs if not needed
  integrations: (integrations) =>
    integrations.filter((i) => i.name !== 'Console'),
});
```

### Limit Breadcrumbs

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  maxBreadcrumbs: 20, // Default is 100
});
```

### Batch Events

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Buffer events before sending
  transport: Sentry.makeNodeTransport,
  transportOptions: {
    // Batch events (reduces network calls)
  },
});
```
