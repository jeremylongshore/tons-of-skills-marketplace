---
name: adobe-migration-deep-dive
description: >-
  Analyze and execute a multi-workload migration into or across Adobe services with contract evidence, dependency waves, dual-run reconciliation, cost controls, and rollback. Use when the task requires adobe platform migration program. Trigger with "Adobe migration plan", "move workflow to Adobe", or "Adobe platform consolidation".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-platform> <target-services> <migration-scope>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, program-migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Platform Migration Program

## Overview

Analyze and execute a multi-workload migration into or across Adobe services with contract evidence, dependency waves, dual-run reconciliation, cost controls, and rollback. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

A migration is a set of product-specific contracts, not an endpoint translation. Auth ownership, entitlement, async behavior, input/output fidelity, storage custody, content rules, limits, events, and operational tooling must each map from source to target. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Choose S2S or user auth per data owner, not migration convenience. Preserve source/target identity and access evidence and never copy secrets or production content into test fixtures.

## Instructions

1. Inventory source workflows, volumes, identities, data classes, formats, SLAs, costs, dependencies, and retirement constraints.
2. Map each capability to current Adobe service/version or classify it as gap, redesign, or retire; exclude EOL products.
3. Define adapters, canonical data contracts, idempotency, provenance, reconciliation, storage, and rollback boundaries.
4. Build synthetic and sampled approved parity tests for outputs, metadata, ordering, policy, latency, and cost.
5. Migrate in dependency waves with shadow/dual-run only where duplicate actions and spend are controlled.
6. Reconcile every wave, cut over from explicit thresholds, archive receipts, and remove approved obsolete paths and credentials.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Program, identity, security, data, product, budget, and operations owners approve their waves. Live content movement, dual writes, cutover, and deletion require separate explicit approval.

## Error Handling

- Do not claim parity from happy-path samples only.
- Do not map a retired Lightroom service to a different Lightroom API by name.
- Pause on count, content, provenance, authorization, or cost divergence.

## Output

Return capability map, contracts, wave plan, test corpus, parity evidence, decisions, cutover/rollback, cleanup, and owners. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Reconcile a synthetic PDF workflow across source and target.
- Classify a source capability with no current Adobe equivalent as a gap.

## Validation

Exercise and record expected and observed results for:

- auth mismatch
- format drift
- policy difference
- duplicate action
- cost drift
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
