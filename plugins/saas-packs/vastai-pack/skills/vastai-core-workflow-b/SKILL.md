---
name: vastai-core-workflow-b
description: >-
  Build and roll out a Vast.ai Serverless endpoint with measured autoscaling, a canary template, and a zero-downtime worker update. Use when production inference capacity or model bytes change. Trigger with: "deploy Vast.ai Serverless", "tune a Vast.ai worker group", "roll a model without downtime".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[endpoint-slo-template-and-load-profile]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - serverless
  - autoscaling
  - rollout
compatibility: 'Requires Vast.ai Serverless access, a tested template, a scoped API key, representative load, and endpoint observability.'
---

# Vast.ai Serverless Endpoint Rollout

## Overview

Replace ad hoc multi-instance orchestration with the provider Serverless control plane. Prove a template independently, establish worker and queue bounds from load evidence, then let the workergroup perform a graceful rolling update.

## Prerequisites

- Latency, error-rate, queue-time, concurrency, and cost objectives
- Immutable model/template candidate and a separate canary endpoint
- Initial, minimum, maximum, cold-worker, and inactivity policy

## Instructions

### Step 1: Prove the candidate template

Launch the new model or environment on a non-production endpoint and verify load, readiness, response schema, and representative outputs.

### Step 2: Define scaling bounds

Set `min_load`, `min_workers`, `max_workers`, `cold_workers`, `inactivity_timeout`, `target_queue_time`, and `max_queue_time` from explicit SLO and budget assumptions.

### Step 3: Exercise convergence

During initial rollout, drive representative load up to roughly twice expected capacity and back down three times so the engine can learn GPU cost/performance.

### Step 4: Establish the pre-update baseline

Record endpoint latency, queue time, error rate, active/inactive workers, model identity, and spend before changing production.

### Step 5: Trigger the rolling update

Save the new template, update the workergroup reference, and monitor inactive workers updating first while active workers drain in-flight requests.

### Step 6: Accept or roll back

Verify every worker is on the candidate and compare SLOs. If it fails, point the workergroup back to the last verified template and observe the reverse rollout.

## Authentication

Use a scoped key with the documented `misc` Serverless permissions and no billing-write authority. Keep model registry credentials in approved environment variables, separate from the Vast.ai key.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Canary and production template identities
- Scaling policy plus load-test and rollout timeline
- SLO comparison, worker convergence, and rollback decision

Return endpoint/workergroup IDs, old and new template identities, scaling bounds, load profile, SLO delta, and final rollout state.

## Examples

A vLLM endpoint validates a new model on a canary, applies bounded queue targets, then updates its workergroup; active requests drain while new requests move to updated workers, with the old template retained for rollback.

## Error Handling

| Failure | Response |
| --- | --- |
| Canary cannot load the model | Do not update production; fix image, model, or environment configuration. |
| Queue time breaches during rollout | Pause acceptance, increase safe capacity within budget, or roll back the template. |
| Workers do not converge | Inspect workergroup logs and configuration; do not claim zero-downtime completion. |
| New output contract regresses | Roll back to the last verified template and preserve comparison evidence. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Serverless architecture](https://docs.vast.ai/guides/serverless/architecture)
- [Managing scale](https://docs.vast.ai/guides/serverless/managing-scale)
- [Zero-downtime worker update](https://docs.vast.ai/guides/serverless/zero-downtime-worker-update)
