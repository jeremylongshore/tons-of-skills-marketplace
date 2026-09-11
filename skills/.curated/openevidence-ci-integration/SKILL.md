---
name: openevidence-ci-integration
description: >-
  Build a repeatable acceptance gate for an OpenEvidence practice rollout without inventing an API or automating clinical judgment. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence ci integration", "OpenEvidence rollout", or a matching workflow request.
argument-hint: "[rollout-plan-path] [pilot-cohort]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- rollout
- acceptance
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Rollout Acceptance Gate

## Overview

Turn practice requirements into a manual, evidence-backed acceptance suite for supported OpenEvidence web or mobile workflows. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence publishes end-user web and mobile workflows, not a public CI or test API contract.
- Acceptance evidence must come from an authorized test account, synthetic scenarios, and current first-party instructions.
- A passing product check never validates the clinical correctness of a real patient decision.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Inventory the rollout requirements, supported devices, accountable clinical owner, and approved synthetic test scenarios.
2. Read the current OpenEvidence guide for each feature in scope; mark undocumented behavior as unverified.
3. Build a matrix covering sign-in, Ask response citations, export/copy behavior, and only the explicitly selected Visits features.
4. Execute with synthetic or properly authorized data; capture timestamps and redacted evidence, never patient identifiers.
5. Record pass, fail, blocked, and not-tested separately; route clinical-content review to a qualified professional.
6. Publish the gate result with owners, exceptions, rollback criteria, and a re-test date.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| No automation interface | Keep the gate manual; do not reverse-engineer private endpoints. |
| Clinical answer varies | Evaluate evidence traceability and review process, not exact generated wording. |
| PHI required | Stop until the institution confirms agreement, authorization, consent, and test-data handling. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
pilot=cardiology; surfaces=Ask+Visits; data=synthetic; gate=pre-launch
```

Expected handoff:

```text
coverage=12 checks; pass=10; blocked=2; clinical-review=pending; launch=no-go
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
