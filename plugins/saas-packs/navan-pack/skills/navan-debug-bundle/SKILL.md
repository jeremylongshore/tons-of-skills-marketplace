---
name: navan-debug-bundle
description: >-
  Assemble a content-free Navan integration support bundle for operators or vendor escalation. Use when triage needs reproducible evidence. Trigger with "collect Navan diagnostics", "Navan support bundle", or "sanitize Navan logs".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <time-window> <incident-id>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, diagnostics]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Sanitized Support Bundle

## Overview

Assemble a content-free Navan integration support bundle for operators or vendor escalation. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

A useful bundle proves configuration shape, contract revision, timing, counts, checksums, and failure class without containing credentials, traveler identity, itinerary, payment, receipt, or free-text content.

## Authentication

Record credential source, age band, and scope label only. Never include tokens, client secrets, cookies, file-transfer keys, authorization headers, or raw identity responses.

## Instructions

1. Define the incident window and minimum evidence questions.
2. Collect version, tenant alias, environment, surface, operation, and contract revision.
3. Add redacted request/response schemas, counts, timings, status class, and correlation identifiers.
4. Hash artifacts and scan them for credentials and sensitive fields.
5. Generate a manifest showing every included and excluded item.
6. Require review before transmitting the bundle outside the approved boundary.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Reading local sanitized evidence is allowed; collecting live data or sending any bundle to Navan or another party requires data-owner and incident-owner approval.

## Error Handling

- Do not solve redaction by replacing only obvious email addresses.
- Free-text support fields can contain passports, receipts, or itineraries.
- If sensitivity cannot be established, keep the artifact local and escalate.

## Output

Return a bundle manifest, checksums, redaction report, evidence gaps, intended recipient, and approval record. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Share a schema mismatch with field names but no values.
- Prove repeated transfer failures using timestamps and content hashes.

## Validation

Run secret, personal-data, archive-path, and recipient-boundary checks before release. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
