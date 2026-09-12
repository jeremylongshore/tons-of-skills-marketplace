---
name: navan-prod-checklist
description: >-
  Audit whether a Navan integration is ready for production using evidence and rollback criteria. Use when preparing to enable a live API, transfer, identity, or finance workflow. Trigger with "ship Navan integration", "Navan go-live", or "Navan production checklist".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <environment> <change-window>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, production]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Production Readiness Gate

## Overview

Audit whether a Navan integration is ready for production using evidence and rollback criteria. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Production readiness binds one documented tenant contract to one identity, destination, data purpose, operating window, and rollback plan. A successful sandbox or fixture test is necessary but not sufficient.

## Authentication

Confirm production credential provenance, least privilege, rotation, revocation, host binding, break-glass ownership, and separation from non-production.

## Instructions

1. Freeze the approved contract revision and change scope.
2. Review security, privacy, retention, accounting, and traveler-impact controls.
3. Prove offline tests, non-production smoke, reconciliation, monitoring, and alert routing.
4. Define canary scope, success thresholds, stop conditions, and rollback owner.
5. Verify runbooks for credential, schema, vendor, destination, and data incidents.
6. Collect named approvals and record the exact release receipt.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Require service, Navan admin, security, data, and finance owners as applicable; no checklist completion can self-authorize production writes or traveler impact.

## Error Handling

- A missing owner or rollback signal is a no-go.
- Do not accept aggregate totals without record-level lineage controls.
- Unknown contract drift blocks release.

## Output

Return GO, CONDITIONAL GO, or NO-GO with evidence, owners, canary, monitoring, rollback, and expiry of the decision. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Approve a read-only booking feed with a one-day canary.
- Block an expense posting workflow whose reversal path is untested.

## Validation

Conduct a tabletop for credential revocation, partial delivery, schema drift, destination outage, and rollback. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
