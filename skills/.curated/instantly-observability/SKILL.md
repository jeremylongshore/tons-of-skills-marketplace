---
name: instantly-observability
description: >-
  Monitor Instantly API, campaign sending, account vitals, background jobs, and webhook delivery with safe telemetry. Use when defining dashboards, alerts, or service-level indicators for an Instantly integration. Trigger with "monitor Instantly API health", "alert on Instantly webhook failures", or "design Instantly telemetry".
argument-hint: "[service] [window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- observability
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Integration Observability

## Overview

Define actionable service signals without logging lead content, email bodies, or credentials. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Use campaign sending-status rather than inferring health from aggregate counts alone.
- Webhook event aggregate endpoints expose success/failure evidence.
- Workspace-wide rate limits require shared client telemetry across keys.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Define service-level indicators for request success, latency, 429s, job age, sending state, and webhook failures.
2. Instrument route templates, status classes, retry counts, request IDs, and workspace-safe labels.
3. Poll documented health and aggregate endpoints at a bounded cadence.
4. Redact API keys, addresses, lead payloads, reply content, and email bodies.
5. Set alerts against measured baselines with owner-reviewed thresholds.
6. Link each alert to diagnosis, containment approval, and rollback steps.

## Approval Boundaries

Do not create, rotate, reveal, or revoke keys; invite or remove members; delegate across workspaces; connect sending accounts; create or activate campaigns; import or delete leads; change suppression or retention; register, patch, resume, or delete webhooks; alter plans or paid capacity; transmit diagnostics; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace-safe scope, files and contracts inspected, exact API v2 routes and required scopes, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| `401` | Stop and verify that the bearer key exists, is current, and was not revoked. |
| `403` | Stop and compare the operation with its exact required scope; do not broaden to `all:all` by default. |
| `429` | Coordinate the workspace-wide budget, honor endpoint overrides, and bound retries. |
| Schema or tenant mismatch | Fail closed, preserve redacted evidence, and do not retry a mutation. |

## Examples

Use a compact handoff that makes scope, mutation authority, and evidence reviewable.

Input:

```text
service=campaign-sync; window=24h; payload-logging=false
```

Expected handoff:

```text
sli=defined; dashboard=planned; sensitive-fields=excluded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
