---
name: building-api-authentication
description: 'Build secure API authentication systems with OAuth2, JWT, API keys,
  and session management.

  Use when implementing secure authentication flows.

  Trigger with phrases like "build authentication", "add API auth", or "secure the
  API".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:auth-*)
version: 1.24.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- authentication
- api-authentication
compatibility: Designed for Claude Code
---
# Building API Authentication

## Overview

Build secure API authentication systems supporting JWT Bearer tokens, OAuth 2.0 authorization code and client credentials flows, API key management, and session-based authentication. Implement token issuance, validation, refresh rotation, revocation, and role-based access control (RBAC) with scoped permissions across all API endpoints.

## Prerequisites

- Cryptographic library: `jsonwebtoken` (Node.js), `PyJWT` (Python), or `jjwt` (Java)
- Secure secret storage: environment variables, AWS Secrets Manager, or HashiCorp Vault for JWT signing keys
- Database table for user credentials, refresh tokens, and API key storage
- Bcrypt or Argon2 for password hashing (never store plaintext passwords)
- OAuth 2.0 provider credentials for third-party auth integration (Google, GitHub, Auth0)

## Instructions

1. Examine existing authentication setup using Grep and Read, identifying current auth mechanisms, middleware placement, and any endpoints bypassing authentication.
2. Implement JWT token issuance on successful login: sign with RS256 (asymmetric) or HS256 (symmetric), including `sub` (user ID), `iat`, `exp` (15-minute access token), `roles`, and `scopes` in the payload.
3. Create authentication middleware that extracts the Bearer token from the `Authorization` header, verifies the signature and expiration, and injects the decoded user context into the request object.
4. Implement refresh token rotation: issue a long-lived refresh token (30 days) alongside the access token, store a hash of the refresh token in the database, and rotate on each refresh (invalidating the previous token).
5. Build role-based access control (RBAC) middleware that checks `user.roles` against endpoint-required roles, supporting both role-level (`admin`, `user`) and scope-level (`read:users`, `write:orders`) authorization.
6. Add API key authentication as an alternative to JWT for machine-to-machine communication: generate cryptographically random keys, store hashed values, and validate against the `X-API-Key` header.
7. Implement OAuth 2.0 client credentials flow for service-to-service authentication, with token caching and automatic renewal before expiration.
8. Add brute-force protection on login endpoints: rate limit to 5 attempts per minute per IP, implement progressive lockout (15 min, 1 hour) after repeated failures, and log all authentication attempts.
9. Write security tests covering: valid/invalid/expired tokens, refresh token rotation, role enforcement, API key validation, brute-force lockout, and token revocation.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/auth/jwt.js` - JWT token issuance, verification, and refresh logic
- `${CLAUDE_SKILL_DIR}/src/auth/middleware.js` - Bearer token authentication middleware
- `${CLAUDE_SKILL_DIR}/src/auth/rbac.js` - Role-based and scope-based access control middleware
- `${CLAUDE_SKILL_DIR}/src/auth/api-keys.js` - API key generation, hashing, and validation
- `${CLAUDE_SKILL_DIR}/src/auth/oauth.js` - OAuth 2.0 flow implementations
- `${CLAUDE_SKILL_DIR}/src/routes/auth.js` - Login, register, refresh, and logout endpoints
- `${CLAUDE_SKILL_DIR}/tests/auth/` - Authentication and authorization security tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Token Expired | JWT `exp` claim is in the past | Client should attempt token refresh; if refresh fails, redirect to login |
| 401 Invalid Signature | JWT signed with different key or tampered payload | Verify signing key matches between issuance and validation; check for key rotation issues |
| 403 Insufficient Scope | Authenticated user lacks required role/scope for endpoint | Return required scope in error body; log authorization failure with user and endpoint details |
| Refresh token reuse | Previously rotated refresh token used (possible token theft) | Invalidate all user sessions immediately; alert user of potential compromise; require re-authentication |
| API key leaked | API key exposed in client-side code, logs, or version control | Revoke compromised key immediately; issue replacement; scan for exposure source |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**JWT with refresh rotation**: Login returns `{accessToken (15min), refreshToken (30d)}`; client stores refresh token securely; on 401, client calls `POST /auth/refresh` with old refresh token, receives new pair, old refresh token is invalidated.

**Multi-provider OAuth**: Support "Sign in with Google" and "Sign in with GitHub" using OAuth 2.0 authorization code flow, creating local user accounts on first sign-in and linking subsequent provider connections.

**API key with scoped permissions**: Generate API keys with specific scopes (`read:analytics`, `write:webhooks`), stored as SHA-256 hashes, displayed to the user only once at creation, with key rotation support.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- RFC 7519 JSON Web Token (JWT): https://tools.ietf.org/html/rfc7519
- RFC 6749 OAuth 2.0 Authorization Framework
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/
- Auth0 architecture patterns: https://auth0.com/docs/
