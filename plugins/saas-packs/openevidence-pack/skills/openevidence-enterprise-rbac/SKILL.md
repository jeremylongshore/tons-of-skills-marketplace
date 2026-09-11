---
name: openevidence-enterprise-rbac
description: >-
  Define and verify institutional OpenEvidence access governance without inventing RBAC, SCIM, or administration APIs. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence enterprise rbac", "OpenEvidence access", or a matching workflow request.
argument-hint: "[access-matrix-path] [institution]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- access
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Institutional Access Governance

## Overview

Translate institutional roles and least-privilege expectations into verifiable product and contract controls. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- No public RBAC, SCIM, provisioning, or administration API contract was found in the audited product documentation.
- Only the current institution agreement and authorized administration interface can establish available controls.
- Shared credentials are prohibited by the published account terms.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Inventory user populations, clinical roles, administrators, support staff, devices, workflows, and sensitive data exposure.
2. Read the agreement and authorized admin documentation; mark SSO, provisioning, audit, and role features confirmed or unknown.
3. Define joiner, mover, leaver, periodic review, break-glass, and compromised-account procedures.
4. Map each workflow to minimum access and an accountable approver; prohibit shared accounts.
5. Run a sample access review using authorized records without exporting unnecessary personal data.
6. Return confirmed controls, gaps, compensating controls, vendor questions, owners, and review cadence.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Admin capability unclear | Mark unknown and seek written confirmation; do not infer an endpoint. |
| Orphaned account | Follow the authorized deprovisioning path and record the owner. |
| Shared login discovered | Stop the practice, preserve evidence, and initiate individual access remediation. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
institution=clinic; users=physicians+schedulers; SSO=unknown; review=quarterly
```

Expected handoff:

```text
controls=confirmed/unknown matrix; gaps=3; shared-accounts=0; owner=IAM
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
