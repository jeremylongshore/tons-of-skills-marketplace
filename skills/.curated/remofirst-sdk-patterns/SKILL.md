---
name: remofirst-sdk-patterns
description: >-
  Build a supported RemoFirst integration boundary across Workday, ADP,
  reports, CSV, and provider-approved private contracts. Use when designing data
  exchange with RemoFirst. Trigger with "RemoFirst integration", "RemoFirst
  SDK", or "connect HRIS to RemoFirst".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-system> <workflow>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, workday, adp, data-exchange]
model: inherit
effort: high
compatibility: Designed for Claude Code; connector setup requires approved accounts in the participating systems
---
# RemoFirst Supported Integration Boundary

## Overview

Choose the narrowest documented exchange mechanism. The public first-party
contract covers named Workday and ADP connectors plus controlled platform
reports and CSV workflows; it does not establish a general RemoFirst SDK or API.

## Prerequisites

- Source system, business object, direction, cadence, owner, and lawful purpose.
- Data classification and approved minimum field set.
- Authorized RemoFirst and source-system administrators for connector changes.

## Current Contract

- Workday is a one-way inbound connector using a Workday integration system user
  and OAuth credentials; the RemoFirst operator starts sync manually.
- Supported Workday data is mapped before sync. Approved time-off and time-entry
  states matter; edits after sync may require reconciliation.
- Workday offboarding can be prefilled but requires human confirmation.
- ADP Workforce Now uses the RemoFirst connector and ADP SSO authorization.
- Reports and documented CSV templates are operator-controlled exports/imports.
- No public general SDK, endpoint, authentication, or versioning contract was found.

## Instructions

1. Classify the request as Workday inbound, ADP connection, report export,
   documented CSV workflow, manual platform operation, or private integration.
2. Reject a generic SDK design unless RemoFirst has issued a written contract to
   this customer. Record its owner and version without copying secrets.
3. Build a field-level map with source, destination, direction, required status,
   transformation, sensitivity, and accountable data owner.
4. For Workday, establish the least-privileged integration system user and OAuth
   client through Workday's approved administration path. Never store secrets here.
5. Test a minimal synthetic population, trigger the documented manual sync, and
   reconcile counts, fields, time rounding, approvals, and unsupported records.
6. For ADP, coordinate the connector and SSO flow while its temporary account ID
   is valid; verify the intended company before authorization.
7. For reports or CSV, preserve the documented schema, minimize sensitive rows,
   transfer through an approved channel, and reconcile import/export totals.
8. Define rollback as pausing the connector and returning to the prior controlled
   process; never assume a sync can reverse prior writes.

## Tool Discipline

Use Read, Glob, and Grep for schemas, mappings, and redacted samples. Use
Write/Edit for design and reconciliation artifacts. Do not authenticate, sync,
export production data, upload CSV, or modify either system.

## Approval Boundaries

Credential creation, connector authorization, production sync, worker export,
CSV upload, mapping change, and offboarding confirmation require accountable
human approval. Legal and privacy owners approve new data purposes.

## Output

Return selected boundary, direction, field map, identity model, status filters,
test cohort, reconciliation controls, approvals, rollback, and unresolved gaps.

## Error Handling

- Unsupported object/field: exclude it or use an approved manual control.
- Count or value mismatch: pause subsequent syncs and reconcile source states.
- Expired ADP setup value: restart the official authorization flow.
- Requested generic API/SDK: require a customer-specific provider contract.

## Examples

- Approved Workday time entries are tested with synthetic values before rollout.
- A report exchange records schema and totals but never commits worker rows.
- A proposed generic client library is rejected because no public SDK contract exists.

## Validation

- The selected mechanism exists in a reviewed first-party source.
- Direction, statuses, sensitive fields, approvals, and rollback are explicit.
- No fabricated SDK class, endpoint, token, or automatic-sync guarantee appears.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
Workday, ADP, reports, timesheet CSV, privacy, and support sources.
