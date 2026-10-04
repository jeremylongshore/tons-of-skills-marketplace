---
name: sentry-prod-checklist
description: 'Production deployment checklist for Sentry integration.

  Use when preparing a production deployment, auditing an existing

  Sentry setup, or running a go-live readiness review.

  Trigger: "sentry production checklist", "deploy sentry",

  "sentry go-live", "audit sentry config", "production readiness sentry".

  '
allowed-tools: Read, Grep, Glob, Bash(npm:*), Bash(npx:*), Bash(node:*), Bash(curl:*),
  Bash(sentry-cli:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- deployment
- production
- checklist
- operations
compatibility: Designed for Claude Code
---
# Sentry Production Deployment Checklist

## Overview

Walk through every production-critical Sentry configuration item before a deploy — SDK init options, source map uploads, alert routing, PII scrubbing, sample rate tuning, and test error verification. Covers `@sentry/node` (v8+) and `sentry-cli` workflows.

**Use when:**

- Preparing a first production deploy with Sentry
- Auditing an existing Sentry config after an incident
- Running a go-live readiness review
- Onboarding a new service into Sentry monitoring

## Prerequisites

- `@sentry/node` (or framework-specific SDK like `@sentry/nextjs`, `@sentry/react`) installed
- Sentry project created with a **dedicated production DSN** (separate from dev/staging)
- `sentry-cli` installed globally or as a devDependency (`npm i -D @sentry/cli`)
- `SENTRY_AUTH_TOKEN` with scope `project:releases` available in CI environment
- Build pipeline that produces source maps

## Instructions

Work through each section in order. Check off each item as you verify it.

### Step 1 — DSN and Environment Variables

- [ ] **DSN set via environment variable, not hardcoded in source code**

```typescript
// CORRECT — DSN from environment
Sentry.init({
  dsn: process.env.SENTRY_DSN,
});

// WRONG — hardcoded DSN leaks project ID and org info
Sentry.init({
  dsn: 'https://abc123@o456.ingest.sentry.io/789',
});
```

Verify with: `grep -r "ingest.sentry.io" src/ --include="*.ts" --include="*.js"` — should return zero results.

- [ ] **`SENTRY_DSN` set in production environment** (not just `.env.local`)
- [ ] **`SENTRY_ORG` and `SENTRY_PROJECT` set for CLI operations**

### Step 2 — Environment Tag

- [ ] **`environment` tag set to `'production'`**

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'production',
});
```

This enables environment-scoped alert rules and release health filtering. Without it, all events land in the default (empty) environment.

### Step 3 — Release Tracking

- [ ] **`release` set to match the deploy version**

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: 'production',
  release: process.env.SENTRY_RELEASE || `myapp@${process.env.npm_package_version}`,
});
```

The release value must match exactly what you pass to `sentry-cli releases new`. Mismatches break source map resolution and release health tracking.

### Step 4 — Error Sample Rate

- [ ] **`sampleRate` tuned — not 1.0 in high-traffic production**

```typescript
Sentry.init({
  // For most apps: 0.1 to 0.25 captures enough to spot trends
  // without burning through your event quota
  sampleRate: 0.25, // 25% of errors captured

  // For low-traffic apps or critical services, 1.0 is fine
  // sampleRate: 1.0,
});
```

| Traffic level | Recommended `sampleRate` |
|---------------|--------------------------|
| < 10K errors/day | 1.0 |
| 10K-100K errors/day | 0.25 |
| > 100K errors/day | 0.1 |

### Step 5 — Traces Sample Rate

- [ ] **`tracesSampleRate` tuned (0.05-0.2 for production)**

```typescript
Sentry.init({
  tracesSampleRate: 0.1, // 10% of transactions traced

  // Or use tracesSampler for endpoint-specific rates
  tracesSampler: (samplingContext) => {
    const name = samplingContext.transactionContext?.name || '';

    // Never trace health checks
    if (name.includes('/health') || name.includes('/ready')) return 0;

    // Always trace payments
    if (name.includes('/checkout') || name.includes('/payment')) return 1.0;

    // Default: 10%
    return 0.1;
  },
});
```

Never ship `tracesSampleRate: 1.0` in production — it generates massive event volume and will exhaust your quota within hours on any real workload.

### Step 6 — Source Map Upload

- [ ] **Source maps uploaded via `sentry-cli releases files`**

```bash
#!/bin/bash
# Run in CI after build, before deploy
set -euo pipefail

VERSION="${SENTRY_RELEASE:-$(git rev-parse --short HEAD)}"

# Create the release
sentry-cli releases new "$VERSION"

# Associate commits for suspect commits feature
sentry-cli releases set-commits "$VERSION" --auto

# Upload source maps from build output
sentry-cli releases files "$VERSION" upload-sourcemaps ./dist \
  --url-prefix '~/static/js' \
  --validate

# Mark release as deployed
sentry-cli releases finalize "$VERSION"
sentry-cli releases deploys "$VERSION" new -e production
```

- [ ] `--url-prefix` matches the path where assets are served (e.g., `~/static/js` or `~/assets`)
- [ ] `--validate` flag is used to catch malformed maps at build time
- [ ] Source maps are NOT served to browsers (add to `.gitignore` or strip from deploy artifact)

Verify upload succeeded:

```bash
sentry-cli releases files "$VERSION" list
# Should show .js and .js.map files with correct paths
```

### Step 7 — `beforeSend` Noise Filter

- [ ] **`beforeSend` configured to drop noise**

```typescript
Sentry.init({
  beforeSend(event, hint) {
    const error = hint?.originalException;
    const message = typeof error === 'string' ? error : error?.message || '';

    // Drop browser noise that is never actionable
    const noise = [
      'ResizeObserver loop',
      'Non-Error promise rejection captured',
      /Loading chunk \d+ failed/,
      'Network request failed',
      'AbortError',
      'TypeError: cancelled',
      'TypeError: Failed to fetch',
    ];

    for (const pattern of noise) {
      if (pattern instanceof RegExp ? pattern.test(message) : message.includes(pattern)) {
        return null; // Drop this event
      }
    }

    // Scrub auth headers if they leak into request context
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
      delete event.request.headers['X-API-Key'];
    }

    return event;
  },
});
```

### Step 8 — PII Scrubbing

- [ ] **PII scrubbing enabled: `sendDefaultPii: false`**

```typescript
Sentry.init({
  sendDefaultPii: false, // Do NOT send cookies, user IPs, or auth headers

  // If you need user context, set it explicitly with scrubbed data
  // Sentry.setUser({ id: user.id }); // ID only, no email/name
});
```

Also verify in Sentry project settings:

- **Settings > Security & Privacy > Data Scrubbing** is enabled
- **IP Address** collection is disabled if not needed
- **Sensitive Fields** list includes your app-specific fields (e.g., `ssn`, `creditCard`)

### Step 9 — Alert Rules

- [ ] **Alert rules configured for production environment**

Set up these minimum alert rules in **Alerts > Create Alert Rule**:

| Alert | Type | Condition | Action |
|-------|------|-----------|--------|
| New issue in production | Issue | First seen, `environment:production` | Slack channel + email |
| Regression detected | Issue | Regressed, `environment:production` | Slack channel |
| Error spike | Metric | Error count > N in 5 min | PagerDuty (on-call) |
| P95 latency breach | Metric | `p95(transaction.duration)` > threshold | Slack #performance |
| Crash-free rate drop | Release health | Crash-free sessions < 99% | Email + Slack |

- [ ] Alert actions route to correct channels (not a dead channel)
- [ ] PagerDuty / OpsGenie integration tested with a test alert

### Step 10 — Process Exit Flush (Serverless / CLI)

- [ ] **`Sentry.flush()` called before process exit**

For serverless functions, CLI tools, or any short-lived process, events may be lost if the process exits before the SDK flushes its queue:

```typescript
// AWS Lambda / serverless
import * as Sentry from '@sentry/node';

export const handler = Sentry.wrapHandler(async (event) => {
  // Your handler logic
  return { statusCode: 200 };
});

// CLI tool / script
async function main() {
  try {
    await doWork();
  } catch (err) {
    Sentry.captureException(err);
    await Sentry.flush(2000); // 2000ms timeout — enough for network round-trip
    process.exit(1);
  }
}
```

For long-running servers (Express, Fastify), this is handled automatically — skip this step.

### Step 11 — Test Error Verification

- [ ] **Test error sent and verified in Sentry dashboard**

```typescript
// Send a test error after deploy
Sentry.captureException(new Error('Production deploy verification — safe to ignore'));

// Or from CLI
// node -e "
//   const Sentry = require('@sentry/node');
//   Sentry.init({ dsn: process.env.SENTRY_DSN, environment: 'production' });
//   Sentry.captureMessage('Deploy verification test');
//   Sentry.flush(2000).then(() => console.log('Test event sent')); // 2s flush timeout
// "
```

After sending, verify in the Sentry dashboard:

1. Event appears in **Issues** with correct `environment:production`
2. Stack trace shows **original source** (not minified) — confirms source maps work
3. Release tag matches your deployed version
4. No PII (cookies, IPs, auth headers) in the event payload

### Step 12 — Inbound Filters

- [ ] **Inbound filters enabled for known browser noise**

In Sentry dashboard under **Settings > Inbound Filters**, enable:

- **Filter out known web crawlers** (Googlebot, Bingbot generate noise)
- **Filter out legacy browsers** (IE 10 and below)
- **Filter out localhost events** (stray dev events)
- **Custom inbound filters** for domains you don't control

These filters drop events server-side before they count against your quota, unlike `beforeSend` which drops client-side after the network request.

### Verification Script

Run this after completing all checklist items:

```bash
#!/bin/bash
# scripts/verify-sentry-prod.sh
set -euo pipefail

echo "=== Sentry Production Verification ==="

PASS=0; FAIL=0

check() {
  if eval "$2" > /dev/null 2>&1; then
    echo "  PASS: $1"; ((PASS++))
  else
    echo "  FAIL: $1"; ((FAIL++))
  fi
}

# Environment variables
for var in SENTRY_DSN SENTRY_ORG SENTRY_PROJECT SENTRY_AUTH_TOKEN; do
  check "$var is set" "[ -n \"\${$var:-}\" ]"
done

# CLI authentication
check "sentry-cli authenticated" "sentry-cli info"

# Source maps uploaded
RELEASE="${SENTRY_RELEASE:-$(git rev-parse --short HEAD)}"
check "Source maps for $RELEASE" \
  "[ \$(sentry-cli releases files \"$RELEASE\" list 2>/dev/null | wc -l) -gt 1 ]"

# Network connectivity
check "sentry.io reachable" \
  "[ \$(curl -s -o /dev/null -w '%{http_code}' https://sentry.io/api/0/) = '200' ]"

# No hardcoded DSN in source
check "No hardcoded DSN in src/" \
  "! grep -r 'ingest.sentry.io' src/ --include='*.ts' --include='*.js' --include='*.tsx' 2>/dev/null | grep -v node_modules"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "All checks passed." || exit 1
```

## Output

After completing this checklist, you will have:

- Production-hardened `Sentry.init()` with tuned sample rates and PII scrubbing
- Source maps uploaded and validated via `sentry-cli` for the current release
- `beforeSend` filtering known browser noise before it burns quota
- Alert rules routing to Slack, email, and PagerDuty for the production environment
- A verified test error visible in the dashboard with readable stack traces
- Inbound filters blocking crawler and legacy browser noise server-side

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Stack traces show minified code | Source maps missing or `--url-prefix` wrong | Re-upload with correct prefix; run `sentry-cli sourcemaps explain` to diagnose |
| Events not appearing in dashboard | Wrong DSN or network blocked | Verify `SENTRY_DSN` is the production DSN; check firewall allows `*.ingest.sentry.io` on HTTPS |
| `release` mismatch warning | SDK release differs from CLI release | Ensure `Sentry.init({ release })` matches `sentry-cli releases new $VERSION` exactly |
| Events from wrong environment | `environment` not set in SDK init | Explicitly set `environment: 'production'` — do not rely on defaults |
| Excessive event volume / quota exhausted | `sampleRate: 1.0` on high-traffic service | Lower to 0.1-0.25; add `beforeSend` filters; enable server-side inbound filters |
| Alerts not firing | Alert rules scoped to wrong environment | Edit alert: filter to `environment:production`; test with `Sentry.captureMessage()` |
| Events lost in serverless / CLI | Process exits before flush | Call `await Sentry.flush(2000)` before `process.exit()` or use `Sentry.wrapHandler()` |
| `beforeSend` dropping real errors | Overly broad noise filter | Audit filter patterns; log dropped events to a secondary sink during rollout |

## Examples

**Example 1: Full production init (Node.js / Express)**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: 'production',
  release: process.env.SENTRY_RELEASE,
  debug: false,
  sendDefaultPii: false,
  sampleRate: 0.25,
  tracesSampleRate: 0.1,
  maxBreadcrumbs: 50,
  attachStacktrace: true,

  ignoreErrors: [
    'ResizeObserver loop',
    'Non-Error promise rejection captured',
    /Loading chunk \d+ failed/,
  ],

  beforeSend(event, hint) {
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
    }
    return event;
  },

  tracesSampler: (ctx) => {
    const name = ctx.transactionContext?.name || '';
    if (name.includes('/health')) return 0;
    if (name.includes('/payment')) return 1.0;
    return 0.1;
  },
});
```

**Example 2: CI source map upload (GitHub Actions)**

```yaml
# .github/workflows/deploy.yml
- name: Upload source maps to Sentry
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: my-org
    SENTRY_PROJECT: my-project
    VERSION: ${{ github.sha }}
  run: |
    npx sentry-cli releases new "$VERSION"
    npx sentry-cli releases set-commits "$VERSION" --auto
    npx sentry-cli releases files "$VERSION" upload-sourcemaps ./dist \
      --url-prefix '~/static/js' --validate
    npx sentry-cli releases finalize "$VERSION"
    npx sentry-cli releases deploys "$VERSION" new -e production
```

**Example 3: Serverless flush pattern (AWS Lambda)**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: 'production',
  release: process.env.SENTRY_RELEASE,
  tracesSampleRate: 0.2,
});

export const handler = Sentry.wrapHandler(async (event, context) => {
  // wrapHandler automatically calls flush() on completion
  const result = await processEvent(event);
  return { statusCode: 200, body: JSON.stringify(result) };
});
```

## Resources

- [Sentry Configuration Options](https://docs.sentry.io/platforms/javascript/configuration/options/) — full SDK init reference
- [Source Maps Upload](https://docs.sentry.io/platforms/javascript/sourcemaps/) — bundler plugins and CLI upload
- [sentry-cli releases](https://docs.sentry.io/cli/releases/) — `new`, `set-commits`, `finalize`, `deploys`
- [Alert Rules](https://docs.sentry.io/product/alerts/) — issue alerts, metric alerts, uptime monitors
- [Release Health](https://docs.sentry.io/product/releases/health/) — crash-free rates and session tracking
- [Data Scrubbing](https://docs.sentry.io/security-legal-pii/scrubbing/) — server-side PII removal
- [Inbound Filters](https://docs.sentry.io/product/data-management-settings/filtering/) — server-side event filtering

## Next Steps

After completing this production checklist:

1. **Set up release health monitoring** — track crash-free session rates across releases
2. **Configure ownership rules** — route issues to the right team based on file paths or error tags
3. **Add custom dashboards** — build a deployment dashboard showing error rates, P95 latency, and throughput per release
4. **Schedule quarterly audits** — re-run this checklist after major dependency upgrades or architecture changes
5. **Enable Session Replay** (if using `@sentry/browser`) — capture user sessions for faster debugging
