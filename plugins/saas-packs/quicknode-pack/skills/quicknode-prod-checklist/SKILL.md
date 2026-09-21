---
name: quicknode-prod-checklist
description: 'Run a fail-closed production-readiness review for a QuickNode endpoint and its SDK, transaction, Stream, or Webhook consumers. Use when preparing a launch, major traffic increase, or provider migration. Trigger with: "QuickNode production checklist", "audit QuickNode readiness", "approve a QuickNode launch".'
allowed-tools: Read, Grep, Bash(qn:*)
version: 2.0.0
argument-hint: '[service-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - quicknode
  - production
  - readiness
  - governance
compatibility: 'Readiness evidence varies by chain, product, plan, and application write authority'
---

# QuickNode Production Readiness

## Overview

Review the actual runtime and QuickNode control plane against declared identity, security, capacity, data, correctness, observability, and recovery contracts. Return a decision with blockers, not a generic checklist score.

## Prerequisites

- Release commit and deployment inventory
- Chain/network, data-retention, and product requirements
- SLOs, budget, incident owner, and rollback runbook

## Instructions

### Step 1: Verify identity and secrets

Use Read and Grep to confirm environment-specific secret references, expected chain IDs, no literal endpoint tokens, separate Admin API keys, and no funded signer in CI or logs.

### Step 2: Verify provider controls

Use Bash(qn:*) for read-only inspection of endpoint status, tokens, filters, method/IP limits, tags, usage, metrics, and active or paused event products. Record unavailable plan-gated evidence.

### Step 3: Verify data and write semantics

Confirm API family, method entitlement, archive/pruning boundary, pagination, block tags, transaction idempotency, nonce owner, confirmation depth, and reorg behavior.

### Step 4: Verify reliability

Check finite timeouts, bounded concurrency, classified retries, circuit breaking, WebSocket recovery, Stream/Webhook idempotency, destination acknowledgement, and backlog monitoring.

### Step 5: Verify observability and cost

Require endpoint and application latency, error layers, request IDs, chain errors, credit use, transaction landing, event completeness, and secret-safe logs.

### Step 6: Exercise recovery

Run a read-only smoke test and tabletop credential rotation, endpoint cutover, provider degradation, event replay, and rollback. Name decision owners and expiry dates for any waiver.

## Tool Discipline

Use Read and Grep for repository evidence and Bash(qn:*) for read-only provider evidence. This review does not deploy, change limits, revoke credentials, pause streams, or approve its own waivers.

## Output

- PASS, CONDITIONAL, or BLOCKED decision
- Evidence per readiness dimension
- Owned blockers and expiring waivers
- Recovery and rollback receipt

## Examples

A service is BLOCKED because it assumes archive state on a pruned chain and has no transaction-reconciliation path, even though its endpoint health and latency are green.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence unavailable | Mark the dimension unproven; do not infer pass |
| Secret exposure found | Block launch and rotate the credential |
| Recovery exercise fails | Block launch until rollback is repaired |
| Waiver has no owner or expiry | Reject the waiver |

## Resources

- [Readiness evidence and source notes](references/official-docs.md)
- [QuickNode dashboard](https://www.quicknode.com/guides/quicknode-products/how-to-use-the-quicknode-dashboard)
- [Supported chains and pruning](https://www.quicknode.com/docs/platform/supported-chains-node-types)
