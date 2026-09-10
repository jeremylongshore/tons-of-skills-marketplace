---
name: miro-install-auth
description: "Analyze and execute this workflow: configure a production Miro REST integration with OAuth, least-privilege scopes, tenant-bound storage, and token rotation. Use when installing or repairing Miro authorization. Trigger with \"set up Miro OAuth\"."
argument-hint: "[app-environment] [required-capabilities]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- oauth
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro OAuth Installation and Token Lifecycle

## Overview

Establish an auditable authorization boundary before any board operation. Prefer expiring-token apps and prove tenant context without exposing credentials; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- A Miro Developer team and an app configuration for the target environment
- Approved redirect URIs and a server-side encrypted token store
- A capability-to-scope map and accountable installation owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- REST apps use OAuth 2.0 Authorization Code; authorization starts at `https://miro.com/oauth/authorize` and exchange uses `https://api.miro.com/v1/oauth/token`.
- The REST resource base is `https://api.miro.com/v2`; OAuth endpoints remain v1 and are not deprecated by the REST v2 migration.
- Expiring-token mode provides a one-hour access token and a sixty-day refresh token; refresh rotates both values and invalidates the prior pair.
- Token-expiration mode is chosen when the app is created and cannot later be enabled, disabled, or changed.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Inventory environments, redirect URIs, requested capabilities, scopes, and installation owners.
2. Create or inspect the environment-specific app and select expiring-token mode for new production apps.
3. Generate the authorization URL with an unguessable, session-bound `state` value and an exact registered redirect URI.
4. Exchange the single-use code server-side, atomically store both tokens and expiry metadata, and discard the code.
5. Call access-token context, compare the returned user/team context with the intended tenant, then perform a read-only board probe.
6. Exercise refresh rotation, concurrent-refresh locking, revocation, reinstall, and recovery before enabling writes.

## Approval Boundaries

Do not add scopes, register a new redirect origin, create a production app, or authorize a different team without the application and data owners' approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return app/environment identity, redirect-URI match, approved scopes, token mode, context result, refresh/revocation evidence, and remaining risks. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| OAuth callback has an error or state mismatch | Reject it; do not exchange the code, and restart from a clean session. |
| Token exchange returns 400 | Check one-time code use, exact redirect URI, app identity, and server clock. |
| Context resolves to the wrong team | Quarantine the token and require an intentional reinstall. |
| Refresh races or returns invalid grant | Serialize rotation per installation and recover through reauthorization if the stored pair is stale. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
environment=staging; scopes=boards:read; expiring=yes; context=matched; refresh-rotation=passed; write-access=disabled
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OAuth guide](https://developers.miro.com/docs/getting-started-with-oauth)
- [Token context](https://developers.miro.com/reference/get-access-token-context)
