---
name: adobe-ci-integration
description: >-
  Build deterministic CI gates for Adobe adapters without giving fork jobs credentials or spending against live creative/document APIs. Use when testing integration changes. Trigger with "test Adobe in CI", "Adobe contract tests", or "gate Adobe deploy".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository> <services> <trusted-lane>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Contract-Safe CI

## Overview

Build deterministic CI gates for Adobe adapters without giving fork jobs credentials or spending against live creative/document APIs. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Pull requests can prove routes, headers, schemas, polling, redaction, EOL bans, errors, and retries offline. Live tests require a protected trusted branch, non-production project/workspace, synthetic fixtures, strict budget, and explicit mutation/cleanup boundaries. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Fork and untrusted PR jobs receive no secrets. Protected lanes use environment-scoped credentials and record aliases only; secret canaries gate artifacts and logs.

## Instructions

1. Map CI trust boundaries, service adapters, fixtures, secret sources, deploy workflows, and fork behavior.
2. Add offline request/response contracts for auth, async URLs, PDF assets, webhooks, errors, throttling, and EOL endpoints.
3. Separate untrusted PR jobs from protected credentialed smoke and deploy jobs.
4. Use synthetic inputs, transaction/generation ceilings, serialized jobs, and deterministic cleanup in any live lane.
5. Gate on secret scans, obsolete-route scans, negative cases, generated-file checks, and immutable artifact identity.
6. Treat skipped trusted tests as unknown and retain redacted receipts plus cleanup evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Repository and sandbox owners approve trusted live lanes; security approves secret access; product and budget owners approve any upload, generation, write, deploy, or deletion.

## Error Handling

- A 429 is not an acceptable successful assertion.
- Never auto-update fixtures from live customer data.
- Fail if a fork can request a secret-bearing environment.

## Output

Return the trust matrix, fixtures, gates, commands, live boundary, secret evidence, cleanup, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Prove a fork job has no Adobe secrets.
- Reject JWT, /sensei/cutout, and Lightroom Firefly Services routes statically.

## Validation

Exercise and record expected and observed results for:

- fork isolation
- secret canary
- contract drift
- 429
- obsolete route
- cleanup

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
