---
name: miro-incident-runbook
description: "Analyze and execute this workflow: triage and recover Miro authorization, capacity, outage, and data-correctness incidents with bounded actions. Use when responding to a Miro service incident. Trigger with \"Miro incident\"."
argument-hint: "[incident-id] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- incident-response
- operations
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Incident Response

## Overview

Stabilize user impact before changing authorization or replaying writes. Keep an UTC action log and make ambiguity explicit; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Incident commander, owners, severity, and affected window
- Current deployment, app/team context, dashboards, and safe logs
- Write-disable, circuit-breaker, reconciliation, and rollback controls

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- 401, 403/404, 409, 429, network, and 5xx failures require different containment.
- One refresh attempt is safe only when serialized against rotating token storage.
- 429 recovery follows observed reset headers and shared credit demand.
- Timeout/5xx on a mutation is ambiguous until target state is reconciled.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Declare incident scope, commander, severity, start time, affected tenants/operations, and change freeze.
2. Contain with write disablement, queue pause, concurrency reduction, or circuit opening appropriate to evidence.
3. Correlate deployment changes, token events, rate headers, semantic drift, and official Miro status.
4. Run the smallest read-only probe to classify auth, tenant, capacity, vendor, network, or local failure.
5. Recover in a canary cohort; reconcile ambiguous operations before draining queues.
6. Verify SLOs and data correctness, document timeline/root cause/follow-ups, and obtain closure approval.

## Approval Boundaries

Credential rotation/revocation, scope or redirect changes, destructive repair, queue replay, and broad re-enable require the incident commander's explicit approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return severity, impact, timeline, evidence, containment, root cause/confidence, recovery metrics, reconciliation, approvals, and follow-ups. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Incident scope expands | Reassess severity and containment before further recovery. |
| Mutation result is unknown | Reconcile; never blind-retry. |
| Shared refresh races | Pause callers and serialize one rotation path. |
| Recovery canary regresses | Recontain and restore the last verified state. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
incident=INC-311; class=rate-exhaustion; writes=paused; headroom=35%; ambiguous=4; reconciled=4/4; recovery=stable
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Miro status](https://status.miro.com/)
- [Rate limits](https://developers.miro.com/reference/rate-limiting)
