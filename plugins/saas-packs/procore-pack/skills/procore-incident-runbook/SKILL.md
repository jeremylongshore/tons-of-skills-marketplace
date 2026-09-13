---
name: procore-incident-runbook
description: >-
  Analyze, triage, and recover a Procore integration incident across provider health, OAuth, company routing, permissions, rate limits, webhooks, files, and synchronization gaps. Use when service objectives or data parity are breached. Trigger with: "run Procore incident response", "Procore sync is down", "recover missing Procore updates".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[incident-id-and-primary-symptom]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - incident-response
  - recovery
compatibility: 'Requires access to application telemetry, Procore status and health evidence, deployment controls, and approved incident communications.'
---

# Procore Integration Incident Command

## Overview

Protect construction data integrity while restoring service. Separate provider outage, identity failure, tenant-routing defect, permission drift, rate exhaustion, event-delivery gap, and internal deployment regression before choosing recovery actions.

## Prerequisites

- Incident commander, severity, affected tenant aliases, start time, and objectives
- Current release, last known good release, queue and reconciliation checkpoints
- Procore status, Integration Health, API activity, and approved communication channels

## Instructions

### Step 1: Stabilize

Pause risky mutations, preserve durable queues, stop retry storms, and keep read-only evidence collection bounded. Do not delete events or rotate credentials without a matching hypothesis.

### Step 2: Classify

Compare Procore status with route-level 401, 403, 404, 422, 429, 503, latency, webhook delivery, and backlog signals. Segment by release, environment, company, project, and operation.

### Step 3: Test the boundary

Run one read-only connection proof using the intended principal and company context. Check app connection, DMSA permissions, permitted projects, enabled tools, and rate headers.

### Step 4: Mitigate narrowly

Roll back a bad release, repair tenant routing, reauthorize or rotate only when credential evidence supports it, reduce concurrency, or disable the affected mutation path.

### Step 5: Recover data

Determine the gap window, replay durable work idempotently, and run REST reconciliation. Validate record counts and state hashes before reopening downstream publication.

### Step 6: Settle and learn

Monitor until objectives recover, record root cause and contributing controls, assign follow-ups, and retain only redacted evidence with a deletion schedule.

## Authentication

Incident probes use the existing OAuth 2.0 principal unless identity failure is the proven cause. Tokens, client secrets, destination headers, and signed URLs never enter the incident timeline or chat.

## Tool Discipline

Use Read and Grep to inspect telemetry, configurations, runbooks, and sanitized logs. Use Write or Edit only for the approved mitigation, recovery artifact, timeline, or receipt; consequential provider changes require the incident commander and administrator.

## Output

- Classification, scope, timeline, and mitigation decision
- Gap-window reconciliation and parity evidence
- Root cause, rollback, follow-up, and redacted incident receipt

Return current severity, customer impact, safe action, owner, recovery signal, and next checkpoint.

## Examples

Webhook deliveries fail during receiver downtime. The team preserves the queue, fixes ingress, identifies the exact gap window, reconciles changed resources through REST, compares downstream state hashes, and resumes mutations only after parity passes.

## Error Handling

| Failure | Response |
| --- | --- |
| Cause is ambiguous | Keep mutations paused and gather one discriminating read-only observation. |
| Retry storm threatens limits | Stop workers, honor provider headers, and resume through controlled queues. |
| Event gap is unknown | Widen reconciliation to the last trusted checkpoint rather than guessing. |
| Credential exposure is confirmed | Rotate or revoke, invalidate caches, and investigate unknown API activity. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Procore system status](https://status.procore.com/)
- [Troubleshooting](https://developers.procore.com/documentation/troubleshooting)
- [Integration Health](https://developers.procore.com/documentation/integration-health)
