---
name: openevidence-deploy-integration
description: >-
  Plan a controlled OpenEvidence rollout across clinical workflows, training, governance, and rollback boundaries. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence deploy integration", "OpenEvidence deployment", or a matching workflow request.
argument-hint: "[practice-plan-path] [workflow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- deployment
- change-management
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Practice Rollout Plan

## Overview

Treat rollout as clinical workflow change, not software API deployment. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence is delivered through documented end-user product surfaces.
- Institution-specific availability, integrations, commitments, and data terms require written confirmation.
- A rollout needs clinical, privacy, security, operational, and training ownership.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Select one bounded workflow and define users, patients affected, systems touched, success criteria, and explicit exclusions.
2. Confirm account eligibility, feature availability, agreement terms, data handling, consent, and support path.
3. Design training for prompting, EvidenceGrade, citation verification, professional judgment, and failure escalation.
4. Pilot with synthetic scenarios, then a small authorized cohort under heightened review.
5. Review quality, safety signals, adoption, workflow burden, and unresolved controls before expansion.
6. Record launch/no-launch, rollback trigger, owners, training evidence, and next review date.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Feature not documented | Exclude it until OpenEvidence or the contract owner confirms support. |
| Governance owner missing | Do not launch the workflow. |
| Pilot creates unsafe reliance | Pause, retrain, and reassess before resuming. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Ask for guideline summaries; cohort=5 clinicians; phase=pilot
```

Expected handoff:

```text
decision=conditional-go; controls=verified; rollback=defined; review=14d
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
