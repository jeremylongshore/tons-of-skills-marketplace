---
name: runway-upgrade-migration
description: >-
  Migrate Runway SDK, API, model, or request contracts through inventory, compatibility fixtures, canaries, and reversible rollout. Use when removing retired behavior. Trigger with: "upgrade Runway SDK", "migrate gen3a_turbo", "Runway API migration".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-to-target]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - migration
  - sdk
  - models
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway SDK and Model Contract Migration

## Overview

A Runway upgrade can change client types, model availability, allowed fields, output behavior, cost, latency, and quality at once. Preserve operation and task compatibility while migrating from retired identifiers through explicit per-model contracts and controlled comparisons.

## Prerequisites

- Current dependency lock, model/request inventory, and task-state schema
- Target SDK changelog, API reference, models, and pricing evidence
- Representative fixtures, canary budget, and rollback owner

## Instructions

### Step 1: Inventory the current surface

Use Read and Grep to find SDK imports, raw endpoints, version headers, model identifiers, ratio and duration literals, wait helpers, error classes, task persistence, output handling, and docs.

### Step 2: Define the target contract

Resolve the target SDK and review its changelog. For model changes, inspect exact input/output variants; `gen3a_turbo` is retired, while `gen4.5` and `gen4_turbo` have different input capabilities and cannot be substituted mechanically.

### Step 3: Build compatibility fixtures

Capture accepted request shapes, every task state, HTTP and task failures, cancellation, timeout, and output-copy behavior. Add explicit rejection tests for retired identifiers and cross-model fields.

### Step 4: Separate code and policy rollout

Introduce a client adapter that can read existing task IDs, then deploy target support disabled. Change model or router policy separately so dependency regressions and output-quality changes remain distinguishable.

### Step 5: Canary both paths

Use safe representative prompts/media and fixed ceilings. Compare schema acceptance, queue/run latency, terminal rate, credits, dimensions, duration, moderation, and blinded product quality.

### Step 6: Migrate and retire

Ramp by tenant or workload, keep retrieval compatibility for old tasks, stop new old-contract admission, then remove deprecated code only after the reconciliation horizon. Retain a rollback that does not recreate tasks.

## Authentication

Migration tests use protected server-side credentials and redacted fixtures. Package registry lookup and documentation are public; live generations require explicit approval and a bounded credit budget.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Current-to-target dependency, model, request, and state map
- Compatibility suite and canary comparison
- Staged rollout, old-task drain, deprecation, and rollback receipt

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A service replaces retired `gen3a_turbo`. It first deploys an adapter able to retrieve existing tasks, adds separate `gen4.5` text and `gen4_turbo` image-input schemas, compares approved canaries, then stops old creates while draining saved task IDs.

## Error Handling

| Failure | Response |
| --- | --- |
| New SDK cannot retrieve old task IDs | Stop rollout and restore compatibility before changing create policy. |
| Model swap copies old ratio or duration | Reject it and rebuild from the target model's exact discriminated schema. |
| Canary cost or quality exceeds policy | Keep the old supported path or revise the target decision with owners. |

## Validation

Run old and target contract suites, reject retired identifiers, resume tasks across mixed worker versions, compare controlled canaries, test rollback after create, and verify docs and lockfiles match the deployed path.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
