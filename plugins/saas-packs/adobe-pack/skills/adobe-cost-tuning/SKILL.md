---
name: adobe-cost-tuning
description: >-
  Reduce Adobe integration spend using contract, invoice, usage, queue, storage, and retry evidence instead of invented per-call prices. Use when the task requires adobe workload cost and waste review. Trigger with "reduce Adobe cost", "Adobe spend review", or "PDF transaction budget".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workload> <billing-window> <budget-objective>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, cost]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Workload Cost and Waste Review

## Overview

Reduce Adobe integration spend using contract, invoice, usage, queue, storage, and retry evidence instead of invented per-call prices. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Firefly entitlements and generative usage, PDF Services document transactions, and application compute/storage/egress are distinct cost classes. Pricing and plan limits are mutable; use the account contract, live usage surface, and dated first-party pages. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Collect aggregated aliases, operation classes, outcomes, retries, bytes, and durations. Prompts, assets, documents, users, tokens, and signed URLs are not cost telemetry.

## Instructions

1. Define billing window, account/contract owner, services, operations, workload units, and non-negotiable quality objectives.
2. Reconcile invoice/contract and service usage with submitted jobs, terminal outcomes, retries, duplicates, and storage/compute costs.
3. Find duplicate submissions, failed transactions, oversized inputs, stale outputs, excessive polling, and unused environments.
4. Model idempotency, caching-by-approved-hash, batching where documented, input sizing, queue admission, and retention changes.
5. Canary one control and measure quality, latency, 429s, usage units, and downstream impact.
6. Adopt only verified savings with budget alerts, anomaly ownership, rollback, and a dated pricing assumption register.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Budget and workload owners approve spend controls; data owner approves hashing/caching/retention; product owner approves quality or freshness changes.

## Error Handling

- Do not publish fixed prices or universal free-tier assumptions in workflow logic.
- Do not cache policy-sensitive prompts or customer outputs without approval.
- Do not lower cost by bypassing entitlements or multiplying credentials.

## Output

Return reconciled baseline, waste map, dated assumptions, control options, canary evidence, verified savings range, alerts, and rollback. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Detect duplicate async submissions from one idempotency key.
- Reconcile a failed PDF job against actual transaction evidence.

## Validation

Exercise and record expected and observed results for:

- duplicate
- failed job
- retry storm
- stale asset
- pricing drift
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
