## Implementation Guide

### Step 1: Environment-Based Configuration

```typescript
import * as Sentry from '@sentry/node';

const isDev = process.env.NODE_ENV === 'development';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: isDev ? 'development' : 'production',

  // Higher sample rates in dev for testing
  tracesSampleRate: isDev ? 1.0 : 0.1,

  // Enable debug mode in development
  debug: isDev,

  // Don't send errors in development (optional)
  enabled: !isDev || process.env.SENTRY_DEV_ENABLED === 'true',
});
```

### Step 2: Development-Only DSN

```bash
# .env.development
SENTRY_DSN=https://dev-key@org.ingest.sentry.io/dev-project

# .env.production
SENTRY_DSN=https://prod-key@org.ingest.sentry.io/prod-project
```

### Step 3: Debug Output

```typescript
// Enable verbose logging in development
if (isDev) {
  Sentry.addIntegration(new Sentry.Integrations.Debug({
    stringify: true,
  }));
}
```

### Step 4: Local Testing Script

```bash
# test-sentry.sh
#!/bin/bash
export NODE_ENV=development
export SENTRY_DEV_ENABLED=true
node -e "
const Sentry = require('@sentry/node');
Sentry.init({ dsn: process.env.SENTRY_DSN, debug: true });
Sentry.captureMessage('Local dev test');
console.log('Check Sentry dashboard');
"
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
