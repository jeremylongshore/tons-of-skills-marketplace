---
name: clerk-rate-limits
description: 'Understand and manage Clerk rate limits and quotas.

  Use when hitting rate limits, optimizing API usage,

  or planning for high-traffic scenarios.

  Trigger with phrases like "clerk rate limit", "clerk quota",

  "clerk API limits", "clerk throttling".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- api
compatibility: Designed for Claude Code
---
# Clerk Rate Limits

## Overview

Understand Clerk's rate limiting system and implement strategies to avoid hitting limits. Covers Backend API rate limits, retry logic, batching, caching, and monitoring.

## Prerequisites

- Clerk account with API access
- Understanding of your application's traffic patterns
- Monitoring/logging infrastructure

## Instructions

### Step 1: Understand Rate Limits

Clerk Backend API enforces rate limits per API key:

| Plan | Rate Limit | Burst |
|------|-----------|-------|
| Free | 20 req/10s | 40 |
| Pro | 100 req/10s | 200 |
| Enterprise | Custom | Custom |

Rate limit headers returned on every response:

- `X-RateLimit-Limit` — max requests per window
- `X-RateLimit-Remaining` — remaining requests
- `X-RateLimit-Reset` — seconds until window resets

### Step 2: Implement Rate Limit Handling with Retry

```typescript
// lib/clerk-api.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (err: any) {
      if (err.status === 429 && attempt < maxRetries) {
        // Parse retry-after header or use exponential backoff
        const retryAfter = err.headers?.['retry-after']
        const waitMs = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000
        console.warn(`Rate limited. Retrying in ${waitMs}ms (attempt ${attempt + 1}/${maxRetries})`)
        await new Promise((resolve) => setTimeout(resolve, waitMs))
        continue
      }
      throw err
    }
  }
  throw new Error('Max retries exceeded')
}

// Usage
export async function getUser(userId: string) {
  return withRetry(() => clerk.users.getUser(userId))
}
```

### Step 3: Batch Operations

```typescript
// lib/clerk-batch.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function batchGetUsers(userIds: string[], batchSize = 10) {
  const results = []

  for (let i = 0; i < userIds.length; i += batchSize) {
    const batch = userIds.slice(i, i + batchSize)
    const users = await Promise.all(batch.map((id) => clerk.users.getUser(id)))
    results.push(...users)

    // Respect rate limits between batches
    if (i + batchSize < userIds.length) {
      await new Promise((resolve) => setTimeout(resolve, 500))
    }
  }

  return results
}

// For listing: use pagination instead of fetching all
async function getAllUsers() {
  const allUsers = []
  let offset = 0
  const limit = 100

  while (true) {
    const batch = await clerk.users.getUserList({ limit, offset })
    allUsers.push(...batch.data)
    if (batch.data.length < limit) break
    offset += limit
    await new Promise((resolve) => setTimeout(resolve, 200)) // Rate limit pause
  }

  return allUsers
}
```

### Step 4: Caching Strategy

```typescript
// lib/clerk-cache.ts
const userCache = new Map<string, { user: any; cachedAt: number }>()
const CACHE_TTL = 60_000 // 1 minute

export async function getCachedUser(userId: string) {
  const cached = userCache.get(userId)
  if (cached && Date.now() - cached.cachedAt < CACHE_TTL) {
    return cached.user
  }

  const { createClerkClient } = await import('@clerk/backend')
  const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })
  const user = await clerk.users.getUser(userId)
  userCache.set(userId, { user, cachedAt: Date.now() })
  return user
}

// Invalidate cache on webhook events
export function invalidateUserCache(userId: string) {
  userCache.delete(userId)
}
```

For production, use Redis instead of in-memory cache:

```typescript
import { Redis } from '@upstash/redis'

const redis = Redis.fromEnv()

export async function getCachedUserRedis(userId: string) {
  const cached = await redis.get(`clerk:user:${userId}`)
  if (cached) return cached

  const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })
  const user = await clerk.users.getUser(userId)
  await redis.set(`clerk:user:${userId}`, JSON.stringify(user), { ex: 60 })
  return user
}
```

### Step 5: Monitor Rate Limit Usage

```typescript
// lib/clerk-monitor.ts
let rateLimitHits = 0

export function trackRateLimit(response: Response) {
  const remaining = parseInt(response.headers.get('X-RateLimit-Remaining') || '999')
  const limit = parseInt(response.headers.get('X-RateLimit-Limit') || '0')

  if (remaining < limit * 0.1) {
    console.warn(`[Clerk] Rate limit warning: ${remaining}/${limit} remaining`)
  }

  if (remaining === 0) {
    rateLimitHits++
    console.error(`[Clerk] Rate limit hit! Total hits this session: ${rateLimitHits}`)
  }
}
```

## Output

- Retry logic with exponential backoff for 429 responses
- Batch operations respecting rate limits
- Multi-level caching (in-memory + Redis)
- Rate limit monitoring with warnings

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit exceeded | Implement retry with backoff, add caching |
| `quota_exceeded` | Monthly MRU quota hit | Upgrade plan or reduce retained users |
| Concurrent limit hit | Too many parallel requests | Queue requests, reduce `batchSize` |
| Stale cache data | Cache not invalidated | Invalidate on `user.updated` webhook |

## Examples

### Quick Rate Limit Check

```bash
# Check current rate limit status
curl -s -D - -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  https://api.clerk.com/v1/users?limit=1 2>&1 | grep -i x-ratelimit
```

## Resources

- [Clerk Rate Limits](https://clerk.com/docs/backend-requests/resources/rate-limits)
- [Backend API Best Practices](https://clerk.com/docs/backend-requests/overview)
- [Clerk Pricing & Quotas](https://clerk.com/pricing)

## Next Steps

Proceed to `clerk-security-basics` for security best practices.
