---
name: sentry-known-pitfalls
description: 'Identify and fix common Sentry SDK pitfalls that cause silent data loss,

  cost overruns, and missed alerts. Covers 10 anti-patterns with fix code.

  Use when auditing Sentry config, debugging missing events, or reviewing

  SDK setup. Trigger: "sentry pitfalls", "sentry anti-patterns",

  "sentry mistakes", "why are sentry events missing".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(node:*), Bash(npm:*), Bash(npx:*),
  Bash(grep:*), Bash(find:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- anti-patterns
- troubleshooting
- best-practices
- sdk
- configuration
compatibility: Designed for Claude Code
---
# Sentry Known Pitfalls

## Overview

Ten production-grade Sentry SDK anti-patterns that silently break error tracking, inflate costs, or leave teams blind to failures. Each pitfall includes the broken pattern, root cause, and production-ready fix.

For extended code samples and audit scripts, see [configuration pitfalls](references/configuration-pitfalls.md), [error capture pitfalls](references/error-capture-pitfalls.md), [SDK initialization pitfalls](references/sdk-initialization-pitfalls.md), [integration pitfalls](references/integration-pitfalls.md), and [monitoring pitfalls](references/monitoring-pitfalls.md).

## Prerequisites

- Active Sentry project with `@sentry/node` >= 8.x or `@sentry/browser` >= 8.x
- Access to the codebase containing `Sentry.init()` configuration
- Environment variable management (`.env`, secrets manager, or CI/CD vars)

## Instructions

### Step 1: Scan for Existing Pitfalls

```bash
# Hardcoded DSNs (Pitfall 1)
grep -rn "ingest\.sentry\.io" --include="*.ts" --include="*.js" src/

# 100% sample rates (Pitfall 2)
grep -rn "sampleRate.*1\.0" --include="*.ts" --include="*.js" src/

# Missing flush calls (Pitfall 3)
grep -rn "Sentry\.flush\|Sentry\.close" --include="*.ts" --include="*.js" src/

# Wrong SDK imports (Pitfall 8)
grep -rn "@sentry/node" --include="*.tsx" --include="*.jsx" src/
```

### Step 2: Pitfall 1 — Hardcoding DSN in Source Code

DSN in source ships in client bundles and cannot be rotated without a deploy. Attackers flood your project with garbage events.

```typescript
// WRONG
Sentry.init({
  dsn: 'https://abc123@o123456.ingest.us.sentry.io/7890123',
});

// RIGHT — environment variable
Sentry.init({ dsn: process.env.SENTRY_DSN });

// RIGHT — browser apps: build-time injection (Vite)
// vite.config.ts: define: { __SENTRY_DSN__: JSON.stringify(process.env.SENTRY_DSN) }
// app.ts: Sentry.init({ dsn: __SENTRY_DSN__ });
```

### Step 3: Pitfall 2 — `sampleRate: 1.0` in Production

100% sampling sends every trace. At 500K requests/day, overage is ~$371/month.

```typescript
// WRONG
Sentry.init({ tracesSampleRate: 1.0 });

// RIGHT — endpoint-specific sampling
Sentry.init({
  tracesSampler: ({ name, parentSampled }) => {
    if (typeof parentSampled === 'boolean') return parentSampled;
    if (name?.match(/\/(health|ping|ready)/)) return 0;
    if (name?.includes('/checkout')) return 0.25;
    return 0.01;  // 1% default
  },
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### Step 4: Pitfall 3 — Not Calling `flush()` in Serverless/CLI

Sentry queues events in memory. Serverless/CLI processes exit before the queue drains — events never reach Sentry.

```typescript
// WRONG — Lambda exits, events lost
export const handler = async (event) => {
  try { return await processEvent(event); }
  catch (error) {
    Sentry.captureException(error);
    throw error;  // Queue never drains
  }
};

// RIGHT — flush before exit
export const handler = async (event) => {
  try { return await processEvent(event); }
  catch (error) {
    Sentry.captureException(error);
    await Sentry.flush(2000);
    throw error;
  }
};

// BEST — use @sentry/aws-serverless wrapper
import * as Sentry from '@sentry/aws-serverless';
export const handler = Sentry.wrapHandler(async (event) => {
  return await processEvent(event);
});
```

### Step 5: Pitfall 4 — `beforeSend` Returning `null` for All Events

Missing `return event` causes JavaScript to return `undefined`, which Sentry treats as "drop." A single missing return kills all tracking.

```typescript
// WRONG — non-error events silently vanish
Sentry.init({
  beforeSend(event) {
    if (event.level === 'error') return event;
    // Falls through — undefined — ALL non-errors dropped
  },
});

// RIGHT — always return event as the last line
Sentry.init({
  beforeSend(event, hint) {
    const error = hint?.originalException;
    if (error instanceof Error && error.message.match(/^NetworkError/)) {
      return null;  // Explicit drop
    }
    return event;  // Always the last line
  },
});
```

### Step 6: Pitfall 5 — Release Version Mismatch (SDK vs Source Maps)

SDK `release` must exactly match `sentry-cli releases new`. A `v` prefix mismatch means source maps never apply.

```typescript
// WRONG — "1.2.3" vs "v1.2.3"
Sentry.init({ release: process.env.npm_package_version });
// CLI: sentry-cli releases new "v1.2.3"

// RIGHT — single source of truth
const SENTRY_RELEASE = `myapp@${process.env.GIT_SHA || 'dev'}`;
Sentry.init({ release: SENTRY_RELEASE });
```

```bash
# CI — same variable feeds both SDK and CLI
export SENTRY_RELEASE="myapp@$(git rev-parse --short HEAD)"
npx sentry-cli releases new "$SENTRY_RELEASE"
npx sentry-cli sourcemaps upload --release="$SENTRY_RELEASE" \
  --url-prefix="~/static/js" ./dist/static/js/
npx sentry-cli releases finalize "$SENTRY_RELEASE"
```

### Step 7: Pitfall 6 — Catching Errors Without Re-Throwing

Capturing to Sentry but not re-throwing means the function returns `undefined`. Downstream code breaks silently.

```typescript
// WRONG — returns undefined
async function getUser(id: string) {
  try {
    return await fetch(`/api/users/${id}`).then(r => r.json());
  } catch (error) {
    Sentry.captureException(error);
    // Returns undefined — callers get TypeError
  }
}

// RIGHT — capture and re-throw
async function getUser(id: string) {
  try {
    return await fetch(`/api/users/${id}`).then(r => r.json());
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
}
```

### Step 8: Pitfall 7 — Missing `environment` Tag

Without `environment`, dev errors pollute prod dashboards. Alert rules fire on local noise. Issue counts are inflated.

```typescript
// WRONG
Sentry.init({ dsn: process.env.SENTRY_DSN });

// RIGHT
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'development',
});

// For Vercel/Railway preview environments:
function getSentryEnvironment(): string {
  if (process.env.VERCEL_ENV) return process.env.VERCEL_ENV;
  if (process.env.RAILWAY_ENVIRONMENT) return process.env.RAILWAY_ENVIRONMENT;
  return process.env.NODE_ENV || 'development';
}
```

### Step 9: Pitfall 8 — Importing `@sentry/node` in Browser Bundle

`@sentry/node` depends on Node.js built-ins (`http`, `fs`). Browser import causes build failures, 100KB+ polyfill bloat, or runtime crashes.

```typescript
// WRONG
import * as Sentry from '@sentry/node';  // In React/Vue/browser code

// RIGHT — platform-specific SDK
import * as Sentry from '@sentry/react';     // React
import * as Sentry from '@sentry/vue';       // Vue
import * as Sentry from '@sentry/nextjs';    // Next.js (client + server)
import * as Sentry from '@sentry/node';      // Server-only
import * as Sentry from '@sentry/aws-serverless';  // AWS Lambda
```

### Step 10: Pitfall 9 — Ignoring `429 Too Many Requests`

When quota is exceeded, Sentry returns 429 and the SDK silently drops events. You lose data during peak traffic — exactly when you need it most.

**Prevention:**

1. Enable **Spike Protection** in Sentry Organization Settings
2. Set **per-key rate limits** in Project Settings > Client Keys
3. Monitor client reports: Project Settings > Client Keys > Stats

```typescript
// Client-side circuit breaker for resilience
let sentryBackoff = 0;
Sentry.init({
  beforeSend(event) {
    if (Date.now() < sentryBackoff) return null;
    return event;
  },
});
```

### Step 11: Pitfall 10 — No Alert Rules Configured

Sentry collects errors but does not notify anyone by default. Without alerts, critical bugs go unnoticed for hours.

**Three-tier alert structure:**

| Tier | Trigger | Channel |
|------|---------|---------|
| Immediate | New fatal/error issue in prod | PagerDuty |
| Urgent | Error rate > 100 events in 5 min | Slack #alerts |
| Awareness | Issue unresolved > 7 days | Email digest |

Set up in Sentry UI: **Alerts > Create Alert > Issue Alert** (Tier 1) or **Metric Alert** (Tier 2). See [monitoring pitfalls](references/monitoring-pitfalls.md) for API-based alert creation.

### Step 12: Run the Full Audit Checklist

See [audit script](references/configuration-pitfalls.md) for a bash script that checks all 10 pitfalls in one pass.

## Output

- Audit report listing which of the 10 pitfalls were found
- Code changes applied for each identified pitfall
- Confirmation that `beforeSend` returns `event` on all paths
- `environment` and `release` properly configured
- Alert rules created or recommended (three tiers)

## Error Handling

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Hardcoded DSN | Spam events from attackers | `process.env.SENTRY_DSN` or build-time injection |
| `sampleRate: 1.0` | 10-50x cost overrun | `tracesSampler` with per-endpoint rates |
| No `flush()` | Zero events from Lambda/CLI | `await Sentry.flush(2000)` before exit |
| `beforeSend` drops all | Events silently vanish | Always end with `return event` |
| Release mismatch | Minified stack traces | Single `SENTRY_RELEASE` env var |
| Swallowed catch | Cascading undefined errors | Re-throw after capture |
| No `environment` | Dev noise in prod dashboard | `environment: process.env.NODE_ENV` |
| Wrong SDK import | Build failure or bloat | Platform-specific SDK package |
| Ignoring 429s | Data loss at peak traffic | Spike protection + circuit breaker |
| No alerts | Bugs accumulate unnoticed | Three-tier alert rules |

## Examples

**Example 1: Full-stack audit of existing Sentry setup**

Request: "Audit our Sentry integration for common mistakes"

Result: Found hardcoded DSN in `config.ts` (Pitfall 1), 100% `tracesSampleRate` (Pitfall 2), no `environment` tag (Pitfall 7), and zero alert rules (Pitfall 10). Applied fixes for all four, added CI gate for DSN detection, created three-tier alert config. See [examples](references/examples.md) for more scenarios.

**Example 2: Debugging missing Lambda errors**

Request: "Sentry shows no errors from our Lambda functions but we know they're failing"

Result: Identified Pitfall 3 — no `flush()` call before Lambda return. Wrapped all handlers with `Sentry.wrapHandler()` from `@sentry/aws-serverless`. Events now appear within 5 seconds of invocation.

**Example 3: Source map stack traces showing minified code**

Request: "Sentry stack traces are all minified even though we upload source maps"

Result: SDK used `release: "2.1.0"` while CLI used `"v2.1.0"` (Pitfall 5). Unified both to `$GIT_SHA` via shared `SENTRY_RELEASE` env var. Stack traces now show original TypeScript source.

## Resources

- [Sentry JavaScript Troubleshooting](https://docs.sentry.io/platforms/javascript/troubleshooting/)
- Sentry Best Practices
- [Sentry Configuration Options](https://docs.sentry.io/platforms/javascript/configuration/options/)
- [Sentry Source Maps](https://docs.sentry.io/platforms/javascript/sourcemaps/)
- [Sentry Quota Management](https://docs.sentry.io/pricing/quotas/)
- [Sentry Alerts](https://docs.sentry.io/product/alerts/)

## Next Steps

- Run the scan commands from Step 1 against your codebase
- Fix pitfalls in priority order: Pitfall 1 (security) > Pitfall 3 (data loss) > Pitfall 10 (alerting)
- Add DSN CI gate to prevent regression
- Set up three-tier alert structure before further Sentry work
