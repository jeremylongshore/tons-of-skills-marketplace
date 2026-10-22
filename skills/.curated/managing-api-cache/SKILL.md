---
name: managing-api-cache
description: 'Implement intelligent API response caching with Redis, Memcached, and
  CDN integration.

  Use when optimizing API performance with caching.

  Trigger with phrases like "add caching", "optimize API performance", or "implement
  cache layer".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:cache-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- redis
- performance
compatibility: Designed for Claude Code
---
# Managing API Cache

## Overview

Implement intelligent API response caching using Redis, Memcached, or in-memory stores with cache key generation, TTL management, cache invalidation strategies, and HTTP cache headers. Support read-through, write-through, and cache-aside patterns with tag-based invalidation for related resources and stale-while-revalidate behavior.

## Prerequisites

- Redis 6+ or Memcached for distributed caching (required for multi-instance deployments)
- Cache client library: `ioredis` (Node.js), `redis-py` (Python), or Lettuce (Java)
- CDN with cache control support for edge caching (CloudFront, Cloudflare, Fastly) -- optional
- Monitoring for cache hit/miss ratios and eviction rates
- Understanding of data freshness requirements per endpoint

## Instructions

1. Analyze endpoint characteristics using Read and Grep to classify endpoints by cacheability: fully cacheable (static data), conditionally cacheable (user-specific data), and never cacheable (mutations, real-time data).
2. Implement cache key generation middleware that creates deterministic keys from method, path, query parameters (sorted), and relevant headers (Accept, Authorization hash for user-specific caches).
3. Build a cache-aside middleware that checks the cache before executing the handler, returning cached responses with `X-Cache: HIT` header, or executing the handler, caching the result, and returning with `X-Cache: MISS`.
4. Configure TTL per endpoint category: long TTL (1 hour) for reference data, medium TTL (5 minutes) for frequently changing lists, short TTL (30 seconds) for near-real-time data.
5. Implement cache invalidation on mutations: when a POST/PUT/DELETE modifies a resource, invalidate all cached responses containing that resource using tag-based invalidation.
6. Add `Cache-Control`, `ETag`, and `Last-Modified` response headers for HTTP-level caching, enabling CDN and browser cache participation.
7. Implement stale-while-revalidate behavior: serve stale cached responses immediately while asynchronously refreshing the cache in the background, reducing perceived latency.
8. Add cache warming for critical endpoints: pre-populate cache entries on application startup or schedule for frequently accessed resources.
9. Write tests verifying cache hits, misses, invalidation correctness, TTL expiration, and stale-while-revalidate behavior.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/cache.js` - Cache-aside middleware with hit/miss tracking
- `${CLAUDE_SKILL_DIR}/src/cache/key-generator.js` - Deterministic cache key generation
- `${CLAUDE_SKILL_DIR}/src/cache/invalidator.js` - Tag-based cache invalidation on mutations
- `${CLAUDE_SKILL_DIR}/src/cache/store.js` - Redis/Memcached cache store abstraction
- `${CLAUDE_SKILL_DIR}/src/config/cache-policies.js` - Per-endpoint TTL and caching policy configuration
- `${CLAUDE_SKILL_DIR}/tests/cache/` - Cache behavior verification tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Cache stampede | TTL expires simultaneously for popular key; many requests hit database | Use lock-based revalidation (only one request refreshes); apply jittered TTLs |
| Stale data served | Cache invalidation missed a related resource after mutation | Implement tag-based invalidation covering all affected cache keys; add invalidation audit logging |
| Redis connection failure | Cache store unavailable due to network or server issue | Fall through to database with degraded performance; log cache bypass; alert on sustained failures |
| Cache key collision | Different requests generating identical cache keys | Include all varying parameters in key; hash the full normalized request for uniqueness |
| Memory pressure | Cache grows unbounded consuming all available Redis memory | Configure Redis `maxmemory-policy` to `allkeys-lru`; set per-key size limits; monitor memory usage |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Product catalog caching**: Cache `GET /products` list for 5 minutes and `GET /products/:id` for 1 hour, invalidating both when any product is created, updated, or deleted via tag `products`.

**User-specific dashboard**: Cache dashboard data per user using `cache:dashboard:{userId}` keys with 30-second TTL, serving stale data during revalidation to keep perceived response time under 50ms.

**CDN edge caching**: Set `Cache-Control: public, max-age=300, stale-while-revalidate=60` on public endpoints, enabling CloudFront to serve cached responses at the edge while revalidating asynchronously.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Redis caching patterns: https://redis.io/docs/manual/patterns/
- HTTP caching (MDN): https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- Cache-aside vs. read-through vs. write-through patterns
- Stale-while-revalidate: RFC 5861
