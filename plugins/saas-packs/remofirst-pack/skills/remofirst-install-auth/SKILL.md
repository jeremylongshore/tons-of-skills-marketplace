---
name: remofirst-install-auth
description: >-
  Prepare secure RemoFirst client access with account activation, 2FA, billing
  contacts, and least-privilege manager groups. Use when onboarding an operator
  or repairing access without inventing API credentials. Trigger with
  "RemoFirst access", "RemoFirst 2FA", "RemoFirst roles", or "activate
  RemoFirst account".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<client-role> <company-or-team>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, authentication, access-control, hr]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Secure Access Readiness

## Overview

Prepare a human-operated RemoFirst account without fabricating an API key, base
URL, SDK, or machine credential; the reviewed public contract covers client
account activation, password login, optional 2FA, manager groups, and named
Workday or ADP connector setup. Treat any custom API access as unavailable until
RemoFirst supplies a customer-specific written contract.

## Prerequisites

- A RemoFirst welcome invitation for the intended person.
- The company, team, billing contact, and required operator duties.
- An approved password manager and 2FA recovery-code storage location.

## Current Contract

- Client activation starts from the welcome email and requires a password,
  acceptance of terms, company review, and at least one billing contact.
- Client 2FA uses an authenticator application and a one-time recovery code.
- Manager groups separate PTO, expense, payroll, finance, people, and team-admin
  duties. Selecting no group defaults the user to Superuser.
- Public first-party sources do not publish a general RemoFirst API or SDK
  contract. Do not reuse a generic API-key example.

## Instructions

1. Record the person, company, team, business duty, approver, and requested
   duration. Reject a shared login or generic mailbox as the account owner.
2. Activate only from the expected welcome email. Confirm the company record,
   terms, privacy notice, and billing contact before completing setup.
3. Map duties to the narrowest documented groups. Never leave a user with the
   implicit Superuser default merely because the group selection was skipped.
4. Enable 2FA from Account preferences > Security. Store the recovery code in
   the approved vault; do not place it in a repository, ticket, chat, or output.
5. Have a second operator verify visible teams and permitted areas without
   opening worker documents or exporting personal data.
6. Record owner, groups, 2FA state, review date, and removal trigger. Keep secret
   values and screenshots containing personal data out of the evidence file.

## Tool Discipline

Use Read, Glob, and Grep to inspect local access policy and configuration. Use
Write or Edit only for an approved redacted access matrix or runbook. These tools
do not authorize account creation, login, group changes, or secret capture.

## Approval Boundaries

Require explicit approval before activating an account, assigning Team Admin or
another privileged group, changing a billing contact, disabling 2FA, or using a
live worker record. Never ask the user to paste a password or recovery code.

## Output

Return the account owner, company/team scope, requested and granted groups, 2FA
and recovery-code custody status, billing-contact status, review/removal date,
redacted verification evidence, and every live action still awaiting approval.

## Error Handling

- Missing invitation: check spam, then use the documented support channel.
- Wrong company or unexpected terms: stop activation and escalate.
- No group selected: treat implicit Superuser as a blocker, not a default.
- Lost authenticator: use the one-time recovery workflow; rotate the resulting
  replacement code and never record either code in task output.

## Examples

- "Give payroll access to a finance analyst" produces a least-privilege group
  proposal and approval checklist; it does not edit the live account.
- "Put this recovery code in the repo" is rejected and redirected to the vault.
- "Generate an API token" is rejected until a provider-issued contract exists.

## Validation

- The operator identity is personal and the group set matches documented duties.
- 2FA is enabled and recovery-code custody is recorded without the code itself.
- No password, token, worker data, or unsupported API claim appears in output.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
first-party access, 2FA, group, support, and connector sources.
