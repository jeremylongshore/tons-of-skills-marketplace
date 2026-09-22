---
name: openevidence-performance-tuning
description: >-
  Improve OpenEvidence question quality and reviewer efficiency through controlled prompt refinement. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence performance tuning", "OpenEvidence prompting", or a matching workflow request.
argument-hint: "[redacted-question] [desired-decision]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- prompting
- quality
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Prompt Refinement

## Overview

Tune context and question structure while holding clinical accountability and source review constant. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The official guide publishes prompt guidance and dedicated workflows for complex cases and Snow.
- More detail is not always safer; include only relevant, authorized context.
- Performance means decision usefulness and evidence traceability, not fastest answer or longest response.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. State the decision, intended user, population, outcome, constraints, and what uncertainty must remain visible.
2. Remove identifiers and irrelevant narrative; separate known facts from assumptions.
3. Run a baseline synthetic or authorized de-identified question and score relevance, citations, applicability, and reviewer effort.
4. Change one prompt element at a time: specificity, timeframe, comparator, output structure, or request for conflicting evidence.
5. Open citations and have a qualified clinician compare versions using the same rubric.
6. Save a reusable pattern only if it improves the defined outcome across multiple representative cases.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Prompt becomes leading | Restore neutral framing and request alternatives or conflicting evidence. |
| Answer gets longer, not better | Optimize for reviewable claims and cited evidence. |
| Case is urgent | Use the clinical emergency workflow, not prompt iteration. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
decision=diagnostic workup; context=de-identified; variants=3; reviewer=clinician
```

Expected handoff:

```text
best-variant=2; traceability=improved; uncertainty=preserved; template=approved
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
