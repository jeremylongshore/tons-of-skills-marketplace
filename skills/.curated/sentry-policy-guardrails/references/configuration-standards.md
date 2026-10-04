# Configuration Standards

## Configuration Standards

### Shared Configuration Package

```typescript
// packages/sentry-config/index.ts
import * as Sentry from '@sentry/node';

export interface SentryConfigOptions {
  serviceName: string;
  environment: string;
  version?: string;
  additionalTags?: Record<string, string>;
}

// Enforced organization defaults
const ORGANIZATION_DEFAULTS = {
  // Never send PII without explicit opt-in
  sendDefaultPii: false,

  // Standard sample rates
  sampleRate: 1.0,
  tracesSampleRate: 0.1,

  // Standard breadcrumb limit
  maxBreadcrumbs: 50,

  // Standard ignore patterns
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection',
    /^Network request failed/,
  ],
};

export function initSentryWithPolicy(options: SentryConfigOptions): void {
  const dsn = process.env.SENTRY_DSN;

  if (!dsn && options.environment === 'production') {
    throw new Error('SENTRY_DSN required in production');
  }

  Sentry.init({
    dsn,
    environment: options.environment,
    release: options.version,
    serverName: options.serviceName,

    // Apply organization defaults (cannot be overridden)
    ...ORGANIZATION_DEFAULTS,

    // Required tags
    initialScope: {
      tags: {
        service: options.serviceName,
        team: process.env.TEAM_NAME || 'unknown',
        ...options.additionalTags,
      },
    },

    // Enforced PII scrubbing
    beforeSend: enforcedBeforeSend,
  });
}

function enforcedBeforeSend(
  event: Sentry.Event,
  hint: Sentry.EventHint
): Sentry.Event | null {
  // Always scrub sensitive data
  return scrubSensitiveData(event);
}
```

### Usage in Services

```typescript
// services/user-service/src/index.ts
import { initSentryWithPolicy } from '@mycompany/sentry-config';

// Teams can't bypass organization policies
initSentryWithPolicy({
  serviceName: 'user-service',
  environment: process.env.NODE_ENV || 'development',
  version: process.env.GIT_SHA,
  additionalTags: {
    feature_area: 'authentication',
  },
});
```
