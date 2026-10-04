# Compliance Enforcement

## Compliance Enforcement

### Required Data Scrubbing

```typescript
// Enforced by shared config - cannot be disabled
function scrubSensitiveData(event: Sentry.Event): Sentry.Event {
  // Remove sensitive headers
  if (event.request?.headers) {
    const sensitiveHeaders = [
      'authorization',
      'cookie',
      'x-api-key',
      'x-auth-token',
    ];
    for (const header of sensitiveHeaders) {
      delete event.request.headers[header];
    }
  }

  // Scrub credit cards
  event = scrubPattern(event, /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g, '[CARD]');

  // Scrub SSNs
  event = scrubPattern(event, /\b\d{3}-\d{2}-\d{4}\b/g, '[SSN]');

  // Scrub emails in extra/contexts (keep user email if explicitly set)
  event = scrubPattern(event, /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]');

  return event;
}

function scrubPattern(event: Sentry.Event, pattern: RegExp, replacement: string): Sentry.Event {
  const scrub = (obj: any): any => {
    if (typeof obj === 'string') {
      return obj.replace(pattern, replacement);
    }
    if (Array.isArray(obj)) {
      return obj.map(scrub);
    }
    if (obj && typeof obj === 'object') {
      return Object.fromEntries(
        Object.entries(obj).map(([k, v]) => [k, scrub(v)])
      );
    }
    return obj;
  };

  return scrub(event);
}
```

### Environment Enforcement

```typescript
// Prevent test data in production
function validateEnvironment(event: Sentry.Event): Sentry.Event | null {
  const env = process.env.NODE_ENV;

  // Block test data in production
  if (env === 'production') {
    const message = event.message?.toLowerCase() || '';
    const tags = event.tags || {};

    if (
      message.includes('test') ||
      tags.test === 'true' ||
      event.user?.email?.includes('@test.com')
    ) {
      console.warn('Blocked test data from production Sentry');
      return null;
    }
  }

  return event;
}
```
