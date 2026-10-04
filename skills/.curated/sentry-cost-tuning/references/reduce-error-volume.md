# Reduce Error Volume

## Reduce Error Volume

### 1. Client-Side Filtering

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Sample errors
  sampleRate: 0.5, // Send 50% of errors

  // Ignore common noisy errors
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection',
    /Loading chunk \d+ failed/,
    'Network request failed',
    'AbortError',
  ],

  // Ignore errors from specific URLs
  denyUrls: [
    /extensions\//i,
    /^chrome:\/\//i,
    /^moz-extension:\/\//i,
    /^safari-extension:\/\//i,
  ],
});
```

### 2. Server-Side Filtering (Inbound Filters)

Enable in Sentry Dashboard:

1. Project Settings > Inbound Filters
2. Enable:
   - Legacy browsers
   - Browser extensions
   - Web crawlers
   - Filtered by IP

### 3. Rate Limits

```bash
# Set project rate limit
curl -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"options": {"sentry:rate-limit": 1000}}' \
  "https://sentry.io/api/0/projects/$ORG/$PROJECT/"
```
