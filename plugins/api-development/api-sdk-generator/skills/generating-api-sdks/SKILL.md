---
name: generating-api-sdks
description: 'Generate client SDKs in multiple languages from OpenAPI specifications.

  Use when generating client libraries for API consumption.

  Trigger with phrases like "generate SDK", "create client library", or "build API
  SDK".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:sdk-*)
version: 1.23.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- api-sdks
compatibility: Designed for Claude Code
---
# Generating API SDKs

## Overview

Generate type-safe client SDKs in multiple languages (TypeScript, Python, Go, Java) from OpenAPI 3.0+ specifications. Produce idiomatic client libraries with authentication handling, automatic retries, pagination helpers, and comprehensive type definitions that mirror the API contract.

## Prerequisites

- OpenAPI 3.0+ specification file (YAML or JSON) with complete schema definitions
- Target language toolchain installed (Node.js/TypeScript, Python 3.10+, Go 1.21+, or Java 17+)
- OpenAPI Generator CLI or equivalent code generation tool
- Package registry credentials for publishing (npm, PyPI, Maven Central, pkg.go.dev)
- CI pipeline for automated SDK builds on spec changes

## Instructions

1. Read and validate the OpenAPI specification using Read, checking for complete schema definitions, proper `$ref` usage, and response type coverage across all endpoints.
2. Extract all operation IDs, request/response models, and authentication schemes from the specification to build the SDK method inventory.
3. Generate typed model classes for every schema component, including nested objects, enums, and discriminated unions with proper nullability annotations.
4. Create a client class with methods for each API operation, mapping operation IDs to idiomatic method names (e.g., `listUsers`, `get_user`, `CreateUser`).
5. Implement authentication handling with support for Bearer tokens, API keys (header and query), and OAuth2 client credentials flow, configurable at client instantiation.
6. Add automatic retry logic with exponential backoff for 429 and 5xx responses, with configurable max retries and backoff multiplier.
7. Build pagination helpers that abstract cursor-based and offset pagination into iterator/generator patterns native to each target language.
8. Generate comprehensive JSDoc/docstring/Javadoc comments from OpenAPI `description` and `summary` fields for full IDE IntelliSense support.
9. Create a test suite that validates SDK methods against a mock server running the OpenAPI spec, covering authentication, error handling, and pagination.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/sdk/typescript/src/client.ts` - Main SDK client class with typed methods
- `${CLAUDE_SKILL_DIR}/sdk/typescript/src/models/` - TypeScript interfaces and type definitions
- `${CLAUDE_SKILL_DIR}/sdk/python/client.py` - Python SDK with dataclass models and async support
- `${CLAUDE_SKILL_DIR}/sdk/go/client.go` - Go SDK with struct types and context-based methods
- `${CLAUDE_SKILL_DIR}/sdk/*/README.md` - Per-language installation and usage documentation
- `${CLAUDE_SKILL_DIR}/sdk/*/tests/` - SDK test suites per language

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Schema generation failure | OpenAPI spec contains `$ref` cycles or missing component definitions | Run spec linting with `spectral` first; resolve circular references with `allOf` composition |
| Type mismatch | API response does not match generated model types at runtime | Add runtime response validation option; log schema drift warnings for API provider notification |
| Auth configuration error | SDK instantiated without required credentials for protected endpoints | Throw descriptive error at client construction time listing required auth parameters |
| Pagination exhaustion | Iterator consumes all pages without termination condition | Enforce maximum page count safety limit; detect empty result sets as termination signal |
| Rate limit handling | SDK retry logic conflicts with application-level retry logic | Expose `retryConfig` option to disable built-in retries; emit retry events for observability |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**TypeScript SDK for payment API**: Generate a fully typed `PaymentsClient` with methods like `createCharge(amount, currency)` returning `Promise<Charge>`, automatic Bearer token injection, and paginated `listTransactions()` returning an async iterator.

**Python SDK with async support**: Produce both sync (`PaymentsClient`) and async (`AsyncPaymentsClient`) clients using `httpx`, with Pydantic models for request/response validation and `__aiter__` pagination support.

**Multi-language CI pipeline**: On OpenAPI spec change, automatically regenerate SDKs in all target languages, run tests against a mock server, bump semantic versions, and publish to respective package registries.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- OpenAPI Generator: https://openapi-generator.tech/
- Speakeasy SDK generation: https://speakeasy.com/
- Microsoft Kiota for API client generation
- OpenAPI Specification 3.1: https://spec.openapis.org/oas/v3.1.0
