---
name: openevidence-debug-bundle
description: >-
  Assemble a reproducible, privacy-safe OpenEvidence support packet for product failures without exposing credentials or patient data. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence debug bundle", "OpenEvidence support", or a matching workflow request.
argument-hint: "[symptom] [evidence-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- support
- diagnostics
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Redacted Support Packet

## Overview

Capture enough browser/app and workflow context for support while excluding PHI, credentials, and speculative API probes. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The supported public surface is the documented product UI and mobile app, not guessed private endpoints.
- A useful packet identifies time, surface, feature, steps, expected result, actual result, and redaction method.
- Clinical disagreement belongs in evidence review; technical malfunction belongs in a support packet.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Classify the issue as access, browser/device, feature availability, data loss, recording, output, or clinical-content concern.
2. Reproduce with synthetic or fully de-identified content when safe; stop if reproduction could affect care.
3. Record UTC time, app/web version cues, browser/device, feature path, steps, expected behavior, and actual behavior.
4. Capture only redacted screenshots or text; remove names, dates of birth, record numbers, credentials, and hidden metadata.
5. Check the current user guide, terms, and public status/trust surfaces before labeling behavior a defect.
6. Write a packet with severity, impact, workaround, owner, consent to transmit, and clinical-safety escalation if applicable.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Cannot reproduce safely | Document the original observation without replaying patient data. |
| Potential data exposure | Switch to the incident runbook and restrict packet distribution. |
| Only clinical content is disputed | Use citation review and clinician escalation, not technical debugging. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
surface=web; feature=Visits note; data=synthetic; symptom=export missing
```

Expected handoff:

```text
repro=yes; packet=redacted; severity=medium; support-owner=assigned
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
