---
name: openevidence-observability
description: >-
  Monitor OpenEvidence workflow quality, evidence traceability, adoption, and safety signals using approved local evidence. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence observability", "OpenEvidence quality", or a matching workflow request.
argument-hint: "[audit-period] [workflow]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- quality
- monitoring
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Quality and Adoption Audit

## Overview

Create a human-centered review loop without claiming access to private product telemetry. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- No public observability API or standard metrics export is documented.
- Measurements must come from authorized account/institution records and redacted quality samples.
- Volume and speed are insufficient without citation, applicability, and safety review.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Define the monitored workflow, cohort, period, data authority, clinical owner, and escalation thresholds.
2. Select measures for completion, citation traceability, unsupported claims, reviewer overrides, time burden, incidents, and training gaps.
3. Sample the minimum authorized records and de-identify evidence used outside the care record.
4. Have qualified reviewers score outputs with a stable rubric and record inter-reviewer disagreement.
5. Trend results without inferring patient outcomes or vendor-wide performance from a local sample.
6. Publish findings, limitations, actions, owners, thresholds, and the next review date.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Telemetry unavailable | Use an approved sample or survey and label coverage. |
| Metric hides harm | Add safety and override measures before reporting success. |
| Sample contains PHI | Keep it in the governed system or stop the audit export. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
period=30d; workflow=Ask; sample=25 de-identified reviews
```

Expected handoff:

```text
traceability=measured; overrides=recorded; incidents=1; actions=3
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
