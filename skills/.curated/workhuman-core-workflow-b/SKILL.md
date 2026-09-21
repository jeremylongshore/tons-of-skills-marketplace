---
name: workhuman-core-workflow-b
description: 'Govern and reconcile Workhuman and Workday worker and award-data flows with explicit field authority and payroll controls. Use when operating the certified Workday integration. Trigger with "reconcile Workhuman and Workday".'
argument-hint: "[integration-scope] [reconciliation-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, workday, hris, reconciliation]
model: inherit
effort: high
compatibility: Designed for Claude Code; worker, award, compensation, payroll, and integration changes require HCM, payroll, security, and program-owner approval
---
# Workhuman and Workday Integration Reconciliation

## Overview

Operate the certified bidirectional integration with a field-level authority map, privacy controls, deterministic reconciliation, and owned exception handling.

## Prerequisites

- Current Workhuman-Workday implementation documentation and configured integration inventory
- HCM, payroll, security, privacy, and recognition-program owners
- Field mappings, schedules, populations, tax and gross-up rules, and recovery objectives

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect mappings and reports, `WebFetch` to re-check first-party integration claims, and `Write` or `Edit` for reconciliation logic, fixtures, and redacted receipts.

## Current Contract

Workhuman publicly states that its certified, prebuilt, bidirectional Workday integration treats Workday as the system of record for foundational and organizational worker data and Workhuman as the recognition and rewards system. Public pages also describe award data flowing to Workday compensation, payroll, and talent use cases.

## Authentication

Use the customer-approved managed-integration principals and Workday security groups. Keep each direction least-privileged, separately owned, rotated, and observable.

## Instructions

1. Freeze each direction, population, field, authority, transformation, cadence, checkpoint, and downstream use.
2. Classify worker, organization, recognition, award, compensation, payroll, and talent fields by privacy and retention.
3. Validate effective dating, worker identifiers, rehires, terminations, contingent workers, locales, currency, taxation, and gross-up ownership.
4. Produce synthetic fixtures for creates, changes, removals, duplicates, late records, partial batches, and rejected values.
5. Run a dry comparison and report additions, updates, exclusions, conflicts, and unknown mappings without applying them.
6. Present the mutation window, exact counts, principals, financial exposure, communications, abort thresholds, and rollback.
7. After all owners approve, canary one bounded cohort and reconcile both systems before broadening.
8. Preserve checkpoint and redacted exception evidence; route payroll or tax mismatches to their owners rather than auto-correcting.

## Approval Boundaries

Do not change worker records, award data, compensation, payroll inputs, tax handling, mappings, schedules, or integration principals without the respective owners.

## Output

Return the authority map, classified mappings, dry-run counts, approvals, canary receipt, bidirectional reconciliation, held exceptions, and recovery state.

## Error Handling

| Condition | Response |
|---|---|
| Systems disagree on an authoritative field | Stop that record and route it to the named field owner. |
| Batch is partially applied | Freeze the checkpoint, reconcile both directions, and execute the approved recovery plan. |
| Payroll or tax result is uncertain | Hold the award-data transition and escalate; never infer financial treatment. |

## Example

A redacted completion receipt might look like this:

```text
window=2026-09-10; worker-source=workday; award-source=workhuman; proposed=84; canary=10; conflicts=1-held; reconciliation=exact
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman and Workday integration overview](https://www.workhuman.com/blog/the-best-workday-integration-you-never-knew-about/)

## Next Steps

Review exception trends, field ownership, and recovery evidence with HCM, payroll, and program owners.
