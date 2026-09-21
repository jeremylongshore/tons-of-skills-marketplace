---
name: alchemy-local-dev-loop
description: >-
  Establish a deterministic local EVM development loop with pinned forks, synthetic fixtures, and bounded Alchemy usage. Use when adding local chain tests or repairing flaky fork-based development. Trigger with "Alchemy local dev", "Hardhat fork with Alchemy", or "pin a mainnet fork".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<framework> <chain> <fork-block>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, testing, hardhat]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Deterministic Local Development Loop

## Overview

Establish a deterministic local EVM development loop with pinned forks, synthetic fixtures, and bounded Alchemy usage. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

A remote mainnet fork is reproducible only when the chain, block number, dependency versions, and fixture state are pinned. It still consumes account-level throughput and can diverge when historical access, method support, or upstream state is unavailable. Alchemy Sandbox is a separate simulation option and must be evaluated against the required test semantics.

## Authentication

Use a development-only app key from local secret injection. Never copy a production key or deployer private key into `.env`, task output, shell history, fixtures, or committed fork URLs.

## Instructions

1. Inventory the project's current Hardhat, Foundry, Anvil, or other EVM test runner and preserve its existing commands.
2. Confirm the target chain and historical method support, then select and record a stable fork block with the business reason for changing it.
3. Inject a development Alchemy endpoint through the established local secret mechanism and ensure configuration fails clearly when it is absent.
4. Use synthetic accounts and deterministic impersonation or funded fixtures; never import a real user or production signer.
5. Run the smallest fork test, a clean-room rerun, and an offline/unit fallback; record request volume and wall time without claiming a universal benchmark.
6. Document how to advance the fork block, refresh fixtures, distinguish provider drift from code failure, and restore the prior block.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

The test owner approves the pinned state and fixture refresh. Security approves secret injection. Forking production state, using customer addresses, or funding a test signer requires data/security approval.

## Error Handling

- A latest-block fork that passes once is not deterministic evidence.
- If the historical block or method is unavailable, stop and classify the provider/test assumption rather than silently changing the block.
- A leaked endpoint is a credential incident even when the key is development-only.

## Output

Return the pinned chain/block/dependency matrix, redacted local configuration, deterministic fixtures, positive and clean-room test receipts, usage observation, drift procedure, and rollback. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Pin an Ethereum fork to the block needed by a contract regression and prove the same result in two clean runs.
- Compare a fork test with Alchemy Sandbox only after documenting which state mutation and tracing behavior the test requires.

## Validation

Exercise and record expected and observed results for:

- missing endpoint
- wrong chain ID
- unpinned block rejected
- fixture reset
- provider timeout
- offline/unit fallback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
