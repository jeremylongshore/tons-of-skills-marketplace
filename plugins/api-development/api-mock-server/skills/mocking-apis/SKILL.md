---
name: mocking-apis
description: 'Generate mock API servers for testing and development with realistic
  response data.

  Use when creating mock APIs for development and testing.

  Trigger with phrases like "create mock API", "generate API mock", or "setup mock
  server".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:mock-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- testing
- mocking-apis
compatibility: Designed for Claude Code
---
# Mocking APIs

## Overview

Generate mock API servers from OpenAPI specifications that return realistic, schema-compliant response data for development and testing. Support dynamic response generation with Faker.js data, configurable latency simulation, stateful CRUD behavior, and request recording for contract testing validation.

## Prerequisites

- OpenAPI 3.0+ specification file with response schema definitions
- Mock server runtime: Prism (Stoplight), json-server, MSW (Mock Service Worker), or WireMock
- Faker.js or equivalent for realistic test data generation
- Docker for containerized mock server deployment (optional but recommended)
- Frontend or consumer application needing API stubs for parallel development

## Instructions

1. Read the OpenAPI specification using Read and extract all endpoint definitions, response schemas, and example values to build the mock response inventory.
2. Generate response fixtures for each endpoint using schema-aware data generation: realistic names (Faker), valid emails, properly formatted dates, and relational IDs that reference other mock entities.
3. Configure the mock server to match requests by method, path pattern, query parameters, and request body content type, returning the appropriate fixture.
4. Add stateful behavior for CRUD operations: POST creates a record in memory, GET returns it, PUT updates it, DELETE removes it -- enabling realistic integration testing flows.
5. Implement configurable response delays (50-500ms per endpoint) to simulate real-world latency and test client timeout handling.
6. Add error scenario mocking: configure specific request patterns to return 400, 401, 404, 429, or 500 responses for testing error handling paths.
7. Enable request recording that captures all incoming requests with timestamps and headers for later replay in contract tests.
8. Create a startup script that launches the mock server on a configurable port with hot-reload when fixture files change.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/mocks/server.js` - Mock server entry point with route registration
- `${CLAUDE_SKILL_DIR}/mocks/fixtures/` - Per-endpoint response fixture JSON files
- `${CLAUDE_SKILL_DIR}/mocks/generators/` - Dynamic response generators using Faker.js
- `${CLAUDE_SKILL_DIR}/mocks/scenarios/` - Error scenario configurations (4xx, 5xx responses)
- `${CLAUDE_SKILL_DIR}/mocks/state.js` - In-memory state store for CRUD behavior
- `${CLAUDE_SKILL_DIR}/mocks/recordings/` - Captured request logs for contract testing
- `${CLAUDE_SKILL_DIR}/docker-compose.mock.yml` - Docker configuration for mock server

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Schema mismatch | Mock response does not match updated OpenAPI spec | Run spec-to-fixture sync on spec change; add CI check comparing fixture schemas |
| Missing endpoint | Consumer requests path not defined in OpenAPI spec | Return 501 with message listing available endpoints; log unknown path for spec update |
| Stale fixtures | Mock data becomes unrealistic after API schema evolution | Regenerate fixtures from latest spec; use generators over static fixtures for evolving APIs |
| Port conflict | Mock server port already in use by another dev service | Make port configurable via environment variable; default to spec-defined server URL port |
| State leak between tests | Stateful mock retains data from previous test run | Reset in-memory state before each test suite; expose `POST /mock/reset` admin endpoint |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Frontend parallel development**: Launch a Prism mock server from the OpenAPI spec so frontend developers can build against realistic API responses while backend implementation is in progress.

**Integration test isolation**: Use MSW (Mock Service Worker) to intercept HTTP requests in Node.js test suites, returning fixture responses without network calls, with per-test response customization.

**Contract testing**: Record all requests to the mock server during frontend E2E tests, then replay them against the real backend to verify the mock accurately represents actual API behavior.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Prism (Stoplight): https://stoplight.io/open-source/prism
- Mock Service Worker (MSW): https://mswjs.io/
- WireMock: https://wiremock.org/
- Faker.js for realistic data generation: https://fakerjs.dev/
