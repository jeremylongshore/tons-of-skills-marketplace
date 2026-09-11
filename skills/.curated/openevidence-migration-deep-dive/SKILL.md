---
name: openevidence-migration-deep-dive
description: >-
  Migrate saved Deep Consult practices to the current Snow model workflow while revalidating output and governance. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence migration deep dive", "OpenEvidence migration", or a matching workflow request.
argument-hint: "[workflow-inventory-path] [pilot-owner]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- migration
- snow
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Deep Consult to Snow Migration

## Overview

Translate legacy Deep Consult use cases into Snow, which the official guide identifies as its replacement. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- The current guide says Deep Consult has been replaced by OpenEvidence Snow in the model selector.
- Legacy Deep Consult examples remain representative, but do not establish current performance, quota, or timing.
- Migration must revalidate prompts, structure, citations, review, data handling, and user training.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Inventory legacy Deep Consult prompts, reports, user groups, downstream decisions, and sensitive-data handling.
2. Classify each workflow as retire, move to ordinary Ask, or pilot in Snow based on complexity and value.
3. Read the current Models and Deep Consult guidance; remove obsolete navigation and invented quota assumptions.
4. Run synthetic paired evaluations and compare coverage, citation traceability, uncertainty, format, and reviewer effort.
5. Update training, templates, governance, and support documentation with a rollback path.
6. Obtain clinical and operational sign-off before retiring the legacy procedure.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Snow unavailable | Confirm account entitlement/support; do not fall back to a guessed endpoint. |
| Output structure changes | Update the review rubric before production use. |
| Legacy prompt contains PHI | Do not reuse it in testing; construct a synthetic equivalent. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
legacy-workflows=8; target=Snow; test-data=synthetic; reviewers=2
```

Expected handoff:

```text
migrate=5; Ask=2; retire=1; signoff=pending; legacy-quota-claims=removed
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
