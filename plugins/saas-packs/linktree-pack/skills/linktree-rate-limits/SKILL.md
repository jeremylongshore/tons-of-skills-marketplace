---
name: linktree-rate-limits
description: 'Build backpressure and capacity controls from an approved Linktree partner contract without publishing guessed quotas. Use when authorized automation needs reliability limits. Trigger with "plan Linktree capacity".'
argument-hint: "[contract-path] [workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- linktree
- capacity
- backpressure
- reliability
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Linktree account and approval from the profile, Workspace, data, or partner-integration owner
---
# Linktree Contract-Grounded Capacity Control

## Overview

Convert documented limits and observed behavior into conservative client controls, while treating every undocumented quota or reset rule as unknown.

## Prerequisites

- An authorized Linktree account or a clearly bounded design-only task
- The profile, Workspace, destination, campaign, data, or integration owner appropriate to the requested change
- Current account evidence for plan-dependent features and user-supplied approved partner documentation for every private interface

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository specifications, sanitized fixtures, policies, tests, and prior receipts.

Use `WebFetch` only for current official Linktree documentation or explicitly approved partner documentation.

Use `Write` or `Edit` only after confirming scope, target, owners, data classification, and approval state. These tools do not confer Linktree access, account authority, or permission to process visitor data. Return exact operator steps or an approval-gated handoff when a live action is not authorized.

## Current Contract

- Linktree's public developer page does not state request quotas, concurrency limits, retry semantics, or headers.
- Only current partner documentation and vendor-confirmed environment evidence can authorize numeric automation limits.
- Public Admin workflows remain human-paced and are not a basis for deriving machine throughput.

## Authentication

For Admin work, use only the operator's individually provisioned Linktree account, documented Workspace role, and enabled MFA. Never request passwords, one-time codes, browser cookies, recovery codes, or session material. For partner automation, use only the authentication method, environment, scope, storage, rotation, and revocation process in the user-supplied approved partner contract. Public help pages do not establish a general API credential.

## Instructions

1. Define the workload, environment, business deadline, maximum staleness, owner, and acceptable partial-progress behavior.
2. Use Read, Glob, and Grep to inspect the approved contract, workload model, adapter, telemetry fields, and synthetic tests.
3. Extract only documented limits, concurrency rules, response signals, retry guidance, and support escalation paths into an evidence table.
4. Design bounded queues, idempotent work units, jittered backoff only where the contract permits it, circuit breaking, and a manual pause control.
5. Use synthetic responses to test saturation, unknown limit signals, prolonged outage, cancellation, replay, and recovery without contacting Linktree.
6. Use Write or Edit to record configuration and tests; keep numeric production settings outside this public skill and tied to contract revision.
7. Use WebFetch only for the public developer boundary, Linktree status, or approved partner documentation.

## Approval Boundaries

Never encode a remembered or third-party quota as Linktree fact, probe production to discover limits, or retry an unauthorized operation.

## Output

Return workload, contract revision, documented limits, unknowns, queue bounds, retry authority, idempotency key source, failure tests, pause control, and approval state.

## Error Handling

| Condition | Response |
|---|---|
| No numeric limit is documented | Keep it unknown, use conservative bounded behavior, and obtain vendor confirmation. |
| Work cannot be made idempotent | Require serialization or an operator checkpoint before retries. |
| Limit behavior changes | Pause the worker, reconcile partial work, and revalidate the contract. |

## Example

The example is a synthetic, redacted operator receipt, not proof of Linktree access or a live account change.

```text
workload=profile-sync; limits=contract-private; queue=bounded; retries=documented-only; idempotency=change-id; saturation-test=pass; production-setting=approval-gated
```

## Resources

- [Official documentation map](references/official-docs.md) — dated evidence and limits for this workflow.

Read the map before acting. Recheck current account and partner-specific evidence for plan-dependent or private behavior.

## Next Steps

Revalidate source dates, owner approval, target profile, and rollback readiness before repeating the workflow in another account, Workspace, campaign, region, plan, or integration.
