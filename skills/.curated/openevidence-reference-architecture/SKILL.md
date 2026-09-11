---
name: openevidence-reference-architecture
description: >-
  Design a governed operating model around OpenEvidence’s supported product workflows and clinician review. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence reference architecture", "OpenEvidence architecture", or a matching workflow request.
argument-hint: "[architecture-notes-path] [workflow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- architecture
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Human-in-the-Loop Operating Model

## Overview

Map people, product surfaces, evidence review, governed records, and incident paths without fabricating integrations. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The documented surface comprises product workflows such as Ask, Visits, and Dialer, subject to current availability.
- No public API, webhook, SDK, or infrastructure deployment contract was found.
- Clinical decisions and official records remain owned by qualified people and approved systems.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Map users, patient touchpoints, product features, source evidence, record systems, support, and governance owners.
2. Draw trust boundaries for credentials, PHI, recordings, copied outputs, citations, and third-party communications.
3. Place clinician review before any care decision and define how evidence is verified and uncertainty recorded.
4. Use only documented handoffs; label desired integrations as vendor-confirmation questions, not architecture facts.
5. Add access lifecycle, monitoring, incident response, downtime alternative, retention, and rollback.
6. Review the model with clinical, privacy, security, legal, operations, and records owners.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Private endpoint appears in design | Remove it until a signed/current contract documents it. |
| AI output becomes system of record automatically | Insert human review and approved record controls. |
| No downtime path | Block go-live until one exists. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Ask-to-clinical-note; systems=OpenEvidence+EHR; integration=manual-copy
```

Expected handoff:

```text
boundaries=6; human-gates=2; undocumented-integrations=0; review=pending
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
