---
name: workhuman-security-basics
description: 'Define shared-responsibility security controls for Workhuman identity, workforce data, recognition, awards, Store, and integrations. Use when reviewing threats or hardening controls. Trigger with "secure a Workhuman integration".'
argument-hint: "[tenant-or-workflow] [data-classification]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, security, privacy, governance]
model: inherit
effort: high
compatibility: Designed for Claude Code; security, privacy, SSO, privilege, retention, and integration changes require accountable owner approval
---
# Workhuman Security and Privacy Baseline

## Overview

Map customer and Workhuman responsibilities and enforce least privilege, data minimization, financial integrity, and evidence-based incident controls.

## Prerequisites

- Tenant products, integrations, data flows, environments, owners, and current agreements
- Workforce-data classification, retention, residency, legal, and incident requirements
- Identity, HCM, payroll, recognition, security, privacy, and vendor contacts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configurations and flows, `WebFetch` to verify current first-party commitments, and `Write` or `Edit` for threat models, control matrices, and redacted evidence.

## Current Contract

Workhuman publicly states support for SSO, fraud detection, granular user privileges and grouping, encryption and monitoring practices, GDPR and CCPA compliance, ISO 27001:2022 and ISO 27701:2019 certification, and defined PCI scope. Confirm scope and customer obligations in current agreements rather than treating marketing statements as the entire control contract.

## Authentication

Separate human SSO, administrator roles, managed connectors, and API principals. Enforce least privilege, tenant isolation, rotation, revocation, break-glass controls, and non-exportable secrets.

## Instructions

1. Diagram identity, worker, recognition, award, redemption, payment-adjacent, reporting, and integration data flows.
2. Classify fields and define purpose, authority, access, retention, residency, export, deletion, and incident ownership.
3. Review SSO, lifecycle, privileges, groups, delegates, separation of duties, dormant access, and emergency access.
4. Threat-model spoofing, cross-tenant access, unsafe messages, approval bypass, award manipulation, fraud, replay, and data exfiltration.
5. Verify encryption, secret storage, egress allowlists, audit evidence, anomaly detection, and redacted observability at each customer-controlled boundary.
6. Reconcile program spend and sensitive administrative actions with independent evidence and named approvers.
7. Test access removal, credential rotation, rejected inputs, duplicate writes, incident containment, and recovery with synthetic fixtures.
8. Present gaps with owner, severity, compensating control, due date, verification, and rollback before changing production.

## Approval Boundaries

Do not alter SSO, roles, groups, retention, exports, fraud controls, integrations, or financial workflows without security, privacy, and business-owner approval.

## Output

Return the responsibility and data-flow maps, access review, threat model, control evidence, gaps, approved changes, test receipts, and residual risks.

## Error Handling

| Condition | Response |
|---|---|
| Agreement scope is unavailable | Mark controls unverified and request the current customer documents. |
| Cross-tenant or financial-integrity risk appears | Stop affected processing and activate the approved incident path. |
| Required data has no owner or retention rule | Block the flow until governance is assigned. |

## Example

A redacted completion receipt might look like this:

```text
tenant=customer-prod; flows=7; principals=4; high-gaps=0; rotation=tested; spend-reconciliation=exact; residual-risk=accepted
```

## Resources

- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)
- [Workhuman privacy policy](https://www.workhuman.com/privacy-policy/)

## Next Steps

Schedule access, data-flow, contract-scope, and recovery reviews on the customer's governance cadence.
