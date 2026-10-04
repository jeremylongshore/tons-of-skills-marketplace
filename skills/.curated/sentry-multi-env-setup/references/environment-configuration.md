# Environment Configuration

## Environment Configuration

### Basic Setup

```typescript
import * as Sentry from '@sentry/node';

const environment = process.env.NODE_ENV || 'development';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: environment,

  // Environment-specific settings
  enabled: environment !== 'development',
  debug: environment === 'development',
});
```

### Environment-Specific Sample Rates

```typescript
const sampleRates: Record<string, { errors: number; traces: number }> = {
  development: { errors: 1.0, traces: 1.0 },
  staging: { errors: 1.0, traces: 0.5 },
  production: { errors: 1.0, traces: 0.1 },
};

const rates = sampleRates[environment] || sampleRates.production;

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment,
  sampleRate: rates.errors,
  tracesSampleRate: rates.traces,
});
```
