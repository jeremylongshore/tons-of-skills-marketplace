---
name: openevidence-common-errors
description: >-
  Diagnose weak, incomplete, or poorly grounded OpenEvidence results using prompt, model, citation, and workflow checks. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence common errors", "OpenEvidence troubleshooting", or a matching workflow request.
argument-hint: "[redacted-query] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- troubleshooting
- quality
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Answer-Quality Troubleshooting

## Overview

Separate access trouble, prompt ambiguity, evidence limitations, and unsafe interpretation before anyone acts on an answer. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence answers cite sources and may expose EvidenceGrade; neither removes the need for professional review.
- Model and feature behavior can change, so the live guide and visible product state outrank cached instructions.
- Do not paste identifiable patient data into a diagnostic packet.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Classify the symptom as access, missing context, irrelevant evidence, conflicting evidence, citation mismatch, or product failure.
2. Reduce the question to the clinical decision, population, intervention, comparator, outcome, and time horizon that matter.
3. Compare an ordinary Ask response with an appropriate model or Snow only when the current guide supports that choice.
4. Open the cited sources and verify population, date, endpoint, recommendation strength, and applicability.
5. Ask a qualified clinician to review the result and document uncertainty or conflicting guidance.
6. Create a redacted support packet only when the behavior appears technical rather than clinical.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| No useful evidence | Broaden terminology or state that evidence is limited; do not manufacture certainty. |
| Citation does not support claim | Treat the claim as unverified and escalate with a redacted example. |
| Urgent patient concern | Leave the tool and follow the organization’s urgent-care or emergency protocol. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
symptom=answer ignores renal impairment; query=de-identified medication comparison
```

Expected handoff:

```text
cause=missing constraint; citations=reviewed; revised-prompt=ready; clinical-owner=assigned
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
