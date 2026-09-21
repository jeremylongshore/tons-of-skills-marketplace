---
name: alchemy-deploy-integration
description: >-
  Deploy an Alchemy-backed service through environment-scoped credentials, chain assertions, canaries, and rollback gates. Use when promoting an integration to hosted environments. Trigger with "deploy Alchemy integration", "Alchemy production deploy", or "promote an Alchemy service".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<platform> <source-env> <target-env>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, deployment, reliability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Deployment and Promotion Control

## Overview

Deploy an Alchemy-backed service through environment-scoped credentials, chain assertions, canaries, and rollback gates. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Deployment artifacts are environment-neutral; credentials, application IDs, chain IDs, allowlists, webhook URLs, and account budgets are injected per environment. A health endpoint proves process health, while readiness must prove the intended chain and endpoint family without exposing credentials or creating a transaction.

## Authentication

Bind separate development, staging, and production Alchemy credentials through the platform secret manager. Deployment identities may reference secrets but may not read their values unless runtime requires it. Wallet signers remain outside the read-service deploy boundary.

## Instructions

1. Inventory artifact SHA, target environment, region, Alchemy application/key identifier, chain, endpoint families, limits, callbacks, and owners.
2. Verify the target chain and feature support and compare the environment manifest against staging; fail on reused credentials or ambiguous chain configuration.
3. Inject secrets by reference, deploy an immutable artifact, and scan build logs, source maps, configuration exports, and images for credential canaries.
4. Run a read-only readiness proof that asserts chain ID and endpoint behavior; separately test partial, rate-limited, and unavailable-provider states.
5. Canary a bounded traffic share while watching latency, error class, completeness, usage, spend, and callback health.
6. Promote only within approved thresholds; otherwise route back to the prior artifact and preserve the deployment and rollback receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Release owns promotion; security owns secret and public-origin configuration; product/operations own degraded behavior and traffic thresholds. Production deployment or rollback requires explicit environment approval.

## Error Handling

- Do not treat a generic `200 /health` as proof of correct chain or Alchemy readiness.
- If a build or log contains a credential canary, stop promotion and rotate when exposure reached an unauthorized boundary.
- Do not promote when the canary hides partial responses or exceeds the approved account envelope.

## Output

Return the environment manifest, immutable artifact, secret-reference proof, chain-aware readiness results, canary metrics, threshold decision, deployment receipt, and tested rollback receipt. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Promote the same artifact from staging to production while changing only approved secret references, chain configuration, and environment metadata.
- Roll back a canary that returns fast HTTP 200 responses but begins surfacing Portfolio `partialErrors` above the completeness threshold.

## Validation

Exercise and record expected and observed results for:

- credential reused across environments
- wrong chain ID
- secret canary in source map
- provider unavailable
- partial response threshold
- rollback to prior artifact

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
