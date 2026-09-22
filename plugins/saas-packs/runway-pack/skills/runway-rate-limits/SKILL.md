---
name: runway-rate-limits
description: >-
  Analyze and control Runway generation concurrency, rolling daily quota, spend limits, and queued tasks without inventing an RPM cap. Use when production traffic is throttled or scaling. Trigger with: "Runway rate limits", "Runway THROTTLED tasks", "Runway concurrency".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-and-tier]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - concurrency
  - quotas
  - backpressure
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Concurrency and Quota Control

## Overview

Runway generation capacity is governed by usage-tier limits, not a universal requests-per-minute number. The application must distinguish accepted-but-queued `THROTTLED` tasks from create requests rejected with `429`, then apply local admission control to protect deadlines and budget.

## Prerequisites

- Current organization tier and per-model limit evidence
- Task creation, state, latency, daily-generation, and credit metrics
- A durable queue with priority, deadline, and cancellation policy

## Instructions

### Step 1: Read live authority

Review the organization Usage page and current tiers documentation. Record per-model concurrency, rolling 24-hour generation cap, 30-day spend cap, and any approved enterprise exception.

### Step 2: Measure by model

Count create attempts, accepted task IDs, `THROTTLED` depth and age, running tasks, terminal states, queue wait, execution time, and rolling daily use per model and organization.

### Step 3: Set local admission control

Use per-model semaphores below the provider concurrency boundary, a global budget guard, priority queues, and customer deadlines. Do not add arbitrary RPM sleeps that hide the actual capacity model.

### Step 4: Treat `THROTTLED` correctly

Keep the existing task ID and continue bounded observation. Do not create a replacement task; Runway has already stored and queued it.

### Step 5: Handle `429` correctly

Determine whether the rolling daily generation quota or another documented limit was exceeded. Stop new admission, calculate when capacity returns, and retry only within the documented transient policy and operation deadline.

### Step 6: Tune with evidence

Adjust worker concurrency from queue age, terminal throughput, failure rate, and spend—not request count alone. Request an official exception when the documented tiers cannot meet the service objective.

## Authentication

Usage and task reads use the same server-side organization credential as generation. Limit telemetry should identify organization and model without exporting the API secret, prompt contents, or temporary media URLs.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Authoritative tier and per-model capacity snapshot
- Admission-control, queue, deadline, and cancellation policy
- Before/after queue, throughput, quota, failure, and spend evidence

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

An organization can run five concurrent jobs for a model. The service admits four, keeps one slot for urgent work, retains additional jobs in its own priority queue, and never duplicates a provider task observed as `THROTTLED`.

## Error Handling

| Failure | Response |
| --- | --- |
| Engineer assumes a fixed RPM limit | Replace the assumption with current per-model concurrency, rolling daily quota, and spend evidence. |
| `THROTTLED` tasks are resubmitted | Stop the duplicate path, reconcile task IDs, and account for unintended credits. |
| Daily quota returns `429` | Pause admission until rolling capacity is available or obtain an approved tier exception. |

## Validation

Load-test the local queue with a fake provider, prove per-model isolation and no duplicate resubmission, simulate `THROTTLED` and rolling-quota `429`, and compare configured controls with current organization limits.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
