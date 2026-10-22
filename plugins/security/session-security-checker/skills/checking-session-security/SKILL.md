---
name: checking-session-security
description: 'Analyze session management implementations to identify security vulnerabilities
  in web applications.

  Use when you need to audit session handling, check for session fixation risks, review
  session timeout configurations, or validate session ID generation security.

  Trigger with phrases like "check session security", "audit session management",
  "review session handling", or "session fixation vulnerability".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(code-scan:*), Bash(security-check:*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- security
- audit
- checking-session
compatibility: Designed for Claude Code
---
# Checking Session Security

## Overview

Audit session management implementations in web applications to identify vulnerabilities including session fixation (CWE-384), insufficient session expiration (CWE-613), and cleartext transmission of session tokens (CWE-319).

## Prerequisites

- Application source code accessible in `${CLAUDE_SKILL_DIR}/`
- Session management code locations identified (auth modules, middleware, session stores)
- Framework and language identified (Express.js, Django, Spring Boot, Rails, ASP.NET, etc.)
- Session configuration files available (`session.config.*`, `settings.py`, `application.yml`)
- Write permissions for reports in `${CLAUDE_SKILL_DIR}/security-reports/`

## Instructions

1. Locate session management code by searching for patterns: `**/auth/**`, `**/session/**`, `**/middleware/**`, and framework-specific files (`settings.py`, `application.yml`, `web.config`).
2. **Analyze session ID generation**: verify use of a cryptographically secure random generator with at least 128 bits of entropy. Flag predictable patterns such as `Date.now()`, `Math.random()`, sequential IDs, or timestamp-based tokens (CWE-330).
3. **Check session fixation protections**: confirm the session ID is regenerated after authentication (`req.session.regenerate()` in Express, `request.session.cycle_key()` in Django). Flag any login handler that sets `authenticated = true` without regenerating the session ID.
4. **Validate cookie security attributes**: verify `HttpOnly` (prevents XSS-based token theft), `Secure` (HTTPS-only transmission), `SameSite=Lax|Strict` (CSRF mitigation), and `__Host-`/`__Secure-` prefix usage. Flag any missing attribute.
5. **Review session expiration**: check idle timeout (recommend 15-30 min for sensitive apps), absolute timeout (recommend 4-8 hours), and sliding window configuration. Flag sessions without any expiration.
6. **Audit session invalidation**: verify logout handlers destroy server-side session state and clear client cookies. Confirm password reset and privilege escalation flows invalidate existing sessions.
7. **Inspect session storage**: flag in-memory stores in production (no persistence across restarts), unencrypted session data at rest, and missing integrity checks on session payloads (e.g., unsigned JWT session tokens).
8. **Identify attack vectors**: assess exposure to session fixation, CSRF via session riding, replay attacks from stolen tokens, and session prediction from weak ID generation.
9. Produce the session security report at `${CLAUDE_SKILL_DIR}/security-reports/session-security-YYYYMMDD.md` with per-finding severity, CWE mapping, vulnerable code snippet, and remediated code example.

See [`references/implementation.md`](references/implementation.md) for the detailed implementation guide. See [`references/critical-findings.md`](references/critical-findings.md) for example vulnerability patterns with before/after code.

## Output

- **Session Security Report**: `${CLAUDE_SKILL_DIR}/security-reports/session-security-YYYYMMDD.md` with findings by severity
- **Cookie Attribute Matrix**: per-cookie compliance table (HttpOnly, Secure, SameSite, prefix)
- **Vulnerable Code Listings**: each finding with file path, line number, vulnerable snippet, and fix
- **Framework-Specific Remediation**: configuration changes tailored to the detected framework

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No session handling code found in `${CLAUDE_SKILL_DIR}/` | Unusual file structure or framework | Search for framework-specific patterns; request explicit file paths |
| Unknown session framework | Custom or uncommon session library | Apply fundamental session security principles; note limited framework-specific guidance |
| Cannot analyze minified/compiled code | Production bundles instead of source | Request unminified source code; document limitation |
| Non-standard session implementation | Custom session management bypassing framework | Apply extra scrutiny; custom implementations are higher risk (CWE-384, CWE-613) |
| Session config in environment variables, not code | Externalized configuration | Request `.env.example` or deployment config documentation |

## Examples

- "Audit session cookie flags and rotation logic for fixation and CSRF risks in the Express.js application."
- "Review logout and password reset flows to confirm sessions are invalidated correctly and old tokens cannot be replayed."
- "Check session ID generation entropy and storage backend security for the Django application."

## Resources

- OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- CWE-384 Session Fixation: https://cwe.mitre.org/data/definitions/384.html
- CWE-613 Insufficient Session Expiration: https://cwe.mitre.org/data/definitions/613.html
- CWE-319 Cleartext Transmission: https://cwe.mitre.org/data/definitions/319.html
- NIST 800-63B Digital Authentication: https://pages.nist.gov/800-63-3/sp800-63b.html
- [`references/critical-findings.md`](references/critical-findings.md) -- example vulnerability patterns
- [`references/errors.md`](references/errors.md) -- full error handling reference
- https://intentsolutions.io
