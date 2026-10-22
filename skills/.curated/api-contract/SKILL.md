---
name: api-contract
description: 'Configure this skill should be used when the user asks about "API contract",
  "api-contract.md", "shared interface", "TypeScript interfaces", "request response
  schemas", "endpoint design", or needs guidance on designing contracts that coordinate
  backend and frontend agents. Use when building or modifying API endpoints. Trigger
  with phrases like ''create API'', ''design endpoint'', or ''API scaffold''.

  '
allowed-tools: Read
version: 1.21.0
author: Damien Laine <damien.laine@gmail.com>
license: MIT
tags:
- community
- api
- typescript
compatibility: Designed for Claude Code
---
# API Contract

## Overview

API Contract guides the creation of `api-contract.md` files that serve as the shared interface between backend and frontend agents during sprint execution. The contract defines request/response schemas, endpoint routes, TypeScript interfaces, and error formats so that implementation agents build to an agreed specification without direct coordination.

## Prerequisites

- Sprint directory initialized at `.claude/sprint/[N]/`
- `specs.md` with defined feature scope and endpoint requirements
- Familiarity with RESTful API conventions (HTTP methods, status codes, JSON schemas)
- TypeScript knowledge for interface definitions (recommended)

## Instructions

1. Create `api-contract.md` in the sprint directory (`.claude/sprint/[N]/api-contract.md`). Define each endpoint using the standard format: HTTP method, route path, description, request body, response body with status code, and error codes. See `${CLAUDE_SKILL_DIR}/references/writing-endpoints.md` for the full template.
2. Define TypeScript interfaces for all request and response types. Use explicit types instead of `any`, mark optional fields with `?`, and use `string | null` for nullable values. Reference `${CLAUDE_SKILL_DIR}/references/typescript-interfaces.md` for canonical type patterns.
3. For list endpoints, include pagination parameters and the `PaginatedResponse<T>` wrapper. Standardize on `page`, `limit`, `sort`, and `order` query parameters as documented in `${CLAUDE_SKILL_DIR}/references/pagination.md`.
4. Document all response states: success (200, 201, 204), client errors (400, 401, 403, 404, 422), and empty states. Use a consistent error response format with `code`, `message`, and optional `details` fields.
5. Follow best practices from `${CLAUDE_SKILL_DIR}/references/best-practices.md`: be specific about field constraints (e.g., "string, required, valid email format"), include request/response examples, reference shared types instead of duplicating, and omit implementation details (no database columns, framework names, or file paths).
6. Share the contract file path in SPAWN REQUEST blocks so both backend and frontend agents read the same interface definition.

## Output

- `api-contract.md` containing all endpoint definitions with typed request/response schemas
- TypeScript interface declarations for `User`, `CreateUserRequest`, `LoginRequest`, `AuthResponse`, `ApiError`, and domain-specific types
- Paginated response wrappers for list endpoints
- Standardized error format across all endpoints

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Backend and frontend schemas diverge | Contract updated without notifying both agents | Always reference a single `api-contract.md`; never duplicate endpoint definitions |
| Missing error response codes | Contract only documents the happy path | Document all status codes: 400, 401, 403, 404, 409, 422 per endpoint |
| Ambiguous field types | Using `string` without constraints | Specify format, length, and validation rules (e.g., "string, required, min 8 chars") |
| Pagination inconsistency | List endpoints use different parameter names | Standardize on the `PaginatedResponse<T>` interface for all list endpoints |
| Type mismatch between JSON and TypeScript | Dates serialized inconsistently | Use ISO 8601 datetime strings; document as `"createdAt": "ISO 8601 datetime"` |

## Examples

**Authentication endpoint contract:**

```markdown
#### POST /auth/register

Create a new user account.

**Request:**
{
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "name": "string (optional)"
}

**Response (201):**  # HTTP 201 Created
{
  "id": "uuid",
  "email": "string",
  "name": "string | null",
  "createdAt": "ISO 8601 datetime"  # 8601 = configured value
}

**Errors:**
- 400: Invalid request body  # HTTP 400 Bad Request
- 409: Email already exists  # HTTP 409 Conflict
- 422: Validation failed  # HTTP 422 Unprocessable Entity
```

**Paginated list endpoint:**

```markdown
#### GET /products

List products with pagination.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page (max 100) |
| sort | string | createdAt | Sort field |
| order | string | desc | Sort order (asc/desc) |

**Response (200):**  # HTTP 200 OK
{
  "data": [Product],
  "pagination": { "page": 1, "limit": 20, "total": 150, "totalPages": 8 }
}
```

**Shared TypeScript interface:**

```typescript
interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}
```

## Resources

- `${CLAUDE_SKILL_DIR}/references/writing-endpoints.md` -- Endpoint definition template and key elements
- `${CLAUDE_SKILL_DIR}/references/typescript-interfaces.md` -- Canonical type definitions and guidelines
- `${CLAUDE_SKILL_DIR}/references/pagination.md` -- Pagination parameters and PaginatedResponse interface
- `${CLAUDE_SKILL_DIR}/references/best-practices.md` -- Contract authoring rules (specificity, DRY, no implementation details)
