---
name: canva-policy-guardrails
description: 'Implement repository and runtime controls for Canva Connect authorization, secrets, previews, data, retries, and CI trust. Use when converting integration policy into testable deny-by-default checks. Trigger with: "add Canva guardrails", "lint Canva integration", "enforce Canva policy".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[repository-path-and-policy-profile]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - policy
  - operations
compatibility: 'Requires an approved policy owner, repository scope, exception process, and current Canva contracts.'
---

# Canva Integration Policy Guardrails

## Overview

Encode high-confidence invariants close to the code and verify them again at runtime. Keep provider-dependent facts versioned so a stale numeric limit or preview assumption cannot become permanent policy.

## Prerequisites

- Policy document, owner, enforcement scope, and exception expiry
- Repository/runtime boundaries and pinned provider contract
- Current secret, scope, data, CI-event, and preview inventory

## Instructions

### Step 1: Classify controls

Separate immutable security controls from versioned provider-contract checks and local operational thresholds. Name the authority for each.

### Step 2: Add secret controls

Use Write or Edit to block client secrets/tokens in source, frontend bundles, logs, snapshots, artifacts, and untrusted CI; scan examples and failure paths too.

### Step 3: Add authorization controls

Require tenant/resource ownership, application policy, explicit minimum scopes, current capabilities, and preview status before dispatch.

### Step 4: Add operation controls

Require operation identity for mutations, bounded retry classification, async job reconciliation, and scoped queues for throttling.

### Step 5: Add contract controls

Pin OpenAPI or checksum, test unknown fields/statuses safely, detect deprecated/preview surface drift, and require review before regeneration.

### Step 6: Add evidence controls

Use Read and Grep to verify each rule fires on a failing fixture, cannot be bypassed by formatting, and produces a redacted reason with owner and exception path.

### Step 7: Govern exceptions

Make exceptions narrow, approved, time-bounded, visible in CI, and automatically fail after expiry.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A CI rule rejects Canva client secrets in browser configuration and privileged live tests on fork events; a runtime guard separately denies a design write without tenant ownership and explicit scope.

## Error Handling

| Failure | Response |
| --- | --- |
| Rule depends on stale numeric limit | Move the value to a versioned contract fixture |
| Exception has no expiry | Reject it |
| Guard logs protected input | Return only a stable reason code |
| Static rule cannot prove runtime ownership | Add a runtime deny-by-default check |

## Resources

- [First-party source notes](references/official-docs.md)
- [Connect security](https://www.canva.dev/docs/connect/guidelines/security/)
- [API versions](https://www.canva.dev/docs/connect/versions/)
