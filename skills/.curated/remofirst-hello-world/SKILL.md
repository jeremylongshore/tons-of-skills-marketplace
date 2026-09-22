---
name: remofirst-hello-world
description: >-
  Run a safe first RemoFirst client session and produce a redacted readiness
  receipt without opening worker records. Use when validating a newly activated
  account or orienting a new operator. Trigger with "RemoFirst first login",
  "RemoFirst readiness check", or "start RemoFirst".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<company> <operator-role>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, onboarding, readiness, hr]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst First-Session Readiness Check

## Overview

Verify that a new client operator can reach the right company and the minimum
navigation required for their job. This is a metadata-only orientation; it does
not list employees, download reports, approve payroll, or call an undocumented
API, and its outcome is a redacted readiness receipt and a list of access gaps.

## Prerequisites

- Completed `remofirst-install-auth` access review.
- The intended company, team, role, and first workflow.
- A safe evidence destination that excludes personal and payroll data.

## Current Contract

RemoFirst's client resource hub organizes work into account setup, hiring and
onboarding, payroll/payments/invoices, team management, benefits/compliance, and
offboarding. Access groups can hide or expose portions of those areas. A missing
menu item is therefore an access signal, not proof that a product feature is gone.

## Instructions

1. Write a preflight card with operator, company, expected groups, expected team,
   intended workflow, approver, and evidence-retention period.
2. Ask the operator to sign in using their own credentials and 2FA. Do not
   collect the password, authenticator code, recovery code, or session cookie.
3. Confirm the displayed company and non-sensitive profile metadata. Stop if the
   tenant is unexpected or if multiple companies are ambiguous.
4. Check only the navigation labels needed for the intended duty, such as People,
   Payroll, Invoices, Timesheets, or Company settings. Do not open a worker row.
5. Confirm the operator can reach the Help Center or in-platform support option.
6. Produce a PASS, LIMITED, or BLOCKED receipt with missing navigation and the
   narrow remediation owner. End the session without changing live data.

## Tool Discipline

Use Read, Glob, and Grep for local policy and readiness templates. Use Write or
Edit only for an approved redacted receipt. This skill does not drive the browser,
perform login, inspect worker data, or mutate RemoFirst configuration.

## Approval Boundaries

Require approval before opening People, Payroll, Invoices, documents, reports,
or any individual record. Visibility checks do not authorize exports, approvals,
invites, payment changes, or connector activation.

## Output

Return company identity, operator role, expected versus visible navigation,
support-path availability, receipt status, access gaps, owner, next review date,
and a list of prohibited or pending live actions.

## Error Handling

- Wrong tenant: sign out and escalate; do not browse for the intended company.
- Missing menu: compare the access matrix before requesting broader privileges.
- Login loop or rejected 2FA: follow the access-recovery runbook and support path.
- Personal data appears: stop capture and remove it from the redacted receipt.

## Examples

- A Payroll Manager who sees Payroll and Invoices but not worker documents can
  receive PASS for payroll-readiness without opening any payroll.
- A user who lands in the wrong company receives BLOCKED and no further browsing.
- A request to "list ten employees as a smoke test" is rejected as unnecessary.

## Validation

- No worker row, payroll amount, invoice, report, credential, or cookie was read.
- Tenant and minimum navigation match the preflight card.
- The receipt contains a status, evidence boundary, owner, and next action.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
client hub, activation, access-group, support, and platform sources.
