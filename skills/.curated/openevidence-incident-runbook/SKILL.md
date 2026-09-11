---
name: openevidence-incident-runbook
description: >-
  Triage an OpenEvidence safety, privacy, access, recording, or evidence incident with containment and accountable escalation. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence incident runbook", "OpenEvidence incident-response", or a matching workflow request.
argument-hint: "[incident-id] [symptom]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- incident-response
- clinical-safety
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Clinical-AI Safety Incident Runbook

## Overview

Protect patients and data first, then preserve a minimum, redacted factual record for clinical and technical resolution. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- OpenEvidence output does not replace clinical judgment or emergency procedures.
- Privacy, recording, and PHI obligations depend on law, policy, consent, and applicable agreements.
- Security concerns can be reported through OpenEvidence’s published security contact; product support paths govern other issues.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. If care may be affected, move to the organization’s clinical escalation or emergency procedure before investigating the tool.
2. Classify patient safety, privacy/PHI, unauthorized access, recording consent, availability, or evidence integrity; set severity.
3. Contain within authority: stop using the affected workflow, prevent further copying, and preserve necessary facts.
4. Notify the accountable clinical, privacy, security, legal, operational, and vendor owners according to policy.
5. Build a redacted timeline and validate citations or product behavior without replaying sensitive content.
6. Document recovery criteria, approvals, communications, corrective actions, and post-incident review.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Active clinical emergency | Do not troubleshoot the product; use emergency clinical channels. |
| Suspected breach | Follow the organization’s breach process and applicable notification decision authority. |
| Unsafe answer | Quarantine it from care, preserve cited evidence, and require clinician review. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
incident=OE-17; class=evidence-integrity; patient-impact=possible
```

Expected handoff:

```text
workflow=paused; clinical-owner=engaged; evidence=redacted; recovery=pending
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
