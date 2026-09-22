---
name: clickup-hello-world
description: >-
  Prove the smallest safe ClickUp API connection by reading the authorized user and Workspaces without creating work. Use when validating a new ClickUp credential. Trigger with "ClickUp hello world", "test ClickUp token", or "first ClickUp API call".
argument-hint: "[personal-token|oauth] [expected-workspace-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- quickstart
model: inherit
effort: high
compatibility: Designed for Claude Code; the live probe requires a ClickUp personal token or OAuth access token
---
# ClickUp Verified First Read

## Overview

Verify authentication, JSON parsing, and Workspace scope before enabling any task or webhook mutation. Keep this first probe read-only and narrowly scoped.

## Prerequisites

- A personal token for individual/testing use or an OAuth token for a user-facing app
- An expected authorized Workspace ID supplied through a safe channel
- A server-side runtime that will not expose the token

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- Send the token in the `Authorization` header; OAuth examples may use the Bearer form documented by ClickUp.
- Use `GET /api/v2/user` to confirm caller identity and `GET /api/v2/team` for authorized Workspaces.
- In v2, returned teams are Workspaces.
- The probe performs zero writes and logs no names, emails, or tokens.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Confirm the auth mode, secret reference, expected Workspace, timeout, and zero-write boundary.
2. Inspect the local client and ensure the base URL is `https://api.clickup.com/api/v2`.
3. Request the authorized user and validate a JSON user object without logging personal fields.
4. Request authorized teams and compare IDs to the expected Workspace allow-list.
5. Record status, latency, response schema, and redacted Workspace match.
6. Keep mutation disabled until the caller explicitly selects a bounded workflow.

## Approval Boundaries

Do not create a test task, regenerate a token, or broaden OAuth Workspace authorization as part of this read-only proof.

## Output

Return auth mode, user-probe result, authorized Workspace count, expected-ID match, latency, and writes performed. A successful result must explicitly report zero writes.

## Error Handling

| Condition | Response |
|---|---|
| 401 or OAuth code | Verify the secret reference and auth flow without printing the token. |
| Expected Workspace absent | Stop; ask the user to reauthorize or choose the correct account. |
| Response is not JSON | Capture metadata only and diagnose proxy/provider behavior. |
| Only a browser runtime exists | Create a server-side boundary; never expose the token. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
auth=oauth; user=verified; workspaces=2; expected-workspace=present; writes=0; secrets-exposed=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
