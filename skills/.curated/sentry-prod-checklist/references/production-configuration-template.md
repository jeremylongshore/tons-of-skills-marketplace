# Production Configuration Template

## Production Configuration Template

```typescript
// sentry.config.ts
import * as Sentry from '@sentry/node';

const isProduction = process.env.NODE_ENV === 'production';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.SENTRY_RELEASE || process.env.npm_package_version,

  // Production settings
  debug: !isProduction,
  sendDefaultPii: false,
  attachStacktrace: true,

  // Sampling
  sampleRate: 1.0,
  tracesSampleRate: isProduction ? 0.1 : 1.0,

  // Filtering
  ignoreErrors: [
    'ResizeObserver loop',
    'Network request failed',
  ],

  // Performance
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
  ],
});

export default Sentry;
```
