---
name: alchemy-ci-integration
description: >-
  Gate Alchemy integration changes with deterministic unit, contract, fork, secret, and negative-path checks. Use when adding Alchemy to CI or hardening an existing pipeline. Trigger with "Alchemy CI", "Alchemy GitHub Actions", or "test Alchemy in CI".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<ci-provider> <test-layers> <deployment-boundary>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, ci-cd, testing]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Continuous Integration Gate

## Overview

Gate Alchemy integration changes with deterministic unit, contract, fork, secret, and negative-path checks. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

CI should keep most provider behavior deterministic through fixtures and contract tests. A live read or pinned-chain fork is a separately labeled integration gate with a scoped non-production key, bounded usage, and an unavailable-provider policy. Pull-request testing never implies authorization to deploy or transact.

## Authentication

Use a least-privilege CI environment secret with no write or wallet-signing authority. Prevent fork-origin workflows from receiving repository secrets and scan logs, artifacts, bundles, source maps, and built assets for canaries.

## Instructions

1. Inventory unit, adapter-contract, fixture, fork, live-read, deployment, and transaction tests and assign each to a trust boundary.
2. Pin runtime and dependencies; validate fixtures against current documented schemas without requiring live credentials for ordinary pull requests.
3. Run secret and deprecated-import gates, including a ban on new `alchemy-sdk` imports and credential-bearing endpoint literals.
4. Run a scoped live read or pinned-block fork only in an approved trusted context, assert chain identity, cap duration/usage, and retain a redacted receipt.
5. Keep testnet deployment or transaction simulation in a separate protected job with environment approval and no automatic production promotion.
6. Prove invalid-key, wrong-chain, provider-unavailable, rate-limited, partial-response, and secret-canary failures before making the gate required.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Repository/security owners approve secret-bearing CI contexts. Release owners approve protected deployment jobs. External fork pull requests never gain secrets solely because a maintainer runs tests.

## Error Handling

- A provider outage must produce the documented gate result; do not silently skip a required live contract.
- Do not expose secret values in command lines, process dumps, cache keys, or build scans.
- Do not combine a read-only CI gate with testnet deployment in the same implicit authority boundary.

## Output

Return the test-layer map, workflow/config change, secret and fork policy, deterministic fixtures, live-gate budget, negative-path receipts, required/advisory decision, and rollback. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Run fixture-backed adapter tests on every fork PR and a single chain-ID-asserted live read only after the trusted environment gate.
- Fail a build that reintroduces `alchemy-sdk` or embeds an Alchemy endpoint credential in a source map.

## Validation

Exercise and record expected and observed results for:

- fork PR without secrets
- invalid key
- wrong chain
- provider unavailable
- HTTP 200 partial error
- secret canary in artifact

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
