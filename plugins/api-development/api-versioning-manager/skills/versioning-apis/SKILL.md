---
name: versioning-apis
description: 'Implement API versioning with backward compatibility, deprecation notices,
  and migration paths.

  Use when managing API versions and backward compatibility.

  Trigger with phrases like "version the API", "manage API versions", or "handle API
  versioning".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:version-*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- migration
- versioning-apis
compatibility: Designed for Claude Code
---
# Versioning APIs

## Overview

Implement API versioning strategies -- URL path (`/v1/`, `/v2/`), header-based (`Accept: application/vnd.api.v2+json`), or query parameter (`?version=2`) -- with backward compatibility layers, deprecation notices, and automated migration paths. Manage concurrent version support, sunset timelines, and breaking change detection across the API surface.

## Prerequisites

- Existing API codebase with route definitions and controller implementations
- Version control history for tracking breaking changes across releases
- OpenAPI specs for each supported API version (or ability to generate them)
- API gateway or reverse proxy capable of version-based routing (optional: Kong, AWS API Gateway)
- Consumer notification channel for deprecation announcements (changelog, email, response headers)

## Instructions

1. Audit existing endpoints using Grep and Read to identify current versioning approach (if any) and catalog all public-facing endpoints with their request/response contracts.
2. Select a versioning strategy based on API consumer patterns: URL path versioning for public APIs, header versioning for APIs needing clean URLs, or content negotiation for advanced use cases.
3. Create a version router that directs requests to the appropriate version handler set based on the extracted version identifier from URL, header, or query parameter.
4. Implement version-specific controller directories (`/v1/controllers/`, `/v2/controllers/`) with shared business logic extracted into version-independent service layers.
5. Build a compatibility layer that transforms v1 requests into v2 format and v2 responses back to v1 format, enabling older versions to run on the latest business logic.
6. Add deprecation headers to sunset versions: `Deprecation: true`, `Sunset: <date>`, and `Link: <migration-guide-url>; rel="sunset"` per the Sunset HTTP header RFC.
7. Create a breaking change detector that compares OpenAPI specs between versions and flags removed fields, changed types, new required parameters, and altered response structures.
8. Write version compatibility tests that send v1-formatted requests and verify correct responses, ensuring the compatibility layer preserves backward compatibility.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/routes/v1/` - Version 1 route definitions
- `${CLAUDE_SKILL_DIR}/src/routes/v2/` - Version 2 route definitions
- `${CLAUDE_SKILL_DIR}/src/middleware/version-router.js` - Version extraction and routing middleware
- `${CLAUDE_SKILL_DIR}/src/compatibility/` - Request/response transformation layers between versions
- `${CLAUDE_SKILL_DIR}/src/utils/breaking-change-detector.js` - OpenAPI diff tool for breaking changes
- `${CLAUDE_SKILL_DIR}/docs/migration-guide-v1-to-v2.md` - Consumer migration documentation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Unsupported Version | Client requests a version that does not exist | Return available versions list in error body; suggest closest valid version |
| 410 Gone | Client requests a sunset version past its end-of-life date | Return migration guide URL and recommended current version in error body |
| Compatibility layer failure | v1-to-v2 transform encounters a field with no mapping | Log unmapped fields; return partial response with warning header; alert API team |
| Version header ignored | Client sets version header but reverse proxy strips custom headers | Document required proxy configuration; add URL path fallback for header-based versioning |
| Breaking change undetected | Semantic change (same field name, different meaning) not caught by schema diff | Add contract tests with business-logic assertions beyond schema structure |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**URL path versioning**: Migrate from `/api/users` to `/api/v1/users` and `/api/v2/users` where v2 changes `name` (string) to `firstName`/`lastName` (object), with v1 compatibility layer that joins the fields.

**Header-based versioning**: Route requests using `Accept: application/vnd.myapi.v2+json` with a default version fallback for clients omitting the header, and version discovery via `OPTIONS` responses.

**Sunset lifecycle management**: Announce v1 deprecation with 6-month sunset timeline, add `Sunset` headers immediately, log v1 usage metrics to track migration progress, and auto-disable after sunset date.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- RFC 8594 The Sunset HTTP Header Field
- API Versioning strategies comparison (Stripe, GitHub, Twilio approaches)
- OpenAPI diff tools: oasdiff, openapi-diff
- Semantic Versioning 2.0.0: https://semver.org/
