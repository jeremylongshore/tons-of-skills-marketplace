---
name: navan-rate-limits
description: >-
  Configure Navan integration concurrency and retry controls from the tenant contract and observed responses. Use when controlling throughput or throttling. Trigger with "Navan rate limit", "throttle Navan sync", or "Navan backpressure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <workload> <deadline>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, capacity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Capacity and Backpressure Control

## Overview

Configure Navan integration concurrency and retry controls from the tenant contract and observed responses. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

No universal public numeric quota should be frozen into code. Treat account limits, file windows, vendor responses, destination capacity, and business deadlines as dated evidence with independent bounds.

## Authentication

Capacity testing uses the least-privilege non-production identity. Never discover limits by flooding a production travel or expense tenant.

## Instructions

1. Capture documented limits and escalation contacts for the enabled surface.
2. Classify reads, writes, transfers, and reconciliation work by side-effect risk.
3. Set application concurrency below the narrowest vendor or destination bound.
4. Honor documented retry signals with capped delay, jitter, and deadlines.
5. Checkpoint pages or files durably and reconcile after ambiguous outcomes.
6. Alert on queue age, throttle rate, deadline risk, and sustained capacity loss.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Load tests, quota-change requests, deadline overrides, write retries, and production concurrency increases require explicit approval.

## Error Handling

- A numeric limit copied from another tenant is not evidence.
- Do not retry authentication or contract failures as throttling.
- A timed-out write remains unknown until reconciled.

## Output

Return documented limits, chosen concurrency, retry classes, queue/deadline model, reconciliation plan, and escalation threshold. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Throttle a backfill behind daily production extraction.
- Pause when destination latency would exhaust the source window.

## Validation

Simulate throttling, long delay, destination slowdown, process restart, deadline exhaustion, and unknown write outcome. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
