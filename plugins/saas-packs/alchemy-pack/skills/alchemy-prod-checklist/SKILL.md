---
name: alchemy-prod-checklist
description: >-
  Make an evidence-backed go or no-go decision for an Alchemy-backed production release. Use when reviewing a launch or material integration change. Trigger with "Alchemy production checklist", "Alchemy go-live review", or "is this Alchemy integration ready".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release-sha> <environment> <change-scope>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, production, governance]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Production Readiness Decision

## Overview

Make an evidence-backed go or no-go decision for an Alchemy-backed production release. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

Production readiness is a signed decision over a specific artifact, environment, Alchemy application, chain and feature set, account contract, data path, SLOs, and rollback. A passing connectivity check or testnet transaction does not authorize production traffic or wallet operations.

## Authentication

Confirm owners and lifecycle for every application key, Admin key, Notify token, webhook signing key, and signer. Prove environment isolation, least privilege, rotation, revocation, log redaction, and break-glass access.

## Instructions

1. Freeze the release SHA and enumerate Node, Data, Portfolio, Wallet, Notify, Admin, chain, address/data, and transaction surfaces in scope.
2. Recheck current first-party feature support, errors, throughput, pricing, and SDK/client guidance; record account-specific observations and dates.
3. Verify deterministic tests, contract fixtures, chain assertions, partial/pagination handling, bounded retries, idempotency, and provider-outage behavior.
4. Review secret, privacy, webhook, wallet-signer, dependency, artifact, and supply-chain evidence plus incident and key-rotation exercises.
5. Review capacity, budget, alerting, runbooks, service ownership, status-page dependency, deployment canary, stop thresholds, and tested rollback.
6. Record each gate as pass, fail, waived-by-owner with expiry, or not applicable; issue go only when blockers are resolved by named authorities.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Release, product, operations, security, privacy/data, and budget owners sign their scopes. A waiver names owner, risk, compensating control, expiry, and follow-up; this skill cannot self-approve.

## Error Handling

- Missing evidence is a failed or unresolved gate, not an assumed pass.
- Do not reuse a testnet or staging receipt as production environment evidence.
- Do not approve if rollback, key rotation, partial-response UX, or provider-unavailable behavior is untested.

## Output

Return the frozen release/environment manifest, gate matrix with evidence links, current-contract review, owner sign-offs, waivers, blockers, go/no-go decision, monitoring window, and rollback receipt. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Issue no-go when the release passes connectivity but has no explicit handling for a Portfolio HTTP 200 partial failure.
- Issue conditional go only when an authorized, expiring waiver identifies its control and does not bypass a non-waivable security boundary.

## Validation

Exercise and record expected and observed results for:

- wrong artifact SHA
- staging evidence substituted
- rotation failure
- provider outage
- budget alert
- rollback exercise

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
