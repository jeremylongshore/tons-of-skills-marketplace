---
name: alchemy-upgrade-migration
description: >-
  Migrate archived Alchemy JavaScript SDK integrations to current capability-specific clients with parity, canary, and rollback evidence. Use when removing alchemy-sdk or upgrading Wallet APIs. Trigger with "migrate alchemy-sdk", "replace alchemy-web3", or "upgrade Wallet APIs to v5".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-client> <capability-set> <release-scope>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, migration, viem]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Archived SDK Migration

## Overview

Migrate archived Alchemy JavaScript SDK integrations to current capability-specific clients with parity, canary, and rollback evidence. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

`alchemy-sdk` is deprecated and its repository is archived. Current migration targets are capability-specific: `viem` for JavaScript EVM RPC, direct documented Data API adapters, `@alchemy/wallet-apis` for transacting apps and Portfolio support, and Solana Web3.js for Solana. Wallet APIs v5 has a separate first-party migration guide.

## Authentication

Inventory every credential the old client could access and grant each replacement adapter only its needed class. Do not let migration move secrets from a server boundary to browser code or merge read and signing authority.

## Instructions

1. Freeze dependency locks and inventory every `alchemy-sdk`, `alchemy-web3`, endpoint, namespace, WebSocket, Notify, Data API, Wallet, and signer use by capability and side effect.
2. Route EVM RPC to viem, product HTTP calls to typed adapters, transacting/Portfolio use to Wallet APIs v5 where applicable, and Solana use to Solana Web3.js.
3. Define normalized parity contracts for values, pagination, partial errors, retryability, chain identity, subscriptions, and transaction intent; preserve raw evidence for differences.
4. Build fixtures and dual-read comparison for read-only paths; use simulation/testnet and explicit authorization for transaction paths.
5. Canary one capability at a time with stop thresholds and the old artifact still deployable; remove deprecated imports only after parity and negative paths pass.
6. Update runbooks, CI bans, lockfiles, observability, owners, and rollback; separately follow the current Wallet APIs v5 guide for v4 consumers.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Architecture approves target routing; security approves changed credential and signing boundaries; release/product approve canary and normalized differences. Production transaction migration requires explicit wallet-policy approval.

## Error Handling

- Do not replace the archived SDK with one universal wrapper that hides product-specific contracts.
- Do not treat different pagination, partial-error, finality, or numeric semantics as cosmetic parity.
- If a canary breaches correctness, completeness, latency, error, or spend thresholds, route back to the prior artifact.

## Output

Return the legacy call inventory, target routing, credential delta, parity schema, fixture/dual-read evidence, canary thresholds, deprecated-import gate, rollout sequence, unresolved differences, and rollback receipt. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Migrate an `alchemy.core.getBalance` call to a viem public client and compare normalized values and chain IDs before switching traffic.
- Migrate Portfolio behavior only after proving the replacement preserves top-level `partialErrors` and fresh retry of failed networks.

## Validation

Exercise and record expected and observed results for:

- archived import scan
- numeric parity
- pagination parity
- partial-error parity
- wrong credential boundary
- canary rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
