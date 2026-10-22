---
name: validating-cors-policies
description: Validate CORS policies for security issues and misconfigurations. Use
  when reviewing cross-origin resource sharing. Trigger with 'validate CORS', 'check
  CORS policy', or 'review cross-origin'.
version: 1.24.0
allowed-tools: Read, WebFetch, WebSearch, Grep
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- validating-cors
compatibility: Designed for Claude Code
---
# Validating CORS Policies

## Overview

Validate Cross-Origin Resource Sharing configurations in web applications and
APIs for security misconfigurations that enable unauthorized cross-origin access.
This skill analyzes CORS headers, middleware configurations, and server response
behavior to detect wildcard origins, reflected origins, credential leakage, and
overly permissive header/method exposure.

## Prerequisites

- Access to the target codebase and configuration files in `${CLAUDE_SKILL_DIR}/`
- For live endpoint testing: WebFetch tool available and target URLs accessible
- Familiarity with the web framework in use (Express, Django, Flask, Spring, ASP.NET, etc.)
- Reference: `${CLAUDE_SKILL_DIR}/references/README.md` for CORS specification details, common vulnerability patterns, and example policies

## Instructions

1. Locate all CORS configuration points by scanning for `Access-Control-Allow-Origin`, `cors()` middleware, `@CrossOrigin` annotations, CORS policy builders, and server config directives (nginx `add_header`, Apache `Header set`) using Grep.
2. Check for wildcard origin (`Access-Control-Allow-Origin: *`) -- flag as severity high when combined with `Access-Control-Allow-Credentials: true`, which browsers reject but indicates a misunderstanding of the security model.
3. Detect origin reflection patterns where the server echoes back the `Origin` request header without validation -- search for code that reads the `Origin` header and sets it directly in the response. Flag as CWE-942 (Permissive Cross-domain Policy), severity critical.
4. Validate the origin allowlist: check that allowed origins use exact string matching rather than substring or regex patterns vulnerable to bypass (e.g., `example.com.evil.com` matching a check for `example.com`).
5. Assess `Access-Control-Allow-Methods` -- flag if dangerous methods (`PUT`, `DELETE`, `PATCH`) are exposed without necessity. Verify that preflight (`OPTIONS`) responses include appropriate method restrictions.
6. Evaluate `Access-Control-Allow-Headers` -- flag wildcard header allowance or exposure of sensitive headers like `Authorization`, `Cookie`, or custom auth headers to broader origins than necessary.
7. Check `Access-Control-Expose-Headers` for leakage of internal headers (e.g., `X-Request-Id`, `X-Internal-Trace`) to cross-origin consumers.
8. Verify `Access-Control-Max-Age` is set to a reasonable value (600-86400 seconds) to balance security with performance -- missing or excessively long max-age values deserve a low-severity note.
9. For live endpoints, issue preflight requests via WebFetch with various `Origin` values (legitimate, malicious, null) and analyze the response headers to confirm server behavior matches the codebase configuration.
10. Compile findings with severity ratings, map to OWASP Testing Guide OTG-CLIENT-007, and provide remediation with correct CORS middleware configuration examples.

## Output

- **CORS configuration inventory**: Table of all CORS-enabled endpoints, their allowed origins, methods, headers, and credentials settings
- **Findings report**: Each finding includes severity, affected endpoint/file, CWE reference (CWE-942, CWE-346), observed behavior, and remediation code
- **Preflight test results**: For live endpoints, a table of Origin values tested and the corresponding server responses
- **Remediation examples**: Framework-specific CORS configuration snippets (Express `cors()`, Django `django-cors-headers`, Spring `@CrossOrigin`, nginx headers)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No CORS configuration found | CORS handled at infrastructure layer (CDN, API gateway) | Check CDN/gateway configs (Cloudflare, AWS API Gateway, nginx) for CORS header injection |
| WebFetch blocked or timed out | Target endpoint unreachable or rate-limited | Verify URL accessibility; fall back to static codebase analysis of CORS middleware configuration |
| Inconsistent CORS behavior across endpoints | Multiple CORS configurations at different layers | Map each layer (application, reverse proxy, CDN) and document the effective policy per endpoint |
| Origin reflection false positive | Dynamic origin validation with a secure allowlist | Verify the allowlist logic uses exact matching; mark as informational if the implementation is secure |
| Preflight not triggering | Request classified as "simple request" by the browser | Note that simple GET/POST requests bypass preflight; test with custom headers to force preflight |

## Examples

### Express.js CORS Middleware Audit

Scan `${CLAUDE_SKILL_DIR}/src/app.js` and `${CLAUDE_SKILL_DIR}/src/middleware/` for `cors()`
configuration. Flag `origin: true` (reflects any origin) as CWE-942, severity
critical. Recommend replacing with an explicit allowlist:
`origin: ['https://app.example.com', 'https://admin.example.com']`.

### Nginx CORS Header Review

Grep `${CLAUDE_SKILL_DIR}/nginx/` for `add_header Access-Control-Allow-Origin`. Flag any
`$http_origin` variable usage that reflects the origin without validation. Verify
that `Access-Control-Allow-Credentials` is only set for origins in the allowlist
using an `if` block or `map` directive.

### API Gateway CORS Configuration

Review `${CLAUDE_SKILL_DIR}/infra/api-gateway.yaml` or equivalent IaC definitions for
CORS settings. Flag wildcard `*` in allowed origins when credentials are enabled.
Verify that `Access-Control-Allow-Methods` is scoped to only the HTTP methods
each endpoint actually supports.

## Resources

- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [OWASP Testing for CORS (OTG-CLIENT-007)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/07-Testing_Cross_Origin_Resource_Sharing)
- [CWE-942: Permissive Cross-domain Policy](https://cwe.mitre.org/data/definitions/942.html)
- [CWE-346: Origin Validation Error](https://cwe.mitre.org/data/definitions/346.html)
- [Fetch Standard: CORS Protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
