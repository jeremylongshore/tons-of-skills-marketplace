---
name: clickup-install-auth
description: >-
  Configure ClickUp personal-token or OAuth authorization with server-side storage, state validation, Workspace verification, and rotation ownership. Use when connecting an application to ClickUp. Trigger with "ClickUp auth", "install ClickUp API", or "ClickUp OAuth setup".
argument-hint: "[repository-path] [personal|oauth]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code; OAuth setup requires a ClickUp app owned by a Workspace owner or admin
---
# ClickUp Authentication Setup

## Overview

Choose the authentication mode by tenancy and ownership, then prove the authorized Workspace boundary without exposing credentials.

## Prerequisites

- A server-side application boundary and governed secret manager
- For personal use/testing, an accountable ClickUp user; for public use, an owner/admin-created OAuth app
- Exact redirect URIs, state storage, and an expected Workspace allow-list

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Personal tokens begin with `pk_`, are intended for individual/testing use, and do not expire unless regenerated or revoked.
- User-facing integrations use OAuth Authorization Code at `https://app.clickup.com/api` and exchange at `https://api.clickup.com/api/v2/oauth/token`.
- OAuth access tokens currently do not expire, but ClickUp marks that behavior subject to change.
- Every API request includes the token in `Authorization`; authorized Workspaces are verified through the teams endpoint.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Choose personal or OAuth mode and record credential owner, environment, and intended Workspaces.
2. Store token/client secret only in a secret manager and inject by reference at runtime.
3. For OAuth, register exact HTTPS redirects, generate/validate state, and exchange each code server-side once.
4. Call `GET /api/v2/user` and `GET /api/v2/team` with bounded timeouts.
5. Compare authorized Workspace IDs with the allow-list and reject cross-tenant ambiguity.
6. Document revocation/rotation, reauthorization, incident, and ownership-transfer procedures.

## Approval Boundaries

Do not print tokens, put a client secret in frontend code, accept unvalidated state, silently expand Workspace authorization, or regenerate a shared token without owner approval.

## Output

Return auth mode, secret-reference name, redirect/state result, authorized Workspace IDs in redacted form, verification status, and rotation owner.

## Error Handling

| Condition | Response |
|---|---|
| State mismatch | Reject the callback and start a new authorization attempt. |
| Redirect mismatch | Correct the registered exact URI; do not relax validation. |
| Workspace not authorized | Stop and require explicit user reauthorization. |
| Credential leaked | Revoke/regenerate, scrub artifacts, and record the incident. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
mode=oauth; redirect=exact; state=valid; token=stored-by-reference; workspace-match=yes; writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
