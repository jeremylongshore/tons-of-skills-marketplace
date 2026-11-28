---
name: vercel-rate-limits
description: 'Handle Vercel API rate limits, implement retry logic, and configure
  WAF rate limiting.

  Use when hitting 429 errors, implementing retry logic,

  or setting up rate limiting for your Vercel-deployed API endpoints.

  Trigger with phrases like "vercel rate limit", "vercel throttling",

  "vercel 429", "vercel retry", "vercel backoff", "vercel WAF rate limit".

  '
allowed-tools: Read, Write, Edit
version: 1.18.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- vercel
- api
- rate-limiting
- security
compatibility: Designed for Claude Code
---
# Vercel Rate Limits

## Overview

Handle Vercel REST API rate limits with proper retry logic, and configure Vercel's WAF rate limiting SDK to protect your deployed API endpoints from abuse. Covers both consuming the Vercel API (outbound) and protecting your own functions (inbound).

## Prerequisites

- Vercel CLI installed and authenticated
- Understanding of HTTP 429 status codes
- For WAF rate limiting: Vercel Pro or Enterprise plan

## Instructions

### Step 1: Vercel REST API Rate Limits

The Vercel REST API enforces rate limits per endpoint. When exceeded, the API returns HTTP 429 with rate limit headers:

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711152000
Retry-After: 60
```

**Known API limits:**

| Endpoint Category | Rate Limit |
|-------------------|-----------|
| Deployments (create) | 100/hour per project |
| Deployments (list/get) | 500/min |
| Projects (CRUD) | 200/min |
| Environment variables | 200/min |
| Domains | 200/min |
| Teams | 200/min |
| DNS records | 200/min |
| General API | 120 requests/min (default) |

### Step 2: Implement Retry with Backoff for Vercel API

```typescript
// lib/rate-limit-handler.ts
interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number; // Unix timestamp
}

function parseRateLimitHeaders(headers: Headers): RateLimitInfo {
  return {
    limit: Number(headers.get('X-RateLimit-Limit') ?? 100),
    remaining: Number(headers.get('X-RateLimit-Remaining') ?? 100),
    reset: Number(headers.get('X-RateLimit-Reset') ?? 0),
  };
}

async function vercelFetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const res = await fetch(url, options);

    if (res.status !== 429) return res;

    if (attempt === maxRetries) {
      throw new Error(`Rate limited after ${maxRetries} retries: ${url}`);
    }

    // Use Retry-After header if present, otherwise exponential backoff
    const retryAfter = res.headers.get('Retry-After');
    const waitMs = retryAfter
      ? Number(retryAfter) * 1000
      : Math.min(1000 * Math.pow(2, attempt) + Math.random() * 1000, 30000);

    console.warn(`Rate limited (attempt ${attempt + 1}/${maxRetries}). Waiting ${Math.round(waitMs)}ms...`);
    await new Promise(r => setTimeout(r, waitMs));
  }
  throw new Error('Unreachable');
}
```

### Step 3: Proactive Rate Limit Avoidance

```typescript
// lib/rate-limiter.ts
// Track remaining quota and slow down before hitting the wall
class VercelRateLimiter {
  private remaining = 100;
  private resetAt = 0;

  async throttle(): Promise<void> {
    // If near the limit, wait until reset
    if (this.remaining < 5) {
      const waitMs = Math.max(0, this.resetAt * 1000 - Date.now()) + 1000;
      console.warn(`Near rate limit (${this.remaining} remaining). Waiting ${waitMs}ms...`);
      await new Promise(r => setTimeout(r, waitMs));
    }
  }

  update(headers: Headers): void {
    this.remaining = Number(headers.get('X-RateLimit-Remaining') ?? this.remaining);
    this.resetAt = Number(headers.get('X-RateLimit-Reset') ?? this.resetAt);
  }
}
```

### Step 4: Protect Your Own Endpoints — Vercel WAF Rate Limiting

Vercel's WAF provides built-in rate limiting for your deployed functions:

```typescript
// middleware.ts — WAF rate limiting via Vercel Firewall SDK
import { ipAddress } from '@vercel/functions';
import { checkRateLimit } from '@vercel/firewall';

export async function middleware(request: Request) {
  const ip = ipAddress(request) ?? '127.0.0.1';

  // Rate limit: 100 requests per 60 seconds per IP
  const { rateLimited } = await checkRateLimit('api-limit', {
    key: ip,
    limit: 100,
    window: '60s',
  });

  if (rateLimited) {
    return new Response(
      JSON.stringify({ error: 'Too many requests. Please try again later.' }),
      { status: 429, headers: { 'Content-Type': 'application/json', 'Retry-After': '60' } }
    );
  }
}

export const config = {
  matcher: '/api/:path*',
};
```

Install: `npm install @vercel/firewall @vercel/functions`

### Step 5: Custom Rate Limiting with Edge Config

```typescript
// api/rate-limited-endpoint.ts
import { get } from '@vercel/edge-config';

export const config = { runtime: 'edge' };

// Simple in-memory sliding window (per-isolate, not global)
const windowMs = 60_000;
const maxRequests = 50;
const requests = new Map<string, number[]>();

function isRateLimited(key: string): boolean {
  const now = Date.now();
  const timestamps = (requests.get(key) ?? []).filter(t => now - t < windowMs);
  timestamps.push(now);
  requests.set(key, timestamps);
  return timestamps.length > maxRequests;
}

export default async function handler(request: Request): Promise<Response> {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';

  if (isRateLimited(ip)) {
    return Response.json({ error: 'Rate limit exceeded' }, { status: 429 });
  }

  return Response.json({ data: 'ok' });
}
```

## Platform Concurrency Limits

| Plan | Concurrent Executions | Builds/Hour |
|------|-----------------------|-------------|
| Hobby | 10 | 32 |
| Pro | 1,000 | 6,000/day |
| Enterprise | 100,000 | Custom |

## Output

- Vercel API calls wrapped with automatic retry and backoff
- Rate limit headers parsed and monitored proactively
- WAF rate limiting protecting deployed API endpoints
- Custom per-IP rate limiting for fine-grained control

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | API rate limit exceeded | Use `vercelFetchWithRetry()` wrapper |
| `FUNCTION_THROTTLED` | Concurrent execution limit hit | Reduce parallelism or upgrade plan |
| Rate limit not applied | Middleware not matching routes | Check `config.matcher` pattern |
| In-memory rate limit resets | Edge function isolate recycled | Use a shared store such as Upstash Redis for persistent state |

## Examples

### Apply a fair API limit without blocking trusted automation

Start with a per-route, per-principal limit in preview and exempt only named, authenticated service identities through a reviewed allowlist. Exercise normal, burst, and retry behavior with synthetic clients, ensuring 429 responses include a safe retry interval and do not reveal internal quota details. Monitor false positives after rollout; if a critical integration is blocked, use a narrowly scoped temporary limit adjustment, then correct the policy instead of disabling rate limiting.

## Resources

- [Vercel Limits](https://vercel.com/docs/limits)
- [WAF Rate Limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting)
- [Rate Limiting SDK](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting-sdk)
- [FUNCTION_THROTTLED](https://vercel.com/docs/errors/FUNCTION_THROTTLED)
- [Concurrency Scaling](https://vercel.com/docs/functions/concurrency-scaling)

## Next Steps

For security best practices, see `vercel-security-basics`.
