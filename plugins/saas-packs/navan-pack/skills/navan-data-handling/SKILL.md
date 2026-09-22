---
name: navan-data-handling
description: >-
  Manage Navan personal, corporate, travel, payment, receipt, profile, and location data across integrations. Use when defining collection, sharing, retention, or AI access. Trigger with "Navan data handling", "Navan privacy", or "classify Navan data".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workflow> <data-classes> <jurisdictions>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Travel and Expense Data Governance

## Overview

Manage Navan personal, corporate, travel, payment, receipt, profile, and location data across integrations. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan's privacy policy distinguishes Corporate Customer Data from other information and names itinerary, profile, passport, loyalty, payment, receipt, location, support, and usage data. Corporate customers remain responsible for lawful instructions and user rights where they act as controller.

## Authentication

Restrict access by purpose, role, tenant, environment, and data class. Third-party AI or MCP connections can process Navan personal information and therefore require an explicit approved boundary.

## Instructions

1. Inventory fields from source through every processor, store, artifact, and human workflow.
2. Classify controller/processor role, purpose, legal basis, jurisdiction, and sensitivity with counsel or privacy owner.
3. Minimize collection and separate business travel from personal travel information.
4. Set retention, deletion, access, portability, correction, and incident procedures.
5. Redact logs, fixtures, prompts, analytics, support bundles, and test artifacts.
6. Verify downstream contracts, access reviews, deletion propagation, and evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

New purposes, processors, AI/MCP use, cross-border transfers, sensitive fields, longer retention, or external sharing require data-owner and privacy approval.

## Error Handling

- Do not assume employer access to personal travel data.
- Opaque identifiers can still be personal data when linkable.
- Deletion requests need downstream and backup handling, not only source deletion.

## Output

Return a data inventory, role/purpose matrix, minimization decisions, retention schedule, rights workflow, and control evidence. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Exclude passport and loyalty data from an analytics feed.
- Review whether a support assistant may receive itinerary details.

## Validation

Trace representative records through access, correction, deletion, export, incident, and processor-offboarding paths. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
