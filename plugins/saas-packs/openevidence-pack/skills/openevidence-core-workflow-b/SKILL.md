---
name: openevidence-core-workflow-b
description: >-
  Audit an OpenEvidence answer’s EvidenceGrade, citations, and applicability before it informs clinical work. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence core workflow b", "OpenEvidence citations", or a matching workflow request.
argument-hint: "[response-or-notes-path] [review-question]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- citations
- evidence-grade
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence EvidenceGrade and Citation Review

## Overview

Treat the displayed grade as a navigation aid, then perform a source-level review of every material claim. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The official user guide documents lettered EvidenceGrade output and links to its methodology.
- A grade summarizes evidence strength; it is not a patient-specific recommendation or correctness guarantee.
- Citation review must consider source type, date, population, outcome, and fit to the decision.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. List each material claim that could change diagnosis, treatment, safety, documentation, or patient communication.
2. Capture the displayed EvidenceGrade and any caveats without treating the grade as the conclusion.
3. Open the supporting citations and map each claim to the exact source or mark it unsupported.
4. Check guideline authority, publication date, study population, intervention, comparator, outcomes, and limitations.
5. Identify disagreements, indirectness, missing subgroups, or newer evidence that alters applicability.
6. Return a clinician-review table with supported, uncertain, contradicted, and not-assessed claims.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Citation unavailable | Mark the linked claim unverified; do not rely on a summary alone. |
| Grade missing | Continue source-level review and state that no grade was available. |
| Source is indirect | Describe the inference and require clinical judgment. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
response=de-identified excerpt; decision=screening interval; review=all material claims
```

Expected handoff:

```text
claims=6; supported=4; uncertain=2; grade=recorded; clinician-signoff=required
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
