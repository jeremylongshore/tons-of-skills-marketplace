---
name: remofirst-local-dev-loop
description: >-
  Rehearse RemoFirst imports, report reconciliation, and operator controls
  offline with synthetic fixtures before touching a client account. Use when
  testing CSV mappings, payroll controls, or connector cutovers. Trigger with
  "RemoFirst local rehearsal", "test RemoFirst import", or "RemoFirst dry run".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workflow> <fixture-directory>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, testing, reconciliation, data-import]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Offline Workflow Rehearsal

## Overview

Validate mappings and controls with synthetic data against RemoFirst's documented
dashboard reports, two-column contractor-timesheet CSV upload, and named
Workday/ADP connectors, which do not include a general public sandbox API. A local loop must therefore model
documented inputs and decisions without claiming provider execution parity.

## Prerequisites

- The workflow and current first-party source that defines its fields.
- A fixture directory containing synthetic—not anonymized production—records.
- Expected counts, invariants, failure cases, and approval owner.

## Current Contract

- Contractor monthly timesheet CSV requires exactly `Email` and `Total Monthly
  Hours`; emails must match active accounts and hours allow up to two decimals.
- Downloadable reports include employee and contractor data and are sensitive.
- Workday mapping and sync semantics are documented separately; local fixtures
  are a model and cannot prove live connector behavior.

## Instructions

1. Name the workflow, source article, fixture schema, assumptions, and the provider
   behavior that the rehearsal explicitly cannot prove.
2. Generate synthetic identities, countries, amounts, dates, and record keys.
   Reject copied or merely masked production rows.
3. Encode field names, types, required/optional rules, uniqueness, rounding, and
   allowed state transitions from the reviewed source.
4. Add positive fixtures plus missing header, duplicate, invalid decimal, unknown
   identity, wrong period, stale mapping, and unsafe-field cases.
5. Run deterministic parsing and reconciliation: input, accepted, rejected,
   duplicate, and output totals must balance.
6. Produce a preview and rollback/checkpoint design. Do not create a live import
   file until a human approves both mapping and data source.
7. Mark PASS only for local controls. Record live validation as PENDING and assign
   an approved operator for the later dashboard step.

## Tool Discipline

Use Read, Glob, and Grep to inspect schemas and fixtures. Use Write/Edit only for
approved synthetic fixtures, mappings, tests, and reports. Do not log in, download
live reports, upload CSV, or access a private interface.

## Approval Boundaries

Require approval before using any export, generating a live upload, opening a
worker record, or running the documented dashboard/connector operation. Local PASS
does not authorize production use.

## Output

Return workflow/source, synthetic-fixture manifest, mapping version, invariants,
test matrix, reconciliation counts, assumptions, unproven provider behavior,
rollback design, live-validation owner, and approval state.

## Error Handling

- Production-like data detected: quarantine and replace with synthetic fixtures.
- Schema source missing: block; do not infer fields from stale examples.
- Reconciliation mismatch: fail without producing a candidate upload.
- Provider behavior unknown: label it PENDING rather than simulating certainty.

## Examples

- A contractor-hours fixture with the two documented headers can test decimals,
  duplicates, and unknown users without containing real email addresses.
- "Download production workers for better fixtures" is rejected.
- A local Workday mapping test states that it cannot prove scheduled sync behavior.

## Validation

- Fixtures are demonstrably synthetic and contain no credentials or personal data.
- Counts balance and every rejected case has a deterministic reason.
- Local and live acceptance criteria are clearly separated.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
timesheet, report, Workday, ADP, payroll, and support contracts.
