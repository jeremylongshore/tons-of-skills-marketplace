---
name: remofirst-core-workflow-b
description: >-
  Manage RemoFirst contractor onboarding from engagement choice through
  agreement, identity, tax, bank, timesheet, invoice, and first-payout readiness.
  Use when engaging or paying an international contractor. Trigger with
  "onboard RemoFirst contractor", "contractor payout readiness", or "RemoFirst
  contractor payment".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<contractor-country> <rate-type> <first-payment-period>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, contractors, payments, compliance]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Contractor Onboarding and First Payout

## Overview

Prepare a contractor engagement and first-payment control record while treating
contractor and EOR engagements as different classification, benefit, control,
and compliance decisions. RemoFirst's documented contractor path is dashboard-operated and
requires agreement, tax, identity, bank, invoice, and payment checkpoints.

## Prerequisites

- Approved engagement model, country, work scope, term, rate, and currency.
- Authorized signatory, line manager, and payment owner.
- A classification review and approved personal-data handling path.

## Current Contract

- Rate types include monthly, daily, hourly, and milestone; available currencies
  and payment frequency belong to the live engagement context.
- The client may generate an agreement in RemoFirst or upload a pre-signed one.
- Contract signing enables timesheet submission; first payout also depends on tax
  forms, identity verification, bank details, and compliant invoicing.
- Approved hours link to an invoice, and payments are processed only after the
  client funds the required payment. A status is not a bank-settlement guarantee.

## Instructions

1. Record why contractor—not EOR—is approved, plus country, scope, term, rate
   type, amount, currency, frequency, manager, signatory, and payment owner.
2. Choose generated or pre-signed agreement handling. Record that RemoFirst does
   not accept legal responsibility for a client-uploaded pre-signed agreement.
3. Reconcile contractor, job, compensation, IP, confidentiality, and signatory
   fields before sending an invitation. Require two-person review for money.
4. Track agreement signature, tax form, identity verification, bank details, and
   invoice readiness as separate gates. Do not mark payout-ready from one gate.
5. For hourly work, review or reject the submitted timesheet. Approval locks the
   entry for payment; rejection must carry a clear correction reason.
6. Match the approved period and hours to the invoice and correct Payment Request
   ID. Confirm client funding without recording bank data in the artifact.
7. Close only when the contractor can see the expected status and the payment
   owner has a documented exception/escalation path.

## Tool Discipline

Use Read, Glob, and Grep for approved scope, classification, and payment records.
Use Write/Edit only for redacted checklists and reconciliation artifacts. This
skill does not invite, sign, approve, reject, fund, or deactivate live records.

## Approval Boundaries

Require approval for engagement classification, agreement path, invitation,
rate/currency/frequency, timesheet decision, invoice payment, refund, direct
payment, conversion to employee, and offboarding. Do not make legal conclusions.

## Output

Return engagement decision, commercial terms, gate matrix, timesheet/invoice
reconciliation, PRID verification state, funding owner, blockers, approvals,
and the exact next human-operated action.

## Error Handling

- Classification uncertain: stop and route to qualified legal/provider review.
- Unsigned agreement: block timesheet and payout readiness.
- Missing tax/identity/bank/invoice gate: keep payout BLOCKED.
- Amount or PRID mismatch: do not pay; use the correction/escalation workflow.

## Examples

- "Ready this hourly contractor for first payment" produces a six-gate checklist
  and invoice reconciliation, not a payment instruction.
- "Skip identity verification because the contract is signed" is rejected.
- "Convert them to employee" routes to a separately approved transition workflow.

## Validation

- Classification and all commercial terms have named approvers.
- Agreement, tax, identity, bank, invoice, and funding gates are independent.
- No bank detail, identity document, credential, or invented API appears in output.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
contractor onboarding, agreement, timesheet, payment, and troubleshooting sources.
