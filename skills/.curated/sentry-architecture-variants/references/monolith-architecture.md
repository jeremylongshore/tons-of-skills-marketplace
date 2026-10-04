# Monolith Architecture — Sentry Deep Dive

## Project Layout

```
Organization: mycompany
└── Project: monolith-app
    └── Single DSN for entire application
```

One project, one DSN. Use tags to separate modules and route alerts to the right team.

## Configuration

```typescript
// instrument.mjs — load via: node --import ./instrument.mjs app.js
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.APP_VERSION,
  tracesSampleRate: 0.1,

  initialScope: {
    tags: { app: 'monolith' },
  },
});
```

## Module Tagging Pattern

```typescript
// Tag errors by module for per-team filtering
function captureModuleError(module: string, error: Error) {
  Sentry.withScope((scope) => {
    scope.setTag('module', module);
    scope.setTag('team', getTeamForModule(module));
    Sentry.captureException(error);
  });
}

// Module-based breadcrumbs
function addModuleBreadcrumb(module: string, message: string, data?: object) {
  Sentry.addBreadcrumb({
    category: module,
    message,
    data,
    level: 'info',
  });
}

// Usage
addModuleBreadcrumb('auth', 'Login attempt', { method: 'oauth' });
captureModuleError('auth', new Error('Token expired'));
captureModuleError('billing', new Error('Payment gateway timeout'));
```

## Dashboard Ownership Rules

```
# In Sentry project settings → Issue Owners:
tags.module:auth         → #platform-team
tags.module:billing      → #payments-team
tags.module:inventory    → #supply-chain-team
tags.module:notifications → #engagement-team

# Filter issues by module:
# Issues → Search: tags.module:auth
# Performance → Search: tags.module:billing
```

## When to Graduate from Monolith Pattern

Move to project-per-service when:

- Module count exceeds 50 (tag cardinality limit)
- Teams need separate DSNs for access control
- Deploy cadence differs per module (independent releases)
- Performance budget isolation needed per team

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
