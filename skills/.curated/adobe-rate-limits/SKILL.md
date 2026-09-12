---
name: adobe-rate-limits
description: >-
  Implement service-specific Adobe admission control, Retry-After handling, bounded retries, and spend-aware queues. Use when scaling workloads or handling 429 responses. Trigger with "Adobe rate limit", "Adobe 429", or "Adobe backoff".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<service> <workload> <recovery-objective>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, throttling]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Throttling and Backpressure

## Overview

Implement service-specific Adobe admission control, Retry-After handling, bounded retries, and spend-aware queues.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Adobe limits differ by service, operation, entitlement, and contract. Recheck first-party limits at execution. A valid Retry-After response is authoritative; absence requires conservative capped exponential backoff with jitter, not a remembered universal rate. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Partition control by approved credential, organization, service, operation, and tenant without exposing tokens or multiplying credentials to evade policy.

## Instructions

1. Inventory traffic, operations, concurrency, queues, retry chains, job durations, transactions, and downstream acknowledgements.
2. Read current service limits and capture observed 429 headers and error bodies from sanitized evidence.
3. Set conservative token buckets, concurrency, queue size, and spend ceilings below verified constraints.
4. Retry only classified transient, idempotent work; honor valid server delay and cap attempts plus elapsed time.
5. Quarantine ambiguous writes/jobs and propagate backpressure rather than recursively retrying.
6. Load-test with synthetic data, publish the safe envelope, and assign an emergency reduction switch.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Workload, budget, and sandbox owners approve load tests and capacity changes. Do not add organizations, users, keys, or projects to circumvent limits.

## Error Handling

- Fixed pack-wide RPM tables are forbidden.
- Do not retry 401, 403, content-policy, validation, or terminal job failures blindly.
- Stop before the retry budget becomes a spend amplifier.

## Output

Return cited current constraints, observed headers, control settings, retry matrix, queue policy, load curve, spend guard, and rollback. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Recover from a 429 with Retry-After.
- Demonstrate queue shedding when the elapsed retry budget expires.

## Validation

Exercise and record expected and observed results for:

- burst
- missing delay
- valid delay
- ambiguous job
- queue saturation
- vendor outage

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
