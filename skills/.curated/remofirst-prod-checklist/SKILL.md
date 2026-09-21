---
name: remofirst-prod-checklist
description: >-
  Review and gate a RemoFirst payroll and invoice cycle with deadline, amount, approval,
  payment-method, and escalation checks. Use when preparing final payroll
  approval or invoice funding. Trigger with "approve RemoFirst payroll", "RemoFirst payroll
  checklist", or "RemoFirst invoice readiness".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<payroll-period> <country-or-team-scope>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, payroll, invoices, change-control]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Payroll and Invoice Production Gate

## Overview

Create a two-person control gate before payroll approval and invoice payment that
tracks RemoFirst's documented early-month revisions, provider review, client
final approval, invoice generation, and prompt payment. Dates may
vary by calendar or worker schedule, so confirm the live period rather than
turning examples into universal guarantees.

## Prerequisites

- Payroll period, countries/teams, employee population, and payroll owner.
- Approved source records for salary, time, leave, expenses, and adjustments.
- Finance approver and verified payment method.

## Current Contract

- The general guide places expense approvals and revisions by the third working
  day, provider review on days one through seven, and client approval around days
  eight through ten with two business days before default approval.
- Approval generates an invoice; delayed approval or payment can delay salaries.
- Additional payments require type, currency, amount, reason, and notes.
- Hourly-worker cutoffs can be schedule-specific; late submission or approval may
  move payment to the next cycle.

## Instructions

1. Freeze the live payroll calendar: period, cutoffs, expected approval window,
   invoice due date, funding lead time, pay date, holidays, and timezone.
2. Reconcile population against prior period: starters, leavers, country/team,
   pay frequency, and status. Investigate every unexplained change.
3. Reconcile base compensation, approved time, time off, expenses, bonuses,
   commissions, deductions, benefits, currency, and reason notes.
4. Separate data preparer, payroll approver, and payment approver. Record any
   exception to separation of duties with owner and compensating review.
5. Review each changed employee and aggregate totals. Request changes rather than
   approving a payroll whose source or calculation is unresolved.
6. Before approval, capture redacted counts/totals and an evidence hash; never
   copy worker-level payroll into a repository.
7. After human approval, reconcile generated invoice, currency, total, payment
   method, due date, and accounting visibility. Escalate discrepancies promptly.

## Tool Discipline

Use Read, Glob, and Grep on approved redacted control artifacts. Use Write/Edit
only for checklists and reconciliation summaries. Do not approve payroll, change
payments, download worker reports, or fund an invoice.

## Approval Boundaries

Final payroll approval, Request changes, additional payment, bank setup, invoice
payment, auto-payment change, or default-approval reliance requires explicit
human authority. Never treat silence as safe approval in this workflow.

## Output

Return calendar, population and financial reconciliation, exception list,
preparer/approvers, evidence hash, payroll decision state, generated-invoice
reconciliation, payment readiness, blockers, and escalation owner.

## Error Handling

- Payroll not ready: wait for provider notification; do not force a state change.
- Missing/incorrect amount: request changes with source-backed reason.
- Cutoff missed: surface the documented next-cycle risk and notify owners.
- Invoice mismatch or unverified payment method: block funding and escalate.

## Examples

- "Approve because the deadline is close" remains BLOCKED with an unresolved total.
- A clean cycle records counts/totals and approvers without worker-level details.
- A late hourly timesheet is flagged for schedule confirmation, not silently added.

## Validation

- Calendar and totals are tied to the live period and source evidence.
- Preparer, payroll approver, and payment approver are identified.
- No unresolved discrepancy, sensitive export, or unauthorized action is hidden.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
payroll, invoice, expense, timesheet, payment-method, and support sources.
