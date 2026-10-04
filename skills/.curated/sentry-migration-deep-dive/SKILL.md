---
name: sentry-migration-deep-dive
description: 'Migrate to Sentry from other error tracking tools like Rollbar, Bugsnag,
  or New Relic.

  Use when replacing an existing error tracker with Sentry, running tools in parallel

  during a transition, or mapping API calls between providers.

  Trigger with phrases like "migrate to sentry", "switch from rollbar to sentry",

  "replace bugsnag with sentry", "sentry migration plan".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(node:*), Grep, Glob
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- migration
- rollbar
- bugsnag
- new-relic
- error-tracking
compatibility: Designed for Claude Code
---
# Sentry Migration Deep Dive

## Overview

Replace an existing error tracking tool (Rollbar, Bugsnag, New Relic, Raygun, Airbrake) with Sentry using a phased migration that runs both tools in parallel before cutover. This skill covers concept mapping between providers, SDK swap patterns, alert rule migration, team training, and rollback strategy.

## Current State

!`npm list 2>/dev/null | command grep -iE "sentry|rollbar|bugsnag|raygun|airbrake|honeybadger|newrelic" || echo 'No error tracking packages found'`

## Prerequisites

- Admin access to the current error tracking tool (API keys, alert rule access)
- Sentry project created with DSN available in environment variables
- Source maps or debug symbols configured for stack trace resolution
- Parallel run timeline agreed with team (2-4 weeks recommended)
- Inventory of current alert rules, integrations, and custom filters

## Instructions

### Step 1: Map Concepts Between Providers

Build a translation table mapping the current tool's terminology and API surface to Sentry equivalents. Scan the codebase for all calls to the existing SDK.

| Concept | Rollbar | Bugsnag | New Relic | Sentry |
|---------|---------|---------|-----------|--------|
| Capture error | `rollbar.error(err)` | `Bugsnag.notify(err)` | `newrelic.noticeError(err)` | `Sentry.captureException(err)` |
| Log message | `rollbar.info(msg)` | `Bugsnag.notify(msg)` | `newrelic.recordCustomEvent()` | `Sentry.captureMessage(msg)` |
| User context | `rollbar.configure({ person: {...} })` | `Bugsnag.setUser(id, email)` | `newrelic.setUserID(id)` | `Sentry.setUser({ id, email })` |
| Tags/metadata | `rollbar.configure({ custom: {...} })` | `bugsnag.addMetadata(tab, data)` | `newrelic.addCustomAttributes()` | `Sentry.setTag()` / `Sentry.setContext()` |
| Breadcrumbs | `rollbar.log(level, msg)` | `Bugsnag.leaveBreadcrumb(msg)` | N/A | `Sentry.addBreadcrumb({ message })` |
| Release tracking | `code_version` config | `appVersion` config | `NEW_RELIC_LABELS` | `Sentry.init({ release: 'v1.2.3' })` |
| Environment | `environment` config | `releaseStage` config | `NEW_RELIC_APP_NAME` suffix | `Sentry.init({ environment: 'prod' })` |
| Error filter | `checkIgnore` callback | `onError` callback | `ignore_errors` config | `beforeSend` hook |
| Performance | N/A | `@bugsnag/plugin-*` | Built-in APM | Built-in `tracesSampleRate` |

Use Grep to find all references: `grep -rn "rollbar\|Bugsnag\|newrelic\|noticeError" --include="*.ts" --include="*.js" src/`

### Step 2: Install Sentry in Parallel

Install the Sentry SDK alongside the existing tool. Route errors to both destinations during the transition period to validate parity before removing the old tool.

```typescript
// instrument.ts -- load BEFORE any other import
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,  // auto-read from package.json
  tracesSampleRate: 0.1,                     // start low, tune after baseline
  sendDefaultPii: false,
});
```

```typescript
// dual-reporter.ts -- send to BOTH tools during parallel run
import * as Sentry from '@sentry/node';

// Keep existing tool import (e.g., Rollbar, Bugsnag)
import Rollbar from 'rollbar';
const rollbar = new Rollbar({ accessToken: process.env.ROLLBAR_TOKEN });

export function captureError(error: Error, context?: Record<string, unknown>) {
  // Sentry (new)
  Sentry.withScope((scope) => {
    if (context) scope.setContext('migration', context);
    Sentry.captureException(error);
  });

  // Old tool (keep running until parity verified)
  rollbar.error(error, context);
}

export function setUserContext(user: { id: string; email?: string }) {
  Sentry.setUser(user);
  rollbar.configure({ payload: { person: { id: user.id, email: user.email } } });
}
```

### Step 3: Migrate Alert Rules, Validate Parity, and Cut Over

1. **Export alert rules** from the old tool. Map each alert to a Sentry equivalent:
   - "New error in production" becomes a Sentry Issue Alert with filter `environment:production` and action "Send Slack notification".
   - "Error rate > 100/min" becomes a Sentry Metric Alert with threshold 100 events per minute and PagerDuty action.
   - Rate-based alerts use Sentry Metric Alerts; occurrence-based alerts use Sentry Issue Alerts.

2. **Validate parity** during the parallel run window:

   ```bash
   # Compare error counts -- Sentry API
   curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
     "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/stats/" | jq '.[] | .total'

   # Compare with old tool API (Rollbar example)
   curl -s -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     "https://api.rollbar.com/api/1/reports/top_recent_items" | jq '.result | length'
   ```

   - Error count should be within 10% between tools.
   - Stack traces must resolve correctly (verify source maps uploaded to Sentry).
   - Breadcrumbs, user context, and tags must appear in Sentry event detail.

3. **Remove the old SDK** after parity is confirmed:

   ```bash
   npm uninstall rollbar @bugsnag/node @bugsnag/plugin-express newrelic || echo "Some packages not found (expected if only one tool was installed)"
   ```

   Search for leftover references and remove them:

   ```bash
   grep -rn "rollbar\|bugsnag\|newrelic\|raygun\|airbrake" \
     --include="*.ts" --include="*.js" --include="*.env*" \
     --exclude-dir=node_modules . || echo "No remaining references found"
   ```

4. **Schedule team training**: walk through the Sentry dashboard (Issues, Performance, Releases views), show how to assign issues, and demonstrate the alert configuration UI.

5. **Rollback strategy**: keep the old tool's npm package in `devDependencies` and its configuration file in a `migration-backup/` directory for 30 days after cutover. If Sentry surfaces fewer errors than expected, re-enable dual reporting and investigate.

## Output

- Concept mapping table translating old API calls to Sentry equivalents
- Dual-reporting wrapper sending errors to both tools during parallel run
- Sentry SDK initialized with environment, release, and sampling configuration
- Alert rules migrated from old tool to Sentry Issue and Metric Alerts
- Parity validation confirming error count, stack traces, and context match
- Old SDK removed and all references cleaned from codebase

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Error count mismatch between tools | Different sampling rates or filter rules | Set both tools to 100% sampling during parallel run; disable `beforeSend` filters temporarily |
| Missing stack traces in Sentry | Source maps not uploaded | Run `sentry-cli sourcemaps upload --release=$(npm pkg get version)` in CI |
| Old tool references remain after removal | Incomplete codebase search | Run grep across all file types including `.env`, CI configs, and infrastructure-as-code |
| Sentry alerts not firing | Alert conditions misconfigured | Test with a synthetic error: `Sentry.captureException(new Error('alert-test'))` and verify delivery |
| New Relic APM data missing after switch | Sentry replaces error tracking only, not full APM | Keep New Relic for APM if needed; Sentry Performance covers traces but not infrastructure metrics |
| Team unfamiliar with Sentry UI | No training provided | Schedule 30-minute walkthrough covering Issues, Performance, and Releases views |

## Examples

**Migrate Express app from Rollbar to Sentry:**

```typescript
// BEFORE: rollbar error handler middleware
import Rollbar from 'rollbar';
const rollbar = new Rollbar({ accessToken: process.env.ROLLBAR_TOKEN });
app.use(rollbar.errorHandler());

// AFTER: Sentry error handler middleware
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: process.env.SENTRY_DSN });
Sentry.setupExpressErrorHandler(app);
```

**Migrate React error boundary from Bugsnag to Sentry:**

```typescript
// BEFORE: Bugsnag React initialization + error boundary
import Bugsnag from '@bugsnag/js';
import BugsnagPluginReact from '@bugsnag/plugin-react';
Bugsnag.start({ plugins: [new BugsnagPluginReact()] });
const ErrorBoundary = Bugsnag.getPlugin('react')!.createErrorBoundary(React);
// Usage: wrap root component with ErrorBoundary

// AFTER: Sentry React initialization + error boundary
import * as Sentry from '@sentry/react';
Sentry.init({ dsn: process.env.SENTRY_DSN });
// Usage: wrap root component with Sentry.ErrorBoundary (accepts fallback prop)
// See @sentry/react docs for ErrorBoundary component API
```

**Post-migration verification script:**

```typescript
import * as Sentry from '@sentry/node';

async function verifyMigration() {
  const eventId = Sentry.captureException(new Error('Migration verification test'));
  console.log('Error captured:', eventId ? 'PASS' : 'FAIL');

  Sentry.captureMessage('Migration complete', 'info');

  const flushed = await Sentry.flush(5000);
  console.log('Events delivered:', flushed ? 'PASS' : 'FAIL');
}

verifyMigration();
```

## Resources

- [Sentry SDK Documentation](https://docs.sentry.io/platforms/)
- [Sentry Migration Guide](https://docs.sentry.io/product/accounts/migration/)
- Sentry vs Rollbar comparison
- Sentry vs Bugsnag comparison
- [Source Maps Upload CLI](https://docs.sentry.io/platforms/javascript/sourcemaps/)
- [Sentry Alert Configuration](https://docs.sentry.io/product/alerts/)

## Next Steps

After migration, proceed to `sentry-performance-tracing` to configure distributed tracing, or `sentry-prod-checklist` to verify production readiness.
