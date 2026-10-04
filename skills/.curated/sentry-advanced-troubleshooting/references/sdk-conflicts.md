# Sdk Conflicts

## SDK Conflicts

### Multiple SDK Instances

```typescript
// Problem: Multiple init() calls
// Solution: Check for existing client
if (!Sentry.getCurrentHub().getClient()) {
  Sentry.init({ dsn: process.env.SENTRY_DSN });
}
```

### Version Mismatches

```bash
# Check all Sentry package versions
npm list | grep sentry

# All packages should be same major version
# @sentry/node@7.x.x
# @sentry/tracing@7.x.x  # Same major version
```

### Framework Integration Conflicts

```typescript
// Example: Next.js conflicts
// Use framework-specific SDK
import * as Sentry from '@sentry/nextjs'; // Not @sentry/node

// Configure in next.config.js
const { withSentryConfig } = require('@sentry/nextjs');
module.exports = withSentryConfig(nextConfig);
```
