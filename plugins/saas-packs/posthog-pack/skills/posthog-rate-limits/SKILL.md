---
name: posthog-rate-limits
description: |
  Design evidence-based PostHog private-API throttling with correct endpoint classes, team-wide budgets, backoff, and export alternatives. Use when a private API returns 429 or a polling job needs a request budget. Trigger with "PostHog rate limit", "PostHog 429", or "PostHog backoff".
argument-hint: "[integration] [endpoint-class]"
allowed-tools: Read, Write, Edit
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- api
compatibility: Designed for Claude Code
---
# PostHog Rate Limits

## Overview

PostHog rate limits apply to private API endpoints authenticated with a personal API key, project secret key where available, or OAuth. Public POST-only capture and flag endpoints have no PostHog request-level rate limit, but capture can still report billing limits in a successful response.

## Prerequisites

- A least-privilege personal API key, project secret key where available, or OAuth token for private endpoints
- Understanding of which endpoints you call and how often
- `posthog-node` or direct API usage

## PostHog Rate Limit Tiers

| Endpoint Category | Rate Limit | Examples |
|-------------------|-----------|----------|
| Public event capture (`/e`, `/i/v0/e`, `/batch/`) | **No request-level limit** | SDK capture and batch ingestion |
| Public feature flags (`/flags`) | **No request-level limit** | Client-side flag evaluation |
| Analytics API (insights, persons, recordings) | **240/min, 1200/hour** | Trend queries, person lookup |
| Events values (`/events/values`) | **60/min, 300/hour** | Event-property value lookup |
| Query API (`/api/projects/:id/query/`) | **2400/hour** | HogQL and structured queries |
| Feature flag local evaluation polling | **600/min** | Server SDK flag definition fetch |
| Other private CRUD endpoints | **480/min, 4800/hour** | Feature flag CRUD, cohorts, annotations |

These budgets apply to the whole PostHog team, not to each key or process. Coordinate workers through a shared limiter when more than one caller uses the same endpoint class.

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Implement Exponential Backoff with Retry-After

```typescript
async function postHogApiCall<T>(
  url: string,
  options: RequestInit,
  maxRetries = 5
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.POSTHOG_PERSONAL_API_KEY}`,
        ...options.headers,
      },
    });

    if (response.ok) {
      return response.json();
    }

    if (response.status === 429) {
      // Honor the Retry-After header from PostHog
      const retryAfter = parseInt(response.headers.get('Retry-After') || '0');
      const backoffMs = retryAfter > 0
        ? retryAfter * 1000
        : Math.min(1000 * Math.pow(2, attempt) + Math.random() * 500, 32000);

      console.warn(`PostHog 429: retrying in ${Math.round(backoffMs)}ms (attempt ${attempt + 1}/${maxRetries})`);
      await new Promise(r => setTimeout(r, backoffMs));
      continue;
    }

    // Don't retry client errors (except 429)
    if (response.status >= 400 && response.status < 500) {
      const body = await response.text();
      throw new Error(`PostHog API ${response.status}: ${body}`);
    }

    // Retry server errors (500+)
    if (attempt < maxRetries) {
      const delay = 1000 * Math.pow(2, attempt);
      await new Promise(r => setTimeout(r, delay));
      continue;
    }

    throw new Error(`PostHog API failed after ${maxRetries} retries: ${response.status}`);
  }

  throw new Error('Unreachable');
}
```

### Step 2: Request Queue for Burst Protection

```typescript
import PQueue from 'p-queue';

// Conservative analytics budget: 20/min averages to 1200/hour.
// A shared limiter is required when multiple workers use the same PostHog team.
const posthogQueue = new PQueue({
  concurrency: 2,       // Max parallel requests
  interval: 60_000,
  intervalCap: 20,
});

async function queuedPostHogCall<T>(
  url: string,
  options: RequestInit
): Promise<T> {
  return posthogQueue.add(() => postHogApiCall<T>(url, options));
}

// Usage: all calls are automatically throttled
const insights = await queuedPostHogCall(
  `https://us.posthog.com/api/projects/${PROJECT_ID}/insights/trend/`,
  { method: 'GET' }
);
```

### Step 3: Cache Frequently Accessed Data

```typescript
// Cache insight results to reduce API calls
class PostHogCache {
  private cache = new Map<string, { data: any; expiry: number }>();

  async get<T>(key: string, fetcher: () => Promise<T>, ttlMs = 300000): Promise<T> {
    const cached = this.cache.get(key);
    if (cached && Date.now() < cached.expiry) {
      return cached.data as T;
    }

    const data = await fetcher();
    this.cache.set(key, { data, expiry: Date.now() + ttlMs });
    return data;
  }

  invalidate(key: string) {
    this.cache.delete(key);
  }
}

const phCache = new PostHogCache();

// Cache trend data for 5 minutes
const trends = await phCache.get('weekly-pageviews', () =>
  queuedPostHogCall(`https://us.posthog.com/api/projects/${PROJECT_ID}/insights/trend/?events=[{"id":"$pageview"}]&date_from=-7d`, { method: 'GET' })
);
```

### Step 4: Monitor Rate Limit Headers

```typescript
class RateLimitMonitor {
  private remaining = Infinity;
  private resetAt = 0;

  update(headers: Headers) {
    const remaining = headers.get('X-RateLimit-Remaining');
    const reset = headers.get('X-RateLimit-Reset');

    if (remaining) this.remaining = parseInt(remaining);
    if (reset) this.resetAt = parseInt(reset) * 1000;
  }

  shouldThrottle(): boolean {
    return this.remaining < 10 && Date.now() < this.resetAt;
  }

  waitTime(): number {
    return Math.max(0, this.resetAt - Date.now());
  }

  log() {
    console.log(`PostHog rate limit: ${this.remaining} remaining, resets in ${Math.round(this.waitTime() / 1000)}s`);
  }
}

const rateLimits = new RateLimitMonitor();

// After each API call, update the monitor
const response = await fetch(url, options);
rateLimits.update(response.headers);
if (rateLimits.shouldThrottle()) {
  console.warn(`Approaching PostHog rate limit — waiting ${rateLimits.waitTime()}ms`);
  await new Promise(r => setTimeout(r, rateLimits.waitTime()));
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| HTTP 429 on insights | >240 req/min on analytics | Queue requests, cache results |
| 429 on flag polling | >600 req/min local eval fetch | Increase `featureFlagsPollingInterval` |
| 429 on query API | >2400 req/hour across the team | Cache query results, reduce frequency, or use an export product |
| 429 on events values | >60 req/min or >300 req/hour | Cache dimensions and avoid interactive polling |
| 429 on other CRUD | >480 req/min or >4800 req/hour | Coordinate callers through a team-wide limiter |
| Thundering herd on retry | All clients retry simultaneously | Add random jitter to backoff |

## Key Points

- **Public capture and `/flags` have no PostHog request-level limit** — still inspect successful capture responses for `quota_limited` and check ingestion warnings.
- **Private endpoints are limited by class** — authentication may be a personal key, project secret key where available, or OAuth.
- **Limits are team-wide** — separate keys do not create separate budgets.
- **Cache aggressively** — insight data rarely needs real-time refresh
- **Honor Retry-After** — PostHog tells you exactly how long to wait

## Output

- Exponential backoff with Retry-After header support
- Endpoint-class request queue that respects both minute and hour budgets
- In-memory cache for API responses
- Rate limit header monitoring

## Examples

For a scheduled HogQL query job, budget against the documented query limit, serialize retries from `Retry-After`, add jitter, and stop after a bounded attempt count. Do not apply private-API limits to public capture endpoints; inspect `quota_limited` and ingestion warnings separately.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog API Overview (rate limits)](https://posthog.com/docs/api)
- [PostHog Feature Flag Local Evaluation](https://posthog.com/docs/feature-flags/local-evaluation)
- [p-queue](https://github.com/sindresorhus/p-queue)

## Next Steps

For security configuration, see `posthog-security-basics`.
