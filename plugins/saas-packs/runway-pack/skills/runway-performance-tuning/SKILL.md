---
name: runway-performance-tuning
description: >-
  Analyze and improve Runway submission, queue, generation, download, and storage latency without unsafe polling or duplicate tasks. Use when an integration is slow. Trigger with: "speed up Runway", "Runway latency", "tune Runway performance".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-and-slo]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - performance
  - latency
  - observability
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Queue-to-Asset Performance Tuning

## Overview

End-to-end latency is a sequence of distinct phases: local admission, upload, provider queue, generation, output download, and owned storage. Optimize the measured bottleneck while preserving model quality, moderation, quota, and cost constraints.

## Prerequisites

- An SLO with percentile, modality, model, duration, and quality dimensions
- Traceable operation and task state timestamps
- Current model, input, tier, and pricing evidence

## Instructions

### Step 1: Instrument the phases

Capture operation accepted, local queue start/end, upload start/end, provider create, each state transition, terminal state, download, validation, and storage completion. Use redacted IDs to join traces.

### Step 2: Separate queue from generation

Report `THROTTLED` and `PENDING` residence independently from `RUNNING`. A concurrency bottleneck should not be misdiagnosed as model execution slowness.

### Step 3: Reduce input overhead

Prefer already hosted HTTPS media or reusable ephemeral uploads when appropriate. Avoid large data URIs, validate formats before submission, and review silent auto-crop work.

### Step 4: Tune observation

Use SDK wait helpers or polling at five seconds or more with jitter and backoff. Replace per-request busy loops with a bounded worker scheduler; more polls do not make generation finish sooner.

### Step 5: Evaluate routing and models

Compare only eligible models or approved router policies on latency, quality, and credits. Use router dry runs for selection evidence and controlled canaries for realized performance.

### Step 6: Protect tail latency

Apply deadlines, queue priorities, cancellation policy, circuit breaking for transient outages, and owned-output download retries. Never create duplicate generations as a latency hedge without explicit cost approval.

## Authentication

Performance traces use server-side Runway access and must redact keys, prompt/media content, and signed URLs. Organization usage access should be restricted to operators who need capacity and cost evidence.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Phase-by-phase latency profile with percentiles and task states
- Ranked bottleneck hypotheses and controlled changes
- Before/after SLO, quality, failure, and credit-impact receipt

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

Tracing shows upload takes 18 seconds while provider execution is stable. The team replaces repeated data URIs with one reusable ephemeral upload, validates the 24-hour expiry path, and improves end-to-end latency without increasing concurrency.

## Error Handling

| Failure | Response |
| --- | --- |
| No state timestamps exist | Add instrumentation before changing models or worker counts. |
| Polling traffic rises but latency does not improve | Restore a five-second-or-longer jittered schedule and focus on queue or execution capacity. |
| Faster model misses quality policy | Reject the optimization or route it only to an approved lower-risk use case. |

## Validation

Replay representative synthetic workloads, compare percentiles per phase and model, verify polling bounds and no duplicate tasks, and include quality, failure, moderation, and credits beside latency.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
