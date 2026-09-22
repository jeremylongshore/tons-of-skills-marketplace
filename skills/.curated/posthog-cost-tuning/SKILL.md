---
name: posthog-cost-tuning
description: |
  Reduce PostHog usage cost without silently losing decision-critical data by measuring billable volume, applying product limits, and filtering noise. Use when forecasting spend or responding to a usage spike. Trigger with "PostHog cost", "PostHog billing", or "reduce PostHog usage".
argument-hint: "[project-path] [product-or-budget]"
allowed-tools: Read, Grep, Bash(curl:*)
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- api
- monitoring
- cost-optimization
compatibility: Designed for Claude Code
---
# PostHog Cost Tuning

## Overview

Measure the live billable volume for each enabled PostHog product, trace changes to instrumentation releases, and reduce only traffic that the product owner has classified as noise or safely sampleable. Pricing, free allowances, and product entitlements are live facts; read them from the billing dashboard, pricing calculator, and approved product limits at execution time.

## Prerequisites

- PostHog Cloud account with billing access
- Application instrumented with posthog-js
- Understanding of which events drive your analytics

## Authentication

- Usage inspection through private query and billing APIs requires a least-privilege personal API key or OAuth token on a trusted machine.
- Event capture and browser-side filtering use only the public project token; never ship a personal or secure key to the browser.
- Read private credentials from a secret manager, redact command output before sharing it, and select the private US or EU API host that matches the project.

## Live Pricing Boundary

Do not copy prices or free allowances into implementation code. Record the billing-dashboard timestamp, current product limit, projected usage, unit price from the live calculator, and the owner who approved any data-loss tradeoff. Recheck those values before applying a change.

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries.

### Step 1: Audit Current Event Volume

```bash
set -euo pipefail
# See which events consume the most quota (last 30 days)
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/query/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": "HogQLQuery",
      "query": "SELECT event, count() AS total FROM events WHERE timestamp > now() - interval 30 day GROUP BY event ORDER BY total DESC LIMIT 20"
    }
  }' | jq '.results[] | {event: .[0], count: .[1]}'
```

### Step 2: Tune Autocapture

`$autocapture` is often the largest event volume. Restrict it to only useful interactions.

```typescript
import posthog from 'posthog-js';

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',
  autocapture: {
    // Only capture click and submit events (skip change, scroll, etc.)
    dom_event_allowlist: ['click', 'submit'],
    // Only capture meaningful elements
    element_allowlist: ['a', 'button', 'form', 'input[type=submit]'],
    // Only capture elements with this CSS class
    css_selector_allowlist: ['.track-click', '[data-track]'],
    // Skip internal/admin pages entirely
    url_ignorelist: ['/admin', '/health', '/api/internal', '/_next'],
  },
});
```

### Step 3: Event Sampling with before_send

```typescript
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',
  before_send: (event) => {
    // 1. Always send business-critical events (no sampling)
    const critical = ['purchase', 'signup', 'subscription_started', 'subscription_canceled', 'error'];
    if (critical.includes(event.event)) return event;

    // 2. Drop bot traffic entirely
    const ua = navigator?.userAgent?.toLowerCase() || '';
    if (/bot|crawler|spider|scrapy|headless|phantom|puppeteer/i.test(ua)) {
      return null;
    }

    // 3. Apply only the sample rate approved for this event class.
    if (event.event === '$pageview') {
      const highTraffic = ['/', '/pricing', '/blog'];
      const url = event.properties?.$current_url || '';
      if (highTraffic.some(p => url.endsWith(p))) {
        return Math.random() < approvedPageviewSampleRate ? event : null;
      }
      return event;
    }

    // 4. Use a separately approved rate for autocapture.
    if (event.event === '$autocapture') {
      return Math.random() < approvedAutocaptureSampleRate ? event : null;
    }

    return event; // Keep all other events
  },
});
```

### Step 4: Optimize Session Recording Costs

```typescript
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',
  session_recording: {
    // Load the reviewed rate from configuration; document analysis impact.
    sampleRate: approvedSessionRecordingSampleRate,
    // Don't record sessions shorter than 5 seconds (bounces)
    minimumDurationMilliseconds: 5000,
    // Record 100% of sessions with errors (most valuable for debugging)
    // This is configured in PostHog dashboard under Session Replay settings
  },
});

// Alternatively: disable recording for non-paying users
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',
  disable_session_recording: true, // Start disabled
});

// Enable only for paying users
if (user.plan !== 'free') {
  posthog.startSessionRecording();
}
```

### Step 5: Monitor Usage and Set Alerts

```bash
set -euo pipefail
# Check current month's event usage
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/query/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": "HogQLQuery",
      "query": "SELECT count() AS total_events, uniq(distinct_id) AS unique_users, count() / dateDiff('"'"'day'"'"', toStartOfMonth(now()), now()) AS events_per_day FROM events WHERE timestamp > toStartOfMonth(now())"
    }
  }' | jq '.results[0] | {
    total_events: .[0],
    unique_users: .[1],
    avg_events_per_day: .[2],
    projected_monthly: (.[2] * 30)
  }'
```

```typescript
// Automated cost monitoring
async function checkPostHogBudget() {
  const result = await queryPostHog(`
    SELECT count() AS events_this_month
    FROM events
    WHERE timestamp > toStartOfMonth(now())
  `);

  const eventsThisMonth = result.results[0][0];
  const approvedMonthlyLimit = Number(process.env.POSTHOG_MONTHLY_EVENT_LIMIT);
  if (!Number.isFinite(approvedMonthlyLimit)) {
    throw new Error('Set POSTHOG_MONTHLY_EVENT_LIMIT from the current billing configuration');
  }
  const projectedMonthly = eventsThisMonth / (new Date().getDate() / 30);

  if (projectedMonthly > approvedMonthlyLimit * 0.8) {
    await sendSlackAlert(`PostHog usage alert: ${Math.round(projectedMonthly)} events projected against reviewed limit ${approvedMonthlyLimit}`);
  }
}
```

## Decision Record

For each proposed filter or sample, record the baseline count, affected event or product, chosen rate, expected analytical limitation, rollback trigger, and measured result after one full review window. Never report generic savings estimates as if they were measured for the target project.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Event volume spike | New feature without volume estimate | Forecast events before launch |
| Bill higher than expected | Bot traffic | Add bot filtering in `before_send` |
| Missing critical events | Sampling too aggressive | Exclude revenue events from sampling |
| Approved product limit reached mid-month | Volume exceeds the reviewed budget | Apply the least destructive approved control and preserve conversion events |

## Output

- Autocapture restricted to meaningful interactions
- Reviewed event-sampling policy with its analytical limitations recorded
- Bot traffic filtered
- Session-recording control derived from the live billing configuration
- Budget monitoring against the approved product limit

## Examples

For an autocapture spike, compare billing-dashboard volume with the release timeline, preserve named conversion events, narrow noisy autocapture, and set a reviewed product limit. Report expected data loss explicitly; do not invent savings percentages.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Pricing](https://posthog.com/pricing)
- [PostHog Autocapture Config](https://posthog.com/docs/product-analytics/autocapture)
- [PostHog before_send](https://posthog.com/docs/libraries/js/config)
- [Session Recording Control](https://posthog.com/docs/session-replay/how-to-control-which-sessions-you-record)
