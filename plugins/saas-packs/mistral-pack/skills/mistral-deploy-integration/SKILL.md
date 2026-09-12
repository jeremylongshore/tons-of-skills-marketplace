---
name: mistral-deploy-integration
description: >-
  Deploy a Mistral-backed service with secret isolation, bounded concurrency, health semantics, canary evidence, and rollback. Use when preparing runtime delivery. Trigger with "deploy a Mistral app", "configure Mistral production", or "canary a Mistral service".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<platform> <environment> <release-sha>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Deployment Integration

## Overview

Prepare a platform-neutral runtime boundary. Separate application health from provider readiness, keep credentials server-side, and make overload, provider failure, and rollback predictable.

## Prerequisites

- An immutable artifact, lockfile, release SHA, and deployment owner.
- An environment-scoped secret, egress policy, and tenant authorization design.
- Capacity, timeout, queue, spend, observability, canary, and rollback policies.

## Current Contract

The API is `https://api.mistral.ai` with Bearer auth. Model and workspace capacity are runtime dependencies; application startup should not require a paid inference call.

## Authentication

Inject the key into a trusted server and restrict egress. Never pass it to browser, build output, health response, or an edge runtime without protected secret semantics.

## Instructions

1. Map build, runtime, secret, egress, scaling, queue, and shutdown behavior.
2. Package the pinned adapter and validate config without contacting Mistral during build.
3. Set end-to-end deadlines, bounded concurrency, cancellation, and overload behavior.
4. Implement local liveness and a separate dependency/readiness signal without provider data.
5. Deploy to staging, run offline checks, then request approval for a synthetic canary.
6. Compare evidence, promote within a fixed traffic bound, and prove rollback plus queue reconciliation.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Deployment, secret mutation, traffic shift, scaling, canary spend, and rollback execution each require explicit scope and approval.

## Error Handling

- Inference in liveness amplifies outage and spend.
- Autoscaling without a shared limiter exceeds workspace capacity.
- Rollback without queue/state reconciliation can duplicate work.

## Output

Return artifact/release identity, topology, secret/egress boundary, limits, health semantics, canary, traffic state, and rollback receipt.

## Examples

- Build once and inject production secrets only at runtime.
- Keep liveness green during provider degradation while product behavior fails safely.

## Validation

Inspect artifact for secrets and test denied egress, overload, shutdown, outage, canary abort, rollback, and queue convergence.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
