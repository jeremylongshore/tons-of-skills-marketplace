---
name: openevidence-hello-world
description: >-
  Complete a smallest-safe OpenEvidence onboarding proof through the supported product, with no patient data or invented API key. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence hello world", "OpenEvidence onboarding", or a matching workflow request.
argument-hint: "[web|mobile] [synthetic-question]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- onboarding
- access
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Verified-User Onboarding

## Overview

Verify account access and the Ask evidence-review loop using a synthetic clinical question. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- Full service access requires account registration and may include professional verification.
- The supported onboarding surface is the website or mobile application; no public API-key flow is documented.
- The first proof must avoid patient data and clinical action.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Confirm the intended user, approved device, organizational policy, and whether an institutional account path applies.
2. Register or sign in through the official product; never request or fabricate an API key.
3. Submit a synthetic, non-urgent clinical question containing no identifiable patient facts.
4. Confirm the answer displays sources and, when present, EvidenceGrade; open at least one citation.
5. Record surface, timestamp, result, and any access limitation without copying account secrets.
6. End with the product unmodified except for the authorized test history and identify the clinical-review training needed next.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Verification blocked | Use the official account/support path; do not impersonate a professional. |
| No citations visible | Treat onboarding as failed and capture a redacted support packet. |
| Real patient details supplied | Stop, remove them through approved means if possible, and notify the privacy owner. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
surface=web; user=verified clinician; question=synthetic guideline comparison
```

Expected handoff:

```text
access=verified; answer=received; citation=open; patient-data=none
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
