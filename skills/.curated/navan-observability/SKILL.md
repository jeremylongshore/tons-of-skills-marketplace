---
name: navan-observability
description: >-
  Observe Navan integrations with content-free signals that support reconciliation and incidents. Use when defining logs, metrics, traces, and alerts. Trigger with "monitor Navan", "Navan observability", or "alert on Navan sync".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <service-objectives> <oncall>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, observability]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Integration Observability

## Overview

Observe Navan integrations with content-free signals that support reconciliation and incidents. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Operational signals should identify tenant alias, environment, surface, contract revision, window, stage, counts, timing, status class, and reconciliation state without exposing travel, payment, receipt, credential, or free-text content.

## Authentication

Telemetry backends receive no Navan secrets or authorization metadata. Restrict sensitive correlation mappings and raw evidence to the approved incident boundary.

## Instructions

1. Define freshness, completeness, correctness, latency, and recovery objectives.
2. Emit structured stage events with bounded labels and content-free identifiers.
3. Measure source reads, accepted records, quarantine, destination acknowledgements, and reconciliation deltas.
4. Alert on stalled checkpoints, repeated denial, contract drift, queue age, and unexplained totals.
5. Link alerts to status checks, runbooks, owners, and evidence locations.
6. Test dashboards and paging with synthetic failures.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

New telemetry processors, raw payload capture, sensitive label expansion, production tracing, and on-call routing changes require approval.

## Error Handling

- Do not use traveler email or booking detail as a metric label.
- HTTP success without reconciliation is not pipeline health.
- Suppressions must expire and retain an owner.

## Output

Return objectives, event schema, metric and alert catalog, redaction policy, dashboards, owners, and test receipts. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Alert when a booking window is read but not acknowledged downstream.
- Track expense quarantine by reason code without transaction content.

## Validation

Inject stale checkpoint, source denial, schema drift, destination failure, reconciliation mismatch, and redaction canaries. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
