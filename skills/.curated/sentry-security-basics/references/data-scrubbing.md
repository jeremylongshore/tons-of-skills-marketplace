# Data Scrubbing

## Data Scrubbing

### 1. Built-in Scrubbing (Server-Side)

Enable in Sentry Dashboard:

1. Project Settings > Security & Privacy
2. Enable "Data Scrubber"
3. Configure sensitive fields

### 2. Client-Side Scrubbing

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event) {
    // Scrub user data
    if (event.user) {
      delete event.user.email;
      delete event.user.ip_address;
    }

    // Scrub request body
    if (event.request?.data) {
      const data = JSON.parse(event.request.data);
      delete data.password;
      delete data.creditCard;
      delete data.ssn;
      event.request.data = JSON.stringify(data);
    }

    // Scrub cookies
    if (event.request?.cookies) {
      delete event.request.cookies.session;
      delete event.request.cookies.auth;
    }

    return event;
  },
});
```

### 3. Sensitive Fields Configuration

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Don't send specific data
  sendDefaultPii: false, // Disable automatic PII collection

  beforeBreadcrumb(breadcrumb, hint) {
    // Scrub sensitive data from breadcrumbs
    if (breadcrumb.category === 'xhr') {
      const url = breadcrumb.data?.url;
      if (url?.includes('password') || url?.includes('token')) {
        return null;
      }
    }
    return breadcrumb;
  },
});
```
