---
name: remofirst-upgrade-migration
description: >-
  Control a RemoFirst workflow cutover to supported Workday, ADP, report, or CSV
  exchange with reconciliation and rollback. Use when replacing a manual data
  handoff or changing a connector. Trigger with "migrate to RemoFirst", "RemoFirst
  cutover", or "change RemoFirst integration".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-process> <target-boundary>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, migration, workday, change-control]
model: inherit
effort: high
compatibility: Designed for Claude Code; production cutover requires authorized administrators and business owners
---
# RemoFirst Controlled Workflow Cutover

## Overview

Plan a reversible change from a manual/export process to a documented RemoFirst
connector or from one supported boundary to another. This is a business-data
cutover, not an API-version migration; no public general API version contract was
found in the reviewed first-party documentation.

## Prerequisites

- Current and target process owners, systems, populations, countries, and dates.
- Baseline counts/totals and an approved minimum field map.
- Change approver, privacy/security review, rollback owner, and support path.

## Current Contract

- Workday provides one-way inbound data to RemoFirst through mapped fields and a
  manually initiated sync.
- Approved time-off/time-entry state affects eligible Workday data; edits may not
  automatically resync, and time is subject to documented conversion/rounding.
- Workday offboarding data is prefilled but still needs human confirmation.
- ADP authorization uses its named connector, SSO flow, and temporary account ID.
- Reports and CSV workflows remain controlled alternatives for supported tasks.

## Instructions

1. Document the current process, target boundary, business objective, exclusions,
   accountable owners, freeze window, and success/abort criteria.
2. Inventory and classify fields. Map only documented target fields, record
   direction and transformations, and exclude unsupported or unnecessary data.
3. Establish least-privileged connector identities and approvals without copying
   credentials into the plan, repository, ticket, or support bundle.
4. Test with synthetic records, then a small approved cohort. Reconcile source and
   destination counts, values, status, time conversion, and ownership.
5. Run a time-boxed parallel period against the current controlled process. Keep
   one authoritative writer per field and prevent duplicate payroll actions.
6. At the change gate, obtain explicit business, system, security/privacy, and
   payroll approval. Start the production sync or authorization only then.
7. Reconcile immediately after cutover and again at the first payroll/invoice
   boundary. Human-confirm every offboarding or other irreversible action.
8. If an abort threshold is crossed, pause the connector, retain evidence, revert
   to the documented prior process, notify owners, and engage RemoFirst support.

## Tool Discipline

Use Read, Glob, and Grep on approved redacted maps, baselines, and results. Use
Write/Edit for plans and reconciliation records. Do not authorize connectors,
sync production data, upload worker files, approve payroll, or execute rollback.

## Approval Boundaries

Production credential creation, connector activation, sync, export/import,
offboarding confirmation, payroll impact, rollback, and decommissioning require
named human owners. New data purposes require privacy review.

## Output

Return current/target boundary, field map, test cohorts, parallel-run plan,
counts/totals baseline, approvals, success/abort thresholds, cutover sequence,
post-cutover checks, rollback, decommission criteria, and open risks.

## Error Handling

- Unsupported field/state: keep it in the approved manual process.
- Reconciliation mismatch: stop expansion and investigate before another sync.
- Duplicate or irreversible action risk: abort and require owner review.
- Missing private contract: do not reinterpret the change as an API migration.

## Examples

- A Workday pilot proves approved-time behavior before adding all employees.
- The old CSV control remains available through the first reconciled payroll.
- An offboarding prefill is reviewed by a human before confirmation.

## Validation

- Every field, action, approval, threshold, and rollback owner is explicit.
- Parallel results reconcile without exposing worker-level data in the artifact.
- No generic SDK, API version, automatic reversal, or zero-downtime claim appears.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
Workday, ADP, reports, timesheet, payroll, DPA, and support sources.
