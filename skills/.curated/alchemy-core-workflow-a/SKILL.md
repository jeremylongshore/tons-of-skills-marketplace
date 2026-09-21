---
name: alchemy-core-workflow-a
description: >-
  Design a multi-chain holdings workflow on Alchemy Portfolio APIs with explicit pagination, partial-failure, privacy, and reconciliation contracts. Use when building wallet portfolio views. Trigger with "Alchemy portfolio", "multi-chain token balances", or "wallet holdings dashboard".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<address-set> <network-set> <freshness-slo>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, portfolio, data-api]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Multi-Chain Portfolio Workflow

## Overview

Design a multi-chain holdings workflow on Alchemy Portfolio APIs with explicit pagination, partial-failure, privacy, and reconciliation contracts. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Portfolio APIs aggregate fungible tokens and NFTs across requested networks. Multi-network fanout can return HTTP 200 while reporting `error.partialErrors`; failed networks can be absent from pagination. Therefore HTTP success is not completeness, and retries for failed networks begin as fresh bounded requests rather than continuing the successful-network cursor.

## Authentication

Use an application API key appropriate to Portfolio APIs and keep it in the approved server boundary. Wallet addresses are personal or customer-linked data when the product context makes them identifiable; apply the declared notice, consent, retention, and logging policy.

## Instructions

1. Define the supported network set, address source, freshness SLO, display currency, pagination limit, and completeness status shown to users.
2. Confirm every requested Portfolio network in current documentation and validate each address before provider access.
3. Call the appropriate Portfolio token or NFT endpoint through a response-validating adapter; retain the request's network set with the result.
4. Persist successful network pages and surface top-level `error.partialErrors` as named unavailable networks rather than dropping them.
5. Continue cursors only for successful result sets; retry each failed network as a fresh request within a bounded budget and reconcile without duplicating holdings.
6. Prove empty, partial, paginated, stale, and total-provider-failure states in the UI/API, then document cache invalidation and data deletion.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Product and privacy owners approve address collection and retention. Operations approves freshness and degraded-mode semantics. Exporting addresses or holdings, increasing retention, or adding networks requires explicit approval.

## Error Handling

- Never label an HTTP 200 response complete until `partialErrors`, requested networks, and pagination have been reconciled.
- Do not continue a successful-network page key for a network that failed out of the original response.
- Do not convert missing price or metadata into a zero-valued asset.

## Output

Return the network/address contract, validated adapter schema, pagination and partial-error state machine, cache policy, privacy controls, degraded UX, reconciliation evidence, and rollback. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Render Ethereum and Base holdings while explicitly marking a failed Arbitrum query unavailable, then retry Arbitrum as a fresh bounded request.
- Show an empty portfolio as a valid complete result only when every requested network completed and pagination is exhausted.

## Validation

Exercise and record expected and observed results for:

- empty complete wallet
- multi-page success
- HTTP 200 with partialErrors
- one failed network retry
- duplicate reconciliation
- data-deletion request

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
