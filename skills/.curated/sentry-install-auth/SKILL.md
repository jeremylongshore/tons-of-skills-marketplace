---
name: sentry-install-auth
description: 'Install and configure Sentry SDK authentication with DSN setup.

  Use when setting up Sentry error tracking, configuring DSN,

  or initializing Sentry in a Node.js or Python project.

  Trigger with "install sentry", "setup sentry", "sentry auth",

  "configure sentry DSN".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Grep
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- monitoring
- error-tracking
compatibility: Designed for Claude Code
---
# Sentry Install & Auth

## Overview

Install the Sentry SDK, configure DSN-based authentication, and verify error tracking is operational. Covers Node.js (`@sentry/node`), browser (`@sentry/browser`), and Python (`sentry-sdk`) with environment-based configuration and auth token setup for CLI/CI workflows.

## Prerequisites

- Node.js 18.19+ or 20.6+ (required for ESM support in Sentry SDK v8)
- Package manager: npm, pnpm, or pip
- Sentry account with a project created at https://sentry.io
- DSN from **Project Settings > Client Keys (DSN)**
- For CLI/CI: auth token from https://sentry.io/settings/auth-tokens/

## Instructions

### Step 1 — Install the SDK

**Node.js / TypeScript:**

```bash
npm install @sentry/node
# For profiling support (optional):
npm install @sentry/profiling-node
```

**Browser / Framework-specific:**

```bash
npm install @sentry/browser
# Or pick your framework:
npm install @sentry/react    # React
npm install @sentry/nextjs   # Next.js
npm install @sentry/vue      # Vue
```

**Python:**

```bash
pip install sentry-sdk
```

### Step 2 — Store the DSN securely

The DSN (Data Source Name) tells the SDK where to send events. It looks like `https://<key>@<org>.ingest.sentry.io/<project-id>`. Never hardcode it — use environment variables.

```bash
# .env (add this file to .gitignore)
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=1.0.0
```

For production, store the DSN in your secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, etc.) and inject it at deploy time.

### Step 3 — Initialize the SDK

**Node.js (ESM) — create `instrument.mjs` at project root:**

This file MUST be imported before any other modules. The `--import` flag ensures Sentry instruments HTTP, database, and framework integrations via monkey-patching at load time.

```typescript
// instrument.mjs — import BEFORE your app code
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT || 'development',
  release: process.env.SENTRY_RELEASE,

  // Performance: 100% in dev, 10-20% in production
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,

  // Debug mode — disable in production
  debug: process.env.NODE_ENV !== 'production',

  // Never send PII by default
  sendDefaultPii: false,

  integrations: [
    // Built-in integrations (httpIntegration, expressIntegration)
    // are auto-detected — no manual registration needed
  ],
});
```

**Start your app with the `--import` flag:**

```bash
node --import ./instrument.mjs app.mjs
```

Or in `package.json`:

```json
{
  "scripts": {
    "start": "node --import ./instrument.mjs app.mjs"
  }
}
```

**Browser:**

```typescript
import * as Sentry from '@sentry/browser';

Sentry.init({
  dsn: process.env.SENTRY_DSN, // injected at build time
  environment: process.env.NODE_ENV,
  release: process.env.SENTRY_RELEASE,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
});
```

**Python:**

```python
import os
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    release=os.environ.get("SENTRY_RELEASE"),
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

### Step 4 — Verify the installation

Send a test event and confirm it appears in the Sentry dashboard:

**Node.js:**

```typescript
import * as Sentry from '@sentry/node';

Sentry.captureMessage('Sentry SDK installed successfully', 'info');

// Ensure the event is flushed before process exits
await Sentry.flush(2000);
```

**Python:**

```python
import sentry_sdk

sentry_sdk.capture_message("Sentry SDK installed successfully")

# Ensure the event is flushed
sentry_sdk.flush(timeout=2)
```

Check the **Issues** tab in your Sentry project within 30 seconds. If the message appears, authentication is working.

### Step 5 — Set up auth token for CLI and CI

The DSN authenticates the SDK for sending events. For the Sentry CLI (source maps, releases, deploys), you need a separate **auth token**.

Generate one at https://sentry.io/settings/auth-tokens/ with scopes:

- `project:releases` — create releases and upload source maps
- `org:read` — read organization data

```bash
# Install Sentry CLI
npm install -g @sentry/cli

# Set the token
export SENTRY_AUTH_TOKEN=sntrys_YOUR_TOKEN_HERE

# Verify auth works
sentry-cli info
```

In CI, store `SENTRY_AUTH_TOKEN` as a secret environment variable.

## Output

- SDK package installed (`@sentry/node`, `@sentry/browser`, or `sentry-sdk`)
- DSN stored in environment variables (never committed to git)
- `instrument.mjs` created and loaded before app entry point (Node.js)
- Sentry initialized with environment, release, and sample rates configured
- Test event visible in Sentry dashboard confirming DSN auth works
- Auth token configured for CLI/CI workflows (optional)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid Sentry Dsn` | Malformed DSN string | Copy DSN exactly from Project Settings > Client Keys (DSN). Format: `https://<key>@<org>.ingest.sentry.io/<project-id>` |
| Events not appearing in dashboard | DSN env var not loaded | Verify with `console.log(process.env.SENTRY_DSN)` before `Sentry.init()`. Check `.env` is loaded (use `dotenv` or framework equivalent) |
| HTTP 401 Unauthorized | Invalid or revoked auth token | Regenerate token at https://sentry.io/settings/auth-tokens/. Verify with `sentry-cli info` |
| HTTP 429 Too Many Requests | Rate-limited by Sentry | Lower `tracesSampleRate`. Check quota at Settings > Subscription. Events are dropped, not queued |
| `Express is not instrumented` | SDK initialized after Express import | Move `import './instrument.mjs'` to first line or use `--import` flag. SDK must load before any framework imports |
| HTTP 403 Forbidden | Auth token missing required scopes | Regenerate token with `project:releases` and `org:read` scopes |
| `ECONNREFUSED` / network errors | Sentry ingest endpoint unreachable | Check https://status.sentry.io for outages. Verify firewall allows `*.ingest.sentry.io` on port 443 |
| ESM compatibility error | Node.js < 18.19 or < 20.6 | Upgrade Node.js. SDK v8 requires these minimum versions for ESM `--import` support |

## Examples

**Express.js with full error handler:**

```typescript
// instrument.mjs
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT || 'development',
  tracesSampleRate: 0.2,
});
```

```typescript
// app.mjs — start with: node --import ./instrument.mjs app.mjs
import * as Sentry from '@sentry/node';
import express from 'express';

const app = express();

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/api/debug-sentry', (req, res) => {
  throw new Error('Sentry test error');
});

// Sentry error handler must be registered after all routes
Sentry.setupExpressErrorHandler(app);

// Fallback error handler
app.use((err, req, res, next) => {
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(3000, () => console.log('Server running on :3000'));
```

**Python Flask:**

```python
import os
import sentry_sdk
from flask import Flask

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    traces_sample_rate=0.2,
    send_default_pii=False,
)

app = Flask(__name__)

@app.route("/api/health")
def health():
    return {"status": "ok"}

@app.route("/api/debug-sentry")
def debug_sentry():
    raise Exception("Sentry test error")  # Automatically captured
```

**Graceful shutdown with flush:**

```typescript
import * as Sentry from '@sentry/node';

process.on('SIGTERM', async () => {
  console.log('Shutting down gracefully...');
  await Sentry.flush(5000); // wait up to 5s for pending events
  process.exit(0);
});
```

## Resources

- [Node.js Setup Guide](https://docs.sentry.io/platforms/javascript/guides/node/)
- [Browser SDK Setup](https://docs.sentry.io/platforms/javascript/)
- [Python SDK Setup](https://docs.sentry.io/platforms/python/)
- [Configuration Options](https://docs.sentry.io/platforms/javascript/configuration/options/)
- [SDK Migration v7 to v8](https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/)
- [Auth Tokens](https://docs.sentry.io/account/auth-tokens/)
- [Sentry Status Page](https://status.sentry.io)

## Next Steps

For configuring alerts and issue management, see `sentry-alerts-config`.
