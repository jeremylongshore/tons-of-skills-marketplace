---
name: rate-limiting-apis
description: 'Implement sophisticated rate limiting with sliding windows, token buckets,
  and quotas.

  Use when protecting APIs from excessive requests.

  Trigger with phrases like "add rate limiting", "limit API requests", or "implement
  rate limits".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:ratelimit-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- rate-limiting
compatibility: Designed for Claude Code
---
# Rate Limiting APIs

## Overview

Implement sophisticated rate limiting using sliding window, token bucket, and fixed window counter algorithms with Redis-backed distributed state. Configure per-endpoint, per-user, and per-API-key limits with tiered quotas, burst allowances, and standard response headers that communicate limit status to API consumers.

## Prerequisites

- Redis 6+ for distributed rate limit state (required for multi-instance deployments)
- Rate limiting library: `rate-limiter-flexible` (Node.js), `slowapi` (Python/FastAPI), or Bucket4j (Java)
- API key or user identification mechanism for per-consumer tracking
- Monitoring for rate limit hit rates and rejected request metrics
- Documentation system for publishing rate limit policies to API consumers

## Instructions

1. Analyze endpoint traffic patterns using Read and Grep on access logs or metrics to determine appropriate rate limits per endpoint category (read-heavy, write-heavy, resource-intensive).
2. Select the rate limiting algorithm per endpoint: token bucket for bursty traffic allowance, sliding window log for precise per-second limits, or fixed window counter for simple quota enforcement.
3. Implement rate limiting middleware that extracts the client identifier (API key from header, user ID from JWT, or IP address as fallback) and checks against the configured limit.
4. Configure tiered rate limits per API consumer plan: Free (100 req/min), Pro (1000 req/min), Enterprise (10000 req/min) with per-endpoint overrides for expensive operations.
5. Add burst allowance using token bucket: allow 2x the sustained rate for 10 seconds to handle legitimate traffic spikes without penalizing well-behaved clients.
6. Set standard rate limit response headers on every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix timestamp), and `RateLimit-Policy` (draft IETF standard).
7. Return 429 Too Many Requests with `Retry-After` header (seconds until next allowed request) and a JSON body explaining the limit, current usage, and reset time.
8. Implement rate limit bypass for internal service-to-service calls using shared secret or mutual TLS identification to prevent internal traffic from consuming consumer quotas.
9. Write tests that verify rate limits engage at exact thresholds, headers reflect correct remaining counts, and limits reset at the configured window boundary.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/rate-limiter.js` - Rate limiting middleware with algorithm selection
- `${CLAUDE_SKILL_DIR}/src/config/rate-limits.js` - Per-endpoint and per-tier rate limit configuration
- `${CLAUDE_SKILL_DIR}/src/utils/rate-limit-store.js` - Redis-backed distributed counter implementation
- `${CLAUDE_SKILL_DIR}/src/middleware/rate-limit-headers.js` - Standard rate limit response header injection
- `${CLAUDE_SKILL_DIR}/tests/rate-limiting/` - Rate limit threshold verification tests
- `${CLAUDE_SKILL_DIR}/docs/rate-limits.md` - Consumer-facing rate limit documentation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 429 Too Many Requests | Client exceeded configured rate limit for the endpoint | Return `Retry-After` header with seconds until reset; include limit details in JSON body |
| Redis connection failure | Rate limit state store unavailable | Fail open (allow requests) or fail closed (reject all) based on security posture; alert immediately |
| Clock skew between instances | Distributed rate limit windows misaligned across servers | Use Redis server time (`TIME` command) as canonical clock; avoid relying on application server clocks |
| Inconsistent counts | Race condition in read-check-increment cycle | Use Redis `MULTI/EXEC` transaction or Lua script for atomic increment-and-check operations |
| Bypass abuse | Internal bypass mechanism exploited by external client | Validate bypass credentials per-request; restrict bypass to specific IP ranges or mTLS certificates |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Sliding window with Redis**: Implement a sliding window rate limiter using Redis sorted sets, where each request adds a timestamped entry and the window count is computed by `ZRANGEBYSCORE` over the last 60 seconds.

**Tiered SaaS quotas**: Free tier gets 100 requests/minute with no burst, Pro tier gets 1000 requests/minute with 2x burst for 10 seconds, Enterprise tier gets 10000 requests/minute with custom per-endpoint overrides.

**Login endpoint protection**: Apply strict rate limit of 5 attempts per minute per IP on `/auth/login` to prevent brute force attacks, with progressive lockout (15 min, 1 hour, 24 hours) after repeated violations.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- IETF RateLimit header fields draft: https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/
- Token bucket algorithm explained
- `rate-limiter-flexible` library: https://github.com/animir/node-rate-limiter-flexible
- Redis rate limiting patterns with Lua scripts
