---
name: validating-csrf-protection
description: Validate CSRF protection implementations for security gaps. Use when
  reviewing form security or state-changing operations. Trigger with 'validate CSRF',
  'check CSRF protection', or 'review token security'.
version: 1.27.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- validating-csrf
compatibility: Designed for Claude Code
---
# Validating CSRF Protection

## Overview

Validate Cross-Site Request Forgery protection across web application endpoints,
forms, and API routes. This skill examines synchronizer token patterns,
double-submit cookie implementations, SameSite cookie attributes, Origin/Referer
header validation, and custom header requirements to identify state-changing
operations vulnerable to CSRF attacks.

## Prerequisites

- Access to the target codebase and configuration files in `${CLAUDE_SKILL_DIR}/`
- Familiarity with the web framework in use (Express, Django, Rails, Spring, Laravel, etc.)
- Standard shell utilities and Grep/Glob available for codebase scanning
- Reference: [`references/README.md`](references/README.md) for CSRF protection methods, OWASP CSRF Prevention Cheat Sheet, and framework-specific API examples

## Instructions

1. Inventory all state-changing endpoints by scanning for POST, PUT, PATCH, and DELETE route handlers using Grep. Include form action attributes in HTML templates, AJAX calls in JavaScript, and API route definitions.
2. For each state-changing endpoint, verify that at least one CSRF protection mechanism is in place: synchronizer token, double-submit cookie, SameSite cookie attribute, Origin validation, or custom header requirement.
3. Validate synchronizer token implementation: confirm tokens are generated server-side using a CSPRNG, bound to the user session, included in forms as hidden fields or request headers, and validated on every state-changing request. Flag tokens that are static, predictable, or reused across sessions as CWE-352 (Cross-Site Request Forgery).
4. Check double-submit cookie patterns: verify the cookie value matches the request body or header value, the cookie uses `Secure` and `HttpOnly` attributes, and the comparison is timing-safe to prevent token extraction.
5. Assess SameSite cookie attributes on session cookies: verify `SameSite=Strict` or `SameSite=Lax` is set. Flag `SameSite=None` without `Secure` as severity high. Note that `SameSite=Lax` permits top-level GET navigations, which may be insufficient for GET endpoints that trigger state changes.
6. Verify Origin/Referer header validation: check that the server validates the `Origin` header against an allowlist on state-changing requests. Flag implementations that fall back to no protection when the header is absent.
7. For API endpoints using token-based auth (JWT in Authorization header), confirm that cookies are not also sent -- if cookies are used alongside bearer tokens, CSRF protection remains necessary.
8. Check for CSRF bypass vectors: look for state-changing GET endpoints, JSONP endpoints, content-type sniffing (missing `Content-Type` enforcement), and Flash/Silverlight crossdomain.xml files.
9. Classify each finding by severity (critical for unprotected financial/admin endpoints, high for other state-changing endpoints, medium for defense-in-depth gaps).
10. Generate remediation guidance with framework-specific CSRF middleware configuration examples.

## Output

- **Endpoint inventory**: Table of all state-changing endpoints with their CSRF protection status (Protected, Partially Protected, Unprotected)
- **Findings report**: Each finding includes severity, CWE-352 reference, affected endpoint/file, attack scenario description, and remediation code
- **Protection coverage**: Percentage of state-changing endpoints with validated CSRF protection
- **SameSite cookie audit**: Table of all session/auth cookies with their SameSite, Secure, HttpOnly, and Path attributes
- **Remediation guide**: Framework-specific middleware setup (e.g., `csurf` for Express, `@csrf_protect` for Django, `csrf_meta_tags` for Rails)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No state-changing endpoints found | Unconventional routing patterns or SPA architecture | Check for client-side routing frameworks (React Router, Vue Router) and trace API calls from frontend code |
| CSRF middleware detected but not applied globally | Middleware applied per-route rather than globally | Verify every state-changing route has the middleware applied; flag gaps in coverage |
| Token generation source unclear | Framework abstracts CSRF token generation | Check framework documentation for default CSPRNG usage; inspect framework source if needed |
| SameSite attribute not set in code | Cookie attributes set at infrastructure layer | Check reverse proxy, load balancer, or CDN cookie rewriting rules |
| Mixed protection strategies | Different endpoints use different CSRF mechanisms | Document each strategy and verify consistency; recommend standardizing on one approach |

## Examples

### Express.js CSRF Token Validation

Scan `${CLAUDE_SKILL_DIR}/src/routes/` for `router.post` and `router.put` handlers. Verify
each includes `csurf` middleware or equivalent token validation. Flag any POST
handler that directly processes `req.body` without `csrfProtection` middleware
as CWE-352, severity critical for financial operations, high for other state changes.

### Django CSRF Middleware Audit

Grep `${CLAUDE_SKILL_DIR}/settings.py` for `django.middleware.csrf.CsrfViewMiddleware` in
the `MIDDLEWARE` list. Scan views for `@csrf_exempt` decorators -- flag each
exempted view as a potential CSRF vulnerability requiring justification. Verify
templates include `{% csrf_token %}` in all form tags.

### SPA + API CSRF Assessment

For a React frontend calling a REST API, verify that the API enforces a custom
header requirement (e.g., `X-Requested-With`) or uses double-submit cookies.
Check that the SPA reads the CSRF token from a cookie and includes it in the
`X-CSRF-Token` header. Flag API endpoints that accept `application/x-www-form-urlencoded`
without CSRF validation as severity high (exploitable via HTML forms).

## Resources

- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [CWE-352: Cross-Site Request Forgery](https://cwe.mitre.org/data/definitions/352.html)
- [SameSite Cookies Explained](https://web.dev/samesite-cookies-explained/)
- [OWASP Testing for CSRF (OTG-SESS-005)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery)
- [Synchronizer Token Pattern](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#synchronizer-token-pattern)
