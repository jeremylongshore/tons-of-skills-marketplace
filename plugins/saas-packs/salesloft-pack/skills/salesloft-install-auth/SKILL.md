---
name: salesloft-install-auth
description: >-
  Select and implement the correct Salesloft authentication flow with least-privilege scopes and safe token rotation. Use when onboarding a customer, partner, or private server integration. Trigger with "Salesloft auth", "Salesloft OAuth", or "Salesloft API key setup".
argument-hint: "[repository-path] [integration-type]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- authentication
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Authentication Decision

## Overview

This skill chooses an authentication boundary before code is written. It distinguishes partner authorization, customer API keys, and admin-enabled private client credentials instead of treating them as interchangeable.

## Prerequisites

- A named repository, Salesloft team, and integration owner
- The integration type: partner, customer-owned, or private backend
- Approved callback URIs and minimum endpoint scopes
- A secret store that supports atomic token replacement

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect existing auth code, environment schemas, and secret names. Use `WebFetch` only for current official Salesloft documentation. Use `Write` or `Edit` only after confirming the repository and auth design.

## Current Contract

- API requests use `Authorization: Bearer <credential>` against `https://api.salesloft.com/v2`.
- Partners use OAuth; Salesloft does not approve partner applications that rely on API keys.
- Customer API keys act as the issuing user and must remain server-side.
- Client credentials are admin-enabled, private-use only, cannot be allowlisted, inherit the creating admin's permissions, expire after 7,200 seconds, and have no refresh token.
- Authorization-code refresh returns a new refresh token and revokes the old one, so replacement must be atomic.

## Authentication

Use authorization code for user-authorized partner applications, client credentials only for an approved private server process, or a scoped API key for a customer-owned integration. Request only scopes required by the current endpoint reference.

## Instructions

1. Inventory every Salesloft endpoint, caller, team boundary, and required scope.
2. Select one supported flow and document why it fits the integration type.
3. Register exact callback URIs or private-app settings in Salesloft Account.
4. Store client secrets, API keys, access tokens, and refresh tokens outside source and logs.
5. Implement Bearer injection plus expiry-aware refresh or reacquisition.
6. For authorization code, replace the access and refresh token together in one durable transaction.
7. Prove access with a bounded read such as `GET /v2/me`; never print the response body in CI.

## Approval Boundaries

Do not broaden scopes, enable client credentials, create or revoke credentials, or change production callback URIs without the integration owner and Salesloft admin. Never expose a token in a command, URL, patch, log, or example.

## Output

Return the integration type, chosen flow, scope matrix, secret references, rotation behavior, read-only proof, and unresolved administrator actions.

## Error Handling

| Condition | Response |
|---|---|
| `invalid_grant` | Recheck redirect URI and one-time code, then restart authorization if needed. |
| 401 | Verify access-token injection and expiry; do not submit a refresh token to the API. |
| 403 | Compare granted scopes and acting-user permissions with the endpoint contract. |
| Concurrent refresh | Serialize refresh and atomically persist the newly rotated token pair. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
integration=partner; flow=authorization-code; proof=GET /v2/me; writes=forbidden
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OAuth authorization code](https://developers.salesloft.com/docs/platform/api-basics/oauth-authentication/)
- [OAuth client credentials](https://developers.salesloft.com/docs/platform/api-basics/client-creds/)
- [API key authentication](https://developers.salesloft.com/docs/platform/api-basics/api-key-authentication/)
