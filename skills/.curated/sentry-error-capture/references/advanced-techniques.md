# Advanced Techniques

## Advanced Techniques

### Breadcrumb Trail

```typescript
// Automatic breadcrumbs (enabled by default)
// Manual breadcrumbs for custom events
Sentry.addBreadcrumb({
  type: 'navigation',
  category: 'route',
  message: `Navigated to ${path}`,
  level: 'info',
});

Sentry.addBreadcrumb({
  type: 'http',
  category: 'api',
  message: `API call to ${endpoint}`,
  data: { method, status },
  level: status >= 400 ? 'warning' : 'info',
});
```

### Attachments

```typescript
Sentry.captureException(error, (scope) => {
  scope.addAttachment({
    filename: 'debug.json',
    data: JSON.stringify(debugInfo),
    contentType: 'application/json',
  });
  return scope;
});
```

### Event Filtering

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event, hint) {
    // Filter out specific errors
    if (hint.originalException?.message?.includes('Network')) {
      return null; // Don't send
    }

    // Modify event
    event.tags = { ...event.tags, processed: 'true' };
    return event;
  },
});
```
