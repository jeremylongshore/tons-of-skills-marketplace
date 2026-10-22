---
name: throttling-apis
description: 'Implement API throttling policies to protect backend services from overload.

  Use when controlling API request rates.

  Trigger with phrases like "throttle API", "control request rate", or "add throttling".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:throttle-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- throttling-apis
compatibility: Designed for Claude Code
---
# Throttling APIs

## Overview

Implement API throttling policies that protect backend services from overload by controlling request concurrency, queue depth, and processing rates. Apply backpressure mechanisms including concurrent request limits, priority queues, circuit breakers, and adaptive throttling that adjusts limits based on real-time backend health metrics.

## Prerequisites

- Middleware-capable web framework (Express, FastAPI, Spring Boot, Gin)
- Redis or in-memory store for distributed throttle state tracking
- Monitoring system exposing backend latency and error rate metrics (Prometheus, CloudWatch)
- Load testing tool (k6, Artillery, wrk) for validating throttle behavior under pressure
- Queue system for request buffering during throttle events (optional: Bull, SQS)

## Instructions

1. Analyze existing route handlers and middleware using Grep and Read to identify endpoints with high latency, database-heavy operations, or external service dependencies that need throttle protection.
2. Implement a concurrency limiter middleware that tracks in-flight requests per endpoint and rejects new requests with 503 Service Unavailable when the concurrent limit is reached.
3. Add priority queue support that classifies requests by API key tier (free, pro, enterprise) and serves higher-tier requests first when approaching throttle limits.
4. Build a circuit breaker for downstream service calls that opens after configurable failure thresholds (e.g., 5 failures in 10 seconds), returning 503 with `Retry-After` during the open state.
5. Configure adaptive throttling that monitors backend response latency percentiles (p95, p99) and automatically reduces concurrency limits when latency exceeds SLO thresholds.
6. Add throttle state headers to all responses: `X-Throttle-Limit`, `X-Throttle-Remaining`, and `X-Throttle-Reset` for client-side awareness.
7. Implement graceful degradation strategies per endpoint: serve cached responses, return partial results, or queue requests for deferred processing.
8. Write load tests that verify throttle engagement at expected thresholds, proper 503 responses with `Retry-After`, and recovery behavior when load subsides.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/throttle.js` - Concurrency and request rate throttling middleware
- `${CLAUDE_SKILL_DIR}/src/middleware/circuit-breaker.js` - Circuit breaker for downstream service protection
- `${CLAUDE_SKILL_DIR}/src/middleware/priority-queue.js` - Tier-based request prioritization
- `${CLAUDE_SKILL_DIR}/src/config/throttle-config.js` - Per-endpoint throttle policy definitions
- `${CLAUDE_SKILL_DIR}/tests/throttle/` - Load tests validating throttle engagement and recovery

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 503 Service Unavailable | Concurrency limit reached for the endpoint | Return `Retry-After` header with estimated wait time; include throttle state headers |
| 503 Circuit Open | Circuit breaker tripped due to downstream failures | Return cached response if available; provide circuit reset time in response body |
| Queue overflow | Request buffer exceeded maximum depth | Reject with 503; alert operations team; consider scaling backend capacity |
| Stale throttle state | Redis connection lost; throttle counters become inaccurate | Fall back to in-process counters; reconnect with backoff; log state inconsistency |
| Priority starvation | Low-tier requests never served under sustained high-tier load | Reserve minimum throughput percentage for each tier to prevent complete starvation |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Database-heavy endpoint protection**: Apply concurrency limit of 10 to a report generation endpoint that runs expensive aggregation queries, queueing additional requests with estimated wait times.

**Multi-tier SaaS throttling**: Enterprise tier gets 100 concurrent requests, Pro tier gets 25, Free tier gets 5, with priority queue ensuring enterprise requests are served first during contention.

**Adaptive autoscaling trigger**: Throttle middleware emits metrics that trigger horizontal pod autoscaling when throttle engagement rate exceeds 20% sustained over 5 minutes.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Circuit Breaker pattern: Martin Fowler's design patterns
- Resilience4j (Java) and cockatiel (Node.js) circuit breaker libraries
- Netflix Concurrency Limits library for adaptive throttling
- Token bucket and leaky bucket algorithm implementations
