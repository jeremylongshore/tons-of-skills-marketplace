---
name: abridge-webhooks-events
description: "Implement and verify callbacks only from an approved tenant-specific Abridge event contract, with replay and PHI protections. Use when vendor implementation documents authorize event delivery. Trigger with \"build the Abridge event handler\"."
argument-hint: "[contract-revision] [event-purpose]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- events
- callbacks
- idempotency
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Partner Event Contract Handler

## Overview

Build a fail-closed receiver whose transport, authentication, event names, schema, delivery semantics, and registration process come from the approved private contract. If no such contract exists, produce a polling or manual handoff design instead of inventing webhooks.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- The cited public Abridge materials do not publish a universal webhook catalog, HMAC header, registration endpoint, or retry schedule.
- Session or encounter identifiers can be sensitive even when a payload omits note text.
- Duplicate, delayed, and out-of-order delivery must not duplicate EHR actions.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Verify contract owner, revision, event purpose, transport, authentication, schema, ordering, retry, retention, and support route.
2. Use `Read`, `Glob`, and `Grep` to inspect the receiver, queue, idempotency store, logs, and downstream action boundary.
3. Reject unknown events and fields according to contract; authenticate before parsing sensitive content and cap body size and age.
4. Persist an opaque event key and processing state; design duplicates, replays, gaps, poison events, and manual reconciliation.
5. Use `Write` or `Edit` to add the handler and synthetic contract tests without committing private payload examples.
6. Use `WebFetch` only for official workflow context; do not derive protocol details from marketing pages.

## Approval Boundaries

Do not expose a callback publicly, register it with a vendor tenant, or enable downstream clinical writes without security, network, vendor, and EHR change approval.

## Output

Return contract revision, authenticated boundary, accepted events, rejection policy, idempotency model, retention, test evidence, and unimplemented assumptions. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| No approved event contract | Do not implement a webhook; propose a bounded alternative. |
| Authentication is ambiguous | Reject all deliveries until resolved. |
| Duplicate may repeat a clinical action | Quarantine and require reconciliation. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
contract=partner-events-r3; auth=contract-defined; accepted=2; unknown=reject; duplicate-test=pass; live-registration=no
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
