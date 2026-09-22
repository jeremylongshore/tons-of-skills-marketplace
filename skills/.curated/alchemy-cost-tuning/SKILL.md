---
name: alchemy-cost-tuning
description: >-
  Govern Alchemy compute usage and spend with current account evidence, workload attribution, budgets, and reversible optimizations. Use when forecasting or reducing Alchemy cost. Trigger with "Alchemy cost", "Alchemy compute units", or "reduce Alchemy spend".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<account> <billing-window> <budget>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, cost, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Usage and Cost Governance

## Overview

Govern Alchemy compute usage and spend with current account evidence, workload attribution, budgets, and reversible optimizations. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Alchemy pricing plans, included capacity, compute-unit costs, and elastic-demand terms are mutable. Cost decisions use the current account contract, current method-cost documentation, and observed usage—not embedded plan tables. Admin usage access requires an authorized Admin access key or dashboard owner.

## Authentication

Treat billing, application attribution, and usage data as restricted operational data. Keep Admin access keys separate from application keys and never place usage exports or credentials in public repositories.

## Instructions

1. Record the account, billing window, plan, approved budget, elastic-demand state, currency, owner, and dated source evidence.
2. Attribute observed usage by application, environment, method family, chain, traffic class, and release using the authorized dashboard or Admin usage interface.
3. Reconcile observed compute units and charges to the current contract; label estimates and unattributed usage explicitly.
4. Rank optimizations by correctness risk: remove duplicate calls, cache immutable data, bound pages, batch where documented, schedule background work, and reserve capacity for critical traffic.
5. Forecast base, burst, and failure/retry scenarios with ranges rather than a false point estimate; set budget alerts and an approved response owner.
6. Canary one change, compare cost and SLO deltas, preserve completeness, and roll back if savings depend on hidden errors or stale data.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Finance/budget owner approves plan, capacity, and elastic spend. Product approves freshness or degraded-mode tradeoffs. Security approves Admin API credential use.

## Error Handling

- Do not quote remembered plan allowances or method costs as current facts.
- Do not reduce cost by hiding partial errors, skipping pagination, or silently serving stale data.
- If usage cannot be attributed, surface the gap before recommending a plan change.

## Output

Return the dated account contract, usage attribution, reconciliation, forecast ranges, optimization register, budget alerts, canary evidence, SLO impact, and approval/rollback decision. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Attribute a backfill spike to its application and method family, then schedule and cap it without consuming the critical-read reserve.
- Reject a cache proposal whose apparent savings come from labeling partial Portfolio results complete.

## Validation

Exercise and record expected and observed results for:

- unattributed usage
- changed method cost
- burst forecast
- retry amplification
- budget threshold
- optimization rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
