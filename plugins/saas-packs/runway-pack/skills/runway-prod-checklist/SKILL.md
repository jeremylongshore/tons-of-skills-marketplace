---
name: runway-prod-checklist
description: >-
  Approve or reject a Runway launch using contract, billing, capacity, moderation, storage, observability, and rollback evidence. Use when preparing go-live. Trigger with: "Runway production checklist", "launch Runway integration", "Runway readiness review".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-and-release]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - runway
  - production
  - readiness
  - go-live
compatibility: 'Requires server-side Runway Dev access, current first-party documentation, an approved credit budget, and controlled media storage.'
---

# Runway Production Readiness Gate

## Overview

Go-live is an evidence gate, not a list of intentions. The release must prove model-aware validation, durable asynchronous state, credit and concurrency controls, moderation handling, owned output storage, secret rotation, observability, and a rollback that does not orphan provider tasks.

## Prerequisites

- Release SHA, environment, owner, SLO, budget, and rollback candidate
- Current first-party API, models, limits, pricing, and go-live guidance
- Passing contract, security, load, failure, and canary evidence

## Instructions

### Step 1: Verify contract and supply chain

Pin the reviewed SDK, API version, model or router schemas, and lockfile. Reject retired identifiers such as `gen3a_turbo` and any request shape copied across model variants.

### Step 2: Verify identity and secrets

Confirm organization, roles, key consumers, secret-manager delivery, redaction, rotation owner, and explicit old-key disable procedure. Prove the browser has no provider credential.

### Step 3: Verify task reliability

Prove operation and task ID persistence, restart recovery, all six states, bounded polling, transient retry classes, explicit cancellation, and no duplicate create after ambiguity.

### Step 4: Verify capacity and billing

Record tier, per-model concurrency, rolling daily quota, spend cap, credit balance, autobilling alerts, canary ceiling, and stop conditions. Treat `THROTTLED` as queued work.

### Step 5: Verify content and storage

Confirm rights, moderation policy, supported input, crop review, failed-safety handling, output validation, owned private storage, URL expiry, retention, and deletion.

### Step 6: Run and decide

Execute one approved canary, trace it through terminal state and storage, test alerts, then rehearse rollback: stop admission, drain or cancel compatible tasks, and preserve reconciliation.

## Authentication

Production keys live only in the secret manager and are scoped operationally through server access controls. The readiness evidence contains aliases and hashes, never usable bearer values or signed media URLs.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, lockfiles, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, cancel, delete, retry, deploy, rotate, revoke, publish, or otherwise mutate production Runway resources without explicit operator approval.

## Output

- Pass/fail matrix with owner and evidence link per control
- Canary task and owned-output receipt under an explicit ceiling
- Launch or rejection decision with drain, cancellation, and rollback state

Return the environment, organization alias, operation and task identifiers, API and SDK versions, model or router policy, source-contract fingerprint, task-state evidence, credit boundary, output disposition, unresolved risk, rollback state, and final decision without exposing API secrets, prompt or media contents, or temporary signed URLs.

## Examples

The canary succeeds, but rollback testing shows the old worker cannot read tasks created by the new schema. The reviewer rejects launch until dual-read compatibility or a safe drain plan is proven.

## Error Handling

| Failure | Response |
| --- | --- |
| Credit alerts or stop conditions are untested | Reject launch; unexpected depletion can halt the service. |
| Rollback recreates nonterminal tasks | Reject launch and repair task persistence and compatibility. |
| Output remains only at Runway URL | Reject launch until owned storage and access control are verified. |

## Validation

Require exact-release evidence for every checklist row, run happy and failure canaries, inspect logs and artifacts for secrets, simulate throttling and outage, and sign the decision with unresolved risk explicitly stated.

## Resources

- [First-party source notes](references/official-docs.md)
- [Runway agent context](https://docs.dev.runwayml.com/ai-context.md)
- [API reference](https://docs.dev.runwayml.com/api.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
