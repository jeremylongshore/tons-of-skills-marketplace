---
name: attio-install-auth
description: >-
  Choose and configure Attio REST authentication for a single workspace or multi-workspace OAuth app, including least-privilege scopes and a read-only verification. Use when connecting a service to Attio. Trigger with "Attio auth", "Attio API key", or "Attio OAuth setup".
argument-hint: "[repository-path] [single-workspace|oauth]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- authentication
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Authentication Setup

## Overview

This skill selects the correct Attio access-token path, maps endpoint scopes, and proves the credential with a non-mutating request.

## Prerequisites

- The integration's workspace and tenancy model
- Exact endpoints and operations the application will use
- An approved secret store and rotation owner
- Registered redirect URIs when OAuth is required

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the local auth wrapper, secret names, redirect configuration, and endpoint use. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after the auth model and target files are confirmed.

## Current Contract

- Prefer OAuth 2.0 for an app that serves multiple Attio workspaces.
- Use a manually generated workspace API key for one controlled workspace.
- Both credential types can be sent as `Authorization: Bearer <access_token>`.
- Required scopes are documented per endpoint and should be granted operation by operation.
- Attio also supports Basic authentication with the token as username and an empty password, but Bearer is recommended.

## Authentication

For OAuth, validate `state`, use the registered redirect URI exactly, exchange the code server-side, and encrypt the resulting token at rest. For a workspace key, create it in developer settings with the minimum scopes and store it only in the approved secret manager.

## Instructions

1. Classify the integration as single-workspace or multi-workspace.
2. Inventory methods and endpoints, then derive scopes from their current reference pages.
3. Define secret storage, tenant-to-token mapping, rotation, revocation, and audit ownership.
4. Implement server-side credential injection without token logging.
5. For OAuth, bind and verify `state`; never expose the client secret to browser code.
6. Verify with one read-only endpoint and record only status, workspace alias, and granted scope names.

## Approval Boundaries

Do not generate or broaden production credentials, modify redirect URIs, or migrate tenant tokens without the owning administrator's approval and a rollback plan.

## Output

Return the chosen auth model, endpoint-to-scope map, secret reference, OAuth control evidence if applicable, read-only verification, and rotation owner.

## Error Handling

| Condition | Response |
|---|---|
| Tenancy model is unclear | Stop before choosing a credential type. |
| OAuth state mismatch | Reject the callback and start a fresh authorization flow. |
| 403 after verification | Compare the exact endpoint scopes; do not grant all scopes. |
| Token appears in logs | Revoke or rotate it and scrub retained output. |

## Examples

Input:

```text
tenancy=multiple-workspaces; endpoint=GET /v2/tasks; storage=encrypted-server-side
```

Expected handoff:

```text
auth=oauth; state=verified; scopes=endpoint-derived; read-test=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [OAuth tutorial](https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth)
- [REST API overview](https://docs.attio.com/rest-api/overview)
