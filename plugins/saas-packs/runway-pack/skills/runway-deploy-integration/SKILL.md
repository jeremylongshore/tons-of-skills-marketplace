---
name: runway-deploy-integration
description: >-
  Deploy a restart-safe Runway generation service with durable tasks, bounded polling, cancellation, and output ownership. Use when moving an integration to production. Trigger with: "deploy Runway worker", "productionize Runway API", "Runway job architecture".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - deployment
  - workers
  - reliability
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Deploy an Asynchronous Runway Worker

## Overview

Runway generation does not fit a synchronous request-response handler. Production deployment should accept intent quickly, persist it, execute through bounded workers, reconcile provider task state after restarts, and move successful assets into owned storage.

## Prerequisites

- A deployment environment with queues, durable database, and object storage
- Server-side secrets, egress policy, and reviewed Runway contract
- Capacity, credit, moderation, retention, and rollback owners

## Instructions

### Step 1: Split API from worker

Make the public endpoint validate intent, assign an operation ID, persist approval and request fingerprint, enqueue work, and return an internal status handle. Do not hold an HTTP request open for generation.

### Step 2: Persist provider identity

The worker records the provider task ID immediately after create. Retries and restarts must retrieve that task before any new create decision.

### Step 3: Control capacity

Apply per-model concurrency, deadline, priority, and credit guards. Treat provider `THROTTLED` tasks as already accepted; never resubmit them just because they have not started.

### Step 4: Reconcile state

Run a bounded scheduler that retrieves nonterminal tasks, adds jitter/backoff, handles all terminal states, and can resume after deployment. A local shutdown or timeout does not cancel provider work.

### Step 5: Own successful assets

Download successful output promptly to controlled object storage, verify it, set access and retention, and discard signed provider URLs from normal application records.

### Step 6: Roll out and roll back

Deploy a no-create read probe, one approved canary, then staged traffic. Rollback stops new admission while the old compatible worker drains or cancels existing tasks according to policy.

## Authentication

Workers receive `RUNWAYML_API_SECRET` from the deployment secret manager and use the reviewed API version. Public handlers and browser bundles never receive the provider key or signed asset URLs.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- API, queue, worker, state-store, and output-store deployment map
- Capacity, retry, timeout, cancellation, drain, and rollback controls
- Canary and staged-rollout receipt with terminal-state and storage evidence

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A deployment is rolled back after elevated `503` responses. New admission stops, saved task IDs remain in the database, the previous worker version resumes retrieval, and successful assets are stored without recreating tasks.

## Error Handling

| Failure | Response |
| --- | --- |
| Worker crashes after create | Recover the saved provider task ID and retrieve; do not submit again. |
| Rollback strands nonterminal tasks | Run the compatible reconciliation worker or explicitly cancel under the documented policy. |
| Output copy fails | Keep the task and temporary URL in restricted retry state and retry download before its expiry window. |

## Validation

Kill workers at each lifecycle boundary, prove state recovery and no duplicate create, simulate `THROTTLED` and transient outages, test drain/cancel rollback, and verify outputs survive provider URL expiry.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
