---
name: sentry-cost-tuning
description: 'Optimize Sentry costs, reduce event volume, and manage quota spend.

  Use when analyzing Sentry billing, reducing error/transaction volume,

  configuring sampling rates, or preventing overage charges.

  Trigger: "reduce sentry costs", "sentry billing optimization",

  "sentry quota management", "optimize sentry spend", "sentry sampling".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(curl:*), Bash(node:*), Bash(npx:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- cost-optimization
- billing
- quotas
- sampling
compatibility: Designed for Claude Code
---
# Sentry Cost Tuning

## Overview

Reduce Sentry spend by 60-95% through SDK-level sampling, server-side inbound filters, `beforeSend` event dropping, and quota management — without losing visibility into production errors that matter.

## Prerequisites

- Active Sentry account with `org:read` and `project:read` scopes on an auth token
- Access to the project's `Sentry.init()` configuration (typically `sentry.client.config.ts` or `instrument.ts`)
- Current plan tier identified: Developer (free, 5K errors/mo), Team ($26/mo, 50K errors + 100K transactions), or Business ($80/mo, 100K errors + 500K transactions)
- `SENTRY_AUTH_TOKEN` and `SENTRY_ORG` environment variables set for API calls
- `@sentry/node` >= 8.0 or `@sentry/browser` >= 8.0 installed

## Instructions

### Step 1 — Audit Current Usage via the Stats API

Query the Sentry Usage Stats API to understand where volume comes from before making changes. This endpoint returns event counts grouped by category over any time period.

```bash
# Pull 30-day usage breakdown by category
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats/usage/?statsPeriod=30d&groupBy=category&field=sum(quantity)&interval=1d" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('=== 30-Day Usage by Category ===')
for group in data.get('groups', []):
    cat = group['by']['category']
    total = sum(interval[1] for interval in group.get('series', {}).get('sum(quantity)', []))
    print(f'  {cat}: {total:,} events')
"
```

```bash
# Identify top error-producing projects
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats/usage/?statsPeriod=30d&groupBy=project&category=error&field=sum(quantity)" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
projects = []
for group in data.get('groups', []):
    proj = group['by']['project']
    total = sum(interval[1] for interval in group.get('series', {}).get('sum(quantity)', []))
    projects.append((proj, total))
projects.sort(key=lambda x: -x[1])
print('=== Top Error-Producing Projects ===')
for name, count in projects[:10]:
    print(f'  {name}: {count:,}')
"
```

Record the baseline numbers. You need these to measure savings after optimization.

### Step 2 — Configure Error Sampling with `sampleRate`

The `sampleRate` option in `Sentry.init()` controls the percentage of error events sent to Sentry. Setting it to `0.1` means only 10% of errors are sent, yielding a 90% cost reduction on the error category.

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // 10% of errors sent = 90% cost reduction
  // Sentry extrapolates counts in the Issues dashboard
  sampleRate: 0.1,
});
```

**Trade-off:** Low-frequency errors (< 10 occurrences/day) may be missed entirely. Mitigate this by using `beforeSend` to always send errors with specific severity or tags rather than relying on blanket sampling.

### Step 3 — Configure Performance Sampling with `tracesSampleRate` and `tracesSampler`

Performance monitoring (transactions/spans) is typically the largest cost driver. A `tracesSampleRate` of `0.05` sends only 5% of traces, cutting performance costs by 95%.

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Static: 5% of all traces (95% cost reduction)
  tracesSampleRate: 0.05,

  // Dynamic: per-endpoint sampling for fine-grained control
  // When tracesSampler is defined, it overrides tracesSampleRate
  tracesSampler: (samplingContext) => {
    const { name, attributes } = samplingContext;

    // Never trace health checks, readiness probes, static assets
    if (name?.match(/\/(health|healthz|ready|livez|ping|robots\.txt|favicon)/)) {
      return 0;
    }
    if (name?.match(/\.(js|css|png|jpg|svg|woff2?|ico)$/)) {
      return 0;
    }

    // High-value: payment and auth flows get 50% sampling
    if (name?.includes('/checkout') || name?.includes('/payment')) {
      return 0.5;
    }
    if (name?.includes('/auth') || name?.includes('/login')) {
      return 0.25;
    }

    // API routes: 5%
    if (name?.includes('/api/')) {
      return 0.05;
    }

    // Everything else: 1%
    return 0.01;
  },
});
```

The `tracesSampler` function receives a `samplingContext` with the transaction `name` (usually the route) and `attributes`. Return a number between `0` (drop) and `1` (always send), or `true`/`false`.

### Step 4 — Drop Noisy Events with `beforeSend`

The `beforeSend` hook fires for every error event before it is sent to Sentry. Returning `null` drops the event entirely — it never counts against quota.

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event, hint) {
    const error = hint?.originalException;
    const message = typeof error === 'string' ? error : error?.message || '';

    // Drop ResizeObserver noise (Chrome fires this constantly, never actionable)
    if (message.includes('ResizeObserver loop')) return null;

    // Drop network errors from flaky client connections
    if (/^(Failed to fetch|NetworkError|Load failed|AbortError)$/i.test(message)) {
      return null;
    }

    // Drop cancelled navigation (user clicked away)
    if (message.includes('cancelled') || message.includes('AbortError')) {
      return null;
    }

    // Drop browser extension errors by checking stack frames
    const frames = event.exception?.values?.[0]?.stacktrace?.frames || [];
    if (frames.some(f => f.filename?.match(/extensions?\//i) || f.filename?.match(/^(chrome|moz)-extension:\/\//))) {
      return null;
    }

    // Always send critical errors regardless of sampleRate
    // Re-enable any that were sampled out
    if (event.level === 'fatal' || event.tags?.critical === 'true') {
      return event;
    }

    return event;
  },

  // Complementary: block errors from known noisy patterns
  ignoreErrors: [
    'ResizeObserver loop completed with undelivered notifications',
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    /Loading chunk \d+ failed/,
    /Unexpected token '<'/,       // HTML returned instead of JS (CDN issue)
    /^Script error\.?$/,          // Cross-origin script with no details
  ],

  // Block events from third-party scripts
  denyUrls: [
    /extensions\//i,
    /^chrome:\/\//i,
    /^chrome-extension:\/\//i,
    /^moz-extension:\/\//i,
    /hotjar\.com/,
    /intercom\.io/,
    /google-analytics\.com/,
    /googletagmanager\.com/,
    /cdn\.segment\.com/,
  ],
});
```

### Step 5 — Enable Server-Side Inbound Data Filters (Free)

Inbound data filters drop events at Sentry's edge before they are ingested and counted against quota. They cost nothing to enable.

Navigate to **Project Settings > Inbound Filters** (or use the API) and enable:

| Filter | What it drops | Impact |
|--------|--------------|--------|
| Browser Extensions | Errors from Chrome/Firefox extensions | 5-15% of frontend errors |
| Legacy Browsers | IE 11, old Safari/Chrome versions | 2-10% depending on audience |
| Localhost Events | Errors from `localhost` and `127.0.0.1` | Dev noise (variable) |
| Web Crawlers | Bot-triggered errors (Googlebot, Bingbot) | 1-5% of frontend errors |
| Filtered Transactions | Health checks, static asset requests | 10-40% of transactions |

```bash
# Enable inbound filters via API
for filter in browser-extensions legacy-browsers localhost-events web-crawlers; do
  curl -s -X PUT \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"active": true}' \
    "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters/$filter/"
  echo " -> Enabled: $filter"
done
```

Add custom error message filters for project-specific noise:

```bash
# Add custom inbound filter for error messages
curl -s -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": true, "subfilters": ["ResizeObserver", "ChunkLoadError", "Script error"]}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters/custom-error-messages/"
```

### Step 6 — Configure Spike Protection and Per-Key Rate Limits

**Spike protection** is auto-enabled on all Sentry plans and caps burst events during sudden spikes (deploy bugs, infinite loops). Verify it is active under **Organization Settings > Spike Protection**.

**Per-key rate limits** restrict events per DSN key per time window. Set these in **Project Settings > Client Keys (DSN) > Rate Limiting** or via the API:

```bash
# Set rate limit: 1000 errors per hour per DSN key
curl -s -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rateLimit": {"window": 3600, "count": 1000}}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/keys/$KEY_ID/"
```

**Spend allocations** (Team and Business plans): Set per-category budgets under **Settings > Subscription > Spend Allocations** to cap on-demand spending per billing period.

### Step 7 — Optimize Reserved vs On-Demand Volume

Sentry offers two pricing models for volume above the plan's included quota:

| Model | Rate (errors) | Best for |
|-------|--------------|----------|
| Reserved volume | ~$0.000180/event (pre-paid blocks) | Predictable workloads |
| On-demand volume | ~$0.000290/event (pay-as-you-go) | Spiky/seasonal traffic |

Reserved volume is approximately 38% cheaper per event than on-demand. If your 30-day audit shows consistent volume, purchase reserved blocks to match the P90 usage. Let spikes overflow into on-demand.

```
Example calculation:
  Average monthly errors:  120,000
  Plan included:            50,000  (Team plan)
  Overage:                  70,000

  On-demand cost:  70,000 x $0.000290 = $20.30/month
  Reserved cost:   70,000 x $0.000180 = $12.60/month
  Monthly savings: $7.70 ($92.40/year)
```

### Step 8 — Reduce Event Payload Size

Smaller payloads mean lower bandwidth costs and faster event processing. These settings do not reduce event count but lower overall resource consumption.

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Reduce breadcrumbs from default 100 to 20
  maxBreadcrumbs: 20,

  // Truncate long string values (default 250)
  maxValueLength: 500,

  // Disable features you are not actively using
  replaysSessionSampleRate: 0,    // Session replays off
  replaysOnErrorSampleRate: 0,    // Error replays off
  profilesSampleRate: 0,          // Profiling off

  beforeSend(event) {
    // Truncate large request bodies
    if (event.request?.data && typeof event.request.data === 'string') {
      if (event.request.data.length > 2000) {
        event.request.data = event.request.data.substring(0, 2000) + '...[truncated]';
      }
    }

    // Strip unnecessary headers
    if (event.request?.headers) {
      const keep = ['content-type', 'user-agent', 'referer', 'accept-language'];
      event.request.headers = Object.fromEntries(
        Object.entries(event.request.headers)
          .filter(([k]) => keep.includes(k.toLowerCase()))
      );
    }

    return event;
  },
});
```

### Step 9 — Verify Savings

After deploying changes, wait 48-72 hours and re-run the usage audit from Step 1 to measure actual savings.

```bash
# Compare current period vs previous period
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats/usage/?statsPeriod=7d&groupBy=category&field=sum(quantity)&interval=1d" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('=== Post-Optimization 7-Day Usage ===')
for group in data.get('groups', []):
    cat = group['by']['category']
    total = sum(interval[1] for interval in group.get('series', {}).get('sum(quantity)', []))
    print(f'  {cat}: {total:,} events')
print()
print('Compare against your Step 1 baseline to calculate % reduction.')
"
```

## Output

After completing this skill:

- SDK sampling configured: `sampleRate` for errors, `tracesSampler` for performance traces
- `beforeSend` hook dropping non-actionable errors (ResizeObserver, network failures, browser extensions)
- `ignoreErrors` and `denyUrls` blocking known noisy patterns
- Server-side inbound data filters enabled (browser extensions, legacy browsers, localhost, crawlers)
- Spike protection verified and per-key rate limits set
- Unused features disabled (replays, profiling) to eliminate wasted quota
- Cost projection completed with reserved vs on-demand volume comparison
- Spend allocations configured to prevent overage surprises

## Error Handling

| Problem | Cause | Fix |
|---------|-------|-----|
| Critical errors missing from Sentry | `sampleRate` too low | Add `beforeSend` logic that always sends `level: 'fatal'` events regardless of sampling |
| Zero performance data | `tracesSampleRate: 0` or `tracesSampler` returning `0` for all routes | Set minimum `0.01` baseline in the `tracesSampler` default return |
| Unexpected overage charges | No rate limits or spend allocations | Set per-key rate limits (Step 6) and spend allocations in billing settings |
| Spike consuming entire monthly quota | Spike protection disabled or infinite error loop | Verify spike protection is active; add circuit breaker in `beforeSend` |
| Usage API returns 403 | Auth token missing `org:read` scope | Generate new token at sentry.io/settings/auth-tokens with `org:read` + `project:read` |
| `beforeSend` drops too aggressively | Overly broad regex patterns | Test patterns against recent events in Sentry's Discover tab before deploying |
| Inbound filters not reducing volume | Filters enabled after events ingested | Filters are prospective only; wait for new events to see impact |

## Examples

### Example 1 — Startup on Team Plan ($26/mo) with 800K Monthly Transactions

```
Before: 45K errors + 800K transactions
  Included: 50K errors + 100K transactions
  Overage: 700K transactions x $0.000025 = $17.50/month

After optimization:
  tracesSampler → 800K reduced to 40K (95% drop)
  ignoreErrors + beforeSend → 45K reduced to 28K (38% drop)
  Inbound filters → additional 5% reduction

  New monthly overage: $0
  Annual savings: $210
```

### Example 2 — Business Plan ($80/mo) with High Frontend Error Volume

```
Before: 450K errors + 200K transactions + 5K replays
  Included: 100K errors + 500K transactions + 5K replays
  Overage: 350K errors x $0.000290 = $101.50/month

After optimization:
  sampleRate 0.25 → 450K reduced to 112K
  beforeSend filtering → 112K reduced to 85K
  Inbound filters → 85K reduced to 72K

  New monthly overage: $0 (72K < 100K included)
  Annual savings: $1,218
```

### Example 3 — Dynamic Sampling for Microservices

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampler: (samplingContext) => {
    const { name } = samplingContext;

    // Internal services: minimal sampling
    if (name?.startsWith('internal.')) return 0.001;

    // Customer-facing API: moderate sampling
    if (name?.startsWith('api.')) return 0.05;

    // Background jobs: low sampling
    if (name?.includes('worker') || name?.includes('cron')) return 0.01;

    return 0.01;
  },
});
```

## Resources

- [Sentry Quota Management](https://docs.sentry.io/pricing/quotas/) — official guide to managing event quotas
- [Manage Your Error Quota](https://docs.sentry.io/pricing/quotas/manage-event-stream-guide/) — step-by-step error volume reduction
- [Sentry Pricing](https://sentry.io/pricing/) — current plan tiers and per-category rates
- [SDK Filtering Configuration](https://docs.sentry.io/platforms/javascript/configuration/filtering/) — `beforeSend`, `ignoreErrors`, `denyUrls`
- [Dynamic Sampling](https://docs.sentry.io/platforms/javascript/configuration/sampling/) — `tracesSampler` reference
- [Inbound Data Filters](https://docs.sentry.io/concepts/data-management/filtering/) — server-side filter configuration
- [Usage Stats API](https://docs.sentry.io/api/organizations/retrieve-event-counts-for-an-organization-v2/) — `GET /api/0/organizations/{org}/stats/usage/`
- [Spike Protection](https://docs.sentry.io/pricing/quotas/spike-protection/) — automatic burst event capping

## Next Steps

1. Run the Step 1 usage audit to establish a baseline before making any changes
2. Deploy SDK sampling changes (`sampleRate`, `tracesSampler`, `beforeSend`) to a staging environment first
3. Enable all free inbound data filters immediately — zero risk, immediate savings
4. Monitor the Sentry Stats page for 72 hours post-deployment to verify reduction targets
5. Set spend allocations and rate limits as guardrails against future spikes
6. Evaluate reserved volume blocks if monthly overage exceeds $15 consistently
7. Schedule quarterly reviews of `beforeSend` filters against new error patterns in Discover
