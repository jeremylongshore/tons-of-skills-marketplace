---
name: openevidence-sdk-patterns
description: >-
  Select supported OpenEvidence interaction and prompting patterns while preventing use of nonexistent public SDKs. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence sdk patterns", "OpenEvidence patterns", or a matching workflow request.
argument-hint: "[use-case] [surface]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- patterns
- no-sdk
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Supported Interaction Patterns

## Overview

Convert an SDK-shaped request into a documented product workflow or a vendor-confirmation question. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The audited first-party materials do not publish an OpenEvidence SDK or developer API.
- Similarly named npm and PyPI packages are not an authenticated OpenEvidence integration path.
- Supported patterns include end-user Ask and documented feature workflows, subject to current guide and account availability.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Identify the desired outcome and why the requester thinks code integration is required.
2. Search current first-party documentation for an explicit developer contract, package, authentication method, and terms.
3. If absent, reject package installation, private-endpoint probing, browser automation, and credential extraction.
4. Map the outcome to a supported product pattern: focused Ask, Snow literature investigation, Collections, Dotflows, Visits, or approved manual handoff.
5. If automation remains necessary, write precise vendor questions covering API, auth, scope, PHI, limits, SLA, and support.
6. Return the supported pattern, rejected assumptions, evidence date, and approval owner.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Third-party package found | Do not trust namespace alone; require first-party documentation and provenance. |
| Requester needs bulk automation | Escalate to vendor/contract owner; do not scrape or reverse-engineer. |
| Manual workflow unacceptable | Record the product gap and stop. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
request=embed evidence search in app; package=@openevidence/sdk
```

Expected handoff:

```text
sdk=unsupported; install=blocked; documented-alternative=manual Ask; vendor-questions=7
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
