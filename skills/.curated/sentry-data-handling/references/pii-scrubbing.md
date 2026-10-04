# Pii Scrubbing

## PII Scrubbing

### Built-in Data Scrubbing

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Enable server-side scrubbing
  sendDefaultPii: false, // Default

  // Client-side scrubbing
  beforeSend(event) {
    // Remove sensitive headers
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
      delete event.request.headers['X-API-Key'];
    }
    return event;
  },
});
```

### Custom Data Scrubbing

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event, hint) {
    // Scrub email addresses
    if (event.user?.email) {
      event.user.email = '[REDACTED]';
    }

    // Scrub credit card numbers
    const ccRegex = /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g;
    if (event.message) {
      event.message = event.message.replace(ccRegex, '[CREDIT_CARD]');
    }

    // Scrub phone numbers
    const phoneRegex = /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g;
    if (event.extra) {
      event.extra = JSON.parse(
        JSON.stringify(event.extra).replace(phoneRegex, '[PHONE]')
      );
    }

    return event;
  },
});
```

### Scrub Specific Fields

```typescript
function scrubSensitiveData(obj: Record<string, unknown>): Record<string, unknown> {
  const sensitiveKeys = [
    'password', 'secret', 'token', 'apiKey', 'api_key',
    'ssn', 'social_security', 'credit_card', 'cvv',
  ];

  return Object.entries(obj).reduce((acc, [key, value]) => {
    if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
      acc[key] = '[FILTERED]';
    } else if (typeof value === 'object' && value !== null) {
      acc[key] = scrubSensitiveData(value as Record<string, unknown>);
    } else {
      acc[key] = value;
    }
    return acc;
  }, {} as Record<string, unknown>);
}

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event) {
    if (event.extra) {
      event.extra = scrubSensitiveData(event.extra);
    }
    return event;
  },
});
```
