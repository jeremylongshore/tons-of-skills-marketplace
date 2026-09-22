---
name: adobe-local-dev-loop
description: >-
  Build a repeatable local loop for Adobe adapters using synthetic contracts before any remote Runtime or product call. Use when implementing or debugging locally. Trigger with "develop Adobe integration locally", "mock Adobe API", or "aio app dev".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <service> <feature>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, development]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Isolated Development Loop

## Overview

Build a repeatable local loop for Adobe adapters using synthetic contracts before any remote Runtime or product call. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

App Builder local modes differ: aio app dev runs actions locally and lacks activation records and some Runtime-only storage capabilities; aio app run uses remote Runtime actions with local UI. Offline fixtures must cover both product responses and those environment differences. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Use synthetic data and non-production aliases. Keep .env and .aio out of version control; pass configured values to actions rather than assuming local environment variables exist in deployed Runtime.

## Instructions

1. Inventory the adapter, SDK locks, App Builder configuration, fixtures, and current local-mode assumptions.
2. Define typed request, response, async-status, error, throttling, and redaction contracts from current docs.
3. Create synthetic fixtures for success, additive fields, malformed data, 401/403, 429, 5xx, and ambiguous completion.
4. Run unit and contract tests with network access disabled and secret canaries enabled.
5. If App Builder is used, exercise aio app dev and a separately approved aio app run path where Runtime fidelity matters.
6. Record mode differences, cleanup remote test artifacts, and keep only sanitized deterministic fixtures.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Require sandbox-owner approval for remote Runtime or Adobe API calls and separate approval for uploads, generation, writes, or deletion.

## Error Handling

- Fail if a production hostname, organization, credential, or asset enters a fixture.
- Do not snapshot signed URLs or document/image bytes into source control.
- Treat locally unsupported State or Files behavior as unknown until remote testing.

## Output

Return the client seam, fixture manifest, commands, secret scan, local/remote matrix, cleanup, and remaining unknowns. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Replay a 429 with and without Retry-After.
- Prove aio app dev limitations are not represented as production behavior.

## Validation

Exercise and record expected and observed results for:

- offline success
- additive field
- auth denial
- 429
- Runtime-only feature
- secret canary

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
