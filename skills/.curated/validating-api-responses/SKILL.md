---
name: validating-api-responses
description: 'Validate API responses against schemas to ensure contract compliance
  and data integrity.

  Use when ensuring API response correctness.

  Trigger with phrases like "validate responses", "check API responses", or "verify
  response format".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:validate-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- compliance
- validating-api
compatibility: Designed for Claude Code
---
# Validating API Responses

## Overview

Validate API responses against OpenAPI schemas, JSON Schema definitions, and contract specifications to detect data integrity violations, schema drift, and backward compatibility regressions. Run validation in middleware (development/staging) or as post-deployment contract tests to ensure every response conforms to the documented API contract.

## Prerequisites

- OpenAPI 3.0+ specification with complete response schema definitions for all endpoints
- JSON Schema validator: Ajv (Node.js), jsonschema (Python), or everit-org/json-schema (Java)
- Response validation middleware or test harness integrated into CI pipeline
- API test client for exercising endpoints and capturing response bodies
- Schema diff tool for detecting contract changes between versions

## Instructions

1. Read the OpenAPI specification using Read and extract all response schemas per endpoint, including success responses (200, 201), error responses (400, 404, 500), and header definitions.
2. Compile JSON Schema validators for each endpoint-status combination, enabling strict mode (`additionalProperties: false`) to detect undocumented fields leaking into responses.
3. Implement response validation middleware that intercepts outgoing responses and validates the body against the corresponding schema, logging violations without blocking responses in production.
4. Configure validation strictness per environment: `strict` (fail on violation) in development/staging, `warn` (log only) in production, with violation metrics emitted for monitoring.
5. Add header validation to verify required response headers (Content-Type, Cache-Control, rate limit headers) match the OpenAPI specification.
6. Build a contract test suite that sends representative requests to each endpoint and validates every response field, including nested objects, arrays, enums, nullable fields, and format constraints (date-time, email, URI).
7. Implement schema drift detection that compares the current response shape against the documented schema after each deployment, alerting when undocumented fields appear or documented fields disappear.
8. Generate a validation coverage report showing which endpoints and response codes have schema validation, identifying gaps in the specification.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/response-validator.js` - Response schema validation middleware
- `${CLAUDE_SKILL_DIR}/src/validators/` - Compiled JSON Schema validators per endpoint
- `${CLAUDE_SKILL_DIR}/tests/contract/` - Contract test suite validating all endpoint responses
- `${CLAUDE_SKILL_DIR}/reports/validation-coverage.md` - Schema coverage report per endpoint and status code
- `${CLAUDE_SKILL_DIR}/reports/schema-drift.json` - Detected undocumented response field changes
- `${CLAUDE_SKILL_DIR}/src/config/validation.js` - Per-environment validation strictness configuration

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Additional property detected | Response contains field not defined in schema | Add field to schema if intentional; remove from serializer if data leak; configure `additionalProperties` |
| Type mismatch | Field returns string instead of documented integer (or vice versa) | Fix serializer to match schema type; add type coercion test; check ORM field mapping |
| Required field missing | Response omits a field marked required in schema | Verify database query includes the field; check conditional serialization logic |
| Null value on non-nullable | Field returns null but schema does not include `nullable: true` | Update schema to allow null, or fix data source to guarantee non-null values |
| Format validation failure | Date field does not match RFC 3339 format or email field format invalid | Apply format serialization at the ORM/model level before response construction |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**CI contract gate**: On every pull request, run contract tests that validate all endpoint responses against the OpenAPI spec, failing the build if any response violates the documented schema.

**Production response sampling**: In production, validate 5% of responses against schemas (sampled randomly), emitting `response_validation_failure` metrics to detect schema drift caused by data changes.

**Backward compatibility check**: Compare v1 and v2 response schemas to verify that v2 is a superset of v1 (no removed fields, no type changes), ensuring existing consumers are not broken.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- JSON Schema Specification: https://json-schema.org/specification
- Ajv JSON Schema validator: https://ajv.js.org/
- OpenAPI response validation best practices
- Consumer-Driven Contract Testing with Pact: https://pact.io/
