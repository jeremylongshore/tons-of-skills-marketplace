---
name: openevidence-security-basics
description: >-
  Assess OpenEvidence security claims and institution-specific controls using current first-party evidence and accountable review. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence security basics", "OpenEvidence security", or a matching workflow request.
argument-hint: "[assessment-path] [workflow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- security
- due-diligence
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Security and Contract Due Diligence

## Overview

Separate public vendor assertions from the controls and commitments actually governing the institution’s use. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The public security page states HIPAA handling, SOC 2 Type II, encryption in transit and at rest, annual penetration testing, and a disclosure contact.
- The Trust Center provides current security-program evidence, while access to detailed artifacts may be controlled.
- Institution commitments are governed by applicable MSA, BAA, SLA, and other written agreements.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Scope workflow, users, data classes, recording, communications, devices, exports, and downstream systems.
2. Collect the dated security page, Trust Center evidence, terms/privacy, and current institution agreements.
3. Map vendor claims and contract commitments separately to required controls; mark absent evidence unknown.
4. Review identity lifecycle, minimum necessary data, encryption boundaries, retention/deletion, subprocessors, incident notice, availability, and exit.
5. Route gaps to security, privacy, legal, clinical, procurement, and vendor owners.
6. Issue approve, conditional, or reject with evidence dates, exceptions, compensating controls, and reassessment trigger.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Public claim lacks artifact | Treat it as a vendor assertion, not independently verified control. |
| Contract conflicts with webpage | Escalate to legal/procurement; do not choose silently. |
| Vulnerability discovered | Use responsible disclosure and the organization’s incident process. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Visits with PHI; evidence=security-page+BAA; artifacts=Trust-Center
```

Expected handoff:

```text
decision=conditional; verified-claims=5; contract-gaps=2; owners=assigned
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
