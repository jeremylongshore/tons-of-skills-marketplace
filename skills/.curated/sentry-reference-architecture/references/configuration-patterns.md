# Configuration Patterns

## Configuration Patterns

### Centralized Config Module

```typescript
// lib/sentry.ts
import * as Sentry from '@sentry/node';

interface SentryConfig {
  serviceName: string;
  environment: string;
  release?: string;
}

export function initSentry(config: SentryConfig): void {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: config.environment,
    release: config.release || process.env.SENTRY_RELEASE,
    serverName: config.serviceName,

    // Standard settings
    tracesSampleRate: config.environment === 'production' ? 0.1 : 1.0,
    sendDefaultPii: false,
    attachStacktrace: true,

    // Standard integrations
    integrations: [
      new Sentry.Integrations.Http({ tracing: true }),
    ],

    // Standard filtering
    ignoreErrors: [
      'ResizeObserver loop',
      'Network request failed',
    ],

    // Standard tags
    initialScope: {
      tags: {
        service: config.serviceName,
      },
    },
  });
}

export { Sentry };
```

### Usage Across Services

```typescript
// user-service/src/index.ts
import { initSentry, Sentry } from '@mycompany/shared/sentry';

initSentry({
  serviceName: 'user-service',
  environment: process.env.NODE_ENV,
  release: process.env.GIT_SHA,
});
```
