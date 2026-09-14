---
name: runway-reference-architecture
description: >-
  Design a Runway integration that separates admission, provider execution, reconciliation, media storage, and governance. Use when reviewing system boundaries. Trigger with: "Runway architecture", "design Runway service", "Runway production topology".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[system-and-scale]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - architecture
  - governance
  - reliability
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Production Control-Plane Architecture

## Overview

The stable architecture centers on an internal operation record rather than a provider request. It isolates credentials, models asynchronous task state, applies cost and concurrency admission, preserves media in owned storage, and makes provider/API drift reviewable.

## Prerequisites

- Workload, SLO, data-classification, and budget requirements
- Current Runway API, model, limits, pricing, and output contracts
- Owners for security, media rights, moderation, operations, and finance

## Instructions

### Step 1: Define trust zones

Place clients outside the provider credential boundary. Put the admission API, task worker, reconciler, secret access, and provider egress in a server zone; isolate raw media and final assets by classification.

### Step 2: Make operation state authoritative

Persist operation ID, actor, approval, request fingerprint, model or router policy, provider task ID, state timeline, budget, and output object. Enforce legal state transitions and unique provider IDs.

### Step 3: Separate control and data planes

The control plane validates, queues, retrieves, cancels, and emits internal events. The data plane stages input, performs ephemeral upload when needed, validates output, and copies assets to owned storage.

### Step 4: Apply governance at admission

Check rights, moderation policy, tenant quotas, credit ceiling, model allowlist, duration and ratio schema, and retention before creating billable work.

### Step 5: Reconcile asynchronously

Workers honor per-model concurrency; reconcilers observe `THROTTLED` and terminal states with bounded polling. Internal consumers receive idempotent events derived from persisted transitions.

### Step 6: Design for change

Pin SDK and API contracts, fingerprint official docs, use model-aware fixtures, canary upgrades, and support both direct model and approved router policies without scattering identifiers.

## Authentication

Only server-side workers and restricted operational readers access the organization-scoped key. Signed media URLs are short-lived capabilities; application clients receive controlled internal asset URLs instead.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Component, trust-zone, data-flow, and state-transition design
- Capacity, budget, security, retention, and failure policies
- Migration, canary, rollback, and operational evidence plan

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

A multi-tenant product stores one internal operation per request, admits against tenant and organization budgets, submits through a per-model worker, reconciles provider state, signs an internal event, and serves the copied asset through its own authorization layer.

## Error Handling

| Failure | Response |
| --- | --- |
| Architecture has no durable provider task ID | Add transactional task identity before accepting restart or retry safety. |
| Browser calls Runway directly | Move the credential and provider call behind a protected server boundary. |
| Provider URL is the product asset URL | Introduce owned storage and an internal access-control layer. |

## Validation

Walk happy path, client disconnect, worker crash, throttling, safety failure, provider outage, output-copy failure, cancellation, key rotation, SDK upgrade, and rollback. Every scenario must preserve operation identity and bounded side effects.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
