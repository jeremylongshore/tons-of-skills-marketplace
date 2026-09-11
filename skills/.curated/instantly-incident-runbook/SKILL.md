---
name: instantly-incident-runbook
description: >-
  Analyze and triage Instantly campaign, account, webhook, job, and API failures with explicit containment approvals. Use when responding to a live degradation, delivery anomaly, or integration outage. Trigger with "triage an Instantly incident", "contain Instantly sending failure", or "investigate an Instantly outage".
argument-hint: "[incident-id] [severity]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- instantly
- incident-runbook
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Instantly workspace and API v2 key
---
# Instantly Incident Response

## Overview

Contain a production incident while preserving evidence, tenant boundaries, and reversible recovery actions. Record assumptions, evidence, approval state, and rollback ownership so another operator can reproduce the result.

## Prerequisites

- The target repository, Instantly workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved API v2 key only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Instantly documentation and package metadata. Use `Write` or `Edit` only when implementation was requested and exact target files are known; never write credentials, lead data, email content, or unrestricted environment output.

## Current Contract

- Campaign pause, account pause, webhook resume, and key revocation are state-changing actions.
- Sending-status, account vitals, background jobs, and webhook aggregates provide documented evidence surfaces.
- Workspace-wide 429s require coordinated throttling across every key.

## Authentication

Use an API v2 key as `Authorization: Bearer <key>` against `https://api.instantly.ai/api/v2`. Grant only the endpoint-specific scopes needed, inject the key from an approved server-side secret manager, and never print, persist, commit, or place it in a URL. Treat key creation, rotation, revocation, member changes, workspace delegation, and production access as owner-approved actions.

## Instructions

1. Declare severity, affected workspace, owner, time window, and customer impact.
2. Preserve redacted request IDs, statuses, deploy SHA, campaign state, and aggregate health.
3. Classify identity, scope, quota, sending, account, job, webhook, or provider failure.
4. Propose the smallest containment action with blast radius and rollback.
5. Execute pause, resume, revoke, or rollback only after incident-owner approval unless a pre-approved runbook applies.
6. Verify recovery, monitor recurrence, and record follow-up ownership.

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
incident=INC-123; severity=P2; action=diagnose-only
```

Expected handoff:

```text
cause=scope-regression; containment=proposed; approval=required
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Instantly API v2 documentation](https://developer.instantly.ai/)
- [Instantly API v2 OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)
