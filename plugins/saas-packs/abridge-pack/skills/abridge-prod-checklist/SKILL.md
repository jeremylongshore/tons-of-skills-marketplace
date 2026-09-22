---
name: abridge-prod-checklist
description: "Run an evidence-backed Abridge production readiness decision across clinical, privacy, security, EHR, training, support, and rollback owners. Use when preparing a pilot or cohort expansion. Trigger with \"review Abridge go-live\"."
argument-hint: "[environment] [cohort] [go-live-date]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- production-readiness
- go-live
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Production Go-Live Checklist

## Overview

Convert the implementation plan into a fail-closed go/no-go record. A green technical test is insufficient without consent, clinical review, EHR mapping, access, privacy, training, support, monitoring, and rollback evidence.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge is used through clinical and EHR-integrated workflows that retain clinician review.
- Abridge publicly describes enterprise security and governance, while tenant-specific control evidence may require Trust Center access or implementation records.
- Care-setting features and downstream behavior must be verified for the licensed tenant and cohort.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze environment, cohort, care setting, note types, capabilities, owners, date, and change ticket.
2. Use `Read`, `Glob`, and `Grep` to gather signed evidence for consent, access, EHR mapping, test results, privacy, security, training, and support.
3. Verify the clinician review and wrong-patient controls, test-record procedure, audit evidence, downtime path, and rollback.
4. Confirm monitoring includes safety, workflow completion, adoption, support, and integration health without PHI.
5. Use `WebFetch` only to check current official product and security context; do not substitute public claims for tenant evidence.
6. Use `Write` or `Edit` to publish the decision with explicit owners, expiries, exceptions, and stop triggers.

## Approval Boundaries

Only the named change, clinical, privacy, security, and EHR authorities may accept their risks. Missing evidence is a no-go, not an assumed pass.

## Output

Return gate-by-gate evidence, exceptions, owners, expiry dates, rollback trigger, monitoring window, and final go/no-go decision. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Required owner has not signed | Record no-go. |
| Evidence applies to another environment | Reject it and test the target environment. |
| Rollback was not rehearsed | Delay launch. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
environment=prod; cohort=40; gates=12/12; exceptions=0; rollback=rehearsed; owners=5/5; decision=go-bounded-pilot
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
