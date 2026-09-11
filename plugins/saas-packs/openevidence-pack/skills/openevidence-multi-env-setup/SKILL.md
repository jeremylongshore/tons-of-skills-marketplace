---
name: openevidence-multi-env-setup
description: >-
  Verify a governed OpenEvidence workflow across supported web and mobile surfaces without fictitious dev or staging hosts. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence multi env setup", "OpenEvidence web", or a matching workflow request.
argument-hint: "[workflow] [web|mobile|both]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- web
- mobile
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Web and Mobile Workflow Parity

## Overview

Define which surface supports each step and test handoff, device, consent, and export behavior. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The official guide documents web and mobile experiences for Ask and Visits workflows.
- No public dev or staging domains are documented; environment separation belongs to the institution’s test-data and rollout process.
- Browser-specific capabilities, such as some recording inputs, must be checked against current guidance.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Map the workflow steps, user role, device, browser/app, data class, and expected handoffs.
2. Read the current feature page for web/mobile differences and supported-browser notes.
3. Test with synthetic data on each authorized surface; record unavailable or divergent behavior.
4. Verify that copied notes, citations, recordings, and notifications stay within approved systems.
5. Define the supported surface, fallback, training note, and re-test trigger for each step.
6. Return a parity matrix with evidence date, owners, gaps, and rollout impact.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Feature absent on one surface | Document the supported route; do not invent parity. |
| Recording input unsupported | Use a documented supported browser/device or stop that test. |
| Cross-device data surprise | Pause and route the data flow to privacy/security review. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
workflow=Visits note; surfaces=Chrome+iOS; data=synthetic
```

Expected handoff:

```text
parity=partial; recording=web-supported; editing=both; gaps=1
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
