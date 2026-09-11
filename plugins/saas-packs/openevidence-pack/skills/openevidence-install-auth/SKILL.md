---
name: openevidence-install-auth
description: >-
  Establish authorized OpenEvidence account access through official registration and institutional pathways. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence install auth", "OpenEvidence authentication", or a matching workflow request.
argument-hint: "[web|mobile] [individual|institution]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- authentication
- account
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Account Verification and Access

## Overview

Choose the supported user access path and verify it without packages, tokens, shared accounts, or private endpoints. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence terms require account registration for full service access and make users responsible for account confidentiality.
- The product is intended for healthcare professionals and may verify registration information.
- No public OpenEvidence SDK package, API token, OAuth, or service-account contract was found.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Identify individual versus institution-managed access, professional role, approved email/device, and accountable access owner.
2. Read current registration, terms, privacy, security, and institution-specific access instructions.
3. Complete only the official sign-up, sign-in, or administrator-issued path; do not install similarly named packages.
4. Enable organization-required device and account protections and keep credentials in approved user-controlled storage.
5. Verify access with a synthetic Ask workflow and record only non-secret evidence.
6. Document recovery, termination, role-change, and suspected-compromise contacts.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Package suggested | Reject it unless current first-party documentation explicitly names and authenticates it. |
| Shared credential proposed | Require separate authorized accounts. |
| Account compromised | Change credentials through official controls and notify the security owner. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
access=institution-managed; role=physician; surface=mobile; patient-data=none
```

Expected handoff:

```text
registration=verified; auth=official-ui; shared-secret=no; recovery-owner=known
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
