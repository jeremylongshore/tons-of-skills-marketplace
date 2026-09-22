---
name: navan-deploy-integration
description: >-
  Deploy a Navan integration with tenant isolation, canary controls, and reversible data flow. Use when releasing an API, file, identity, or finance connector. Trigger with "deploy Navan integration", "release Navan connector", or "canary Navan sync".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <target> <canary-scope>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, deployment]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Integration Deployment

## Overview

Deploy a Navan integration with tenant isolation, canary controls, and reversible data flow. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Deployment binds the application adapter to a documented Navan surface and an approved destination. Separate ingestion, normalization, publication, and write-back so each can stop without losing evidence.

## Authentication

Inject a production secret by reference at runtime; bind tenant, host, scope, destination, and environment. Verify revocation and break-glass procedures before traffic.

## Instructions

1. Pin the reviewed artifact, contract revision, and configuration manifest.
2. Deploy dark with network or scheduling disabled.
3. Verify secret binding, egress allowlist, storage, redaction, and alert routing.
4. Enable a bounded tenant/window canary and collect reconciliation evidence.
5. Increase scope only after thresholds and owner review pass.
6. Keep rollback, replay protection, checkpoints, and raw evidence until acceptance.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Production enablement, egress, data movement, scheduling, scope expansion, and write-back require explicit service and data-owner approval.

## Error Handling

- Stop on tenant or destination mismatch.
- Do not roll forward through unexplained count or total drift.
- Rollback must preserve the ability to reconcile ambiguous deliveries.

## Output

Return artifact and contract IDs, canary scope, controls, metrics, reconciliation, approvals, and rollback receipt. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Dark-deploy a booking ingestion worker before scheduling it.
- Canary one legal entity for an expense export.

## Validation

Exercise disabled mode, revoked secret, egress denial, partial delivery, process restart, and rollback. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
