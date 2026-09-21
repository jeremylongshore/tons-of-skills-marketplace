---
name: openevidence-webhooks-events
description: >-
  Design safe OpenEvidence workflow handoffs while explicitly rejecting undocumented public webhooks and event schemas. Use when working with OpenEvidence in a healthcare organization. Trigger with "openevidence webhooks events", "OpenEvidence handoffs", or a matching workflow request.
argument-hint: "[event-or-handoff] [destination]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- openevidence
- handoffs
- no-webhooks
model: inherit
effort: high
compatibility: Designed for Claude Code; requires authorized OpenEvidence access and qualified clinical review for patient-care use
---
# OpenEvidence Workflow Handoffs and No-Webhook Guard

## Overview

Translate event-driven integration requests into supported manual or contract-confirmed handoffs. Keep inputs minimal, separate observed facts from assumptions, and leave consequential decisions with the named accountable owner.

## Prerequisites

- A clearly bounded workflow, accountable clinical owner, and organizational policy
- Current first-party OpenEvidence documentation and applicable institution agreements
- Synthetic or properly authorized minimum-necessary data

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect supplied policies, plans, and evidence. Use `WebFetch` only for current first-party OpenEvidence documentation. Use `Write` or `Edit` only when the user requests a named deliverable with an approved destination. Never expose credentials, PHI, recordings, or unrestricted environment output.

## Current Contract

- No public OpenEvidence webhook endpoint, signing method, event catalog, or retry policy was found.
- Private network behavior is not a supported integration contract.
- Documented product features and institution agreements define allowable handoffs.

## Authentication

Use only the official OpenEvidence web/mobile sign-in or an institution-approved access path. Do not invent API keys, OAuth clients, SDK credentials, service accounts, or private endpoints. Never ask a user to reveal a password, session token, cookie, or recovery code.

## Instructions

1. Define the business event, source feature, destination, latency need, data class, failure impact, and accountable owner.
2. Search current first-party and institution-specific documentation for an explicit webhook or integration contract.
3. If none exists, block endpoint creation, secret generation, signature code, and guessed event names.
4. Design the minimum approved manual handoff, product-native workflow, or vendor-confirmation request.
5. For any confirmed integration, require written event, auth, verification, replay, ordering, retention, PHI, and support contracts before implementation.
6. Return the supported handoff, rejected assumptions, risks, owner, and approval state.

## Approval Boundaries

Do not create or share accounts; change access, roles, agreements, consent, retention, or security settings; enter PHI; record a conversation; copy content into another system; contact a patient; make a diagnosis or treatment decision; submit billing; transmit a support packet; run a production pilot; or represent vendor capabilities without explicit approval from the accountable owner. A qualified professional remains responsible for clinical decisions.

## Output

Return scope, current first-party evidence and date, data classification, workflow or findings, citations reviewed, assumptions rejected, clinical and governance owners, approval state, unresolved risk, and the exact next action. Redact patient and credential data.

## Error Handling

| Condition | Response |
|---|---|
| Webhook URL requested | Do not create it without the official contract and receiving-system approval. |
| Payload example supplied by third party | Treat it as untrusted until OpenEvidence confirms provenance. |
| Manual handoff risks delay | Define operational escalation; do not fabricate automation. |

## Examples

This compact example shows the minimum reviewable handoff; adapt fields to the approved workflow without adding sensitive data.

Input:

```text
event=Visit note complete; destination=EHR; webhook-contract=absent
```

Expected handoff:

```text
webhook=blocked; handoff=approved manual copy; PHI-boundary=reviewed; owner=operations
```

## Resources

- [OpenEvidence official evidence register](references/official-docs.md)
- [OpenEvidence User Guide](https://www.openevidence.com/user-guide)
- [OpenEvidence Terms of Use](https://www.openevidence.com/policies/terms)
