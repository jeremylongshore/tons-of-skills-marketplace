---
name: alchemy-performance-tuning
description: >-
  Tune Alchemy-backed reads with measured latency, cache semantics, batching, concurrency, and freshness SLOs. Use when an integration is slow or wasteful. Trigger with "optimize Alchemy performance", "cache Alchemy data", or "reduce Alchemy latency".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<endpoint-class> <freshness-slo> <traffic-shape>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, performance, caching]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Performance and Freshness Tuning

## Overview

Tune Alchemy-backed reads with measured latency, cache semantics, batching, concurrency, and freshness SLOs. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Performance depends on endpoint family, chain, response size, pagination, account throughput, region, cache state, and application work. There is no universal latency or batch-size guarantee. Optimization must preserve chain context, finality, partial-error semantics, and the product's freshness contract.

## Authentication

Telemetry may include key identifiers, wallet addresses, or request metadata; log only approved low-cardinality fields and never credential-bearing URLs or full user payloads.

## Instructions

1. Define endpoint-specific latency, completeness, freshness, and cost SLOs plus the user-visible degraded state.
2. Measure an approved baseline by chain, method, payload/page size, cache state, and concurrency; record percentiles rather than a single average.
3. Remove duplicate calls, bound pagination, choose current batch endpoints only where their documented semantics match, and cap concurrency below the shared account budget.
4. Cache immutable block-scoped data longer than head-sensitive data; include chain, method, normalized parameters, block/finality context, and schema version in keys.
5. Propagate partial failures and staleness metadata through caches; never cache a degraded result as complete success.
6. Load-test the proposed envelope, compare against baseline, prove invalidation and rollback, then promote with telemetry and stop thresholds.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Product owns freshness and degraded UX; operations owns capacity and stop thresholds; privacy owns cached address data. Increasing spend or retention requires explicit approval.

## Error Handling

- Do not optimize by dropping failed networks, pages, or assets without declaring incompleteness.
- Do not cache `latest` as though it were immutable; attach an observed block/finality context.
- If an optimization worsens tail latency, error rate, freshness, or compute usage beyond threshold, roll it back.

## Output

Return the SLOs, segmented baseline, call graph, cache/batch/concurrency design, partial/stale state contract, load results, telemetry, stop thresholds, and rollback receipt. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Cache token metadata by chain and contract while refreshing head-sensitive balances under a shorter product-approved freshness SLO.
- Reject a faster multi-chain result when it hides one network's `partialErrors` and therefore violates completeness semantics.

## Validation

Exercise and record expected and observed results for:

- cold cache
- warm cache
- stale invalidation
- multi-page response
- partial failure through cache
- load rollback threshold

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
