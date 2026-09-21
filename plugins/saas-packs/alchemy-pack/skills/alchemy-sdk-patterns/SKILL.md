---
name: alchemy-sdk-patterns
description: >-
  Route Alchemy work to viem, direct Data APIs, Wallet APIs v5, or Solana Web3.js without reviving the archived SDK. Use when designing shared clients and adapters. Trigger with "Alchemy SDK pattern", "replace alchemy-sdk", or "choose an Alchemy client".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<capability> <runtime> <chain-set>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, architecture, viem]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Client and API Routing Patterns

## Overview

Route Alchemy work to viem, direct Data APIs, Wallet APIs v5, or Solana Web3.js without reviving the archived SDK. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

There is no single current JavaScript Alchemy SDK for every product. EVM Node reads belong behind a `viem` transport adapter, Data APIs behind response-contract adapters, transacting applications behind Wallet APIs v5, and Solana behind Solana Web3.js. The archived `alchemy-sdk` is migration input, not a new architecture choice.

## Authentication

Each adapter declares the credential it accepts and rejects other credential classes. Keep application keys, Admin access keys, Notify tokens, webhook signing keys, and wallet signing authority in separate types and secret paths.

## Instructions

1. Inventory each existing call by capability, chain, runtime, side effect, data owner, and credential class.
2. Assign Node RPC calls to a typed viem public client and keep the configured chain adjacent to the transport.
3. Assign NFT, Transfers, Prices, Simulation, or Portfolio calls to a narrow HTTP adapter that validates the documented response and pagination contract.
4. Assign smart-wallet creation and transaction flows to the current Wallet APIs v5 surface; isolate signing policy from data reads.
5. Represent partial success, pagination, retryability, and unsupported-chain outcomes explicitly instead of returning `null` or an untyped provider exception.
6. Add contract fixtures for success and every documented failure class, then ban new `alchemy-sdk` imports with a focused repository test.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Architecture owns capability routing and adapter boundaries. Security owns credential types and signing policy. Replacing a production provider or transaction path requires a canary and rollback approval.

## Error Handling

- Do not wrap every Alchemy product in a generic client that erases pagination, partial errors, or credential distinctions.
- Do not convert a partial Portfolio response into complete success.
- Do not let a read adapter gain wallet signing authority for convenience.

## Output

Return the call inventory, capability routing table, typed adapter contracts, credential separation, error algebra, fixture matrix, deprecated-import gate, migration order, and rollback boundaries. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Route `eth_getBalance` through a viem public client while routing multi-chain holdings through a Portfolio adapter that surfaces `partialErrors`.
- Keep Wallet APIs transaction construction behind a separately approved signer boundary rather than extending a generic read client.

## Validation

Exercise and record expected and observed results for:

- unsupported chain
- partial Portfolio success
- pagination continuation
- rate limit
- wrong credential class
- archived import reintroduced

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
