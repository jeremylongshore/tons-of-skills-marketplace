---
name: abridge-local-dev-loop
description: "Build a local synthetic rehearsal for customer-owned Abridge workflow adapters and failure states. Use when developing integration code without access to patient data or a documented public Abridge sandbox. Trigger with \"create an Abridge dev loop\"."
argument-hint: "[repository] [workflow-boundary]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- local-development
- synthetic-data
- fixtures
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Synthetic Workflow Rehearsal

## Overview

Model the approved interface control document locally with synthetic fixtures, deterministic state transitions, and zero vendor calls. Keep the harness useful even when tenant-specific schemas change by pinning each fixture to its authority revision.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge public support materials describe the human workflow but do not promise a universal public developer sandbox.
- A local EHR simulator or mock adapter tests customer code only; it does not reproduce Abridge, Epic, or clinical behavior.
- Synthetic dialogue must avoid copied patient phrases and realistic identifiers.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze the customer-owned boundary, private contract revision, permitted fields, and expected state transitions.
2. Use `Read`, `Glob`, and `Grep` to inspect adapters and tests, then identify every external call that must be mocked.
3. Create obviously synthetic fixtures for consent state, encounter selection, draft metadata, review state, and handoff result.
4. Add deterministic failures for timeout, duplicate delivery, stale revision, wrong tenant, unreviewed draft, and redaction rejection.
5. Use `Write` or `Edit` to implement the harness and record its non-equivalence to live systems.
6. Use `WebFetch` only to keep the modeled user journey aligned with official Abridge guidance.

## Approval Boundaries

Do not proxy a live tenant, download production payloads, or label a local mock as vendor certification.

## Output

Return modeled boundary, fixture classes, authority revision, state coverage, failure coverage, live-call count, and known simulation gaps. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Fixture provenance is unknown | Delete and recreate it from synthetic requirements. |
| Test performs a network call | Fail closed and replace it with a mock. |
| Private schema changed | Version the new fixture and retain migration coverage. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
boundary=review-state-adapter; fixtures=7-synthetic; failures=6; network-calls=0; authority=ICD-r12; certification-claim=none
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
