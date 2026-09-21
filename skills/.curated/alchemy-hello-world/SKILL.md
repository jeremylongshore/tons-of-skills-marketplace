---
name: alchemy-hello-world
description: >-
  Build a minimal, reviewable Alchemy EVM read with viem and prove its network, authentication, and failure behavior. Use when starting an Alchemy integration or replacing an SDK sample. Trigger with "Alchemy hello world", "read an Ethereum block", or "test my Alchemy connection".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<chain> <read-method> <fixture>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, viem, web3]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Read-Only Connectivity Proof

## Overview

Build a minimal, reviewable Alchemy EVM read with viem and prove its network, authentication, and failure behavior. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

The current Ethereum quickstart uses `viem`. A successful `eth_blockNumber` proves endpoint connectivity only; it does not prove Enhanced API, NFT API, Portfolio, Wallet API, or Admin entitlement. Chain identity must be checked from the response context rather than assumed from an endpoint string.

## Authentication

Use a development application key through the repository's approved server-side secret boundary. Never print the URL when it contains a credential. A browser proof requires the allowlist or short-lived-JWT protections documented in the approved threat model.

## Instructions

1. Choose one supported EVM chain and verify its current endpoint and feature support in first-party documentation.
2. Install a repository-approved, pinned `viem` release and preserve the lockfile review; do not add `alchemy-sdk`.
3. Create a public client with the declared viem chain and an Alchemy HTTP transport supplied from the server secret boundary.
4. Read the chain ID and latest block number, assert that the chain ID equals the configured chain, and record only redacted timing and block evidence.
5. Exercise an invalid credential and a deliberately mismatched chain expectation so the proof demonstrates fail-closed behavior.
6. Return the source, lockfile, test output, and rollback change without making a transaction or requesting a signing key.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Read-only development proof needs the application owner's scoped key. Installing a dependency follows repository review. Any transaction, wallet connection, browser credential, or production call is outside this skill and requires separate approval.

## Error Handling

- Treat `401` or `403` as a credential or policy failure, not as a reason to broaden access.
- Treat a chain-ID mismatch as a hard configuration failure even if the block-number call succeeded.
- Honor `429` and provider `5xx` with a bounded retry budget; never loop until success.

## Output

Return the chosen chain, current source links, dependency decision, minimal viem client, chain-ID assertion, redacted positive and negative test receipts, and rollback command. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Prove an Ethereum Sepolia client returns the expected chain ID and a positive block number without logging its transport URL.
- Show that an Ethereum client pointed at another chain fails the chain-ID assertion instead of returning a misleading success banner.

## Validation

Exercise and record expected and observed results for:

- valid development key
- invalid key
- wrong chain
- rate-limit response
- provider timeout
- credential canary absent from logs

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
