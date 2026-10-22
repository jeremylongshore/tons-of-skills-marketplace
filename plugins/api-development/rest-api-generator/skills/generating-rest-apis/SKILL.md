---
name: generating-rest-apis
description: 'Generate complete REST API implementations from OpenAPI specifications
  or database schemas.

  Use when generating RESTful API implementations.

  Trigger with phrases like "generate REST API", "create RESTful API", or "build REST
  endpoints".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:rest-*)
version: 1.24.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- database
- rest-apis
compatibility: Designed for Claude Code
---
# Generating REST APIs

## Overview

Generate complete, production-ready REST API implementations from OpenAPI specifications, database schemas, or resource definitions. Scaffold CRUD endpoints with proper HTTP method semantics, content negotiation, pagination, filtering, and HATEOAS link generation across Express, FastAPI, Spring Boot, and Gin frameworks.

## Prerequisites

- Node.js 18+ with Express/Fastify, or Python 3.10+ with FastAPI/Flask, or Java 17+ with Spring Boot, or Go 1.21+ with Gin/Echo
- OpenAPI 3.0+ specification or database schema (SQL DDL, Prisma, Sequelize models)
- HTTP testing tool: curl, httpie, or Postman
- Database server (PostgreSQL, MySQL, MongoDB) accessible for ORM integration
- Package manager configured (npm, pip, Maven, or go modules)

## Instructions

1. Scan the project for existing OpenAPI specs, database models, or route definitions using Glob and Read to establish current API surface area.
2. Parse resource entities from the specification and generate model definitions with field types, validation constraints, and relationship mappings.
3. Create route files implementing all five standard REST operations per resource: `GET /resources` (list with pagination), `GET /resources/:id`, `POST /resources`, `PUT /resources/:id`, and `DELETE /resources/:id`.
4. Implement controller logic with input validation using JSON Schema or framework-native validators (Zod, Pydantic, Bean Validation).
5. Add query parameter support for filtering (`?status=active`), sorting (`?sort=-created_at`), field selection (`?fields=id,name`), and cursor-based or offset pagination.
6. Wire authentication middleware to protect mutation endpoints (POST, PUT, DELETE) while allowing read access per configuration.
7. Generate standardized error response envelopes with RFC 7807 Problem Details format for all 4xx/5xx responses.
8. Create integration tests covering happy paths, validation failures, 404s, and auth rejection for every endpoint.
9. Produce or update the OpenAPI 3.0 specification to match the generated implementation.

See [`references/implementation.md`](references/implementation.md) for the full step-by-step implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/routes/` - Express/Fastify route definitions with HTTP method handlers
- `${CLAUDE_SKILL_DIR}/src/controllers/` - Business logic separated from routing
- `${CLAUDE_SKILL_DIR}/src/models/` - ORM models with validation rules and relationships
- `${CLAUDE_SKILL_DIR}/src/middleware/auth.js` - JWT/API key authentication middleware
- `${CLAUDE_SKILL_DIR}/src/middleware/validate.js` - Request schema validation middleware
- `${CLAUDE_SKILL_DIR}/openapi.yaml` - Generated OpenAPI 3.0 specification
- `${CLAUDE_SKILL_DIR}/tests/` - Integration test suite per resource endpoint

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Request body fails schema validation | Return field-level validation errors with JSON pointer paths to invalid fields |
| 401 Unauthorized | Missing or malformed Authorization header | Respond with `WWW-Authenticate` header indicating expected auth scheme |
| 404 Not Found | Resource ID does not exist in data store | Return RFC 7807 body with resource type and requested ID for debugging |
| 409 Conflict | Unique constraint violation on create/update | Include conflicting field name and existing value hint in error response |
| 429 Too Many Requests | Client exceeds rate limit | Return `Retry-After` header with seconds until next allowed request window |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**E-commerce product API**: Generate CRUD endpoints for a Product resource with nested Category relationships, image upload handling, and inventory tracking fields with optimistic concurrency via ETags.

**Multi-tenant SaaS API**: Scaffold tenant-scoped endpoints where all queries automatically filter by `tenant_id` extracted from JWT claims, with tenant isolation enforced at the middleware layer.

**Public read API with admin writes**: Create a dual-access API where `GET` endpoints are publicly cacheable (Cache-Control headers) while `POST/PUT/DELETE` require admin-role JWT tokens.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- OpenAPI Specification 3.1: https://spec.openapis.org/oas/v3.1.0
- RFC 7807 Problem Details for HTTP APIs
- JSON:API Specification for standardized response formatting
- Express.js, FastAPI, Spring Boot, and Gin framework documentation
