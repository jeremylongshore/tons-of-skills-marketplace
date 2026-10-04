---
name: sentry-upgrade-migration
description: 'Upgrade Sentry SDK versions and migrate breaking API changes.

  Use when upgrading from Sentry v7 to v8, migrating Python SDK v1 to v2,

  replacing deprecated Hub/Transaction APIs, or running the migr8 codemod.

  Trigger: "upgrade sentry", "sentry migration", "sentry breaking changes",

  "migrate sentry v7 to v8", "update sentry sdk".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(pip:*), Bash(node:*),
  Grep, Glob
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- migration
- upgrade
- sdk
- breaking-changes
compatibility: Designed for Claude Code
---
# Sentry Upgrade Migration

Detect installed Sentry SDK versions, identify breaking API changes, apply automated codemods, and verify the upgrade succeeds with test events and traces.

## Current State

!`npm list 2>/dev/null | command grep @sentry || echo 'No npm Sentry packages found'`
!`pip show sentry-sdk 2>/dev/null | command grep -E '^(Name|Version)' || echo 'No Python sentry-sdk found'`
!`node --version 2>/dev/null || echo 'Node.js not available'`

## Overview

Sentry SDK upgrades require careful handling of breaking API changes. The v7 to v8 JavaScript migration is the most impactful, removing the Hub pattern, replacing Transaction/Span APIs with `startSpan()`, converting class-based integrations to functions, and requiring ESM-first initialization. Python SDK v1 to v2 similarly replaces `configure_scope()` with `get_current_scope()`. This skill automates version detection, runs the official `@sentry/migr8` codemod, applies manual fixes for patterns the codemod misses, and validates the upgrade with test events.

## Prerequisites

- Current Sentry SDK version identified (run DCI above)
- Target version changelog reviewed
- Non-production environment for testing upgrades
- All `@sentry/*` packages at the same major version before starting
- Node.js >= 18.19.0 or >= 20.6.0 for SDK v8 (ESM support required)

## Instructions

### Step 1. Identify Current SDK Version and Scan for Deprecated APIs

```bash
# JavaScript: list all Sentry packages and their versions
npm ls 2>/dev/null | command grep "@sentry/"

# Python: check installed version
pip show sentry-sdk 2>/dev/null

# Verify all @sentry/* packages are the same major version (critical!)
# Mixed versions cause runtime crashes
npm ls @sentry/core @sentry/node @sentry/browser @sentry/utils 2>/dev/null
```

Scan the codebase for deprecated patterns that need migration:

```bash
# Detect v7 Hub usage (removed in v8)
command grep -rn "getCurrentHub\|configureScope\|hub\.capture" src/ --include="*.ts" --include="*.js"

# Detect v7 Transaction API (replaced in v8)
command grep -rn "startTransaction\|\.startChild\|\.finish()" src/ --include="*.ts" --include="*.js"

# Detect class-based integrations (replaced in v8)
command grep -rn "new Sentry\.\|new BrowserTracing\|new Integrations\." src/ --include="*.ts" --include="*.js"

# Detect @sentry/tracing imports (package removed in v8)
command grep -rn "from '@sentry/tracing'" src/ --include="*.ts" --include="*.js"

# Python: detect v1 scope API (replaced in v2)
command grep -rn "configure_scope\|push_scope" src/ --include="*.py"
```

### Step 2. Run the Automated Migration Codemod (JavaScript v7 to v8)

```bash
# First upgrade to latest v7 to get deprecation warnings
npm install @sentry/node@7

# Run the official migr8 codemod — rewrites deprecated APIs automatically
npx @sentry/migr8@latest
# Handles: Hub removal, integration class→function, import path changes
# Does NOT handle: Transaction→startSpan, ESM init pattern, custom transports

# Now upgrade to v8
npm install @sentry/node@8
```

### Step 3. Apply Breaking Change Fixes the Codemod Misses

**Breaking Change: Transaction/Span API replaced with `startSpan()`**

```typescript
// v7 (OLD) — manual transaction lifecycle
const transaction = Sentry.startTransaction({ name: 'process', op: 'task' });
const span = transaction.startChild({ op: 'db.query', description: 'SELECT users' });
// ... do work
span.finish();
transaction.finish();

// v8 (NEW) — callback-based, auto-finishes on return
await Sentry.startSpan({ name: 'process', op: 'task' }, async () => {
  await Sentry.startSpan({ name: 'SELECT users', op: 'db.query' }, async () => {
    // ... do work
  }); // span auto-finishes when callback returns
}); // root span auto-finishes when callback returns
```

**Breaking Change: Hub removed, use Scope API**

```typescript
// v7 (OLD)
const hub = Sentry.getCurrentHub();
hub.configureScope((scope) => {
  scope.setTag('region', 'us-east-1');
});
const transaction = hub.startTransaction({ name: 'my-tx' });

// v8 (NEW)
Sentry.withScope((scope) => {
  scope.setTag('region', 'us-east-1');
});
Sentry.startSpan({ name: 'my-tx', op: 'custom' }, (span) => {
  // work within span
});
```

**Breaking Change: Integrations are functions, not classes**

```typescript
// v7 (OLD)
import * as Sentry from '@sentry/node';
Sentry.init({
  integrations: [new Sentry.Integrations.Http({ tracing: true })],
});

// v8 (NEW) — most integrations are auto-enabled
Sentry.init({
  integrations: [
    Sentry.httpIntegration({ tracing: true }),
  ],
});
```

**Breaking Change: `@sentry/tracing` removed**

```typescript
// v7 (OLD)
import { BrowserTracing } from '@sentry/tracing';
Sentry.init({
  integrations: [new BrowserTracing()],
});

// v8 (NEW) — built into @sentry/browser and @sentry/node
Sentry.init({
  integrations: [
    Sentry.browserTracingIntegration(),
  ],
});
```

**Breaking Change: ESM initialization requires separate file**

```typescript
// v7 (OLD) — init at top of entry file
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: '...' });
// ... app code

// v8 (NEW) — must be in separate file, loaded via --import
// instrument.mjs (separate file)
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: '...' });

// Run with: node --import ./instrument.mjs app.mjs
// Or in package.json: "start": "node --import ./instrument.mjs app.mjs"
```

**Breaking Change: Custom transport must return response**

```typescript
// v7 (OLD) — send could return void
makeRequest(request) {
  sendToBackend(request);
}

// v8 (NEW) — must return TransportMakeRequestResponse
makeRequest(request) {
  sendToBackend(request);
  return { statusCode: 200 };
}
```

See [major-version-migrations.md](references/major-version-migrations.md) for v6-to-v7 and Python v1-to-v2 migration details.

### Step 4. Python SDK v1 to v2 Migration

```python
# v1 (OLD) — configure_scope / push_scope
import sentry_sdk

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("key", "value")

with sentry_sdk.push_scope() as scope:
    scope.set_extra("debug_info", data)
    sentry_sdk.capture_message("scoped message")

# v2 (NEW) — get_current_scope / new_scope
import sentry_sdk

scope = sentry_sdk.get_current_scope()
scope.set_tag("key", "value")

with sentry_sdk.new_scope() as scope:
    scope.set_extra("debug_info", data)
    sentry_sdk.capture_message("scoped message")
```

```bash
# Upgrade Python SDK
pip install --upgrade sentry-sdk

# Verify version
python -c "import sentry_sdk; print(sentry_sdk.VERSION)"
```

### Step 5. Align All Package Versions and Update Bundler Plugins

```bash
# All @sentry/* packages MUST be the same major version
# Mixed versions cause "Cannot read properties of undefined" runtime errors
npm install @sentry/node@8 @sentry/browser@8 @sentry/react@8 @sentry/profiling-node@8

# Remove deprecated packages
npm uninstall @sentry/tracing @sentry/hub 2>/dev/null

# Update bundler plugins (must be v2.14.2+ for SDK v8 compatibility)
npm install @sentry/webpack-plugin@latest @sentry/vite-plugin@latest 2>/dev/null
```

### Step 6. Verify the Upgrade with Test Events

```typescript
// test-migration.mjs — run after upgrading
import * as Sentry from '@sentry/node';

async function verifyUpgrade() {
  console.log('SDK Version:', Sentry.SDK_VERSION);

  // 1. Test error capture
  try {
    throw new Error('Migration verification error');
  } catch (e) {
    const eventId = Sentry.captureException(e);
    console.log('Error captured:', eventId ? 'PASS' : 'FAIL');
  }

  // 2. Test scoped context (v8 API)
  Sentry.withScope((scope) => {
    scope.setTag('test', 'migration-verify');
    scope.setUser({ id: 'test-user' });
    Sentry.captureMessage('Scoped context test');
  });
  console.log('Scoped context: PASS');

  // 3. Test performance span (v8 API — replaces startTransaction)
  await Sentry.startSpan(
    { name: 'migration-verify', op: 'test' },
    async (span) => {
      await Sentry.startSpan(
        { name: 'child-operation', op: 'test.child' },
        async () => {
          await new Promise((r) => setTimeout(r, 50));
        }
      );
      console.log('Span created:', span ? 'PASS' : 'FAIL');
    }
  );

  // 4. Test breadcrumbs
  Sentry.addBreadcrumb({
    category: 'test',
    message: 'Migration breadcrumb',
    level: 'info',
  });
  console.log('Breadcrumb: PASS');

  // 5. Flush and verify delivery
  const flushed = await Sentry.flush(5000);
  console.log('Flush:', flushed ? 'PASS' : 'FAIL');
}

verifyUpgrade();
```

See [testing-after-upgrade.md](references/testing-after-upgrade.md) for the full verification checklist.

### Step 7. Gradual Rollout Strategy

1. Upgrade in development environment, run full test suite
2. Watch for `Sentry.startTransaction is not a function` or similar runtime errors
3. Deploy to staging, monitor Sentry dashboard for 1-2 days
4. Check source maps still resolve (re-upload if bundler plugin changed)
5. Verify trace propagation between services (check `sentry-trace` header)
6. Deploy to production with rollback plan ready

## Output

- SDK upgraded to target version with all `@sentry/*` packages aligned
- Deprecated APIs migrated: Hub removed, Transaction replaced with `startSpan()`, integrations converted to functions
- ESM initialization pattern applied (separate `instrument.mjs` file)
- `@sentry/tracing` package removed (functionality built into core packages)
- Bundler plugins updated to v2.14.2+
- Post-migration test events captured successfully in Sentry dashboard
- Source maps verified, traces propagating across services

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot find module '@sentry/hub'` | Package removed in v8 | Replace hub imports with `@sentry/node` scope APIs |
| `Sentry.startTransaction is not a function` | API removed in v8 | Use `Sentry.startSpan()` callback pattern instead |
| `new Integrations.X is not a constructor` | Classes removed in v8 | Use functional form: `Sentry.xIntegration()` |
| `Cannot find module '@sentry/tracing'` | Package removed in v8 | Remove import; tracing is built into `@sentry/node` v8 |
| Mixed version runtime crash | Some `@sentry/*` at v7, others at v8 | Align all packages: `npm install @sentry/node@8 @sentry/browser@8` |
| `ERR_MODULE_NOT_FOUND` on startup | ESM init file missing or wrong path | Create `instrument.mjs`, run with `node --import ./instrument.mjs` |
| Source maps not resolving | Bundler plugin version incompatible | Update `@sentry/webpack-plugin` or `@sentry/vite-plugin` to v2.14.2+ |
| Python `AttributeError: configure_scope` | API removed in Python SDK v2 | Use `sentry_sdk.get_current_scope()` instead |
| `Transport.send must return object` | Custom transport missing return | Return `{ statusCode: 200 }` from `makeRequest()` |
| Node.js version error | SDK v8 requires Node 18.19+ or 20.6+ | Upgrade Node.js: `nvm install 20 && nvm use 20` |

See [errors.md](references/errors.md) for additional error patterns.

## Examples

**Example 1: Full v7 to v8 JavaScript Migration**

Request: "Upgrade our Express app from Sentry v7 to v8"

```bash
# Detect current state
npm ls 2>/dev/null | command grep "@sentry/"
# @sentry/node@7.114.0
# @sentry/tracing@7.114.0

# Run codemod
npx @sentry/migr8@latest

# Upgrade packages
npm install @sentry/node@8
npm uninstall @sentry/tracing
```

Before (v7 Express setup):

```typescript
import * as Sentry from '@sentry/node';
import { Integrations } from '@sentry/tracing';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [new Integrations.Express({ app })],
  tracesSampleRate: 0.2,
});

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());
// ... routes
app.use(Sentry.Handlers.errorHandler());
```

After (v8 Express setup):

```typescript
// instrument.mjs — must be separate file
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.2,
});

// app.mjs — run with: node --import ./instrument.mjs app.mjs
import express from 'express';
import * as Sentry from '@sentry/node';

const app = express();

// v8: Sentry auto-instruments Express — no manual handlers needed
// Sentry.Handlers.requestHandler() and tracingHandler() are removed
// Error handler replaced with Sentry.setupExpressErrorHandler()
Sentry.setupExpressErrorHandler(app);

app.listen(3000);
```

Result: SDK upgraded to v8.49.0, `@sentry/tracing` removed, Express auto-instrumented, source maps verified, test error captured in dashboard.

**Example 2: Python v1 to v2 Migration**

Request: "Upgrade sentry-sdk from 1.x to 2.x in our Flask app"

```python
# Before (v1)
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="...",
    integrations=[FlaskIntegration()],
)

with sentry_sdk.configure_scope() as scope:
    scope.set_tag("deploy", "v2.1")

# After (v2)
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="...",
    integrations=[FlaskIntegration()],
)

scope = sentry_sdk.get_current_scope()
scope.set_tag("deploy", "v2.1")
```

Result: SDK upgraded to 2.x, `configure_scope` replaced with `get_current_scope`, `push_scope` replaced with `new_scope`, Flask integration unchanged, test error captured.

## Resources

- [JavaScript v7 to v8 Migration Guide](https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/)
- [Node.js v7 to v8 Guide](https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/)
- [Express v7 to v8 Guide](https://docs.sentry.io/platforms/javascript/guides/express/migration/v7-to-v8/)
- [Python SDK v1 to v2 Migration](https://docs.sentry.io/platforms/python/migration/1.x-to-2.x/)
- [@sentry/migr8 Codemod Tool](https://github.com/getsentry/sentry-migr8)
- [Sentry SDK Changelog](https://github.com/getsentry/sentry-javascript/blob/develop/CHANGELOG.md)

## Next Steps

- Run sentry-performance-tracing to configure v8 span-based tracing
- Run sentry-ci-integration to update CI source map upload after SDK change
- Run sentry-release-management to tag the upgraded release
- Run sentry-known-pitfalls to review common post-upgrade issues
