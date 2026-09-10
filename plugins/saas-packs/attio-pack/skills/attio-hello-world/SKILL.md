---
name: attio-hello-world
description: >-
  Prove the smallest safe Attio REST connection by listing objects and validating the response envelope without changing CRM data. Use when checking a new token, workspace, or integration path. Trigger with "Attio hello world", "first Attio request", or "test Attio connection".
argument-hint: "[repository-path] [workspace-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- getting-started
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Attio Verified First Read

## Overview

This skill proves authentication, workspace reachability, JSON parsing, and object discovery with one read-only request. It does not create a demonstration contact in a real CRM.

## Prerequisites

- A named repository and non-production or approved workspace
- A single-workspace access token or OAuth access token
- The `object_configuration:read` scope required by the object-list endpoint
- A runtime with HTTPS and JSON support

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the local client, environment-variable names, and tests. Use `WebFetch` only for current official Attio documentation. Use `Write` or `Edit` after confirming the repository and intended implementation file.

## Current Contract

- Base URL: `https://api.attio.com/v2`.
- Send `Authorization: Bearer <access_token>`; Bearer authentication is the recommended form.
- Start with `GET /v2/objects` and validate a `{ data: [...] }` response.
- Keep the credential out of source, output, exceptions, and request logging.

## Authentication

Use a workspace API key for a single workspace or OAuth for an app serving multiple workspaces. Do not request write scopes for this proof.

## Instructions

1. Confirm the repository, runtime, workspace alias, secret source, and granted scope.
2. Add or inspect a tiny request wrapper with explicit base URL and Bearer header injection.
3. Request `/objects` with a bounded timeout and capture status plus content type.
4. On success, parse `data` and record only object slugs or counts that are safe to expose.
5. Assert that at least one expected object is visible to the workspace.
6. Add a fixture test for success plus 401, 403, and non-JSON failure handling.

## Approval Boundaries

Do not add create, update, assert, or delete calls to the first-read proof. Never print the access token or persist a raw workspace response.

## Output

Return the redacted configuration, status, response-envelope assertion, safe object summary, fixture-test result, and next integration boundary.

## Error Handling

| Condition | Response |
|---|---|
| 401 | Verify credential injection and replace an invalid token. |
| 403 | Confirm `object_configuration:read` without broadening other scopes. |
| Non-JSON response | Preserve status/content type and stop parsing. |
| Unexpected workspace data | Stop and verify workspace identity. |

## Examples

Input:

```text
workspace=development; request=GET /v2/objects; writes=forbidden
```

Expected handoff:

```text
auth=pass; envelope=pass; expected-object=present; secrets-exposed=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Authentication](https://docs.attio.com/rest-api/guides/authentication)
- [Objects and lists](https://docs.attio.com/docs/objects-and-lists)
