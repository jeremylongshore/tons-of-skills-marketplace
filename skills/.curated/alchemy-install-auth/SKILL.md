---
name: alchemy-install-auth
description: >-
  Select and prove the current Alchemy client, key type, network, and authentication boundary before integration work. Use when creating or repairing Alchemy connectivity. Trigger with "set up Alchemy", "configure an Alchemy API key", or "choose viem or Wallet APIs".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<product-api> <chain> <environment>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, authentication, web3]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Installation and Authentication Intake

## Overview

Select and prove the current Alchemy client, key type, network, and authentication boundary before integration work. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

The legacy `alchemy-sdk` JavaScript repository is archived and deprecated. New EVM reads use `viem` or direct documented HTTP APIs; transacting applications and Portfolio support use `@alchemy/wallet-apis`; Solana work uses Solana Web3.js. An application API key, an Admin access key, a Notify auth token, and a webhook signing key are different credentials and are not interchangeable.

## Authentication

Prefer server-side request-header authentication for confidential workloads. A browser key is acceptable only when the current Alchemy guidance, explicit domain allowlists, least privilege, and the product threat model allow it; short-lived JWTs are the stronger frontend option. Store Admin, Notify, webhook, and signing credentials only in approved secret storage.

## Instructions

1. Classify the requested capability as Node RPC, Data API, Portfolio, Wallet APIs, Notify management, webhook receipt, Admin usage, or Solana.
2. Confirm the required chain and feature in the live supported-chain and feature-support matrices; do not infer feature parity from RPC support.
3. Select `viem`, direct HTTP, `@alchemy/wallet-apis`, or Solana Web3.js from the capability—not from the archived SDK examples.
4. Create or identify a non-production application and a least-privilege key; separately identify any Admin access key or Notify token actually required.
5. Configure the credential through the repository's established secret mechanism and document whether requests use a server header, server URL, or approved restricted browser boundary.
6. Run one read-only chain-specific proof, record the redacted request shape and response, then document rotation, revocation, owner transfer, and environment separation.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

The application owner selects the product and chain. Security approves any browser credential boundary and production secret store. Creating, rotating, revoking, or deleting a live key requires explicit approval from its owner.

## Error Handling

- A valid key on an unsupported feature or chain is not a successful setup.
- Do not substitute an application API key for an Admin access key, Notify token, or webhook signing key.
- If a secret appears in source, logs, or artifacts, stop, revoke or rotate it, remove the exposure, and preserve a redacted incident receipt.

## Output

Return the capability-to-client decision, chain/feature proof, credential-class matrix, redacted connectivity result, secret lifecycle, owners, evidence date, and unresolved gaps. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- For a server-rendered Ethereum balance view, select `viem`, prove one read with a development app key, and keep the production key in the server secret boundary.
- For a transacting smart-wallet application, select Wallet APIs v5 and reject an archived `alchemy-sdk` bootstrap even if an old repository still imports it.

## Validation

Exercise and record expected and observed results for:

- wrong chain
- unsupported feature on a supported chain
- missing or invalid key
- application key supplied to an Admin endpoint
- revoked key
- secret-canary scan

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
