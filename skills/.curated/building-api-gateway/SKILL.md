---
name: building-api-gateway
description: 'Create API gateways with routing, load balancing, rate limiting, and
  authentication.

  Use when routing and managing multiple API services.

  Trigger with phrases like "build API gateway", "create API router", or "setup API
  gateway".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:gateway-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- authentication
- api-gateway
compatibility: Designed for Claude Code
---
# Building API Gateway

## Overview

Create an API gateway that provides unified entry point routing, load balancing, authentication enforcement, rate limiting, request transformation, and response aggregation across multiple backend microservices. Support path-based and header-based routing, circuit breaker protection for downstream services, and centralized cross-cutting concern management.

## Prerequisites

- Multiple backend API services with known endpoints, health check URLs, and authentication requirements
- Gateway framework: Express Gateway, Kong (declarative config), KrakenD, or custom Node.js/Go implementation
- Service registry or static upstream configuration for backend service discovery
- TLS certificates for gateway termination and optional mTLS for backend communication
- Centralized logging and metrics collection for gateway-level observability

## Instructions

1. Inventory all backend services using Read and Grep, documenting their base URLs, endpoint paths, authentication requirements, and health check endpoints.
2. Define routing rules that map public-facing URL patterns to backend service endpoints: path-based (`/users/*` -> user-service), header-based (`X-API-Version: 2` -> v2-service), or method-based routing.
3. Implement authentication at the gateway layer: validate JWT tokens, API keys, or OAuth2 tokens once at the gateway and forward authenticated user context to backend services via headers (`X-User-ID`, `X-User-Roles`).
4. Add rate limiting at the gateway level with per-consumer quotas, applying limits before requests reach backend services to protect all downstream services uniformly.
5. Configure request transformation: strip internal headers from incoming requests, add correlation IDs, rewrite URL paths for backend routing, and inject service-specific headers.
6. Implement response aggregation for composite endpoints that fan out to multiple backend services, merge responses, and return a unified payload to the client.
7. Add circuit breaker protection per backend service: open the circuit after configurable failure thresholds, return 503 with the failed service identified, and auto-recover after health check success.
8. Configure health check aggregation: gateway `/health` endpoint reports overall status based on individual backend service health, with degraded state support for non-critical service failures.
9. Write integration tests covering routing correctness, auth enforcement, rate limiting, circuit breaker behavior, and response aggregation.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/gateway/config/routes.yaml` - Route mapping definitions (path -> service)
- `${CLAUDE_SKILL_DIR}/gateway/middleware/auth.js` - Gateway-level authentication enforcement
- `${CLAUDE_SKILL_DIR}/gateway/middleware/rate-limiter.js` - Centralized rate limiting
- `${CLAUDE_SKILL_DIR}/gateway/middleware/circuit-breaker.js` - Per-service circuit breaker
- `${CLAUDE_SKILL_DIR}/gateway/middleware/transform.js` - Request/response transformation logic
- `${CLAUDE_SKILL_DIR}/gateway/aggregators/` - Response aggregation for composite endpoints
- `${CLAUDE_SKILL_DIR}/gateway/health.js` - Aggregated health check endpoint
- `${CLAUDE_SKILL_DIR}/tests/gateway/` - Gateway integration test suite

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 502 Bad Gateway | Backend service returned invalid response or connection refused | Return descriptive error identifying the failed backend; trigger circuit breaker if threshold met |
| 503 Circuit Open | Backend service circuit breaker is open due to repeated failures | Return `Retry-After` header; serve cached response if available; route to fallback service if configured |
| 504 Gateway Timeout | Backend service response exceeded gateway timeout threshold | Configure per-route timeout limits; implement timeout cascading shorter than client timeout |
| Routing miss | Request path does not match any configured route | Return 404 with list of available API paths; log unmatched routes for route configuration review |
| Auth header stripping | Proxy strips Authorization header before forwarding to backend | Configure gateway to preserve or transform auth headers; verify proxy `proxy_pass_header` settings |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Microservices gateway**: Route `/users/*` to user-service (port 3001), `/orders/*` to order-service (port 3002), and `/products/*` to product-service (port 3003), with unified JWT validation and per-service circuit breakers.

**BFF (Backend for Frontend)**: Gateway aggregates data from user-service, preferences-service, and notification-service into a single `/dashboard` response, reducing frontend API calls from 3 to 1.

**API versioning gateway**: Route requests to different backend deployments based on `Accept-Version` header, enabling blue-green deployments and gradual version migration without client-side URL changes.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Kong API Gateway: https://konghq.com/
- Express Gateway: https://www.express-gateway.io/
- KrakenD: https://www.krakend.io/
- API Gateway pattern: Microservices.io
