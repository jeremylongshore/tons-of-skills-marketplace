# Debug Information Checklist

## Debug Information Checklist

### 1. SDK Version and Configuration

```bash
# Get SDK version
npm list @sentry/node @sentry/react @sentry/browser 2>/dev/null

# Or for Python
pip show sentry-sdk
```

### 2. Configuration Export

```typescript
// Create debug config export
const debugConfig = {
  sdkVersion: Sentry.SDK_VERSION,
  dsn: process.env.SENTRY_DSN?.replace(/\/\/(.+?)@/, '//**REDACTED**@'),
  environment: process.env.NODE_ENV,
  release: process.env.SENTRY_RELEASE,
  tracesSampleRate: 0.1,
  sampleRate: 1.0,
};

console.log('Sentry Config:', JSON.stringify(debugConfig, null, 2));
```

### 3. Network Connectivity Test

```bash
# Test Sentry ingest endpoint
curl -v https://sentry.io/api/0/ 2>&1 | head -20

# Test DSN endpoint (replace with your org)
curl -I https://o123456.ingest.sentry.io/api/123456/envelope/
```

### 4. Event Capture Test

```typescript
// Debug event capture
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  debug: true,
  beforeSend(event, hint) {
    console.log('Event being sent:', JSON.stringify(event, null, 2));
    return event;
  },
});

const eventId = Sentry.captureMessage('Debug test message');
console.log('Event ID:', eventId);
```

### 5. Integration Status

```typescript
const client = Sentry.getCurrentHub().getClient();
const integrations = client?.getIntegrations?.() || [];

console.log('Active integrations:', integrations.map(i => i.name));
```
