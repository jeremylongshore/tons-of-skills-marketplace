---
name: openevidence-upgrade-migration
description: >-
  Adopt a documented OpenEvidence feature or model change through inventory, pilot, review, training, and rollback. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence upgrade migration", "OpenEvidence change-management", or a matching workflow request.
argument-hint: "[change-description] [affected-workflows-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- change-management
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Feature-Change Adoption

## Overview

Prevent silent workflow drift when navigation, models, outputs, or product features change. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence features and model choices can change; current first-party guidance is the baseline.
- Deep Consult-to-Snow is one documented replacement, but other changes require their own evidence.
- Saved prompts and procedures must be revalidated when model or output behavior changes.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Capture the change source, evidence date, affected users, workflows, data, templates, records, training, and controls.
2. Separate documented facts from assumptions and determine whether the change is mandatory, optional, or unavailable to the account.
3. Run synthetic before/after scenarios using a stable rubric for citations, applicability, uncertainty, format, and effort.
4. Review privacy, consent, security, clinical, operational, and records impacts.
5. Update procedures and training, define rollback or fallback, and obtain accountable approval.
6. Monitor the first cohort and close only after acceptance evidence and residual risks are recorded.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| No authoritative change notice | Treat the observation as unverified and seek vendor confirmation. |
| Rollback impossible | Use a smaller pilot and independent fallback. |
| Clinical behavior regresses | Pause adoption and escalate to the clinical owner. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
change=model selector update; workflows=4; cohort=pilot; data=synthetic
```

Expected handoff:

```text
affected=4; passed=3; blocked=1; training=updated; rollout=paused
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
