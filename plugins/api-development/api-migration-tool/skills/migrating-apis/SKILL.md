---
name: migrating-apis
description: 'Implement API migrations between versions, platforms, or frameworks
  with minimal downtime.

  Use when upgrading APIs between versions.

  Trigger with phrases like "migrate the API", "upgrade API version", or "migrate
  to new API".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:migrate-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- migration
- migrating-apis
compatibility: Designed for Claude Code
---
# Migrating APIs

## Overview

Implement API migrations between versions, frameworks, or platforms with minimal downtime using strangler fig pattern, parallel running, and traffic shadowing. Generate migration plans that map old endpoints to new equivalents, transform request/response formats, and validate data consistency between legacy and target implementations.

## Prerequisites

- Source API codebase and OpenAPI specification accessible for analysis
- Target framework or platform environment provisioned and accessible
- Traffic routing capability for gradual cutover (reverse proxy, feature flags, or API gateway)
- Database migration tools if schema changes accompany the API migration (Flyway, Alembic, Prisma Migrate)
- Integration test suite covering all existing API consumers

## Instructions

1. Inventory all existing endpoints using Grep and Read, documenting HTTP methods, URL patterns, request/response schemas, authentication mechanisms, and consumer dependencies.
2. Generate an endpoint mapping table that pairs each legacy endpoint with its target equivalent, flagging breaking changes in URL structure, field names, data types, and authentication flow.
3. Create request/response adapters that transform legacy format to target format, handling field renames, nested-to-flat conversions, and enum value changes.
4. Implement a traffic router (reverse proxy rules or middleware) that directs requests to either the legacy or target implementation based on migration phase, endpoint, or feature flag.
5. Set up traffic shadowing to duplicate production requests to the target implementation without serving target responses, comparing outputs for data consistency validation.
6. Build a migration dashboard tracking per-endpoint migration status (legacy-only, shadow, canary, migrated), error rates, and latency comparison between implementations.
7. Execute phased cutover: shadow (compare only) -> canary (1% traffic to target) -> gradual ramp (10%, 25%, 50%, 100%) -> legacy decommission, with automatic rollback triggers.
8. Validate migration completeness by running the full integration test suite against the target implementation and comparing response bodies with legacy for a representative request sample.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/migration/endpoint-mapping.json` - Legacy-to-target endpoint mapping with change annotations
- `${CLAUDE_SKILL_DIR}/migration/adapters/` - Request/response transformation functions per endpoint
- `${CLAUDE_SKILL_DIR}/migration/router.js` - Traffic routing middleware with phase-based switching
- `${CLAUDE_SKILL_DIR}/migration/shadow-compare.js` - Traffic shadow comparison and diff reporting
- `${CLAUDE_SKILL_DIR}/migration/dashboard.md` - Migration progress tracking per endpoint
- `${CLAUDE_SKILL_DIR}/tests/migration/` - Parity tests comparing legacy and target responses

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Response mismatch in shadow | Target returns different data than legacy for same request | Log diff details; classify as expected (intentional change) or bug; fix before canary phase |
| Adapter transformation failure | Legacy request contains edge-case field values not handled by adapter | Add fallback handling; log unmatched fields; expand adapter test coverage |
| Rollback triggered | Canary error rate exceeds threshold (e.g., >2% 5xx) | Automatically route traffic back to legacy; alert migration team; analyze failures |
| Consumer authentication break | Target uses different auth scheme than legacy | Run auth adapter translating legacy tokens to target format during transition |
| Data inconsistency | Database schema migration introduced transformation errors | Run data validation queries comparing legacy and target data stores; fix transformation logic |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Express to FastAPI migration**: Migrate a Node.js Express API to Python FastAPI, using nginx as the traffic router, shadowing production traffic for 1 week, then canary-releasing endpoint by endpoint over 4 weeks.

**REST to GraphQL migration**: Implement GraphQL resolvers that call the existing REST endpoints internally, gradually replacing REST data fetching with direct database access while maintaining the REST surface via a thin GraphQL-to-REST adapter.

**Monolith to microservices**: Extract a user management module from a monolithic API into a standalone service, using the strangler fig pattern with API gateway routing to direct `/users/*` traffic to the new service while other endpoints remain on the monolith.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Strangler Fig Application pattern: Martin Fowler
- Feature flag services: LaunchDarkly, Unleash, Flagsmith
- Traffic shadowing with Envoy proxy or Istio service mesh
- Blue-green and canary deployment strategies
