---
name: remofirst-security-basics
description: >-
  Review RemoFirst account, group, report, connector, and worker-data controls.
  Use when onboarding an operator, auditing access, or preparing a sensitive
  workflow. Trigger with "RemoFirst security", "review RemoFirst access", or
  "RemoFirst least privilege".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<operator-or-workflow> <scope>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, security, privacy, access-control]
model: inherit
effort: high
compatibility: Designed for Claude Code; account and group changes require an authorized RemoFirst administrator
---
# RemoFirst Security and Privacy Baseline

## Overview

Produce an evidence-based access and data-handling review for RemoFirst client
operations. Focus on interactive account security, explicit group assignment,
least data, controlled exports, connector credentials, and escalation.

## Prerequisites

- Named operator or service integration, business duty, countries, and teams.
- Current group membership and workflow inventory from an authorized source.
- Privacy, security, and business owners for exceptions.

## Current Contract

- Client users can enable authenticator-based two-factor authentication and
  receive a one-time recovery code that is replaced after use.
- A manager without an assigned group receives Superuser access by default.
- Groups constrain access by responsibility and team; direct-manager assignment
  is a separate workforce relationship.
- Reports may contain payroll, invoice, time-off, and worker information.
- Workday connector credentials originate in Workday; they are secrets.
- The reviewed public sources describe GDPR/DPA handling but not a general API key.

## Instructions

1. Inventory each identity, accountable owner, duty, group, team scope, last
   review, two-factor state, and termination/change trigger.
2. Treat no-group assignment as high risk because the documented default is
   Superuser. Assign the narrowest group through an authorized administrator.
3. Require two-factor authentication for client operators. Confirm recovery-code
   custody without collecting the code or any authenticator seed.
4. Separate workforce reporting lines from application permission groups; verify
   both independently when a manager changes role or team.
5. Inventory reports, CSV files, support attachments, and reconciliation
   artifacts. Minimize fields, redact identifiers, encrypt approved transfers,
   and define retention/deletion.
6. Keep Workday OAuth material and any provider-issued private credential only in
   an approved secret manager. Record owner and rotation evidence, not values.
7. Verify the applicable DPA and lawful purpose with privacy owners before adding
   a new data flow, country, integration, or support attachment.
8. Capture exceptions with risk owner, compensating control, expiry, and review date.

## Tool Discipline

Use Read, Glob, and Grep on approved redacted inventories and policies. Use
Write/Edit for the review artifact. Do not reveal secrets, recovery codes, bank
details, identity files, tax documents, payroll rows, or production exports.

## Approval Boundaries

Group changes, Superuser access, two-factor reset/disable, credential issuance,
report download, worker-data disclosure, DPA acceptance, and exception approval
require the appropriate human authority.

## Output

Return identity/group matrix, two-factor status, default-Superuser findings,
data-flow and export inventory, credential controls, retention, DPA status,
exceptions, owners, and remediation dates without sensitive values.

## Error Handling

- Unknown group: treat access as unverified and escalate to an administrator.
- Lost second factor: use the official recovery/support path; never bypass it.
- Sensitive file in an unsafe location: restrict access and invoke incident policy.
- Unclear legal basis or DPA: stop the new flow pending privacy review.

## Examples

- A manager with no group is flagged for immediate least-privilege review.
- A support bundle reports affected record IDs only after approved redaction.
- A credential inventory records vault reference and owner, never the secret.

## Validation

- Every identity and sensitive flow has an owner, purpose, scope, and review date.
- Two-factor, group default, exports, connectors, and DPA are addressed.
- The artifact contains no secret or worker-level sensitive value.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
two-factor, groups, manager, reports, Workday, DPA, and support sources.
