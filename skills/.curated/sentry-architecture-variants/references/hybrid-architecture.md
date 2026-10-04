# Hybrid Architecture — Sentry Deep Dive

## Project Layout

```
Organization: mycompany
├── Project: frontend-web        (@sentry/react)
├── Project: mobile-app          (@sentry/react-native)
├── Project: api-gateway         (@sentry/node)
├── Project: payment-service     (@sentry/node)
├── Project: notification-worker (@sentry/node)
└── Project: lambda-functions    (@sentry/aws-serverless)
```

## End-to-End Trace Flow

```
User clicks "Place Order" in browser
  │
  ├── @sentry/react: button.click span (transaction start)
  │     └── fetch('/api/orders') adds sentry-trace + baggage headers
  │
  ├── api-gateway (@sentry/node): auto-continues trace from headers
  │     ├── calls payment-service via HTTP (headers auto-propagated)
  │     └── publishes to Kafka (headers injected manually)
  │
  ├── payment-service (@sentry/node): auto-continues from HTTP headers
  │     └── calls Stripe API (outbound HTTP traced)
  │
  └── notification-worker (@sentry/node): continues from Kafka headers
        └── sends email via SES (outbound HTTP traced)
```

All spans share a single `trace_id`. Sentry Trace View renders the full waterfall.

## Critical Configuration: tracePropagationTargets

The browser/mobile SDK will NOT attach trace headers unless the API domain matches `tracePropagationTargets`:

```typescript
// Frontend — MUST match your API domain
Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [Sentry.browserTracingIntegration()],
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.yourapp\.com/,
  ],
});
```

Without this, the browser-to-API boundary breaks the trace chain.

## Cross-Platform Correlation

For debugging, correlate traces across platforms using custom tags:

```typescript
// Backend: tag with the frontend trace origin
app.use((req, res, next) => {
  const sentryTrace = req.headers['sentry-trace'];
  if (sentryTrace) {
    Sentry.setTag('trace_origin', 'browser');
  }
  next();
});

// Search in Sentry: tags.trace_origin:browser
// Shows all backend issues triggered by frontend user actions
```

## Migration Path: Monolith → Hybrid

When extracting services from a monolith:

1. Keep the monolith's Sentry project for remaining modules
2. Create new project for each extracted service
3. Add distributed tracing headers between monolith and new services
4. Tag the monolith with `migration_status: in_progress`
5. Remove module tags as modules are fully extracted

```typescript
// Monolith calling new extracted service
async function callExtractedService(path: string, data: object) {
  return Sentry.startSpan(
    { name: `extracted.${path}`, op: 'http.client' },
    async () => {
      // SDK auto-adds sentry-trace + baggage headers
      return fetch(`https://new-service.internal${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    }
  );
}
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
