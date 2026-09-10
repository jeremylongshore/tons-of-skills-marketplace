---
name: salesloft-hello-world
description: >-
  Prove a Salesloft credential and team boundary with one bounded read-only request and response-envelope check. Use when testing a new integration without creating CRM data. Trigger with "Salesloft hello world", "first Salesloft request", or "test Salesloft connection".
argument-hint: "[repository-path] [team-alias]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- getting-started
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Verified First Read

## Overview

This skill proves credential injection, team identity, HTTPS handling, and the Salesloft response envelope. It deliberately avoids creating a person or enrolling anyone in a cadence.

## Prerequisites

- A named repository and non-production or explicitly approved team
- A scoped OAuth access token or customer API key
- A runtime with HTTPS, JSON parsing, and a bounded timeout
- Permission to read the authenticated identity

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the local HTTP wrapper, environment-variable names, and tests. Use `WebFetch` only for current official Salesloft documentation. Use `Write` or `Edit` after confirming the target implementation file.

## Current Contract

- Base URL: `https://api.salesloft.com/v2`.
- Send the credential as a Bearer value; do not put it in a query parameter.
- Use the documented path without assuming every endpoint requires a `.json` suffix.
- Successful response bodies place returned data under `data`; list responses can also include `metadata`.

## Authentication

Use a partner OAuth access token, approved private-app token, or customer API key appropriate to the integration. The proof must not request or exercise write scopes.

## Instructions

1. Confirm repository, team alias, auth flow, secret source, and expected identity.
2. Configure an explicit base URL, Bearer injection, Accept header, and timeout.
3. Request `GET /v2/me` once without retries that could hide an auth failure.
4. Validate status, JSON content type, and the `data` envelope.
5. Compare only a safe team or user identifier with the expected target.
6. Add fixtures for success, 401, 403, and non-JSON responses.

## Approval Boundaries

Do not create a demonstration person, change a cadence, or print the credential or raw identity payload. Stop if the returned team is not the approved target.

## Output

Return redacted configuration, status, envelope assertion, expected-target match, fixture results, and the next authorized workflow.

## Error Handling

| Condition | Response |
|---|---|
| 401 | Check credential type, expiry, and Bearer injection. |
| 403 | Confirm identity-read scope and acting-user permissions. |
| Non-JSON response | Preserve status and content type, then stop parsing. |
| Wrong team | Stop all work and correct the credential mapping. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
team=staging; request=GET /v2/me; envelope=pass; writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API basics](https://developers.salesloft.com/docs/platform/api-basics/)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
