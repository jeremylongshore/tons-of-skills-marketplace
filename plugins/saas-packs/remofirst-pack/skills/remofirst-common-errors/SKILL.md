---
name: remofirst-common-errors
description: >-
  Debug RemoFirst contractor payment, invoice, timesheet, and access failures
  with evidence-safe decision paths. Use when a payment is late, mismatched,
  returned, unreconciled, or blocked. Trigger with "RemoFirst payment issue",
  "RemoFirst PRID", "contractor not paid", or "RemoFirst invoice error".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<issue-type> <redacted-payment-reference>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, troubleshooting, contractor-payments, invoices]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Payment and Workflow Error Triage

## Overview

Classify a RemoFirst operational failure before suggesting a correction while
keeping payment state, bank settlement, invoice reconciliation, timesheet
approval, and account visibility separate. A dashboard status such as Paid is evidence of
platform state, not proof that funds reached the receiving account.

## Prerequisites

- A redacted issue summary, expected outcome, event time, and affected period.
- The authorized payment or workflow owner and escalation contact.
- Access to approved evidence without copying bank or identity data.

## Current Contract

- Delayed funds may require Proof of Payment, ISO/MX evidence, or an MT103 trace
  coordinated through RemoFirst; do not invent a transfer status.
- A wrong or missing Payment Request ID can prevent automatic reconciliation.
- Issued invoice changes require RemoFirst; approved credits apply later, while
  overpayments are refunded rather than credited to a future invoice.
- Unsigned agreements, incomplete onboarding gates, unapproved timesheets, or
  non-compliant invoices can block contractor payment.

## Instructions

1. Classify the issue as access, onboarding gate, timesheet, invoice, PRID,
   client funding, in-transit delay, returned payment, amount mismatch, or other.
2. Build a redacted timeline: expected amount/currency, invoice period, submitted
   and approved dates, payment status changes, and first observed failure.
3. For access or missing objects, verify tenant and group scope before requesting
   broader permissions. Never treat missing visibility as a deleted record.
4. For timesheet/invoice blocks, reconcile agreement, onboarding gates, approved
   hours, invoice, PRID, and client payment in sequence.
5. For delayed funds, request provider-approved trace evidence. Do not tell the
   contractor to retry, change bank details, or accept direct payment by default.
6. For correction, recall, refund, or urgent reprocessing, obtain finance and
   RemoFirst approval and record the duplicate-payment risk.
7. Close only on verified resolution or a provider ticket with owner, promised
   next update, and a privacy-safe evidence index.

## Tool Discipline

Use Read, Glob, and Grep to inspect redacted reconciliation records. Use Write or
Edit only for approved timelines, decision logs, and support drafts. Do not query
live accounts, execute payments, or store bank and identity fields.

## Approval Boundaries

Require approval before invoice correction, refund, recall, reprocessing, direct
payment, bank-detail change, timesheet decision, or privilege change. Never infer
legal, tax, sanctions, or banking conclusions from a symptom.

## Output

Return classification, redacted timeline, expected versus observed state, checked
gates, evidence available/missing, safest next action, owner, escalation channel,
duplicate-payment risk, and actions requiring explicit approval.

## Error Handling

- Paid but not received: classify as settlement delay and request trace evidence.
- Wrong PRID: stop further payment and request reconciliation support.
- Incorrect invoice: do not alter source records; request provider correction.
- Ambiguous duplicate: freeze reprocessing until finance reconciles both paths.

## Examples

- "Paid status, no funds after five days" yields a trace-ready timeline.
- "Pay again while the recall is pending" is blocked for duplicate-payment risk.
- "Change the contractor bank account" requires identity-safe provider handling.

## Validation

- One issue class and one accountable owner are named.
- Timeline and evidence contain no bank, identity, credential, or worker document.
- Corrective actions are provider-grounded and approval-gated.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
payment troubleshooting, invoice, onboarding, timesheet, and support sources.
