---
name: adobe-sdk-patterns
description: >-
  Create narrow, version-pinned Adobe SDK and REST adapters with typed contracts, redaction, bounded polling, and compatibility evidence. Use when writing or upgrading integration code. Trigger with "Adobe SDK patterns", "wrap Adobe API", or "review Adobe client".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<language> <services> <operations>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, sdk]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Versioned Adapter Patterns

## Overview

Create narrow, version-pinned Adobe SDK and REST adapters with typed contracts, redaction, bounded polling, and compatibility evidence. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

SDK package versions and REST product versions change independently. Keep auth, transport, schema validation, returned status URLs, request identifiers, storage custody, and retry classification behind service-specific interfaces. The retired Lightroom Firefly Services SDK is excluded. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Inject a credential provider; never let callers pass raw secrets. Bind every client to environment, organization/project, service, scopes, product profiles, and redaction policy.

## Instructions

1. Inventory languages, package locks, direct REST calls, generated snippets, and target operations.
2. Pin supported SDK versions and trace every operation to its current REST documentation.
3. Define typed service adapters that preserve unknown fields and structured vendor error evidence.
4. Centralize token reuse, header construction, request IDs, timeouts, retry budgets, and signed-URL redaction.
5. Implement async polling by following returned status URLs with terminal-state and cancellation guards.
6. Run offline contracts plus one approved sandbox compatibility canary and publish the matrix.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Code owners approve adapter changes; security approves auth and URL handling. Any live write, generation, upload, cancellation, or deletion requires product-owner approval.

## Error Handling

- Do not hardcode a remembered latest SDK or endpoint version.
- Do not reconstruct status URLs when the response returns one.
- Quarantine unknown terminal states and additive response shapes.

## Output

Return dependency evidence, adapter interfaces, auth binding, schemas, fixtures, compatibility results, migration notes, and owner. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Accept an additive response field without dropping required evidence.
- Reject a retired Lightroom client at build time.

## Validation

Exercise and record expected and observed results for:

- SDK drift
- REST version drift
- unknown status
- 429
- signed URL redaction
- retired client

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
