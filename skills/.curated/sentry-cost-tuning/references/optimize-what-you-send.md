# Optimize What You Send

## Optimize What You Send

### Reduce Event Size

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Limit string lengths
  maxValueLength: 250,

  // Limit breadcrumbs
  maxBreadcrumbs: 20,

  // Strip large data
  beforeSend(event) {
    // Remove large request bodies
    if (event.request?.data) {
      const size = JSON.stringify(event.request.data).length;
      if (size > 1000) {
        event.request.data = '[TRUNCATED]';
      }
    }
    return event;
  },
});
```

### Disable Unused Features

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Disable session tracking if not needed
  autoSessionTracking: false,

  // Disable profiling if not needed
  profilesSampleRate: 0,

  // Disable replay if not needed
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
});
```
