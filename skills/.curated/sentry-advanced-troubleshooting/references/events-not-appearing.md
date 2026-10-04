# Events Not Appearing

## Events Not Appearing

### Check 1: SDK Initialization

```typescript
// Verify SDK is initialized
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  debug: true, // Enable debug logging
});

// Check if client exists
const client = Sentry.getCurrentHub().getClient();
console.log('Sentry client initialized:', !!client);
console.log('DSN:', client?.getDsn()?.toString());
```

### Check 2: Network Issues

```typescript
// Test network connectivity
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Add transport debugging
  beforeSend(event) {
    console.log('Sending event:', event.event_id);
    return event;
  },

  // Capture transport errors
  transport: (options) => {
    const transport = Sentry.makeNodeTransport(options);
    return {
      ...transport,
      send: async (request) => {
        try {
          const result = await transport.send(request);
          console.log('Transport success');
          return result;
        } catch (error) {
          console.error('Transport error:', error);
          throw error;
        }
      },
    };
  },
});
```

### Check 3: Sampling Configuration

```typescript
// Verify sample rates
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Check these aren't too low
  sampleRate: 1.0, // 100% of errors (for debugging)
  tracesSampleRate: 1.0, // 100% of transactions

  // Check sampler isn't dropping events
  tracesSampler: (ctx) => {
    console.log('Sampling context:', ctx);
    return 1.0; // Force sampling for debug
  },
});
```

### Check 4: beforeSend Filtering

```typescript
// Temporarily disable filtering
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event, hint) {
    console.log('beforeSend called:', event.message);
    // Return event always (don't filter during debug)
    return event;
  },
});
```
