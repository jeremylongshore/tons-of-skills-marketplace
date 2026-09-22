---
name: alchemy-debug-bundle
description: >-
  Collect a deterministic, secret-safe Alchemy diagnostic bundle for triage and escalation. Use when a provider issue needs reproducible evidence. Trigger with "Alchemy debug bundle", "collect Alchemy diagnostics", or "prepare an Alchemy support case".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <time-window> <endpoint-class>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, diagnostics, support]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy Redacted Diagnostic Bundle

## Overview

Collect a deterministic, secret-safe Alchemy diagnostic bundle for triage and escalation. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

A useful diagnostic bundle captures configuration identity, endpoint class, chain, dependency locks, sanitized request and response envelopes, request IDs, timing, retry history, and status observations. It never contains API keys, Admin keys, Notify tokens, signing keys, private keys, raw customer payloads, or credential-bearing URLs.

## Authentication

Use a redaction allowlist, not a blacklist. Replace embedded endpoint credentials with a stable one-way fingerprint only when policy permits correlation. Keep the unredacted source in its existing protected system rather than copying it into the bundle.

## Instructions

1. Define the incident window, affected endpoint family, chain, environment, expected behavior, and authorized evidence recipients.
2. Inventory runtime, package lock, adapter version, configured chain ID, feature, deployment SHA, and key identifier without reading or exporting secret values.
3. Collect sanitized request/response shapes, HTTP and JSON-RPC status, selected safe headers, request IDs, duration, attempt count, and partial-error fields.
4. Add current Alchemy status, supported-chain/feature evidence, and account-usage observation from the authorized owner; distinguish observation from inference.
5. Scan the complete bundle for secret and personal-data canaries, manually review it, then hash the immutable artifact.
6. Reproduce once with a synthetic fixture where safe, attach the positive or failed receipt, and specify retention and deletion dates.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

The incident owner approves scope and recipients; security/privacy approve any potentially identifying evidence. Sending a bundle to Alchemy or another external party requires explicit disclosure approval.

## Error Handling

- If redaction cannot be proven, do not export the bundle.
- Do not install or report the archived `alchemy-sdk` merely to populate an SDK-version field.
- A service-status screenshot without request IDs and environment facts is context, not root-cause evidence.

## Output

Return the incident manifest, sanitized environment and request facts, status/feature evidence, reproduction receipt, redaction scan, artifact hash, recipients, retention date, and gaps. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Build a bundle for intermittent Ethereum RPC timeouts containing request IDs and timings but no endpoint URL or address payload.
- Reject a draft bundle when its command transcript contains the application key in a URL, then rotate if exposure crossed the approved boundary.

## Validation

Exercise and record expected and observed results for:

- secret canary detected
- customer-address canary detected
- missing request ID
- partial error preserved
- artifact hash reproducible
- recipient authorization absent

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
