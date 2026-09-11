---
name: openevidence-local-dev-loop
description: >-
  Evaluate OpenEvidence product workflows safely with synthetic cases before any clinical rollout. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence local dev loop", "OpenEvidence evaluation", or a matching workflow request.
argument-hint: "[evaluation-plan-path] [feature]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- evaluation
- synthetic-testing
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Synthetic Workflow Evaluation Loop

## Overview

Replace the nonexistent local developer loop with a repeatable browser/app evaluation process. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence does not publish a local runtime, sandbox SDK, or public test API in the audited documentation.
- Synthetic scenarios are the default evaluation input; real PHI requires the full approved data boundary.
- Evaluation tests workflow fitness and evidence review, not medical-device validation.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Define feature, user role, expected workflow outcome, unacceptable failure, and clinical reviewer.
2. Create synthetic scenarios spanning routine, ambiguous, conflicting-evidence, and failure-path cases.
3. Read the current guide and record the model, feature, and surface used for each run.
4. Execute manually through the supported product, preserving only de-identified prompts, citations, and observations.
5. Have a qualified reviewer score traceability, applicability, uncertainty, and workflow burden.
6. Iterate one variable at a time and publish a go, revise, or stop recommendation.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| No sandbox | Use synthetic inputs in an authorized account; do not probe private infrastructure. |
| Output non-deterministic | Score invariant qualities rather than exact wording. |
| Reviewer disagreement | Preserve both rationales and escalate to the clinical owner. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
feature=Ask; cases=12 synthetic; reviewer=clinical lead; surface=web
```

Expected handoff:

```text
runs=12; acceptable=9; revise=2; stop=1; next-change=prompt
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
