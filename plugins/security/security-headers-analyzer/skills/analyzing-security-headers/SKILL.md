---
name: analyzing-security-headers
description: 'Analyze HTTP security headers of web domains to identify vulnerabilities
  and misconfigurations.

  Use when you need to audit website security headers, assess header compliance, or
  get security recommendations for web applications.

  Trigger with phrases like "analyze security headers", "check HTTP headers", "audit
  website security headers", or "evaluate CSP and HSTS configuration".

  '
allowed-tools: Read, WebFetch, WebSearch, Grep
version: 1.29.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Analyzing Security Headers

## Overview

Evaluate HTTP response headers for web applications against OWASP Secure Headers Project recommendations and browser security baselines. Identify missing, misconfigured, or information-leaking headers across both HTTP and HTTPS responses.

## Prerequisites

- Target URL or domain name accessible over the network
- Authorization to perform HTTP requests against the target domain
- Network connectivity for both HTTP and HTTPS protocols
- Optional: write access to `${CLAUDE_SKILL_DIR}/security-reports/` for persisting results

## Instructions

1. Accept the target domain. If only a domain name is provided, default to `https://`. For batch analysis, accept a newline-separated list.
2. Fetch response headers using `WebFetch` for both HTTP and HTTPS endpoints. Record the full redirect chain and final destination URL.
3. Evaluate **critical headers** -- flag any that are missing or misconfigured:
   - `Strict-Transport-Security`: require `max-age>=31536000`, `includeSubDomains`, and preload eligibility
   - `Content-Security-Policy`: check for `unsafe-inline`, `unsafe-eval`, overly broad `default-src`, and missing `frame-ancestors`
   - `X-Frame-Options`: require `DENY` or `SAMEORIGIN`
   - `X-Content-Type-Options`: require `nosniff`
   - `Permissions-Policy`: verify camera, microphone, geolocation restrictions
4. Evaluate **important headers** -- report status and recommendations:
   - `Referrer-Policy`: recommend `strict-origin-when-cross-origin` or `no-referrer`
   - `Cross-Origin-Embedder-Policy` (COEP), `Cross-Origin-Opener-Policy` (COOP), `Cross-Origin-Resource-Policy` (CORP)
5. Check for **information disclosure** -- flag `Server`, `X-Powered-By`, `X-AspNet-Version`, and any header revealing technology stack or version numbers.
6. Inspect cookie attributes on `Set-Cookie` headers: verify `Secure`, `HttpOnly`, `SameSite=Lax|Strict`, and `__Host-`/`__Secure-` prefix usage.
7. Calculate a security grade: A+ (95-100), A (85-94), B (75-84), C (65-74), D (50-64), F (<50) based on weighted presence and correctness of each header.
8. Generate per-header remediation directives with configuration examples for Nginx, Apache, and Cloudflare.

See [`references/implementation.md`](references/implementation.md) for the five-phase implementation workflow.

## Output

- **Headers Analysis Report**: overall grade, per-header status (present/missing/misconfigured), and risk impact
- **Remediation Checklist**: prioritized fixes with server configuration snippets
- **Cookie Security Assessment**: attribute compliance for each `Set-Cookie` header
- **Comparison Table**: side-by-side HTTP vs. HTTPS header differences

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Failed to connect to domain | DNS resolution failure, firewall block, or domain down | Verify domain spelling and DNS records; test alternate protocols |
| SSL certificate verification failed | Expired, self-signed, or mismatched certificate | Note TLS issue in report; indicates HSTS not properly enforced |
| Too many redirects | Redirect loop between HTTP and HTTPS | Report the redirect chain and analyze headers at each hop |
| HTTP 429 Too Many Requests | Rate limiting by target server | Implement backoff; queue domain for delayed re-analysis |
| Headers differ between HTTP and HTTPS | Inconsistent server configuration | Report both sets; highlight critical differences and flag HSTS gap |

## Examples

- "Analyze security headers for `https://tonsofskills.com` and explain any CSP or HSTS issues."
- "Check headers for `example.com` on both HTTP and HTTPS and provide an Nginx remediation config."
- "Batch-analyze headers for five staging domains and rank them by security grade."

## Resources

- OWASP Secure Headers Project: https://owasp.org/www-project-secure-headers/
- MDN Security Headers Guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#security
- Security Headers Scanner: https://securityheaders.com/
- Content Security Policy Reference: https://content-security-policy.com/
- HSTS Preload Submission: https://hstspreload.org/
- [`references/errors.md`](references/errors.md) -- full error handling reference
- [`references/examples.md`](references/examples.md) -- additional usage examples
- https://intentsolutions.io
