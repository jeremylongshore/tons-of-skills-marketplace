---
name: openevidence-prod-checklist
description: >-
  Gate an OpenEvidence clinical workflow for go-live across access, privacy, safety, training, support, and rollback. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence prod checklist", "OpenEvidence go-live", or a matching workflow request.
argument-hint: "[workflow] [launch-date]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- go-live
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Clinical Go-Live Checklist

## Overview

Produce a binary, owner-signed readiness decision for one clearly bounded workflow. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- Go-live approval belongs to the accountable institution, not this skill or the product output.
- Current first-party terms, privacy, security, feature guidance, and institution agreements all matter.
- A successful technical test does not waive clinical review or data obligations.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Freeze workflow scope, users, surfaces, data classes, dependencies, success measures, and exclusions.
2. Verify account/access lifecycle, agreements, PHI boundary, consent, retention, approved exports, and security review.
3. Complete synthetic acceptance tests and clinician-led evidence/citation review across normal and failure cases.
4. Verify training, support contacts, incident response, downtime alternative, and rollback authority.
5. Record unresolved items as blockers or explicitly accepted risks with named decision owners.
6. Issue go, conditional-go, or no-go with evidence links, signatures, launch window, and first review date.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Owner unsigned | No-go. |
| Critical control unknown | No-go until confirmed in writing. |
| Rollback untested | Run a tabletop or keep the workflow in pilot. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Visits notes; launch=2026-10-01; cohort=10; approvals=matrix
```

Expected handoff:

```text
decision=no-go; blockers=consent-script+rollback-test; owners=assigned
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
