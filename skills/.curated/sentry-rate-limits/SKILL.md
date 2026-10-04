---
name: sentry-rate-limits
description: 'Manage Sentry rate limits, quotas, and event volume optimization.

  Use when hitting 429 errors, tuning sampleRate/tracesSampleRate,

  filtering noisy browser errors with beforeSend, configuring

  inbound data filters, setting per-key rate limits, or monitoring

  quota usage via the Sentry stats API.

  Trigger: "sentry rate limit", "sentry quota", "reduce sentry events",

  "sentry 429", "sentry spike protection", "sentry sampling".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(curl:*), Bash(node:*), Bash(python3:*),
  Bash(pip:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- cost-optimization
- rate-limiting
- quotas
- observability
compatibility: Designed for Claude Code
---
# Sentry Rate Limits & Quota Optimization

## Overview

Manage Sentry rate limits, sampling strategies, and quota usage to control costs without losing visibility into critical errors. Covers client-side sampling, `beforeSend` filtering, server-side inbound filters, per-key rate limits, spike protection, and the usage stats API.

## Prerequisites

- Sentry account with a project DSN configured
- `SENTRY_AUTH_TOKEN` with `org:read` and `project:write` scopes (Settings > Auth Tokens)
- `SENTRY_ORG` and `SENTRY_PROJECT` slugs known
- SDK installed: `@sentry/node` (npm) or `sentry-sdk` (pip)
- Current event volume visible at `sentry.io/stats/`

## Instructions

### Step 1 — Understand Rate Limit Behavior

When your project exceeds its quota, Sentry returns `429 Too Many Requests` with a `Retry-After` header. The SDK automatically stops sending events until the cooldown expires. Events generated during this window are permanently lost — there is no replay mechanism.

**Rate limit tiers by plan:**

| Plan | API Rate Limit | Notes |
|------|---------------|-------|
| Developer | 50 RPM | Shared quota, no reserved volume |
| Team | 1,000 RPM | Per-organization, includes spike protection |
| Business | 10,000 RPM | Per-organization, custom quotas available |
| Enterprise | Custom | Negotiated per contract |

**Quota categories (billed separately):**

- **Errors** — exceptions and log messages
- **Transactions** — performance monitoring spans
- **Replays** — session replay recordings
- **Attachments** — file uploads (crash dumps, minidumps)
- **Profiles** — continuous profiling data
- **Cron monitors** — scheduled job check-ins

Rate limit headers returned on 429:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-Sentry-Rate-Limit-Limit: 50
X-Sentry-Rate-Limit-Remaining: 0
X-Sentry-Rate-Limit-Reset: 1711324800
```

### Step 2 — Configure Client-Side Sampling

Sampling is the first line of defense. Set `sampleRate` for errors and `tracesSampleRate` for performance transactions.

**TypeScript / Node.js:**

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Error sampling: 0.0 (drop all) to 1.0 (capture all)
  sampleRate: 0.25, // Capture 25% of errors

  // Transaction sampling: 0.0 to 1.0
  tracesSampleRate: 0.1, // Capture 10% of transactions

  // Dynamic transaction sampling — route-aware cost control
  tracesSampler: (samplingContext) => {
    const { name, parentSampled } = samplingContext;

    // Respect parent sampling decision in distributed traces
    if (parentSampled !== undefined) return parentSampled;

    // Drop health checks and readiness probes entirely
    if (name === 'GET /health' || name === 'GET /readiness') return 0;
    if (name?.includes('/health')) return 0;

    // High-value: payment and auth flows at 100%
    if (name?.includes('/api/payment') || name?.includes('/api/auth')) return 1.0;

    // Medium-value: API routes at 20%
    if (name?.startsWith('GET /api/') || name?.startsWith('POST /api/')) return 0.2;

    // Low-value: static assets — never trace
    if (name?.startsWith('GET /static/') || name?.startsWith('GET /assets/')) return 0;

    // Default fallback: 5%
    return 0.05;
  },
});
```

**Python:**

```python
import sentry_sdk

def traces_sampler(sampling_context):
    tx_name = sampling_context.get("transaction_context", {}).get("name", "")

    # Drop health checks
    if "/health" in tx_name or "/readiness" in tx_name:
        return 0

    # High-value flows
    if "/api/payment" in tx_name or "/api/auth" in tx_name:
        return 1.0

    # API routes
    if tx_name.startswith(("GET /api/", "POST /api/")):
        return 0.2

    # Static assets
    if tx_name.startswith(("GET /static/", "GET /assets/")):
        return 0

    return 0.05

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    sample_rate=0.25,          # 25% of errors
    traces_sample_rate=0.1,    # 10% of transactions (fallback if no sampler)
    traces_sampler=traces_sampler,
)
```

### Step 3 — Filter Noisy Errors with beforeSend

Use `beforeSend` to drop events before they count against your quota. This runs client-side, so filtered events never reach Sentry.

**TypeScript / Node.js:**

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  beforeSend(event, hint) {
    const error = hint?.originalException as Error | undefined;

    // Drop browser extension errors (common in frontend SDKs)
    if (event.exception?.values?.some(e =>
      e.stacktrace?.frames?.some(f =>
        f.filename?.includes('extensions://') ||
        f.filename?.includes('moz-extension://') ||
        f.filename?.includes('chrome-extension://')
      )
    )) {
      return null; // Drop the event
    }

    // Drop known noisy browser errors
    if (error?.message?.match(/ResizeObserver loop/)) return null;
    if (error?.message?.match(/Non-Error promise rejection/)) return null;
    if (error?.name === 'AbortError') return null;
    if (error?.message?.match(/Load failed/)) return null;

    // CRITICAL: Always capture payment errors regardless of sampleRate
    if (error?.message?.includes('PaymentError') ||
        event.tags?.['transaction.type'] === 'payment') {
      return event; // Force capture
    }

    return event;
  },

  // Pattern-based error filtering (faster than beforeSend for known strings)
  ignoreErrors: [
    'ResizeObserver loop completed with undelivered notifications',
    'Non-Error promise rejection captured',
    /Loading chunk \d+ failed/,
    'Network request failed',
    'Failed to fetch',
    'AbortError',
    /^Script error\.?$/,
    'TypeError: cancelled',
    'TypeError: NetworkError when attempting to fetch resource',
  ],

  // Block errors originating from third-party scripts
  denyUrls: [
    /extensions\//i,
    /^chrome:\/\//i,
    /^chrome-extension:\/\//i,
    /^moz-extension:\/\//i,
    /hotjar\.com/,
    /google-analytics\.com/,
    /googletagmanager\.com/,
    /intercom\.io/,
  ],
});
```

**Python:**

```python
def before_send(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, _ = hint["exc_info"]

        # Drop known noisy exceptions
        if exc_type.__name__ in ("ConnectionResetError", "BrokenPipeError"):
            return None

        # Drop health check 404s
        msg = str(exc_value)
        if "health" in msg.lower() and "404" in msg:
            return None

    # Always capture payment errors
    if event.get("tags", {}).get("transaction.type") == "payment":
        return event

    return event

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    before_send=before_send,
    ignore_errors=[
        "ConnectionResetError",
        "BrokenPipeError",
    ],
)
```

### Step 4 — Enable Server-Side Inbound Data Filters

Inbound filters run on Sentry's servers before quota counting. Filtered events do not consume quota — this is free filtering.

Configure at **Project Settings > Inbound Filters**:

| Filter | What it blocks | Recommended |
|--------|---------------|-------------|
| Legacy browsers | IE 9/10, old Safari, old Android | Enable |
| Browser extensions | Errors from browser extension code | Enable |
| Localhost events | Events from localhost / 127.0.0.1 | Enable for production projects |
| Web crawlers | Bot-generated errors (Googlebot, etc.) | Enable |
| Filtered releases | Specific release versions | Use for deprecated releases |
| Error message patterns | Custom regex patterns | Add known false-positive patterns |

**Configure via API:**

```bash
# Enable legacy browser filter
curl -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": true}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters/legacy-browsers/"

# Enable browser extension filter
curl -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": true}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters/browser-extensions/"

# Enable web crawler filter
curl -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": true}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters/web-crawlers/"
```

### Step 5 — Set Per-Key Rate Limits

Each DSN (Client Key) can have its own rate limit. This prevents a single project from exhausting the organization's entire quota.

Configure at **Project Settings > Client Keys > Configure > Rate Limiting**.

```bash
# Set rate limit to 1000 events per hour on a specific client key
# First, list client keys to find the key ID
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/keys/" \
  | python3 -m json.tool

# Then set the rate limit
curl -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rateLimit": {"window": 3600, "count": 1000}}' \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/keys/$KEY_ID/"
```

**Strategy for multi-environment setups:**

- Production DSN: 5,000 events/hour (critical errors matter)
- Staging DSN: 500 events/hour (only need representative sample)
- Development DSN: 100 events/hour (prevent local debugging floods)

### Step 6 — Enable Spike Protection

Spike protection is auto-enabled on Team and Business plans. It detects sudden event volume increases and temporarily rate-limits the project to prevent quota exhaustion from error storms.

Configure at **Organization Settings > Spike Protection**.

When spike protection triggers:

1. Sentry detects volume exceeding 10x normal baseline
2. Events are temporarily dropped (429 returned to SDK)
3. An email notification is sent to organization owners
4. Protection auto-disables after the spike subsides

For programmatic spike alerts, set up a Sentry alert rule:

- **Condition:** Number of events in project exceeds threshold
- **Action:** Send notification to Slack/PagerDuty/email
- **Frequency:** Alert once per hour

### Step 7 — Monitor Quota Usage via API

```bash
# Organization-wide usage stats for the last 7 days, grouped by category
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats_v2/?field=sum(quantity)&groupBy=category&interval=1d&statsPeriod=7d" \
  | python3 -m json.tool

# Per-project usage breakdown
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats_v2/?field=sum(quantity)&groupBy=project&category=error&interval=1d&statsPeriod=7d" \
  | python3 -m json.tool

# Outcome-based stats (accepted, filtered, rate_limited, invalid)
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/stats_v2/?field=sum(quantity)&groupBy=outcome&category=error&interval=1d&statsPeriod=24h" \
  | python3 -m json.tool
```

### Step 8 — Reduce Payload Size and Deduplicate

Reduce event size and improve grouping to lower quota consumption:

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  maxBreadcrumbs: 30,   // Default: 100
  maxValueLength: 500,   // Default: 250

  beforeSend(event) {
    // Truncate large request bodies
    if (event.request?.data && typeof event.request.data === 'string') {
      event.request.data = event.request.data.substring(0, 1000);
    }
    // Remove cookies
    if (event.request?.cookies) delete event.request.cookies;

    // Custom fingerprinting: normalize dynamic values for better grouping
    if (event.exception?.values?.[0]) {
      const { type, value } = event.exception.values[0];
      const normalized = value
        ?.replace(/\b[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\b/gi, '<UUID>')
        ?.replace(/\b\d+\b/g, '<N>') || '';
      event.fingerprint = [type || 'unknown', normalized];
    }
    return event;
  },
});
```

## Output

After completing these steps, you will have:

- Sampling rates configured (`sampleRate`, `tracesSampleRate`, `tracesSampler`) to reduce event volume while preserving visibility into critical paths
- `beforeSend` filtering dropping noisy browser errors (ResizeObserver, AbortError, extension errors) before they count against quota
- `ignoreErrors` and `denyUrls` patterns blocking known false positives
- Server-side inbound filters enabled for free pre-quota filtering
- Per-key rate limits set to prevent single-project quota exhaustion
- Spike protection enabled and alert rules configured
- Quota monitoring via the `/stats_v2/` API endpoint
- Custom fingerprinting reducing event duplication

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Quota exhausted for current billing period | Lower `sampleRate` and `tracesSampleRate`, add patterns to `ignoreErrors`, enable per-key rate limits |
| Events silently dropped | Client SDK respecting `Retry-After` header | Reduce volume at source; SDK auto-recovers after cooldown expires |
| Critical errors missed | `sampleRate` too low | Use `beforeSend` to force-return critical errors regardless of sampling; never filter payment/auth errors |
| Quota exhausted early in period | No per-project rate limits | Set hourly rate limits per client key to spread quota evenly across the billing period |
| Spike consuming entire quota | Spike protection not enabled or threshold too high | Enable spike protection in organization settings; set up volume alert rules |
| `401 Unauthorized` on stats API | Invalid or expired auth token | Regenerate token at Settings > Auth Tokens with `org:read` scope |
| Inbound filter not reducing volume | Filter configured but wrong error type | Verify filter targets correct category; browser extension filter only works for JS SDK errors |
| `tracesSampler` not called | `tracesSampleRate` takes precedence in some SDK versions | Remove `tracesSampleRate` when using `tracesSampler` — they conflict |

## Examples

### Example 1 — Quota Monitoring Bash Script

```bash
#!/usr/bin/env bash
# Monitor Sentry quota usage and alert if approaching limit
set -euo pipefail

ORG="${SENTRY_ORG:?Set SENTRY_ORG}"
TOKEN="${SENTRY_AUTH_TOKEN:?Set SENTRY_AUTH_TOKEN}"
THRESHOLD=${QUOTA_THRESHOLD:-80}  # Alert at 80% usage

accepted=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sentry.io/api/0/organizations/$ORG/stats_v2/?field=sum(quantity)&groupBy=outcome&category=error&statsPeriod=1h&interval=1h" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for g in data.get('groups', []):
    if g['by'].get('outcome') == 'accepted':
        print(g['totals']['sum(quantity)']); break
else: print(0)")

echo "Accepted events (last hour): $accepted"
[ "$accepted" -gt "$THRESHOLD" ] && echo "WARNING: volume $accepted > threshold $THRESHOLD"
```

### Example 2 — Enable All Inbound Filters via API

```bash
#!/usr/bin/env bash
set -euo pipefail
BASE="https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/filters"
AUTH="Authorization: Bearer $SENTRY_AUTH_TOKEN"

for filter in legacy-browsers browser-extensions web-crawlers; do
  curl -s -X PUT -H "$AUTH" -H "Content-Type: application/json" \
    -d '{"active": true}' "$BASE/$filter/" && echo "Enabled: $filter"
done
```

## Resources

- [Quota Management](https://docs.sentry.io/pricing/quotas/) — billing categories, quota limits, and overage handling
- [Manage Your Event Stream](https://docs.sentry.io/pricing/quotas/manage-event-stream-guide/) — step-by-step cost reduction guide
- [Sampling Configuration](https://docs.sentry.io/platforms/javascript/configuration/sampling/) — `sampleRate`, `tracesSampleRate`, `tracesSampler`
- [Filtering Events](https://docs.sentry.io/platforms/javascript/configuration/filtering/) — `beforeSend`, `ignoreErrors`, `denyUrls`
- [Inbound Data Filters](https://docs.sentry.io/concepts/data-management/filtering/) — server-side free filtering
- [Rate Limiting API](https://docs.sentry.io/api/projects/update-a-client-key/) — per-key rate limit configuration
- [Stats API v2](https://docs.sentry.io/api/organizations/retrieve-event-counts-for-an-organization-v2/) — usage monitoring endpoint

## Next Steps

- **Cost review**: Query `/stats_v2/` weekly to track spend trends by category
- **Alert rules**: Create Sentry alerts for volume spikes per project
- **Replay sampling**: Apply `replaysSessionSampleRate` and `replaysOnErrorSampleRate` for session replay cost control
- **Server-side sampling**: Explore Sentry Dynamic Sampling (server-side) for organization-wide policies
- **Audit `ignoreErrors`**: Review quarterly — patterns may suppress real bugs as code evolves
