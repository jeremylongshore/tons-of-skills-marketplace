---
name: posthog-observability
description: |
  Observe a PostHog integration through application-side delivery metrics, ingestion warnings, billing volume, destination logs, and status evidence. Use when defining health signals or investigating silent analytics loss. Trigger with "monitor PostHog", "PostHog ingestion health", or "PostHog alerts".
argument-hint: "[service] [signal]"
allowed-tools: Read, Write, Edit
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- monitoring
- observability
- dashboard
compatibility: Designed for Claude Code
---
# PostHog Observability

## Overview

Observe four boundaries independently: application capture attempts and failures, SDK queue and flush behavior, PostHog ingestion warnings and accepted event volume, and feature-flag cache or remote-fallback behavior. Treat every Prometheus metric below as application-owned instrumentation, not as a metric exported by PostHog.

## Prerequisites

- PostHog project with personal API key (`phx_...`)
- Application instrumented with PostHog SDK
- Prometheus/Grafana or equivalent monitoring stack (optional)

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.


### Step 1: Event Ingestion Health Check

```bash
set -euo pipefail
# Check if events are flowing (last 24 hours)
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/query/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": "HogQLQuery",
      "query": "SELECT toStartOfHour(timestamp) AS hour, count() AS events FROM events WHERE timestamp > now() - interval 24 hour GROUP BY hour ORDER BY hour"
    }
  }' | jq '.results | map({hour: .[0], events: .[1]}) | .[-3:]'
```

### Step 2: Instrument Flag Evaluation Latency

```typescript
// posthog-instrumented.ts
import { PostHog } from 'posthog-node';

const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  host: 'https://us.i.posthog.com',
  personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
});

// Wrap flag evaluation with timing
async function getFlag(flagKey: string, userId: string): Promise<any> {
  const start = performance.now();
  const value = await posthog.getFeatureFlag(flagKey, userId);
  const durationMs = performance.now() - start;

  // Emit metrics to your monitoring system
  emitHistogram('posthog_flag_eval_duration_ms', durationMs, { flag: flagKey });
  emitCounter('posthog_flag_evals_total', 1, { flag: flagKey, result: String(value) });

  // Alert on slow evaluations (likely means local eval not configured)
  if (durationMs > 200) {
    console.warn(`[PostHog] Slow flag eval: ${flagKey} took ${durationMs.toFixed(0)}ms — inspect secure-key cache and fallback behavior`);
  }

  return value;
}

// Example: emit to Prometheus via prom-client
import { Histogram, Counter, Gauge } from 'prom-client';

const flagDuration = new Histogram({
  name: 'posthog_flag_eval_duration_ms',
  help: 'PostHog feature flag evaluation duration',
  labelNames: ['flag'],
  buckets: [1, 5, 10, 50, 100, 200, 500, 1000],
});

const flagEvals = new Counter({
  name: 'posthog_flag_evals_total',
  help: 'Total PostHog feature flag evaluations',
  labelNames: ['flag', 'result'],
});

function emitHistogram(name: string, value: number, labels: Record<string, string>) {
  flagDuration.observe(labels, value);
}

function emitCounter(name: string, value: number, labels: Record<string, string>) {
  flagEvals.inc(labels, value);
}
```

### Step 3: Monitor Event Volume and Billing

```typescript
// Run on a cron (e.g., every 6 hours)
async function checkEventVolume() {
  const result = await fetch(
    `https://us.posthog.com/api/projects/${process.env.POSTHOG_PROJECT_ID}/query/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.POSTHOG_PERSONAL_API_KEY}`,
      },
      body: JSON.stringify({
        query: {
          kind: 'HogQLQuery',
          query: `
            SELECT
              count() AS events_this_month,
              uniq(distinct_id) AS unique_users,
              count() / dateDiff('day', toStartOfMonth(now()), now()) AS daily_avg
            FROM events
            WHERE timestamp > toStartOfMonth(now())
          `,
        },
      }),
    }
  );

  const data = await result.json();
  const [eventsThisMonth, uniqueUsers, dailyAvg] = data.results[0];
  const projectedMonthly = dailyAvg * 30;
  const approvedMonthlyLimit = Number(process.env.POSTHOG_MONTHLY_EVENT_LIMIT);
  if (!Number.isFinite(approvedMonthlyLimit)) {
    throw new Error('Set POSTHOG_MONTHLY_EVENT_LIMIT from the live billing configuration');
  }

  const metrics = {
    events_this_month: eventsThisMonth,
    unique_users: uniqueUsers,
    daily_average: Math.round(dailyAvg),
    projected_monthly: Math.round(projectedMonthly),
    pct_of_approved_limit: Math.round((projectedMonthly / approvedMonthlyLimit) * 100),
  };

  // Emit gauge metrics
  const volumeGauge = new Gauge({
    name: 'posthog_events_month_total',
    help: 'PostHog events this month',
  });
  volumeGauge.set(eventsThisMonth);

  // Apply the organization's reviewed warning ratio to the live product limit.
  const warningRatio = Number(process.env.POSTHOG_USAGE_WARNING_RATIO ?? '0.8');
  if (projectedMonthly > approvedMonthlyLimit * warningRatio) {
    await sendAlert(`PostHog projected usage is ${Math.round(projectedMonthly / approvedMonthlyLimit * 100)}% of the reviewed limit`);
  }

  return metrics;
}
```

### Step 4: Prometheus Alert Rules

```yaml
# prometheus/posthog-alerts.yml
# These are application-emitted metrics. Rename them to match the target service.
groups:
  - name: posthog
    rules:
      - alert: PostHogCaptureDeliveryFailures
        expr: rate(posthog_capture_delivery_failures_total[5m]) > 0
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "The application is reporting PostHog delivery failures"

      - alert: PostHogFlagEvalSlow
        expr: increase(posthog_flag_eval_slo_breaches_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Application-observed PostHog flag evaluation latency exceeded its reviewed threshold"

      - alert: PostHogUsageLimitWarning
        expr: posthog_usage_limit_ratio > posthog_usage_warning_ratio
        labels:
          severity: info
        annotations:
          summary: "Projected PostHog usage crossed the organization's reviewed warning ratio"

      - alert: PostHogCaptureErrors
        expr: rate(posthog_capture_errors_total[5m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "PostHog capture errors elevated — events may be lost"
```

### Step 5: Health Check Dashboard Queries

```typescript
// Dashboard panels to track PostHog health
const dashboardQueries = {
  // Events per hour (last 24h)
  eventRate: `
    SELECT toStartOfHour(timestamp) AS hour, count() AS events
    FROM events WHERE timestamp > now() - interval 24 hour
    GROUP BY hour ORDER BY hour
  `,

  // Events by type (last 7 days)
  eventsByType: `
    SELECT event, count() AS total
    FROM events WHERE timestamp > now() - interval 7 day
    GROUP BY event ORDER BY total DESC LIMIT 15
  `,

  // Unique users per day (last 30 days)
  dailyActiveUsers: `
    SELECT toDate(timestamp) AS day, uniq(distinct_id) AS users
    FROM events WHERE timestamp > now() - interval 30 day
    GROUP BY day ORDER BY day
  `,

  // Event ingestion latency estimate
  ingestionFreshness: `
    SELECT max(timestamp) AS latest_event,
           dateDiff('second', max(timestamp), now()) AS seconds_behind
    FROM events
  `,
};
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Zero events for 1h+ | SDK not initialized or API down | Check PostHog status, verify SDK init |
| Flag evaluation exceeds the service SLO | Cold cache, fallback, or network path | Inspect secure-key configuration, cache state, and fallback counts |
| Event volume spike | New feature autocapturing | Review autocapture config, add filters |
| Rate limit 429 | Too many API queries | Cache results, reduce poll frequency |

## Output

- Flag evaluation latency instrumentation
- Event volume and billing monitoring
- Prometheus rules over application-emitted integration metrics
- HogQL dashboard queries for key metrics
- Automated alerts for ingestion drops and billing limits

## Examples

For a server event pipeline, instrument queue depth, flush failures, request latency, and fallback counts in the application; correlate them with ingestion warnings and billing volume. Do not claim PostHog exposes Prometheus metrics unless the target deployment proves that surface.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog API Overview](https://posthog.com/docs/api)
- [PostHog HogQL](https://posthog.com/docs/sql)
- [PostHog Status Page](https://status.posthog.com)
- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
