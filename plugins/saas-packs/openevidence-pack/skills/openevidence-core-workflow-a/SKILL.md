---
name: openevidence-core-workflow-a
description: >-
  Structure and review an OpenEvidence clinical consult while preserving clinician accountability and evidence traceability. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence core workflow a", "OpenEvidence clinical-consult", or a matching workflow request.
argument-hint: "[clinical-question] [context-policy]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- clinical-consult
- evidence
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Clinical Consult Workflow

## Overview

Convert a clinical uncertainty into a focused Ask workflow, then validate the evidence before using it in care. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The platform is informational and educational and does not replace diagnosis or professional clinical judgment.
- The public guide describes Ask for evidence-based clinical questions with cited sources.
- Only enter patient context permitted by applicable policy, agreement, authorization, and consent.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Define the decision to support and the minimum context needed; remove direct identifiers unless approved and necessary.
2. Frame the question with population, intervention or exposure, comparator, outcomes, and relevant constraints.
3. Choose the documented Ask model or workflow appropriate to complexity; use Snow for a literature investigation when warranted.
4. Review EvidenceGrade when present, then open citations and inspect recency, study design, population, and guideline provenance.
5. Reconcile the response with patient-specific facts, contraindications, local policy, and the clinician’s independent judgment.
6. Record the question, evidence reviewed, uncertainty, decision owner, and any follow-up without copying unnecessary PHI.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Evidence conflicts | Surface both positions and have the clinical owner resolve applicability. |
| Patient context exceeds policy | De-identify further or stop until authorization is confirmed. |
| Answer sounds definitive | Restate uncertainty and verify source support before use. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
decision=therapy options; population=de-identified adult; constraints=renal impairment
```

Expected handoff:

```text
question=structured; sources=opened; uncertainty=recorded; decision=clinician-owned
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
