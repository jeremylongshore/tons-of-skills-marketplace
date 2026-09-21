---
name: alchemy-reference-architecture
description: >-
  Design a production Alchemy architecture with capability-specific adapters, explicit trust boundaries, partial-state semantics, and reversible operations. Use when reviewing or creating an Alchemy-backed system. Trigger with "Alchemy architecture", "design an Alchemy dApp backend", or "review Alchemy boundaries".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<product-capabilities> <chain-set> <trust-model>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, architecture, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Production Reference Architecture

## Overview

Design a production Alchemy architecture with capability-specific adapters, explicit trust boundaries, partial-state semantics, and reversible operations. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Current architecture separates EVM RPC through viem, Data APIs through typed HTTP adapters, Wallet APIs v5 through a transaction-policy boundary, Notify intake through authenticated idempotent queues, and Admin usage through restricted operations tooling. No shared archived SDK client or credential should collapse these contracts.

## Authentication

Model browser, edge, API, worker, webhook, Admin, and signer identities separately. Application keys may serve permitted reads; Admin access keys, Notify tokens, webhook signing keys, and wallet signing authority remain isolated by runtime, owner, and policy.

## Instructions

1. Inventory user journeys, data ownership, chains, Node/Data/Portfolio/Wallet/Notify/Admin capabilities, writes, callbacks, SLOs, and regulatory constraints.
2. Draw trust and data-flow boundaries including browser access, server adapters, queue, cache, database, secret store, observability, signer, provider, and external metadata.
3. Define typed capability adapters with chain assertions, pagination, partial success, finality, idempotency, bounded retry, and unsupported-feature outcomes.
4. Keep read paths and transaction intent/signing paths separate; require simulation, policy, user consent, and audit receipts for writes.
5. Design account-wide backpressure, cache freshness, webhook acknowledgement/replay, provider outage, status reconciliation, privacy deletion, and cost controls.
6. Threat-model and failure-test the design, map owners and approvals, then document incremental rollout and rollback variants.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Architecture, security, product, operations, privacy/data, and budget owners approve their boundaries. Introducing a signer, browser credential, new retained data, or external provider requires explicit review.

## Error Handling

- Do not model Alchemy as one reliable box; show endpoint families, account limits, partial responses, indexing, and chain finality.
- Do not let a queue acknowledgement imply successful downstream blockchain or user-visible processing.
- Do not place Admin or signing credentials in the general application API tier.

## Output

Return the context and data-flow diagrams, capability/client matrix, credential and ownership map, state/error contracts, SLO/capacity model, threat model, failure tests, rollout variants, and rollback plan. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Route a browser request through a server Portfolio adapter that preserves partial network state and caches only under an explicit freshness label.
- Place Wallet APIs transaction construction and signer policy outside the read API so a compromised read key cannot authorize a transaction.

## Validation

Exercise and record expected and observed results for:

- browser boundary bypass
- wrong chain
- Portfolio partial success
- queue duplicate
- account saturation
- signer unavailable

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
