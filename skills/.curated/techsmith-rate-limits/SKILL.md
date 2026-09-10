---
name: techsmith-rate-limits
description: >-
  Manage Snagit and Camtasia workstation capacity with explicit capture, recorder, export, disk, and queue limits. Use when scheduling desktop automation or recovering from overload. Trigger with "TechSmith rate limits", "Camtasia queue limits", or "Snagit capacity guardrails".
argument-hint: "[queue-config] [workstation-pool]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- capacity
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Desktop Capacity Guardrails

## Overview

TechSmith desktop automation does not expose a documented request-rate quota like a SaaS API. This skill therefore defines local capacity limits from interactive-session exclusivity, licensed workers, CPU/GPU/memory/disk headroom, artifact growth, deadlines, and operator impact.

## Prerequisites

- Inventory of approved workers, versions, license assignments, and interactive-session constraints
- Measured capture/export duration and peak resource use for representative workloads
- Queue service objective, maximum artifact size, free-space floor, and cancellation policy
- A durable job identity and idempotency key

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Allow at most one interactive capture or recorder controller per desktop session by default.
- Set export concurrency from observed workstation headroom; do not infer it from CPU count alone.
- Reject new work below the disk free-space floor or above the queue-age deadline.
- Retry only transient worker failures with bounded exponential backoff and a fresh health check.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Classify jobs as interactive capture, recorder control, project export, validation, or archival.
2. Assign separate semaphores and timeouts per job class and workstation capability.
3. Before admission, check product/version, session availability, license health, local disk, queue age, and cancellation state.
4. Lease one durable job identity to one worker; heartbeat and reclaim only after a defined expiry.
5. On completion, validate output and release capacity; on failure, classify before any retry.
6. Graph queue depth, oldest age, active leases, resource saturation, retries, failures, and rejected work.

## Approval Boundaries

Do not call workstation capacity a vendor API rate limit. Never bypass a busy interactive user, license restriction, disk floor, or cancellation signal to drain a queue.

## Output

Return admission decision, selected worker, lease, concurrency class, resource headroom, deadline, retry disposition, and capacity metrics.

## Error Handling

| Condition | Response |
|---|---|
| No eligible interactive session | Keep the job queued or route to an approved staffed window. |
| Disk below floor | Reject new media work and clean only policy-approved disposable artifacts. |
| Lease heartbeat lost | Wait for expiry and verify process state before reassignment. |
| Repeated deterministic failure | Dead-letter the job instead of consuming more workstation time. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
job=cap-882; class=snagit-interactive; session_slots=0/1; decision=queued; oldest_age=4m
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Snagit COM behavior](https://assets.techsmith.com/Docs/Snagit-2025-COM-Server-Guide.pdf)
- [Camtasia project storage](https://support.techsmith.com/hc/en-us/articles/203730028-Working-with-Camtasia-Editor-TSCPROJ-and-TREC-Files)
