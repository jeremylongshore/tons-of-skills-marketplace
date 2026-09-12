---
name: adobe-load-scale
description: >-
  Derive a safe Adobe workload envelope from synthetic load, queue/backpressure behavior, current service constraints, spend, and output correctness. Use when the task requires adobe capacity and load envelope. Trigger with "load test Adobe", "scale Firefly jobs", or "Adobe capacity plan".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <target-volume> <sandbox>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, capacity]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Capacity and Load Envelope

## Overview

Derive a safe Adobe workload envelope from synthetic load, queue/backpressure behavior, current service constraints, spend, and output correctness. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Capacity is service-, operation-, entitlement-, and contract-specific. Measure arrival rate, queue age, concurrency, vendor time, 429/5xx, retries, terminal completion, storage transfer, cost units, and correctness. Do not publish guessed universal throughput. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use dedicated sandbox credentials, synthetic non-sensitive inputs, environment assertions, and a hard kill switch. Credential sharding to evade limits is forbidden.

## Instructions

1. Define workload shape, target volume, objectives, data/output checks, budget, ramp, abort thresholds, and cleanup.
2. Read current product constraints and measure a single-job baseline across all lifecycle stages.
3. Build an open/closed load model that drives the queue, not direct uncontrolled vendor floods.
4. Ramp one dimension at a time while recording concurrency, latency, 429s, failures, completions, spend, and artifacts.
5. Exercise backpressure, cancellation, unknown completion, vendor degradation, worker restart, and DLQ recovery.
6. Publish the conservative envelope, autoscaling/queue controls, emergency stop, capacity owner, and retest date.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Sandbox, vendor-account, data, budget, and operations owners approve tests. Bulk generation/transactions, cancellation, and artifact deletion require explicit execution approval.

## Error Handling

- Never load-test production customer workflows.
- Abort on unexpected spend, content leakage, growing unknown jobs, or error threshold.
- Do not use identities or projects as rate-limit shards.

## Output

Return assumptions, current constraints, load model, raw/result metrics, correctness evidence, safe envelope, aborts, cleanup, and retest owner. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Show queue backpressure before the service is saturated.
- Recover a worker restart without duplicate submission.

## Validation

Exercise and record expected and observed results for:

- ramp
- 429
- vendor 5xx
- unknown completion
- worker restart
- kill switch

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
