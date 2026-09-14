---
name: runway-cost-tuning
description: >-
  Reduce Runway credit waste through current pricing, duplicate prevention, model policy, and measured usage without publishing stale price tables. Use when reviewing spend. Trigger with: "optimize Runway cost", "Runway credit usage", "reduce Runway spend".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[organization-and-period]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - cost
  - credits
  - governance
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Evidence-Based Runway Credit Optimization

## Overview

Runway pricing changes independently of models and code. Cost tuning begins from the current pricing page and authorized usage data, then removes accidental duplicates, rejected work, oversized outputs, unnecessary variants, and poor routing without lowering an approved quality or safety bar.

## Prerequisites

- Current first-party pricing and organization usage evidence
- Operation, task, model, duration, output-count, state, and credit records
- A product-owned quality policy and finance-approved budget

## Instructions

### Step 1: Freeze the authority

Record retrieval time and fingerprint for the current pricing page, billing model, organization tier, and contract exceptions. Do not copy a historical credit table into a long-lived calculator.

### Step 2: Reconcile demand to tasks

Join internal operation IDs to provider task IDs and usage. Separate successful, failed, moderated, cancelled, duplicate, abandoned, and stored outputs; account for safety failures that still consume credits.

### Step 3: Find duplicate generation

Identify timeouts, client retries, queue resubmission, race conditions, and lost task IDs. Fix persistence and recovery before trading away output quality.

### Step 4: Compare eligible policies

For each workload, compare approved direct models or Model Router configurations on current estimated credits, latency, and quality. Use router `dryRun` where supported because it returns selection and estimated cost without generating an asset.

### Step 5: Control request shape

Review duration, resolution, output count, reference count, recipe choice, and retries against the product requirement. Reduce only fields that do not violate the approved result.

### Step 6: Roll out with guardrails

Set per-operation and rolling budgets, alerts, concurrency locks, and automatic stop conditions. Compare credits per accepted asset and quality escape rate before expanding.

## Authentication

Use minimally scoped server-side API and authorized organization usage access. Finance exports should contain aggregate identifiers and credits, not API keys, customer media, prompts, or signed output URLs.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Pricing and usage authority snapshot
- Measured credit drivers, duplicate waste, and policy scenarios
- Approved change with before/after credits, quality, latency, and rollback evidence

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

The review finds workers resubmit `THROTTLED` tasks. Persisting task IDs and waiting on the existing jobs removes duplicate spend; a router dry run then identifies a lower-cost eligible model for draft previews without changing final-render policy.

## Error Handling

| Failure | Response |
| --- | --- |
| No authoritative usage data | Report hypotheses and measurement gaps without asserting savings. |
| Price page changed since calculator snapshot | Refresh the source and rerun scenarios before approval. |
| Cheaper option violates quality or safety policy | Keep the current policy or obtain an explicit product and risk decision. |

## Validation

Reconcile sampled usage to task receipts, prove duplicate paths are closed, compare approved variants with blind quality review, and monitor credits per accepted asset through a reversible rollout.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
