---
name: scanning-api-security
description: 'Detect API security vulnerabilities including injection, broken auth,
  and data exposure.

  Use when scanning APIs for security vulnerabilities.

  Trigger with phrases like "scan API security", "check for vulnerabilities", or "audit
  API security".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:security-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- security
- authentication
- audit
compatibility: Designed for Claude Code
---
# Scanning API Security

## Overview

Detect API security vulnerabilities by scanning endpoint implementations, authentication flows, and data handling against the OWASP API Security Top 10. Identify injection vectors, broken authentication, excessive data exposure, mass assignment, and missing rate limiting through static analysis of route handlers, middleware chains, and request validation logic.

## Prerequisites

- API source code with route definitions and controller/handler implementations accessible
- OpenAPI specification for cross-referencing documented vs. implemented security controls
- OWASP API Security Top 10 (2023) checklist familiarity
- Security scanning tools: OWASP ZAP, Burp Suite, or `nuclei` for dynamic testing
- Dependency vulnerability scanner: `npm audit`, `safety` (Python), or `govulncheck`

## Instructions

1. Scan all route definitions using Grep to build a complete inventory of endpoints, HTTP methods, and middleware chains applied to each route.
2. Audit authentication middleware to verify every mutation endpoint (POST, PUT, PATCH, DELETE) has auth enforcement and that no endpoints accidentally bypass auth through route ordering.
3. Check for Broken Object Level Authorization (BOLA) by verifying that resource access checks compare the authenticated user's ID/role against the requested resource ownership, not just valid authentication.
4. Identify excessive data exposure by comparing response serialization against API contracts -- flag endpoints returning full database records instead of explicit field whitelists.
5. Detect mass assignment vulnerabilities by checking whether request bodies are passed directly to ORM `create`/`update` calls without field-level allowlisting.
6. Verify input validation exists on all request parameters, query strings, headers, and body fields, checking for SQL injection, NoSQL injection, and command injection patterns.
7. Audit rate limiting configuration to ensure all public-facing and authentication endpoints have per-IP and per-user rate limits applied.
8. Check security headers (CORS, CSP, HSTS, X-Content-Type-Options) and verify CORS `Access-Control-Allow-Origin` is not set to wildcard `*` on authenticated endpoints.
9. Scan dependencies for known CVEs and generate a prioritized remediation report with severity ratings and fix recommendations.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/reports/security-scan.json` - Machine-readable vulnerability report with severity ratings
- `${CLAUDE_SKILL_DIR}/reports/security-scan.md` - Human-readable report with remediation guidance
- `${CLAUDE_SKILL_DIR}/reports/endpoint-auth-matrix.md` - Endpoint-to-auth-middleware mapping table
- `${CLAUDE_SKILL_DIR}/reports/data-exposure-audit.md` - Fields returned vs. fields documented per endpoint
- Inline code comments marking identified vulnerabilities with `// SECURITY:` annotations

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| False positive on auth bypass | Route uses custom auth decorator not recognized by scanner | Add custom auth patterns to scanner configuration; document non-standard auth middleware |
| BOLA not detected | Authorization check exists but uses flawed comparison logic | Manually review ownership checks; verify tenant isolation in multi-tenant queries |
| Injection false negative | Parameterized queries mask injection in string-built sub-queries | Scan for raw SQL concatenation patterns alongside ORM usage; check dynamic query builders |
| CORS misconfiguration missed | CORS configured at reverse proxy level, not in application code | Extend scan to include nginx/Apache config files and cloud provider CORS settings |
| Dependency scan timeout | Large dependency tree with many transitive dependencies | Run dependency scan in parallel; cache vulnerability database locally |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**OWASP Top 10 audit**: Scan a Node.js Express API against all 10 OWASP API Security categories, generating a compliance matrix showing pass/fail/warning status for each category with specific file:line references.

**Pre-deployment gate**: Integrate security scan into CI pipeline that blocks deployment if any Critical or High severity findings are detected, while allowing Medium/Low with documented exceptions.

**Authentication flow review**: Trace the complete auth flow from login through token issuance, refresh, and revocation, identifying token lifetime issues, missing refresh rotation, and insecure token storage patterns.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- OWASP API Security Top 10 (2023): https://owasp.org/API-Security/
- OWASP ZAP API Scan: https://www.zaproxy.org/
- CWE/SANS Top 25 Most Dangerous Software Weaknesses
- RFC 6749 OAuth 2.0 Authorization Framework
