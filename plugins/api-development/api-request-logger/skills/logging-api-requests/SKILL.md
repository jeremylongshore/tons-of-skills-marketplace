---
name: logging-api-requests
description: 'Monitor and log API requests with correlation IDs, performance metrics,
  and security audit trails.

  Use when auditing API requests and responses.

  Trigger with phrases like "log API requests", "add API logging", or "track API calls".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:log-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- security
- monitoring
- performance
compatibility: Designed for Claude Code
---
# Logging API Requests

## Overview

Implement structured API request logging with correlation IDs, performance timing, security audit trails, and PII redaction. Capture request/response metadata in JSON format suitable for aggregation in ELK Stack, Loki, or CloudWatch Logs, enabling debugging, performance analysis, and compliance auditing across distributed services.

## Prerequisites

- Structured logging library: Pino or Winston (Node.js), structlog (Python), Logback with JSON encoder (Java)
- Log aggregation system: ELK Stack (Elasticsearch, Logstash, Kibana), Grafana Loki, or CloudWatch Logs
- Correlation ID propagation mechanism (middleware-injected or from incoming `X-Request-ID` header)
- PII data classification for the API domain (which fields contain personal data requiring redaction)
- Log retention and rotation policy defined per compliance requirements

## Instructions

1. Examine existing logging configuration using Grep and Read to identify current log format, output destinations, and any structured logging already in place.
2. Implement request logging middleware that captures: timestamp (ISO 8601), correlation ID, HTTP method, URL path (without query string PII), status code, response time (ms), request size, response size, and client IP.
3. Generate a unique correlation ID (`X-Request-ID`) for each request if not provided by the caller, and propagate it to all downstream service calls and log entries within the request scope.
4. Add PII redaction rules that mask sensitive fields (passwords, tokens, SSNs, email addresses) in logged request/response bodies using configurable field-path patterns.
5. Implement log levels per context: `info` for successful requests, `warn` for 4xx client errors, `error` for 5xx server errors with stack traces, and `debug` for request/response bodies (development only).
6. Configure response body logging for error responses only (4xx/5xx), capturing the error payload for debugging while skipping successful response bodies to reduce log volume.
7. Add security audit logging for sensitive operations: authentication attempts, permission changes, data exports, and admin actions, tagged with `audit: true` for separate indexing.
8. Set up log rotation and retention policies: 30 days for application logs, 90 days for audit logs, with automatic compression of logs older than 7 days.
9. Write tests verifying that PII redaction works correctly, correlation IDs propagate through nested calls, and log output matches expected JSON structure.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/middleware/request-logger.js` - Structured request/response logging middleware
- `${CLAUDE_SKILL_DIR}/src/middleware/correlation-id.js` - Correlation ID generation and propagation
- `${CLAUDE_SKILL_DIR}/src/utils/pii-redactor.js` - Field-level PII redaction with configurable patterns
- `${CLAUDE_SKILL_DIR}/src/utils/audit-logger.js` - Security audit event logger for sensitive operations
- `${CLAUDE_SKILL_DIR}/src/config/logging.js` - Log level, format, and output destination configuration
- `${CLAUDE_SKILL_DIR}/tests/logging/` - Logging middleware tests including PII redaction verification

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Log volume overwhelming storage | High-traffic endpoint logging full request/response bodies | Log bodies only for errors; sample successful request bodies at configurable rate (1%) |
| PII leak in logs | New field added to API response containing personal data not covered by redaction rules | Maintain allowlist of loggable fields rather than blocklist; audit log output regularly |
| Correlation ID missing | Upstream service does not propagate X-Request-ID header | Generate new correlation ID when header is absent; log warning about missing upstream propagation |
| Log parsing failure | Log message contains unescaped characters breaking JSON structure | Use structured logging library that handles serialization; never concatenate user input into log strings |
| Audit log gap | Async logging dropped events during high-load period | Use synchronous logging for audit events; implement write-ahead buffer for audit trail completeness |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Structured JSON log entry**: `{"timestamp":"2026-03-10T14:30:00Z","correlationId":"abc-123","method":"POST","path":"/api/users","status":201,"durationMs":45,"userId":"usr_456","audit":false}` -- every field queryable in log aggregation.

**Distributed tracing correlation**: Propagate `X-Request-ID` from API gateway through 3 microservices, enabling a single Kibana query to show the complete request lifecycle across all services.

**Compliance audit trail**: Tag all data modification operations (POST, PUT, DELETE) with `audit: true`, capturing the authenticated user, modified resource ID, and change summary for SOC 2 compliance evidence.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Structured logging best practices (12-Factor App: Logs)
- ELK Stack documentation: https://www.elastic.co/guide/
- Pino logger: https://getpino.io/
- OpenTelemetry for distributed tracing context propagation
