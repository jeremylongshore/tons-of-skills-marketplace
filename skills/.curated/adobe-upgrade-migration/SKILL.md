---
name: adobe-upgrade-migration
description: >-
  Migrate Adobe integrations away from Service Account JWT, Photoshop v1, retired Lightroom Firefly Services, or drifting SDK/API contracts with canaries and rollback. Use when the task requires adobe end-of-life and contract migration. Trigger with "upgrade Adobe integration", "migrate Adobe JWT", or "Photoshop v2 migration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-contract> <target-contract> <cutover-window>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe End-of-Life and Contract Migration

## Overview

Migrate Adobe integrations away from Service Account JWT, Photoshop v1, retired Lightroom Firefly Services, or drifting SDK/API contracts with canaries and rollback. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

Service Account JWT is deprecated. Photoshop API v1 and the Firefly Services Lightroom API are already end-of-life; Remove Background uses Photoshop v2. Do not conflate the retired Lightroom service with separate Lightroom consumer APIs; confirm the dated retirement evidence in the reference map. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Preserve current and target credential, organization, scopes, profiles, and last-use evidence during auth migration. Old-secret or old-credential deletion is irreversible and happens only after verified cutover.

## Instructions

1. Inventory JWT code/configuration, endpoint versions, Lightroom service calls, SDK locks, fixtures, dashboards, and runbooks.
2. Trace every behavior to current first-party docs and classify supported, deprecated, retired, undocumented, or environment-observed.
3. Define target OAuth, Photoshop v2, replacement/retirement, adapter, data, and rollback contracts.
4. Build parity fixtures and dual-run or shadow-read comparisons where they do not duplicate spend or writes.
5. Canary the target, verify outputs and observability, then cut traffic under declared thresholds.
6. Remove obsolete paths and approved credentials, scan for residue, and publish cutover plus rollback receipts.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Identity/security owners approve auth changes and deletions; product/data owners approve API replacement and live comparisons; release owner approves cutover and rollback.

## Error Handling

- Do not leave JWT or v1 as a production fallback.
- Do not substitute a similarly named Lightroom API without contract proof.
- Roll back on output, authorization, storage, spend, or event drift.

## Output

Return the inventory, evidence classification, target design, compatibility tests, canary comparison, cutover decision, cleanup scan, and rollback. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Detect and reject /sensei/cutout in code and docs.
- Prove a rotated OAuth secret before deleting the old one.

## Validation

Exercise and record expected and observed results for:

- JWT residue
- Photoshop v1
- Lightroom EOL
- SDK drift
- canary mismatch
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
