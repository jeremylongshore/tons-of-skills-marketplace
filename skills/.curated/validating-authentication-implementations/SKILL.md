---
name: validating-authentication-implementations
description: Validate authentication mechanisms for security weaknesses and compliance.
  Use when reviewing login systems or auth flows. Trigger with 'validate authentication',
  'check auth security', or 'review login'.
version: 1.27.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- security
- authentication
- compliance
compatibility: Designed for Claude Code
---
# Validating Authentication Implementations

## Overview

Validate authentication mechanisms across web applications, APIs, and backend
services for security weaknesses, compliance gaps, and implementation flaws.
This skill examines password hashing, JWT token handling, session management,
OAuth flows, MFA implementation, and account security controls against OWASP
and NIST standards.

## Prerequisites

- Access to the target codebase and configuration files in `${CLAUDE_SKILL_DIR}/`
- Familiarity with the authentication framework in use (Passport.js, Spring Security, Django Auth, NextAuth, etc.)
- Standard shell utilities and Grep/Glob available for codebase scanning
- Reference: [`references/README.md`](references/README.md) for OWASP authentication cheat sheet, NIST password guidelines, and JWT RFC specifications

## Instructions

1. Identify all authentication entry points by scanning for login routes, token endpoints, session initialization, and OAuth callback handlers using Grep across route definitions and controller files.
2. Examine password storage by locating hashing function calls -- verify use of bcrypt, scrypt, or Argon2id with appropriate cost factors. Flag any use of MD5, SHA-1, SHA-256 without key stretching, or plaintext storage as CWE-916 (Use of Password Hash With Insufficient Computational Effort).
3. Validate JWT implementations: check signing algorithms (reject `none`, flag HS256 with weak secrets), verify `exp`, `iat`, `aud`, and `iss` claims are validated, confirm tokens are not stored in localStorage (XSS exposure), and check for proper refresh token rotation.
4. Assess session management: verify session IDs are regenerated after authentication, sessions have appropriate timeouts (idle and absolute), cookies use `HttpOnly`, `Secure`, and `SameSite=Strict` or `SameSite=Lax` attributes, and session fixation protections are in place.
5. Review OAuth/OIDC flows: confirm `state` parameter usage for CSRF protection, validate redirect URI whitelisting, check PKCE implementation for public clients, and verify token storage security.
6. Evaluate MFA implementation: confirm MFA is available for privileged accounts, check TOTP secret storage encryption, verify backup code generation uses cryptographically secure randomness, and flag any MFA bypass paths.
7. Check account security controls: verify rate limiting on login endpoints, account lockout policies after failed attempts, secure password reset flows (time-limited tokens, no user enumeration), and brute-force protections.
8. Validate credential transmission: confirm all auth endpoints enforce HTTPS, passwords are never logged or included in URLs, and API keys use secure header transmission rather than query parameters.
9. Classify each finding by severity and map to CWE identifiers and OWASP ASVS requirements.
10. Produce a remediation plan with specific code changes for each finding.

## Output

- **Authentication inventory**: List of all auth mechanisms, endpoints, and flows in the codebase
- **Findings report**: Each finding includes severity, CWE reference (e.g., CWE-287 Improper Authentication, CWE-384 Session Fixation, CWE-916 Weak Password Hash), affected file/line, and remediation steps
- **OWASP ASVS compliance matrix**: Pass/fail status for ASVS V2 (Authentication) and V3 (Session Management) requirements
- **Token security analysis**: JWT algorithm, claim validation status, storage mechanism, and expiration policy
- **Executive summary**: Risk rating, total findings by severity, and top priority fixes

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No authentication code found | Incorrect scan scope or unconventional auth patterns | Broaden Grep patterns; check for third-party auth services (Auth0, Firebase Auth, Cognito) configured externally |
| Cannot determine hashing algorithm | Hashing abstracted behind framework | Inspect framework configuration files (e.g., `config/auth.php`, `settings.py`) for algorithm settings |
| JWT library version unknown | Dynamic dependency resolution | Check lock files (`package-lock.json`, `poetry.lock`) for pinned versions and cross-reference known vulnerabilities |
| Session config not in codebase | Session management handled by infrastructure | Check reverse proxy configs (nginx, Apache), cloud session stores (Redis, DynamoDB), or PaaS settings |
| Rate limiting not detectable | Rate limiting at infrastructure layer | Note as "unverifiable from codebase" and recommend confirming at the infrastructure level |

## Examples

### JWT Implementation Review

Scan `${CLAUDE_SKILL_DIR}/src/auth/` and `${CLAUDE_SKILL_DIR}/src/middleware/` for JWT signing and
verification logic. Flag any use of `jwt.sign()` with `algorithm: 'none'` or
`HS256` paired with a secret shorter than 256 bits as CWE-327 (Use of Broken
Crypto Algorithm), severity critical. Verify that `jwt.verify()` validates
`exp`, `aud`, and `iss` claims.

### Password Storage Audit

Grep for `bcrypt`, `argon2`, `scrypt`, `hashSync`, `pbkdf2` across the
codebase. If password hashing uses `crypto.createHash('md5')` or
`hashlib.sha256()` without PBKDF2 wrapping, flag as CWE-916, severity critical.
Verify salt generation uses `crypto.randomBytes()` or equivalent CSPRNG.

### Session Cookie Hardening

Locate session configuration in `${CLAUDE_SKILL_DIR}/config/` or middleware setup files.
Verify cookie attributes include `httpOnly: true`, `secure: true`,
`sameSite: 'strict'`, and `maxAge` under 24 hours. Flag missing `httpOnly` as
CWE-1004 (Sensitive Cookie Without HttpOnly), severity high.

## Resources

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [NIST SP 800-63B: Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [RFC 7519: JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
