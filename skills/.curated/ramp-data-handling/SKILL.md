---
name: ramp-data-handling
description: >-
  Define collection, redaction, retention, access, and deletion controls for Ramp financial, identity, receipt, and card data. Use when designing storage, logs, support bundles, analytics, or card-detail delivery. Trigger with "Ramp data handling" or "Ramp PCI boundary".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[integration-or-environment]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Ramp Developer API documentation and approved access for any live financial, card, identity, accounting, application, or configuration change
tags: [saas, ramp, data-governance, privacy, pci]
---
# Ramp Financial Data Handling Controls

## Overview

Minimize the data plane before implementing controls. Keep card details outside application systems through Embedded Cards where possible, and treat transaction, receipt, user, and accounting data as sensitive business records.

## Prerequisites

- Identify the Ramp application, environment, business entities, affected data and workflows, accountable owner, and rollback boundary.
- Read `references/official-docs.md` and re-check endpoint schemas, scopes, limits, and support status before a live operation.
- Use synthetic fixtures or Ramp sandbox until production access and business effects are explicitly approved.
- Prepare approved secret storage and a sanitized evidence location.

## Current Contract

- Embedded Cards can render card details in a Ramp-hosted iframe so the application server does not receive PAN or CVV.
- Vault API delivery places full card data in the backend data plane and requires Ramp production approval plus the operator's own PCI program.
- OAuth tokens are opaque credentials and must never appear in logs, errors, analytics, or support artifacts.
- Monetary representations and sensitive fields vary by endpoint; use the current schema rather than a universal record assumption.

## Instructions

1. Build a field-level inventory for each endpoint, event, queue, database, log, metric, export, backup, and support path, with owner and business purpose.

2. Classify credentials, card data, identity data, receipts, merchant details, accounting codes, and derived analytics; remove fields without a necessary purpose.

3. Choose embedded iframe delivery unless an approved backend Vault use case requires card data; isolate any Vault service and prohibit general telemetry.

4. Apply encryption, least-privilege service and human access, tenant/entity partitioning, redaction, retention, deletion, backup, and legal-hold controls.

5. Test forbidden-field detection, access denial, tenant separation, deletion propagation, backup expiry, and incident escalation with synthetic sandbox data.

## Tool Discipline

- Use **Glob** to locate candidate code, manifests, fixtures, and evidence without widening scope.
- Use **Grep** to find relevant endpoints, fields, permissions, identifiers, errors, and stale assumptions.
- Use **Read** to inspect the smallest required local files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, configuration, or evidence artifact.
- Use **Edit** only for a bounded approved change with a known rollback.
- Local file tools do not authorize a Ramp operation or replace owner approval.

## Approval Boundaries

Security and privacy approve classifications and retention; finance/data owners approve business use; Ramp and PCI stakeholders approve production Vault handling.

## Output

A field inventory, data-flow diagram, classification matrix, minimized schemas, retention/deletion map, access evidence, redaction tests, and incident contacts.

## Error Handling

| Condition | Response |
|---|---|
| A token or PAN reaches logs | Contain access, stop ingestion, rotate credentials where relevant, preserve a restricted incident record, and remediate every downstream copy. |
| Deletion conflicts with a legal hold | Quarantine the record under documented legal authority and record the exception owner and expiry. |
| A derived metric can identify a person | Reclassify it and apply the same access, retention, and deletion controls as its source. |

## Examples

### Example 1

Redesign card display around Ramp's hosted iframe so the backend and support logs never receive full card details.

### Example 2

Create a receipt-retention schedule that deletes thumbnails, OCR text, warehouse copies, and backups on the same governed timeline.

## Validation

- Every retained field has a purpose, owner, classification, and retention rule.
- Secrets and card details are absent from routine logs, metrics, traces, and tickets.
- Tenant and entity isolation have both positive and negative tests.
- Deletion and incident procedures cover replicas, exports, backups, and vendor support evidence.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract and current OpenAPI schema before any live request.
- Treat unresolved vendor behavior, authority, or financial state as a stop condition.
