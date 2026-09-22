---
name: navan-incident-runbook
description: >-
  Manage containment, reconciliation, and recovery for a Navan integration incident. Use when handling credential, privacy, booking, expense, identity, or delivery failures. Trigger with "Navan incident", "Navan outage", or "Navan data exposure".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-id> <surface> <severity>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, incident]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Integration Incident Command

## Overview

Manage containment, reconciliation, and recovery for a Navan integration incident. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

The source of truth spans Navan, the integration, and downstream systems. Recovery is incomplete until credentials, data windows, financial totals, traveler impact, and destination acknowledgements are reconciled.

## Authentication

Use break-glass access only under the documented incident process. Never paste tokens or traveler data into chat, tickets, status updates, or unapproved AI tools.

## Instructions

1. Declare commander, scope, severity, timeline, and communication boundary.
2. Contain schedules, writes, transfers, credentials, or destinations without erasing evidence.
3. Preserve sanitized logs, checkpoints, schemas, counts, hashes, and approvals.
4. Determine source, destination, traveler, privacy, security, and finance impact.
5. Reconcile the affected window before replay or reopening writes.
6. Recover gradually, monitor, close temporary access, and assign follow-ups.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Credential rotation, replay, backfill, write enablement, customer communication, legal notification, and evidence sharing require the authorized incident roles.

## Error Handling

- Containment comes before reproduction.
- Do not replay an unknown-outcome write blindly.
- Vendor status alone does not prove local recovery.

## Output

Return incident state, timeline, affected windows, containment, exposure assessment, reconciliation, recovery gates, and owners. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Rotate a suspected transfer key and reconcile missed files.
- Pause expense publication after a tenant-mapping error.

## Validation

Tabletop credential leak, personal-data exposure, vendor outage, schema drift, duplicate replay, and destination corruption. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
