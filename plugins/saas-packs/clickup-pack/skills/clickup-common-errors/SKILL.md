---
name: clickup-common-errors
description: >-
  Analyze and diagnose ClickUp authentication, authorization, plan, request, pagination, throttling, webhook, and provider failures from redacted evidence. Use when a ClickUp integration fails or behaves inconsistently. Trigger with "ClickUp error", "ClickUp 429", or "diagnose ClickUp API".
argument-hint: "[status-code-or-error] [endpoint]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- troubleshooting
model: inherit
effort: high
compatibility: Designed for Claude Code; live diagnosis requires authorized ClickUp access and sanitized evidence
---
# ClickUp Error Diagnosis

## Overview

Classify the failure before changing code so authentication, workspace scope, plan gates, schema drift, and transient provider faults receive different remedies.

## Prerequisites

- A redacted status code, ClickUp error code/message, endpoint version, and request shape
- The authorized Workspace ID, auth mode, and current plan facts from an owner
- Access to current ClickUp docs and status information

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- `OAUTH_017` can indicate a missing Authorization header; workspace authorization and revoked-token families have distinct codes.
- Browser-side CORS failures require a server-side boundary, not a permissive token-bearing frontend workaround.
- A 429 is per token; inspect `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and Unix `X-RateLimit-Reset`.
- Retry only bounded transient failures; do not retry malformed requests or permission denials.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Capture the method, versioned path, status, ClickUp error code, response type, and sanitized headers.
2. Confirm whether the caller uses a personal token or OAuth and whether the Workspace was authorized.
3. Validate path parameters, JSON content type, endpoint version, pagination cursor/page, and plan eligibility.
4. Separate 401/403, 404, 409-style state conflicts, 429, timeout, and 5xx classes.
5. Reproduce with the smallest read-only request and compare against the official reference.
6. Recommend the narrowest correction and record the post-fix probe.

## Approval Boundaries

Do not regenerate credentials, reauthorize Workspaces, upgrade a plan, replay writes, or disclose task content merely to diagnose an error.

## Output

Return failure class, evidence, likely cause, safe correction, retry decision, owner action, and verification result.

## Error Handling

| Condition | Response |
|---|---|
| Evidence contains a token or work content | Stop, redact it, and rotate the exposed credential if necessary. |
| Workspace scope is unknown | Do not infer permission; obtain authorized Workspace facts. |
| 429 lacks usable reset data | Pause with bounded backoff and re-probe conservatively. |
| Provider status is degraded | Defer writes and retain the incident window. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
status=401; code=OAUTH_017; class=auth-header; retry=no; correction=restore-server-secret-reference
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Common errors](https://developer.clickup.com/docs/common_errors)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
