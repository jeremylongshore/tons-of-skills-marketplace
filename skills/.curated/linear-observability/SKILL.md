---
name: linear-observability
description: >-
  Instrument Linear API, SDK, webhook, queue, and reconciliation behavior with useful redacted signals. Use when defining service objectives, dashboards, alerts, or audit evidence. Trigger with "monitor Linear integration", "add Linear API metrics", or "observe Linear webhooks".
argument-hint: "[repository-path] [metrics|logs|traces|alerts]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.13.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linear
- observability
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Linear workspace credential
---
# Linear Integration Observability

## Overview

Measure contract health and business freshness without placing tokens, GraphQL variables, issue content, or user identities in telemetry.

## Prerequisites

- The target repository, Linear workspace, environment, and accountable owner
- Current security, privacy, compliance, capacity, and change-control requirements
- An approved Linear credential only when a bounded live verification is necessary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current first-party Linear documentation and package metadata. Use `Write` or `Edit` only for requested implementation with known target files. Never write credentials, customer content, unrestricted environment output, or unredacted GraphQL variables.

## Current Contract

- Linear returns request-limit, endpoint-limit, complexity, remaining-budget, and reset headers that can drive safe capacity telemetry.
- Webhook delivery headers include unique delivery ID, event type, signature, and timestamp; never log the signature as reusable evidence.
- Enterprise audit logs retain 90 days and can be queried or streamed, but are owner-only and contain sensitive actor/IP metadata.

## Authentication

Use a personal API key only for owner-controlled scripts, OAuth with PKCE for user-delegated applications, or an enabled client-credentials grant for approved automation. Personal keys use `Authorization: <API_KEY>`; OAuth tokens use `Authorization: Bearer <ACCESS_TOKEN>`. Store credentials server-side in an approved secret manager.

Treat app approval, team access, scope changes, credential creation, rotation, revocation, and production access as owner-approved actions.

## Instructions

1. Define service objectives for API success, GraphQL application errors, webhook acknowledgement, queue lag, and reconciliation freshness.
2. Emit operation names, status, normalized error code, latency, retry count, and rate/complexity budget—not raw queries or variables.
3. Track webhook delivery ID hashes, event type, verification result, acknowledgement latency, dedupe outcome, and processing lag.
4. Alert on sustained budget exhaustion, auth failures, signature failures, queue age, and reconciliation divergence.
5. Keep audit-log ingestion separate, least-privileged, redacted, and aligned with the organization's retention policy.
6. Test dashboards and alerts with synthetic failures and record owner, runbook, and quieting rules.

## Approval Boundaries

Do not create, reveal, rotate, or revoke credentials; authorize an OAuth app; change scopes or team access; create, mutate, archive, or delete workspace data; configure or re-enable webhooks; import or export data; change roles, SCIM, or audit streaming; transmit diagnostics; change paid entitlements; or perform another production mutation without explicit approval from the accountable owner. Keep diagnosis read-only unless implementation was requested.

## Output

Return the workspace and team scope, auth mode without credential value, files and contracts inspected, exact operation names, evidence collected, validation result, sensitive fields redacted, remaining risk, accountable owner, approval state, and rollback or next action.

## Error Handling

| Condition | Response |
|---|---|
| Sensitive telemetry | Drop and scrub the field before expanding observability. |
| Header absent | Mark the metric unknown; do not fabricate a full budget. |
| Alert storm | Aggregate by workspace/operation and preserve the first actionable evidence. |
| Audit access denied | Confirm Enterprise owner authority; do not work around it with scraped UI data. |

## Examples

Use a compact handoff that makes scope, mutation authority, and verification evidence reviewable.

Input:

```text
slo=webhook-ack<5s; dimensions=workspace-hash,operation; payload-logging=false
```

Expected handoff:

```text
metrics=bounded; alerts=runbook-linked; content=excluded
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Linear developer documentation index](https://linear.app/llms.txt)
- [Linear GraphQL API](https://linear.app/developers/graphql.md)
