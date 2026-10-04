# Secure Configuration

## Secure Configuration

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Security settings
  sendDefaultPii: false,
  attachStacktrace: true,

  // Restrict what's captured
  maxBreadcrumbs: 50,
  maxValueLength: 250,

  // Don't capture certain data
  integrations: [
    new Sentry.Integrations.Breadcrumbs({
      console: false, // Don't capture console logs
    }),
  ],

  // Filter sensitive errors
  beforeSend(event, hint) {
    // Don't send authentication failures
    const error = hint.originalException;
    if (error?.message?.includes('authentication')) {
      return null;
    }

    // Redact sensitive data patterns
    if (event.message) {
      event.message = event.message
        .replace(/api[_-]?key[=:]\s*\S+/gi, 'api_key=**REDACTED**')
        .replace(/bearer\s+\S+/gi, 'Bearer **REDACTED**');
    }

    return event;
  },
});
```
