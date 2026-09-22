---
name: linear-incident-runbook
description: >-
  Analyze and contain Linear integration incidents across authentication, GraphQL, rate budgets, webhooks, and data synchronization. Use when responding to an active degradation or reconciling after an incident. Trigger with "Linear integration incident", "Linear webhook outage", or "Linear API degradation".
argument-hint: "[incident-id] [auth|api|rate|webhook|sync]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- incident-response
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Integration Incident Runbook

## Overview

Restore a safe operating state from read-only evidence first, then reconcile missed or duplicated work without generating diagnostic mutations in production.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Linear webhooks time out after five seconds and retry failed deliveries at one minute, one hour, and six hours, up to three retries.
- Rate-limit evidence comes from request, endpoint, and complexity headers plus `RATELIMITED` GraphQL errors.
- OAuth client-secret rotation invalidates client-credentials tokens immediately but does not revoke existing workspace access/refresh tokens by itself.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Declare severity, commander, affected workspaces/teams, start time, customer impact, and mutation freeze state.
2. Check Linear service status and the smallest read-only authenticated query; capture redacted errors and rate headers.
3. Classify auth, authorization, quota, schema, webhook delivery, downstream queue, or reconciliation failure.
4. Contain retries, pause nonessential producers, preserve webhook delivery IDs, and avoid rotating secrets without an access-impact map.
5. Recover through the smallest approved change, then replay only idempotent or explicitly reconciled work.
6. Close with a gap analysis, missed-event reconciliation, credential review, and regression test.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Service outage | Pause mutation retries and preserve local queues until service recovery is verified. |
| Auth widespread | Map token type and rotation effects before replacing credentials. |
| Webhook backlog | Acknowledge quickly into a durable queue and deduplicate by delivery ID. |
| Data divergence | Run read-only reconciliation before replaying any writes. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
incident=INC-204; symptom=webhook-timeouts; mutation-freeze=true
```

Expected handoff:

```text
class=delivery-path; containment=queue-only; replay=reconciliation-required
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
