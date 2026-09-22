---
name: canva-known-pitfalls
description: 'Analyze a Canva Connect implementation for recurring authorization, async-job, preview, data, and retry hazards. Use when reviewing code, preparing release, or investigating repeated failures. Trigger with: "review Canva pitfalls", "audit Canva integration", "find Canva anti-patterns".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workflow-or-review-scope]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - canva
  - review
  - operations
compatibility: 'Review uses repository and redacted runtime evidence; live mutation is outside this skill.'
---

# Canva Integration Hazard Review

## Overview

Turn common failure patterns into evidence-backed findings rather than universal rules. Reconfirm time-sensitive provider behavior against current first-party contracts before enforcing it.

## Prerequisites

- Repository scope, deployment/config version, and operation inventory
- Pinned OpenAPI, current docs, granted scopes, and preview surfaces
- Data policy, operation ledger, and redacted incident evidence

## Instructions

### Step 1: Review OAuth

Use Read and Grep to find browser-side secrets, missing state/PKCE validation, broad or implied scopes, refresh races, token logging, and incomplete disconnect cleanup.

### Step 2: Review authorization

Check tenant and resource ownership, application role, explicit scopes, capabilities, and preview availability before every Canva-side action.

### Step 3: Review async work

Find request handlers that block on long polling, lost job IDs, unbounded loops, duplicate submissions, and retries that do not reconcile existing state.

### Step 4: Review throttling

Find guessed global quotas, fixed sleeps, assumed response headers, cross-tenant queues, and missing endpoint/user isolation.

### Step 5: Review data and telemetry

Find cached signed URLs, retained content without purpose, token/profile logs, high-cardinality labels, and debug bundles without expiry or review.

### Step 6: Review release posture

Find unpinned provider contracts, preview features on public-review paths, mutable deploys, missing rollback, and live CI on untrusted events.

### Step 7: Record dispositions

Use Write or Edit to classify each finding with exact path/evidence, current provider source, severity, owner, safe fix, rollback, and verification test.

## Authentication

Canva Connect calls use Bearer access tokens obtained by a backend through OAuth 2.0 Authorization Code with SHA-256 PKCE. Request explicit least-privilege scopes, keep client secrets and tokens out of browser-visible state, and serialize refresh so the replacement single-use refresh token is stored atomically.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Canva-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

## Examples

A review finds automatic retry wrapping design creation. The finding requires an operation ledger and existing-job reconciliation, rather than simply increasing a retry count.

## Error Handling

| Failure | Response |
| --- | --- |
| Claim lacks a current source | Mark it unverified and do not enforce it |
| Finding exposes customer data | Redact the evidence and rotate access if needed |
| Fix expands scope | Require separate authorization and user consent |
| Preview feature is release-critical | Escalate the public-review incompatibility |

## Resources

- [First-party source notes](references/official-docs.md)
- [Authentication](https://www.canva.dev/docs/connect/authentication/)
- [API request model](https://www.canva.dev/docs/connect/api-requests-responses/)
