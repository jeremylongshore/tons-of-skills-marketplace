---
name: canva-ci-integration
description: 'Build credential-free Canva contract tests with a separately protected live read. Use when testing adapters, OAuth boundaries, OpenAPI drift, fork behavior, or deployment readiness. Trigger with: "test Canva in CI", "add Canva contract tests", "secure Canva GitHub Actions".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[test-command-and-protected-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - ci
  - operations
compatibility: 'The live lane requires a protected environment and dedicated low-privilege test user; forked code must never receive secrets.'
---

# Canva Fork-Safe CI Contract Lane

## Overview

Keep pull-request validation offline and deterministic. Reserve one minimal live read for trusted commits after environment protection, without rotating production tokens inside CI.

## Prerequisites

- Existing test framework and repository-defined command
- Pinned Canva OpenAPI snapshot or validated fixtures
- Protected environment with dedicated test integration and cleanup owner

## Instructions

### Step 1: Inventory workflow trust

Use Read and Grep to map pull-request events, fork execution, secret references, generated clients, artifact uploads, and any code path that creates Canva resources.

### Step 2: Define offline contracts

Use Write or Edit to test request construction, error parsing, explicit-scope checks, async job states, redaction, and unknown response fields against fixtures.

### Step 3: Pin provider inputs

Version the OpenAPI snapshot or its checksum and make drift visible. Do not silently regenerate clients during an unrelated test run.

### Step 4: Add a protected live read

Use an approved test user to call a non-mutating identity or metadata endpoint. Assert authorization and response shape, not volatile content.

### Step 5: Close secret boundaries

Do not use privileged pull-request events to run untrusted code. Keep client secrets and refresh tokens outside job logs, artifacts, caches, and fork contexts.

### Step 6: Emit exact-head evidence

Record commit, commands, fixture version, live endpoint pattern, protected environment, redaction result, and cleanup status.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

Every fork runs mocked OAuth and response fixtures. A protected main-branch job performs one user-identity read and fails closed when its expected credential is absent.

## Error Handling

| Failure | Response |
| --- | --- |
| Fork can reach secrets | Disable the job and correct the event/environment boundary |
| CI rotates refresh tokens | Move rotation to the application credential service |
| Fixture accepts unknown breakage | Update the pinned contract and review the diff |
| Live test creates content | Replace it with a non-mutating identity or metadata read |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [Latest OpenAPI](https://www.canva.dev/sources/connect/api/latest/api.yml)
