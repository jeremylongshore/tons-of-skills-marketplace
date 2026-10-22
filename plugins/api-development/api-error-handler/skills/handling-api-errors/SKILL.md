---
name: handling-api-errors
description: 'Implement standardized error handling with proper HTTP status codes
  and error responses.

  Use when implementing standardized error handling.

  Trigger with phrases like "add error handling", "standardize errors", or "implement
  error responses".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:error-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- handling-api
compatibility: Designed for Claude Code
---
# Handling API Errors

## Overview

Implement standardized API error handling with RFC 7807 Problem Details responses, centralized error middleware, typed error classes, and environment-aware stack trace exposure. Convert framework exceptions, validation failures, database errors, and upstream service failures into consistent, machine-readable error responses with appropriate HTTP status codes.

## Prerequisites

- Web framework with middleware/error handler support (Express, FastAPI, Spring Boot, Gin)
- Structured logging library for error event recording with correlation IDs
- Error monitoring service: Sentry, Bugsnag, or Rollbar for production error tracking
- RFC 7807 Problem Details specification for response format guidance
- API documentation listing all possible error codes and their meanings

## Instructions

1. Audit existing error handling using Grep to find `try/catch` blocks, error middleware, and exception handlers, identifying inconsistent error response formats across endpoints.
2. Define a standardized error response envelope following RFC 7807: `type` (URI identifying error type), `title` (human-readable summary), `status` (HTTP code), `detail` (specific explanation), and `instance` (request path).
3. Create typed error classes for each error category: `ValidationError` (400), `AuthenticationError` (401), `AuthorizationError` (403), `NotFoundError` (404), `ConflictError` (409), and `RateLimitError` (429).
4. Implement centralized error handling middleware that catches all thrown errors, maps them to the appropriate HTTP status code and RFC 7807 body, and prevents raw stack traces from leaking to clients.
5. Add validation error formatting that transforms framework-specific validation failures into a consistent array of field-level errors with `field`, `message`, and `code` properties.
6. Configure environment-aware error detail: include stack traces and internal error codes in development/staging responses; omit them in production while logging the full error server-side.
7. Integrate error monitoring (Sentry/Bugsnag) that captures 5xx errors with full context (request details, user info, stack trace) and groups them by root cause for triage.
8. Handle unhandled rejections and uncaught exceptions at the process level, returning 500 with a generic error message while logging the full failure and triggering alerts.
9. Write tests verifying that each error type produces the correct HTTP status code, RFC 7807 response body, and that stack traces are hidden in production mode.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/errors/` - Typed error classes (ValidationError, NotFoundError, etc.)
- `${CLAUDE_SKILL_DIR}/src/middleware/error-handler.js` - Centralized error handling middleware
- `${CLAUDE_SKILL_DIR}/src/errors/formatters.js` - Error-to-RFC-7807 response transformation
- `${CLAUDE_SKILL_DIR}/src/errors/codes.js` - Error code registry with human-readable descriptions
- `${CLAUDE_SKILL_DIR}/src/config/error-config.js` - Environment-aware error detail configuration
- `${CLAUDE_SKILL_DIR}/tests/errors/` - Error handling tests for each error type and scenario

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Stack trace leaked | Error handler omits production check; raw Error thrown without wrapping | Verify `NODE_ENV`/`APP_ENV` check in error formatter; wrap all thrown errors in typed classes |
| Inconsistent error format | Some endpoints return `{error: "msg"}` while others return RFC 7807 | Ensure all errors flow through centralized middleware; remove per-handler try/catch that formats differently |
| Unhandled promise rejection | Async handler throws without catch; Express does not catch async errors | Use `express-async-errors` wrapper or explicit async error forwarding with `next(err)` |
| Database error exposed | Raw SQL error message returned to client containing table/column names | Map database errors to generic messages at the error handler layer; log full details server-side |
| Error monitoring noise | High volume of expected 4xx errors flooding Sentry/Bugsnag | Configure error monitoring to capture only 5xx; track 4xx via metrics, not error monitoring |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**RFC 7807 response**: `{"type":"https://api.example.com/errors/validation","title":"Validation Error","status":400,"detail":"Request body contains 2 validation errors","errors":[{"field":"email","message":"Invalid email format","code":"INVALID_FORMAT"}]}`

**Centralized Express error handler**: Single `app.use((err, req, res, next) => {...})` middleware that handles all error types, sets status codes, formats RFC 7807 bodies, logs with correlation ID, and reports to Sentry.

**Graceful upstream failure**: When a downstream payment service returns 500, wrap it in a `ServiceUnavailableError` with a user-friendly message, log the upstream response for debugging, and trigger a circuit breaker.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- RFC 7807 Problem Details for HTTP APIs: https://tools.ietf.org/html/rfc7807
- Sentry error monitoring: https://sentry.io/
- Express error handling best practices
- HTTP status code decision tree for API responses
