---
name: clickup-incident-runbook
description: >-
  Triage, contain, recover, and review ClickUp API and webhook incidents with bounded read-only evidence. Use when ClickUp-backed production behavior is degraded. Trigger with "ClickUp incident", "ClickUp outage", or "ClickUp webhook failing".
argument-hint: "[incident-id] [severity]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- clickup
- incident-response
model: inherit
effort: high
compatibility: Designed for Claude Code; live response requires authorized operational access and an incident commander
---
# ClickUp Integration Incident Response

## Overview

Separate provider health, credential scope, rate exhaustion, webhook suspension, data drift, and application faults before taking recovery action.

## Prerequisites

- An incident commander, severity model, affected service/Workspace inventory, and communication channel
- Read-only diagnostic capability plus audited break-glass procedures
- Known last-good deployment, queue checkpoints, and rollback targets

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, adapters, configuration names, tests, and evidence. Use `WebFetch` only for current official ClickUp documentation. Use `Write` or `Edit` after confirming the target file, Workspace boundary, and requested mode.

## Current Contract

- ClickUp status, API reachability, tenant authorization, and application side effects are independent signals.
- A webhook is failing after unsuccessful or over-seven-second responses; failed events are not resent after their delivery attempts.
- At `fail_count=100` a webhook is suspended; returning 401 suspends it immediately.
- 429 recovery follows the per-token reset header rather than a guessed delay.

## Authentication

Use a personal token only for accountable individual/testing work or OAuth Authorization Code for a user-facing integration. Inject the token server-side through a governed secret reference, send it in `Authorization`, verify authorized Workspace IDs, and never print the token, OAuth client secret, or webhook secret.

## Instructions

1. Declare scope, commander, severity, affected Workspaces, write freeze, and evidence-retention boundary.
2. Check provider status and run metadata-only identity/rate probes.
3. Classify auth, plan/permission, rate, webhook health, schema, queue, deployment, or data-consistency failure.
4. Contain with write disablement, circuit breaking, queue pause, or rollback before rotating credentials.
5. Recover one lane at a time and reconcile missed or duplicate business operations from durable records.
6. Close only after verification, stakeholder communication, evidence capture, and assigned follow-up.

## Approval Boundaries

Do not rotate shared tokens, reactivate webhooks, replay queues, mutate tasks, or suppress evidence without commander and owner approval.

## Output

Return timeline, failure class, containment, affected Workspaces/operations, recovery evidence, reconciliation result, and follow-up owners. Include unresolved risk and the next decision deadline.

## Error Handling

| Condition | Response |
|---|---|
| Evidence includes work content | Redact or quarantine before sharing. |
| Webhook events were dropped | Reconcile from source-of-truth reads; do not assume ClickUp will resend them. |
| Credential ownership is unknown | Freeze writes and escalate before rotation. |
| Recovery increases error rate | Return to containment and roll back. |

## Examples

The example below is a redacted operator receipt; it contains no task text, member data, credential, or webhook secret.

```text
incident=CU-207; provider=healthy; class=webhook-suspended; writes=frozen; reconcile=required; commander=assigned
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Webhook health](https://developer.clickup.com/docs/webhookhealth)
- [Authentication](https://developer.clickup.com/docs/authentication)
- [Rate limits](https://developer.clickup.com/docs/rate-limits)
