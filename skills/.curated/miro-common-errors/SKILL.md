---
name: miro-common-errors
description: "Diagnose Miro OAuth and REST failures from status, context, scopes, rate headers, and safe evidence. Use when a Miro integration returns errors. Trigger with \"debug Miro API error\"."
argument-hint: "[http-status] [operation]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- errors
- diagnostics
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro API Error Diagnosis

## Overview

Classify the failing layer before changing code or credentials. Preserve the response status, safe error code, request timing, and tenant context without retaining board content; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Failing operation and sanitized response metadata
- Expected user, app, team, board, and scopes
- Deployment and token-mode context

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary. These declared tools do not call authenticated Miro APIs or deployment CLIs; implement client, configuration, and test changes, then return exact operator commands or an approval-gated handoff for live execution.

## Current Contract

- 401 generally indicates missing, invalid, expired, or revoked authorization; one refresh attempt is the safe ceiling.
- 403/404 can represent scope, membership, role, plan, resource, or tenant-boundary failures.
- 409 means current state conflicts with the requested mutation and requires a re-read.
- 429 responses must be handled from rate-limit headers; 5xx and network failures do not prove a write was absent.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Reproduce once with the smallest safe request and capture status, safe code, timing, and rate headers.
2. Verify URL, method, API version, token context, required scope, plan, and resource ownership.
3. Separate authorization, validation, conflict, throttling, vendor, and network hypotheses.
4. Test the leading hypothesis with a read-only probe or local schema fixture.
5. For ambiguous mutations, reconcile target state before considering a replay.
6. Return the root cause or a ranked evidence table with one bounded next test.

## Approval Boundaries

Do not broaden scopes, reinstall an app, rotate credentials, or repeat a destructive mutation merely to diagnose an error without owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return classification, evidence, ruled-out causes, tenant/scope result, retry safety, remediation, and unresolved uncertainty. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Response body contains board content | Redact it before storing or sharing evidence. |
| Refresh does not fix 401 | Stop and repair/reinstall authorization. |
| 404 remains ambiguous | Check context and membership with an authorized owner. |
| Vendor outage is plausible | Consult official status and open a bounded circuit. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
operation=get-items; status=403; token-context=expected-team; boards:read=missing; retry-safe=yes; action=request-scope-approval
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [Miro status](https://status.miro.com/)
