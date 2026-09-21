---
name: navan-core-workflow-a
description: >-
  Implement a governed downstream booking-data workflow from Navan into an approved system. Use when consuming the Booking API or booking-data integration. Trigger with "sync Navan bookings", "ingest travel data", or "reconcile booking export".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<tenant> <destination> <sync-window>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, bookings]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Booking Data Ingestion

## Overview

Implement a governed downstream booking-data workflow from Navan into an approved system. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan publicly describes its Booking API as a way for downstream systems to access booking data. Endpoint shape, booking lifecycle states, pagination, correction behavior, and delivery cadence must come from the tenant documentation.

## Authentication

Use a dedicated read-only integration identity or transfer credential scoped to booking data. Traveler itinerary data is personal information and must remain within the approved destination and retention boundary.

## Instructions

1. Define the booking fields and business decisions the destination actually needs.
2. Capture the source schema, identifiers, timestamps, lifecycle states, and correction semantics.
3. Land immutable raw evidence in an access-controlled staging area.
4. Normalize time zones, currencies, traveler references, and status without losing source values.
5. Upsert or append according to documented semantics and quarantine conflicts.
6. Reconcile counts, sums, late changes, deletions, and destination acknowledgements.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Require data-owner approval for itinerary access, new destinations, backfills, retention changes, or any operation that could modify a Navan booking.

## Error Handling

- Never treat a missing page as an empty successful dataset.
- Quarantine unknown lifecycle states instead of coercing them.
- Freeze publication when reconciliation exceeds the agreed threshold.

## Output

Return source revision, extraction window, rows read/landed/rejected, reconciliation deltas, sensitive-field handling, and next checkpoint. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Reconcile yesterday's booking changes into a duty-of-care warehouse.
- Backfill a bounded period after a destination outage.

## Validation

Exercise empty windows, duplicate delivery, late correction, cancellation, partial page, currency variance, and destination rollback. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
