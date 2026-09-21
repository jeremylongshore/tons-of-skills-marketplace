---
name: alchemy-security-basics
description: >-
  Analyze and secure Alchemy credentials, browser access, wallet authority, webhook verification, and untrusted chain data. Use when securing an Alchemy-backed application. Trigger with "secure Alchemy", "Alchemy API key exposure", or "verify an Alchemy webhook".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<application> <credential-class> <runtime>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, security, web3]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Credential and Trust-Boundary Security

## Overview

Analyze and secure Alchemy credentials, browser access, wallet authority, webhook verification, and untrusted chain data. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

An Alchemy application key identifies and limits provider access but is not a wallet private key. Frontend use is not categorically forbidden: current guidance supports explicit allowlists and recommends short-lived JWTs where appropriate. Admin keys, Notify tokens, webhook signing keys, and transaction signing authority remain server-side and separately controlled.

## Authentication

Create a credential matrix covering application keys, access keys, Admin access, Notify management, webhook verification, and wallet signers. Assign owner, storage, runtime, scopes/allowlists, rotation, revocation, monitoring, and incident procedure to each.

## Instructions

1. Map browser, edge, server, CI, webhook, admin, and wallet trust boundaries and the data crossing each boundary.
2. Choose server header auth for confidential workloads; if browser access is justified, apply exact allowlists or short-lived JWTs and test bypass conditions.
3. Validate chain IDs, addresses, block selectors, contract ABIs, method allowlists, response sizes, and remote NFT metadata before use.
4. Keep read clients separate from signers; require explicit transaction simulation, user intent, policy checks, and approval in a distinct workflow.
5. Verify Notify payloads against the raw body using HMAC-SHA256 and the per-webhook signing key before parsing or side effects.
6. Run source, artifact, log, browser-bundle, and configuration secret scans; exercise rotation and incident response before production.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Security approves browser keys, JWT issuers, secret stores, signing boundaries, and incident response. Wallet transactions, new allowlists, credential rotation, or revocation require the named owner.

## Error Handling

- Do not compare webhook signatures with ordinary string equality or after reserializing JSON.
- Do not let an application API key or read client imply transaction-signing permission.
- If credential material is exposed, fail closed, rotate or revoke it, inspect downstream use, and preserve a redacted receipt.

## Output

Return the threat model, credential matrix, browser/server decision, input and response controls, signer separation, webhook verification contract, scan evidence, rotation exercise, and open risks. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Approve a restricted browser read only after proving the configured origin allowlist rejects an unlisted origin and the bundle contains no broader credential.
- Reject a webhook whose signature is valid only after JSON reserialization because verification must cover the exact raw body.

## Validation

Exercise and record expected and observed results for:

- unlisted browser origin
- expired short-lived JWT
- wrong chain
- oversized response
- bad webhook signature
- secret canary in build artifact

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
