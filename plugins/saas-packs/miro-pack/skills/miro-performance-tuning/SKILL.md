---
name: miro-performance-tuning
description: "Analyze and execute this workflow: tune Miro reads and writes from measured latency, cursor behavior, bulk semantics, and credit cost. Use when improving Miro throughput or freshness. Trigger with \"miro integration performance tuning\"."
argument-hint: "[operation] [target-slo]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- miro
- performance
- pagination
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Miro app and redacted evidence
---
# Miro Integration Performance Tuning

## Overview

Optimize credits, latency, payload, or reconciliation time without sacrificing correctness or tenant fairness; use the evidence produced here to make the next decision explicit and reviewable.

## Prerequisites

- Approved Miro application, tenant, and board scope
- Current repository and deployment evidence
- Named owner, success criteria, and rollback or recovery boundary

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the repository, configuration names, adapters, tests, and evidence. Use `WebFetch` only for current official Miro documentation. Use `Write` or `Edit` after confirming the requested mode, target environment, tenant, board, and approval boundary.

## Current Contract

- Calls consume endpoint-specific credits under a shared user/application budget.
- Cursor presence, not guessed page fullness, controls collection continuation.
- Bulk create supports at most twenty items and charges Level 2 credits per item.
- Board searches without team/project filters may have indexing delay.

## Authentication

For REST work, use OAuth 2.0 Authorization Code with the narrowest Miro scopes. Bind each encrypted token record to its user, application, authorized team, and granted scopes. Never print access tokens, refresh tokens, client secrets, authorization codes, or board content.

## Instructions

1. Measure latency, pages, items, bytes, credits, errors, and queue age by operation.
2. Find redundant reads, unbounded traversal, duplicate callers, and reconciliation hot spots.
3. Apply narrow filters, checkpoints, deduplication, bounded concurrency, and explicit cache freshness.
4. Use bulk create only when transactional and per-item credit semantics fit.
5. Load-test synthetic data under a fixed credit budget and verify tenant fairness.
6. Canary one change and retain rollback thresholds for latency, drift, errors, and credits.

## Approval Boundaries

Do not relax reconciliation, increase concurrency, or cache board content without service and data-owner approval. Pause when the responsible owner or exact target is uncertain.

## Output

Return scope, observed contract, proposed or completed actions, verification evidence, approvals, residual risks, and next owner. State what was not inspected or changed so the receipt cannot overclaim coverage.

## Error Handling

| Condition | Response |
|---|---|
| Tenant or board context mismatches | Stop before mutation and quarantine the credential mapping. |
| Current docs contradict the implementation | Treat the official current contract as a blocker and design an explicit migration. |
| A mutation result is ambiguous | Reconcile state before retrying. |
| Required evidence is unavailable | Return a blocked decision with the smallest safe next probe. |

## Examples

The example is a redacted operator receipt; identifiers are hashes or bounded labels, not board content or credentials.

```text
operation=get-items; p95=2.8s->1.1s; credits=-31%; drift=0; fairness=passed
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Rate limits](https://developers.miro.com/reference/rate-limiting)
- [Bulk create](https://developers.miro.com/reference/create-items)
