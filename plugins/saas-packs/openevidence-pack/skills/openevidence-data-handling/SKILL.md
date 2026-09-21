---
name: openevidence-data-handling
description: >-
  Design a minimum-necessary OpenEvidence data-handling workflow for questions, Visits recordings, notes, and exports. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence data handling", "OpenEvidence privacy", or a matching workflow request.
argument-hint: "[workflow-name] [policy-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- privacy
- phi
- consent
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence PHI and Consent Boundary

## Overview

Establish whether data may enter OpenEvidence, who authorizes it, and how outputs move into governed systems. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence terms recommend removing identifying information before submission and assign users responsibility for lawful content.
- Covered entities choosing to transmit PHI are governed by the applicable BAA or customer-specific agreement.
- Visits records conversations; required notice and consent depend on law and organizational policy.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Classify the workflow, data elements, users, systems, jurisdiction, retention needs, and whether recording occurs.
2. Read the current Terms, Privacy Policy, Security page, applicable BAA/MSA, and institutional policy.
3. Minimize identifiers and free text; prefer synthetic or de-identified content when patient identity is unnecessary.
4. Document authorization, recording notice and consent, role access, approved export destination, and deletion/retention owner.
5. Test the workflow with synthetic data before any authorized real-data use.
6. Produce a data-flow record with unresolved legal, privacy, security, and clinical review items.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| BAA or policy unavailable | Block PHI use and continue only with synthetic/de-identified data. |
| Consent uncertain | Do not record; route to privacy or legal owner. |
| Output copied to unmanaged tool | Stop propagation, preserve facts, and follow the incident procedure. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Visits recording; jurisdiction=known; data=PHI; agreements=pending
```

Expected handoff:

```text
decision=blocked; synthetic-test=allowed; approvals=privacy+clinical+security
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
