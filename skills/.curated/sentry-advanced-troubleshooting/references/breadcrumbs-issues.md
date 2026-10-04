# Breadcrumbs Issues

## Breadcrumbs Issues

### Debug Breadcrumb Capture

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Increase breadcrumb limit for debugging
  maxBreadcrumbs: 100,

  beforeBreadcrumb(breadcrumb, hint) {
    console.log('Breadcrumb:', breadcrumb.category, breadcrumb.message);
    return breadcrumb;
  },
});
```

### Manual Breadcrumb Test

```typescript
// Add test breadcrumb
Sentry.addBreadcrumb({
  category: 'test',
  message: 'Test breadcrumb',
  level: 'info',
});

// Capture error to see breadcrumbs
Sentry.captureMessage('Test message');

// Check Sentry dashboard for breadcrumbs
```
