---
name: flyio-webhooks-events
description: >-
  Detect Fly.io Machine, health, release, and log changes through supported reads, waits, and log export without claiming general app webhooks. Use when building operational event automation. Trigger with: "monitor Fly Machine changes", "replace Fly webhook", "stream Fly health events".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[app-signal-and-observation-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flyio
  - change-detection
  - machine-states
  - observability
compatibility: 'Requires read access to the selected app signals, durable checkpoint state, a bounded observation window, and an approved downstream alert or event sink.'
---

# Fly.io Machine and Health Change Feed

## Overview

The general app platform does not document a customer-configurable webhook subscription and signing surface, so this route uses supported change detection through Machines reads and state waits, health status, deployment evidence, and documented log shipping. Extension-provider machine-event webhooks are a separate partner-specific contract and are not assumed here.

## Prerequisites

- Selected signal types, apps, regions, process groups, and service objectives
- Durable last-seen state, deduplication key, overlap policy, and sink acknowledgement
- Read-only token and redaction rules for Machine, health, release, and log fields

## Instructions

### Step 1: Choose supported signals

Use Machine list or get for inventory, the Machine wait endpoint for a known transition, health-check status for routing readiness, release evidence for deployments, and documented log shipping for application events.

### Step 2: Snapshot the starting boundary

Record active Machine ID and instance version, lifecycle state, image, checks, regions, and the observation-window checkpoint before polling.

### Step 3: Normalize change identity

Create a deterministic key from app, Machine, instance version, signal type, observed transition, and source timestamp. Preserve provider request or release lineage.

### Step 4: Deduplicate before publishing

Compare with last-seen state and the sink acknowledgement store. Publish only changed, validated, redacted records and advance the checkpoint after acknowledgement.

### Step 5: Detect gaps and stale monitors

Alert on missed polls, wait timeouts, health age, log-export lag, state discontinuities, and unknown instance replacement. Re-read authoritative state before replay.

### Step 6: Reconcile downstream action

Operational events may recommend but must not automatically restart, scale, or delete resources without a separately approved control policy.

## Authentication

Use a read-only organization token for monitoring where possible and send bearer credentials only to documented Fly.io endpoints. Keep log-export credentials separate. Do not invent a shared webhook secret or signature header for general Fly Apps.

## Tool Discipline

Use Read and Grep to inspect application configuration, deployment evidence, provider documentation, fixtures, logs, schemas, and existing tests before proposing a change. Use Write or Edit only for an approved plan, configuration, implementation, test, or redacted receipt. Do not create, deploy, scale, restart, stop, suspend, destroy, rotate, revoke, expose, or migrate live Fly.io resources without explicit operator approval.

## Output

- Signal catalog and checkpoint policy
- Normalized redacted changes with deterministic IDs and source lineage
- Lag, gap, deduplication, acknowledgement, and reconciliation receipt

Return the target organization, app, environment, region set, Machine or database identifiers, source-contract fingerprint, evidence, unresolved risks, rollback state, and final decision without exposing tokens, secrets, connection strings, or customer data.

## Examples

A monitor records each Machine ID, active instance version, image, state, and health. After a deploy, it emits one change per replacement, waits for sink acknowledgement, advances state, and never claims that Fly.io delivered a signed webhook.

## Error Handling

| Failure | Response |
| --- | --- |
| Wait endpoint times out | Read the current Machine and instance version, record an unknown or delayed transition, and avoid duplicate action. |
| Health timestamp is misunderstood | Treat last-updated as the last status change, not the most recent check execution. |
| Downstream acknowledgement is unknown | Replay the same deterministic record and let sink deduplication prevent duplicate effects. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Machines API setup](https://fly.io/docs/machines/api/working-with-machines-api/)
- [Automation and tokens](https://fly.io/docs/flyctl/integrating/)
- [App configuration](https://fly.io/docs/reference/configuration/)
- [Machines resource](https://fly.io/docs/machines/api/machines-resource/)
- [Machine states](https://fly.io/docs/machines/machine-states/)
- [Health checks](https://fly.io/docs/reference/health-checks/)
- [Monitoring](https://fly.io/docs/monitoring/)
- [Export logs](https://fly.io/docs/monitoring/exporting-logs/)
