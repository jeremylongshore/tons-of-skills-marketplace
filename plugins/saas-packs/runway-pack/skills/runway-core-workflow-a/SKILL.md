---
name: runway-core-workflow-a
description: >-
  Design a Runway text-to-video job from the current model-discriminated API contract and preserve its asynchronous evidence. Use when implementing direct model generation. Trigger with: "Runway text to video", "choose Runway video model", "submit Runway generation".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[prompt-and-output-contract]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - text-to-video
  - models
  - workflow
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Model-Grounded Text-to-Video Workflow

## Overview

Treat model choice as an API-schema decision, not a marketing label. Runway request bodies are discriminated by `model`; valid ratios, durations, prompt limits, optional controls, price, and even required fields can differ between models.

## Prerequisites

- A product requirement covering quality, latency, duration, ratio, and budget
- Current Runway models, API reference, and pricing pages
- Durable task tracking and owned output storage

## Instructions

### Step 1: Define the output contract

Record modality, intended use, dimensions, duration, audio need, quality threshold, deadline, moderation policy, and maximum credits. Separate hard constraints from preferences.

### Step 2: Choose direct model or router

Use a direct model when reproducibility requires a reviewed identifier. Use a saved Model Router when policy should optimize cost, latency, or quality within approved allow and deny lists; use its dry run before billable work.

### Step 3: Read the exact variant

Inspect the current `text_to_video` schema for the chosen model. For example, `gen4.5` currently supports text input, but this skill does not transplant its ratio or duration fields to another model.

### Step 4: Freeze and submit

Persist the model or router config, normalized request, documentation fingerprint, and approval before create. Store the returned task ID immediately.

### Step 5: Observe without duplication

Use the SDK wait helper or bounded polling. Treat `THROTTLED` as queued and distinguish queue time from execution time. Recover from client interruption by retrieving the saved task.

### Step 6: Validate and preserve

On success, download output, verify media type, duration, dimensions, and checksum, then run the product quality review. On failure, apply the HTTP or task-failure policy rather than silently changing models.

## Authentication

All model, router, task, and usage calls use the server-side Runway API secret. Direct HTTP also sends the reviewed `X-Runway-Version`; temporary output URLs remain confidential until copied to controlled storage.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Reviewed model-or-router decision with current schema and price evidence
- Durable request fingerprint, task timeline, and terminal-state receipt
- Owned output plus technical and product-quality results

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A product requires portrait video under a fixed ceiling. The team reviews two eligible models, dry-runs an approved router, records the selected policy, submits one task, and accepts the asset only after terminal success and media validation.

## Error Handling

| Failure | Response |
| --- | --- |
| No model satisfies hard constraints | Return the incompatibility instead of inventing an identifier or unsupported field. |
| Request receives `400` | Compare every field with the exact selected model variant; do not reuse another model's ratio or duration. |
| Client disconnects after create | Resume from the stored task ID and never infer that no task was created. |

## Validation

Use contract tests for every approved model or router configuration, reject unknown identifiers and extra fields, simulate disconnect recovery, and verify technical plus human quality gates on a controlled canary.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
