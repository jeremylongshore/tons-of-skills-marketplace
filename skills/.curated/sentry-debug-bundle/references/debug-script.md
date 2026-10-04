# Debug Script

## Debug Script

```typescript
// debug-sentry.ts
import * as Sentry from '@sentry/node';

async function collectDebugInfo() {
  const info = {
    timestamp: new Date().toISOString(),
    nodeVersion: process.version,
    platform: process.platform,
    sdkVersion: Sentry.SDK_VERSION,
    env: {
      NODE_ENV: process.env.NODE_ENV,
      SENTRY_DSN: process.env.SENTRY_DSN ? 'SET' : 'NOT SET',
      SENTRY_RELEASE: process.env.SENTRY_RELEASE || 'NOT SET',
    },
    config: {
      debug: true,
      tracesSampleRate: 'configured',
    },
  };

  // Test capture
  try {
    const eventId = Sentry.captureMessage('Debug bundle test');
    info.testEventId = eventId;
    info.captureStatus = 'SUCCESS';
  } catch (error) {
    info.captureStatus = 'FAILED';
    info.captureError = error.message;
  }

  return info;
}

collectDebugInfo().then(info => {
  console.log('=== SENTRY DEBUG BUNDLE ===');
  console.log(JSON.stringify(info, null, 2));
});
```
