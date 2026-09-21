---
name: openevidence-rate-limits
description: >-
  Triage OpenEvidence access, latency, or capacity symptoms without asserting undocumented quotas or retry contracts. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence rate limits", "OpenEvidence capacity", or a matching workflow request.
argument-hint: "[symptom] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- capacity
- troubleshooting
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Access and Capacity Triage

## Overview

Distinguish local connectivity, account/feature access, service behavior, and clinical urgency using safe evidence. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- No public numeric request limit or API retry contract was found for OpenEvidence.
- Browser/app symptoms must not be translated into invented HTTP limits.
- Urgent care needs must use an independent clinical fallback.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Record UTC time, surface, feature, user cohort, duration, impact, and whether patient care is time-sensitive.
2. Move urgent work to the approved clinical fallback before diagnosis.
3. Check local network/browser/device conditions and current first-party status/support information.
4. Reproduce once with synthetic content if safe; do not hammer the service or probe private endpoints.
5. Compare affected users/surfaces and capture a redacted support packet.
6. Report observed capacity symptoms, not a guessed quota, with workaround, owner, and escalation state.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Repeated failures | Stop retries and use the approved fallback. |
| Only one account affected | Check authorized account/feature access without credential sharing. |
| No published limit | Say unknown and ask support or the contract owner for written terms. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
symptom=slow Ask response; surface=web; duration=20m; urgency=non-urgent
```

Expected handoff:

```text
scope=3 users; local-network=cleared; quota=unknown; fallback=active; support=opened
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
