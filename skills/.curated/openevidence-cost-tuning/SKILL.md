---
name: openevidence-cost-tuning
description: >-
  Evaluate OpenEvidence adoption value and access burden without inventing prices, quotas, or usage telemetry. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence cost tuning", "OpenEvidence value", or a matching workflow request.
argument-hint: "[usage-evidence-path] [review-period]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- value
- adoption
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Access and Value Review

## Overview

Build a decision-ready value review from authorized local evidence and current commercial terms. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- Public product pages do not establish institution-specific price, quota, SLA, or entitlement terms.
- Only a current order form, MSA, or authorized account surface can establish commercial commitments.
- Clinical quality and safety outcomes must not be reduced to raw query volume.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Define the decision: pilot continuation, feature expansion, workflow retirement, or contract review.
2. Collect authorized evidence for active users, completed workflows, time saved, failure modes, and training/support burden.
3. Separate product facts from institution-specific contract terms and unverified anecdotes.
4. Measure value by workflow outcome, evidence-review quality, clinician time, and adoption friction; avoid patient-outcome causality claims.
5. Identify unused or duplicative workflows and test a reversible change with the accountable owner.
6. Return a value brief with data provenance, limitations, owner, decision date, and next measurement.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| No usage export | Use a documented sample or local survey and label the evidence incomplete. |
| Price unavailable | Request the current commercial document; never estimate it as fact. |
| Metric encourages unsafe speed | Replace it with quality, review, and workflow-completion measures. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
period=90d; cohort=pilot clinicians; decision=renewal; contract=owner-held
```

Expected handoff:

```text
value=evidence-backed; gaps=2; commercial-terms=unverified; recommendation=conditional
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
