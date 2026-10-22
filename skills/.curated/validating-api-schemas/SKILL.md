---
name: validating-api-schemas
description: 'Validate API schemas against OpenAPI, JSON Schema, and GraphQL specifications.

  Use when validating API schemas and contracts.

  Trigger with phrases like "validate API schema", "check OpenAPI spec", or "verify
  schema".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:schema-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- graphql
- validating-api
compatibility: Designed for Claude Code
---
# Validating API Schemas

## Overview

Validate API specifications against OpenAPI 3.0/3.1, JSON Schema Draft 2020-12, and GraphQL SDL standards using linting rules, structural analysis, and best-practice enforcement. Detect incomplete schemas, undocumented endpoints, inconsistent naming conventions, and breaking changes before they reach consumers.

## Prerequisites

- OpenAPI specification files (YAML or JSON) or GraphQL SDL schema files
- Schema linting tool: Spectral (OpenAPI), `graphql-schema-linter` (GraphQL), or `ajv-cli` (JSON Schema)
- Version control for schema files to enable diff-based breaking change detection
- CI pipeline for automated schema validation on every pull request
- `oasdiff` or `openapi-diff` for breaking change detection between versions

## Instructions

1. Locate all API specification files using Glob, identifying OpenAPI specs, JSON Schema definitions, and GraphQL SDL files across the project.
2. Run structural validation to verify the specification conforms to the declared standard (OpenAPI 3.0, 3.1, or JSON Schema Draft 2020-12) and is syntactically valid.
3. Apply Spectral linting rules to enforce naming conventions (camelCase properties, kebab-case paths), required descriptions on all operations, and example values for request/response schemas.
4. Verify schema completeness: every endpoint has documented request schemas, all response status codes have schemas (including 400, 401, 404, 500), and all `$ref` references resolve.
5. Check for security scheme coverage: every endpoint either declares a security requirement or is explicitly marked as public with rationale.
6. Detect breaking changes by comparing the current schema against the previous released version: removed endpoints, removed required fields, type changes, and narrowed enum values.
7. Validate consistency across endpoints: pagination parameters use the same naming (`page`/`limit` vs `offset`/`count`), error response envelopes follow a single standard, and date formats are consistent.
8. Generate a validation report with severity levels (error, warning, info) and specific file:line references for each finding.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/reports/schema-validation.json` - Machine-readable validation findings with severity
- `${CLAUDE_SKILL_DIR}/reports/schema-validation.md` - Human-readable report with fix recommendations
- `${CLAUDE_SKILL_DIR}/reports/breaking-changes.md` - Breaking change analysis between schema versions
- `${CLAUDE_SKILL_DIR}/.spectral.yaml` - Custom Spectral linting rule configuration
- `${CLAUDE_SKILL_DIR}/scripts/validate-schema.sh` - CI-ready schema validation script
- `${CLAUDE_SKILL_DIR}/reports/schema-coverage.md` - Endpoint documentation completeness matrix

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Unresolved $ref | Schema references a component that does not exist or has a typo | List all `$ref` targets and verify each resolves; check for circular references |
| Missing response schema | Endpoint returns undocumented status codes | Add schemas for all observed response codes; use `default` response as fallback |
| Inconsistent naming | Mix of camelCase and snake_case property names across endpoints | Define naming convention in Spectral ruleset; apply auto-fix where possible |
| Breaking change detected | Required field added to existing request schema | Make new field optional with default value; or create new API version for breaking changes |
| Schema too permissive | Use of `additionalProperties: true` or missing type constraints | Set `additionalProperties: false` by default; require explicit type and format on all properties |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Pre-commit schema lint**: Git pre-commit hook runs Spectral against all modified OpenAPI files, blocking commits that introduce undocumented endpoints, missing descriptions, or inconsistent naming.

**Breaking change CI gate**: On pull requests modifying API specs, `oasdiff` compares against the main branch version, failing the build if backward-incompatible changes are detected without a version bump.

**Schema completeness audit**: Generate a matrix showing every endpoint vs. documentation status (description, request schema, response schemas for 200/400/401/404/500, examples), highlighting gaps with coverage percentage.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Spectral OpenAPI linter: https://stoplight.io/open-source/spectral
- OpenAPI Specification: https://spec.openapis.org/oas/v3.1.0
- JSON Schema specification: https://json-schema.org/
- oasdiff breaking change detection: https://github.com/Tufin/oasdiff
