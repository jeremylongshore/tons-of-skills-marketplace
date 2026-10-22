---
name: generating-api-contracts
description: 'Generate API contracts and OpenAPI specifications from code or design
  documents.

  Use when documenting API contracts and specifications.

  Trigger with phrases like "generate API contract", "create OpenAPI spec", or "document
  API contract".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:contract-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- api-contracts
compatibility: Designed for Claude Code
---
# Generating API Contracts

## Overview

Generate OpenAPI 3.0/3.1 specifications and consumer-driven contract tests from existing API implementations, design documents, or database schemas. Produce machine-readable contracts that serve as the single source of truth for code generation, documentation, testing, and gateway configuration, with Pact integration for consumer-driven contract verification.

## Prerequisites

- API implementation with route definitions and handler logic, or design requirements document
- OpenAPI authoring tool: Swagger Editor, Stoplight Studio, or IDE with OpenAPI extension
- Consumer-driven contract framework: Pact (polyglot), Spring Cloud Contract (Java), or Dredd (generic)
- Schema validation tool: Spectral for OpenAPI linting
- Version control for contract files with diff-based review process

## Instructions

1. Scan existing route handlers and controller files using Grep and Read to extract all endpoint paths, HTTP methods, request parameter names/types, and response body shapes.
2. Generate OpenAPI 3.0 specification from the extracted data, including `info` (title, version, description), `servers` (environment URLs), `paths` (operations), and `components` (reusable schemas).
3. Define request schemas with field-level constraints: `type`, `format`, `required`, `minimum/maximum`, `pattern` (regex), `enum`, and `example` values for every property.
4. Document all response status codes per endpoint with separate schemas: 200/201 for success, 400 for validation errors (with field-level error array), 401/403 for auth failures, and 404/500.
5. Add security scheme definitions (`bearerAuth`, `apiKey`, `oauth2`) and apply them to appropriate operations using the `security` field.
6. Create Pact consumer contract tests that capture expected interactions from the API consumer perspective, defining expected request/response pairs per endpoint.
7. Set up provider verification that replays Pact interactions against the actual API implementation, verifying the provider satisfies all consumer expectations.
8. Generate contract artifacts: OpenAPI spec file, Postman collection, and consumer contract (Pact JSON), all versioned alongside the API source code.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/openapi.yaml` - Complete OpenAPI 3.0/3.1 specification
- `${CLAUDE_SKILL_DIR}/contracts/pact/` - Consumer-driven contract definitions (Pact JSON)
- `${CLAUDE_SKILL_DIR}/contracts/postman/` - Generated Postman collection for API testing
- `${CLAUDE_SKILL_DIR}/tests/contract/consumer/` - Consumer contract test implementations
- `${CLAUDE_SKILL_DIR}/tests/contract/provider/` - Provider verification test suite
- `${CLAUDE_SKILL_DIR}/scripts/generate-contract.sh` - Contract generation automation script

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Spec-code divergence | API implementation changed without updating the OpenAPI spec | Add CI check that generates spec from code and diffs against committed spec |
| Pact verification failure | Provider response does not match consumer expectation | Review consumer contract for correctness; update provider if contract is valid |
| Missing operation ID | Endpoint has no `operationId`, preventing code generation | Generate deterministic operation IDs from method + path (e.g., `getUsers`, `createUser`) |
| Circular schema reference | Components reference each other creating infinite recursion | Break cycles with `allOf` composition or introduce intermediate types |
| Example/schema mismatch | Example values do not validate against their own schema | Auto-validate all examples during spec generation; reject mismatched examples |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Code-first OpenAPI generation**: Scan Express route decorators and Zod validation schemas to auto-generate a complete OpenAPI 3.1 spec with accurate request/response schemas, examples, and descriptions.

**Consumer-driven contract testing**: Frontend team publishes Pact contracts defining the API interactions they depend on; backend CI verifies every contract on each deployment, preventing breaking changes.

**Design-first workflow**: Author OpenAPI spec in Stoplight Studio, generate server stubs and client SDKs from the spec, then implement business logic in the stubs -- spec stays as the single source of truth.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- OpenAPI Specification 3.1: https://spec.openapis.org/oas/v3.1.0
- Pact contract testing: https://pact.io/
- Swagger Editor: https://editor.swagger.io/
- Dredd API contract testing: https://dredd.org/
