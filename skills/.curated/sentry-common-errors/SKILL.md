---
name: sentry-common-errors
description: 'Troubleshoot common Sentry integration issues and fixes.

  Use when encountering Sentry errors, missing events, source map

  failures, rate limits, or configuration problems.

  Trigger: "sentry not working", "sentry errors missing", "fix sentry",

  "sentry troubleshoot", "sentry 429", "source maps not resolving",

  "sentry events not showing", "sentry flush", "sentry CORS".

  '
allowed-tools: Read, Grep, Bash(npm:*), Bash(node:*), Bash(curl:*), Bash(npx:*), Bash(sentry-cli:*),
  Bash(python3:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- troubleshooting
- debugging
- error-monitoring
compatibility: Designed for Claude Code
---
# Sentry Common Errors

## Overview

Diagnose and fix the most frequently encountered Sentry SDK integration issues across Node.js, browser, and Python environments. Covers DSN validation, missing events, source map failures, rate limiting, SDK initialization ordering, serverless flush patterns, CORS configuration, and environment tagging.

## Prerequisites

- Sentry SDK installed (`@sentry/node` v8+, `@sentry/browser` v8+, or `sentry-sdk` for Python)
- Access to Sentry dashboard with project admin or member role
- Application logs available for inspection
- `sentry-cli` installed for source map and release operations

## Instructions

### Step 1 — Detect the installed SDK and current configuration

!`npm list @sentry/node @sentry/browser @sentry/react @sentry/nextjs 2>/dev/null | head -10 || echo "No Node.js Sentry SDK found"`

!`python3 -c "import sentry_sdk; print(f'sentry-sdk {sentry_sdk.VERSION}')" 2>/dev/null || echo "No Python sentry-sdk found"`

!`command -v sentry-cli >/dev/null && sentry-cli --version || echo "sentry-cli not installed"`

Grep the project for Sentry initialization to identify the current configuration:

```bash
grep -rn "Sentry.init\|sentry_sdk.init" --include="*.ts" --include="*.js" --include="*.mjs" --include="*.py" . 2>/dev/null | head -20
```

### Step 2 — DSN not set or invalid DSN format

The DSN (Data Source Name) tells the SDK where to send events. Format: `https://<public-key>@<org>.ingest.sentry.io/<project-id>`

**Symptoms:** No events arrive. SDK silently does nothing. `debug: true` shows "No DSN provided."

```typescript
// WRONG — DSN is undefined because env var is missing or misspelled
Sentry.init({
  dsn: process.env.SENTRI_DSN, // Typo in env var name
});

// CORRECT — validate DSN is present before init
const dsn = process.env.SENTRY_DSN;
if (!dsn) {
  console.error('SENTRY_DSN environment variable is not set');
  process.exit(1);
}
Sentry.init({
  dsn: dsn.trim(),
  debug: true, // Enable during troubleshooting
});
```

**Python equivalent:**

```python
import os, sentry_sdk

dsn = os.environ.get("SENTRY_DSN")
if not dsn:
    raise RuntimeError("SENTRY_DSN not set")

sentry_sdk.init(dsn=dsn.strip(), debug=True)
```

### Step 3 — Events not appearing in dashboard

**Symptoms:** `Sentry.captureException()` runs without errors, but nothing shows up in the Sentry web UI.

**Root causes and fixes:**

1. **`beforeSend` accidentally returning null:**

```typescript
// WRONG — missing return drops all non-exception events
beforeSend(event) {
  if (event.exception) {
    event.tags = { ...event.tags, has_exception: 'true' };
    return event;
  }
  // Implicit return undefined = event DROPPED
}

// CORRECT — always return event unless you explicitly want to filter
beforeSend(event) {
  if (event.message?.includes('ResizeObserver loop')) {
    return null; // Intentionally drop
  }
  if (event.exception) {
    event.tags = { ...event.tags, has_exception: 'true' };
  }
  return event; // ALWAYS return at the end
}
```

1. **`sampleRate` set to 0:**

```typescript
// WRONG
Sentry.init({ sampleRate: 0, tracesSampleRate: 0 }); // Nothing is sent

// CORRECT
Sentry.init({ sampleRate: 1.0, tracesSampleRate: 0.1 });
```

1. **Missing `await Sentry.flush()` in serverless / CLI contexts:**

```typescript
// WRONG — Lambda/CLI process exits before SDK sends the event
export const handler = async (event) => {
  try {
    return await processRequest(event);
  } catch (error) {
    Sentry.captureException(error);
    throw error; // Process exits, event never sent!
  }
};

// CORRECT — flush before returning
export const handler = async (event) => {
  try {
    return await processRequest(event);
  } catch (error) {
    Sentry.captureException(error);
    await Sentry.flush(2000); // Wait up to 2s for event to send
    throw error;
  }
};
```

**Python (AWS Lambda):**

```python
def handler(event, context):
    try:
        return process_request(event)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.flush(timeout=2)  # CRITICAL for Lambda
        raise
```

1. **SDK initialized after error occurs:**

```typescript
// WRONG — error happens before Sentry.init()
import express from 'express';
app.get('/', () => { throw new Error('boom'); }); // Sentry not ready

import * as Sentry from '@sentry/node';
Sentry.init({ dsn: '...' }); // Too late

// CORRECT — Sentry FIRST
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: '...' });
import express from 'express';
```

**Diagnostic checklist for missing events:**

```bash
# 1. Verify DSN is present
echo "DSN set: ${SENTRY_DSN:+yes}"

# 2. Enable debug mode and send test event
node -e "
const Sentry = require('@sentry/node');
Sentry.init({ dsn: process.env.SENTRY_DSN, debug: true });
const id = Sentry.captureMessage('Test from CLI', 'info');
console.log('Event ID:', id);
Sentry.flush(5000).then(() => console.log('Flush complete'));
"

# 3. Check Sentry service status
curl -s https://status.sentry.io/api/v2/status.json | python3 -c "
import sys, json; d = json.load(sys.stdin)
print(f\"Status: {d['status']['description']}\")
" 2>/dev/null || echo "Could not reach status.sentry.io"
```

### Step 4 — Source maps not resolving

**Symptoms:** Stack traces in Sentry show minified variable names and wrong line numbers.

**Root cause 1 — Release version mismatch:** The `release` in `Sentry.init()` must exactly match the release name used during `sentry-cli` upload.

```typescript
Sentry.init({ dsn: process.env.SENTRY_DSN, release: 'my-app@1.2.3' });
```

```bash
# During build/deploy — same version string
export VERSION="my-app@1.2.3"
sentry-cli releases new "$VERSION"
sentry-cli releases files "$VERSION" upload-sourcemaps ./dist \
  --url-prefix '~/static/js'   # Must match how browser loads the files
sentry-cli releases finalize "$VERSION"
```

**Root cause 2 — URL prefix mismatch:**

```bash
# Diagnose with the explain command
sentry-cli sourcemaps explain --org "$SENTRY_ORG" --project "$SENTRY_PROJECT" EVENT_ID
# List uploaded artifacts to verify
sentry-cli releases files "$VERSION" list
```

**Root cause 3 — Source maps uploaded after error occurred:** Sentry does not retroactively apply source maps. Upload before the release goes live.

**Root cause 4 — Build tool not generating source maps:**

```javascript
// webpack: devtool: 'source-map'
// vite: build: { sourcemap: true }
```

### Step 5 — 429 rate limit errors

**Symptoms:** Sentry returns HTTP 429. Events are dropped.

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  sampleRate: 0.25,              // Send 25% of errors
  tracesSampleRate: 0.01,        // 1% of transactions
  maxBreadcrumbs: 20,            // Reduce from default 100
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    /Loading chunk \d+ failed/,
    /Failed to fetch/,
  ],
  beforeSend(event) {
    const frames = event.exception?.values?.[0]?.stacktrace?.frames || [];
    if (frames.some(f => f.filename?.includes('extension://'))) return null;
    return event;
  },
});
```

**Check quota:** Settings > Projects > [Project] > Client Keys > Configure > Rate Limiting.

### Step 6 — SDK version conflicts

**Symptoms:** `TypeError: Sentry.X is not a function`, duplicate events, or missing integrations.

```bash
# All @sentry/* packages must share the same major version
npm list | grep @sentry 2>/dev/null
# Fix: npm install @sentry/node@latest @sentry/browser@latest
```

**SDK v8 breaking change:** `@sentry/tracing` is removed. Tracing is built into the core:

```typescript
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: '...', tracesSampleRate: 0.1 }); // No @sentry/tracing needed
```

### Step 7 — Wrong environment tag

```typescript
// WRONG — hardcoded, same value in dev and prod
Sentry.init({ environment: 'production' });

// CORRECT — derive from runtime
Sentry.init({ dsn: process.env.SENTRY_DSN, environment: process.env.NODE_ENV || 'development' });
```

### Step 8 — CORS issues with browser SDK

The standard SDK sends to `https://<org>.ingest.sentry.io` which has permissive CORS. If you see CORS errors:

1. **CSP blocking** — add `connect-src 'self' https://*.ingest.sentry.io` to your CSP
2. **Tunnel misconfiguration** — your tunnel endpoint must proxy and return CORS headers
3. **Ad blockers** — use the `tunnel` option to route through your domain

```typescript
Sentry.init({ dsn: process.env.SENTRY_DSN, tunnel: '/api/sentry-tunnel' });
```

### Step 9 — Node.js process exits before events are sent

The SDK batches events asynchronously. Short-lived processes must flush before exit.

```typescript
async function main() {
  try { await doWork(); }
  catch (error) { Sentry.captureException(error); }
  finally { await Sentry.flush(5000); } // CRITICAL
}

// Graceful shutdown for servers
process.on('SIGTERM', async () => {
  await Sentry.flush(5000);
  server.close(() => process.exit(0));
});
```

### Step 10 — Express "not instrumented" warning

Sentry must initialize before importing Express so it can monkey-patch HTTP modules:

```typescript
// instrument.mjs — imported first
import * as Sentry from '@sentry/node';
Sentry.init({ dsn: process.env.SENTRY_DSN, tracesSampleRate: 0.1 });

// app.mjs
import './instrument.mjs'; // FIRST
import express from 'express';
const app = express();
Sentry.setupExpressErrorHandler(app); // After all routes
```

Or use `node --import ./instrument.mjs app.mjs`.

## Output

- Root cause identified from the diagnostic steps above
- Configuration fix applied and verified with a test event
- `debug: true` output confirming SDK initialization and event delivery
- Test event visible in Sentry dashboard (search by Event ID)
- `debug: true` removed after issue is resolved

## Error Handling

| Error / Symptom | Cause | Solution |
|-----------------|-------|----------|
| `Invalid Sentry Dsn` | Malformed or empty DSN string | Re-copy DSN from Project Settings > Client Keys. Verify format: `https://<key>@<org>.ingest.sentry.io/<id>` |
| No events in dashboard | `beforeSend` returns `undefined` on some code paths | Add explicit `return event` as the last line of `beforeSend`. Use `return null` only for intentional filtering |
| No events in dashboard | `sampleRate` set to `0` | Set `sampleRate: 1.0` (default) for errors. Use fractional values only for `tracesSampleRate` |
| No events in serverless/CLI | Process exits before SDK flushes its queue | Add `await Sentry.flush(2000)` before `process.exit()`, Lambda return, or CLI exit |
| Minified stack traces | Source map release version does not match `Sentry.init({ release })` | Ensure `release` string is identical in both `Sentry.init()` and `sentry-cli releases` upload |
| Minified stack traces | `--url-prefix` does not match browser JS URL path | Run `sentry-cli sourcemaps explain EVENT_ID` to diagnose the prefix |
| `429 Too Many Requests` | Project or org quota exceeded | Lower `sampleRate`/`tracesSampleRate`, add `ignoreErrors`, set server-side rate limits |
| `TypeError: Sentry.X is not a function` | Mixed SDK major versions (v7 + v8) | Run `npm list @sentry/core` to find duplicates. Upgrade all `@sentry/*` to same major |
| Express not instrumented | `Sentry.init()` called after `import express` | Move init to `instrument.mjs` and import first, or use `node --import` |
| Wrong environment in events | `environment` hardcoded or not set | Set `environment: process.env.NODE_ENV` in `Sentry.init()` |
| CORS errors in browser | CSP blocking `*.ingest.sentry.io` or tunnel missing headers | Add `connect-src https://*.ingest.sentry.io` to CSP, or fix tunnel CORS |
| Duplicate events | Error captured at multiple layers | Capture at ONE level only — catch block OR error middleware, not both |
| Missing stack traces | `Sentry.captureException('string')` instead of Error | Always pass `new Error('message')` — strings have no stack trace |
| ESM `ERR_REQUIRE_ESM` | Node.js version below 18.19 for ESM support | Upgrade to Node.js 18.19+ or 20.6+. Use `--import` flag |

## Examples

**Example 1: Debug missing events in a Next.js app**
Request: "Sentry captureException runs but nothing shows in the dashboard"
Steps: Enable `debug: true` in `Sentry.init()`. Console showed "No DSN provided." The `NEXT_PUBLIC_SENTRY_DSN` env var was not set in `.env.production`. Added the variable, redeployed, confirmed events arrive within seconds.

**Example 2: Fix source maps in a Vite + React app**
Request: "Stack traces in Sentry are all minified"
Steps: Ran `sentry-cli sourcemaps explain EVENT_ID` which reported "source map not found for URL ~/assets/index-abc123.js". The `--url-prefix` was `~/dist` but Vite serves from `~/assets`. Fixed to `--url-prefix '~/assets'` and re-uploaded. Stack traces now resolve correctly.

**Example 3: Lambda events disappearing**
Request: "Sentry.captureException works locally but not in AWS Lambda"
Steps: Added `await Sentry.flush(2000)` before the Lambda handler returns. Events now arrive consistently. Wrapped handler with `Sentry.wrapHandler()` for automatic scope management.

## Resources

- [JavaScript Troubleshooting Guide](https://docs.sentry.io/platforms/javascript/troubleshooting/)
- [Source Maps Troubleshooting](https://docs.sentry.io/platforms/javascript/sourcemaps/troubleshooting_js/)
- [Python Troubleshooting](https://docs.sentry.io/platforms/python/troubleshooting/)
- [Filtering & Sampling Events](https://docs.sentry.io/platforms/javascript/configuration/filtering/)
- [sentry-cli Source Maps Upload](https://docs.sentry.io/cli/releases/#upload-source-maps)
- [Sentry Service Status](https://status.sentry.io)
- [SDK Migration Guide v7 to v8](https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/)

## Next Steps

- After fixing, send a test event with `Sentry.captureMessage('verify-fix', 'info')` and confirm it appears
- Disable `debug: true` before deploying to production
- Consider setting up [Sentry alerts](https://docs.sentry.io/product/alerts/) to catch future issues early
- Review the `sentry-rate-limits` skill if you hit 429 errors frequently
- Review the `sentry-release-management` skill for source map upload automation
