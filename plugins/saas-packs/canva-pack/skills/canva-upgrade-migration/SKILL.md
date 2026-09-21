---
name: canva-upgrade-migration
description: 'Plan and verify a Canva Connect contract upgrade from pinned OpenAPI and changelog evidence. Use when endpoints, scopes, enums, validation, deprecations, or preview behavior change. Trigger with: "upgrade Canva API", "Canva breaking change", "diff Canva OpenAPI".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[current-contract-and-target-version]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - upgrade
  - operations
compatibility: 'Requires current and target contract artifacts, compatibility tests, feature flags, and rollback authority.'
---

# Canva Contract Upgrade

## Overview

Canva uses date-based Connect API versions while the path v1 is an epoch marker. Preview features may change without a new version, so upgrade evidence must include feature status and live protected checks.

## Prerequisites

- Current OpenAPI/checksum, generated code, and deployment version
- Target OpenAPI/changelog and affected operation inventory
- Compatibility suite, migration owner, rollout window, and rollback

## Instructions

### Step 1: Freeze both contracts

Use Read and Grep to record exact source URLs, retrieval times, bytes/checksums, API version metadata, generator version, and current deployed artifact.

### Step 2: Classify the diff

Review endpoints, methods, scopes, required inputs, validation, enums, response requiredness, error/status behavior, deprecations, and preview changes.

### Step 3: Map consumers

Find adapters, schemas, fixtures, policies, UI assumptions, queues, data stores, metrics, and runbooks that depend on each changed fact.

### Step 4: Build compatibility

Use Write or Edit to update code and add old/new fixtures for success, error, unknown additive fields, changed enums, async states, redaction, and rollback.

### Step 5: Protect authorization

Treat any scope or capability change as an authorization migration requiring portal configuration and possibly fresh user consent; never silently broaden.

### Step 6: Roll out gradually

Ship an immutable feature-flagged artifact to a protected environment, run mocked plus read-only live evidence, then expose a bounded cohort under local thresholds.

### Step 7: Reconcile and close

Roll back on drift, preserve job/resource identity across versions, remove deprecated code after the window, and record exact evidence and residual preview risk.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

An OpenAPI diff adds a response field and changes a preview enum. The adapter accepts the additive field, handles unknown preview values safely, and deploys behind a flag without changing scopes.

## Error Handling

| Failure | Response |
| --- | --- |
| Target contract is not pinned | Do not begin implementation |
| Scope changed | Stop for consent and authorization review |
| Preview behavior lacks compatibility | Disable that path or keep rollout experimental |
| Rollback cannot read new state | Add a reversible schema/adapter plan before release |

## Resources

- [First-party source notes](references/official-docs.md)
- [API versions](https://www.canva.dev/docs/connect/versions/)
- [Connect changelog](https://www.canva.dev/docs/connect/changelog/)
