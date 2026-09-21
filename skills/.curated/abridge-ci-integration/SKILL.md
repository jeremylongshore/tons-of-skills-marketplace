---
name: abridge-ci-integration
description: "Build a synthetic-data CI gate for customer-controlled Abridge integration code without calling undocumented vendor interfaces. Use when adding regression checks to an Abridge deployment repository. Trigger with \"test the Abridge integration\"."
argument-hint: "[repository] [workflow-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- ci
- synthetic-data
- contract-testing
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Synthetic Workflow CI Gate

## Overview

Turn the approved deployment contract into deterministic checks for configuration, consent-state handling, note-review handoffs, redaction, and rollback. The gate proves customer-owned behavior; it does not certify Abridge or an EHR tenant.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge documents clinician recording, note review, Linked Evidence, and Epic handoff as user workflows.
- The cited public materials do not define a general Abridge REST sandbox, webhook schema, or public SDK contract.
- Use synthetic encounters and identifiers in CI; never upload patient audio, transcripts, notes, or production tokens.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Inventory the customer-owned adapters, configuration schema, feature flags, and rollback controls with `Read`, `Glob`, and `Grep`.
2. Translate the signed implementation workbook and tenant-specific interface control document into versioned fixtures and schemas.
3. Add negative tests for missing consent state, cross-tenant identifiers, unreviewed note release, and unsafe logs.
4. Mock every vendor and EHR boundary; reject tests that depend on an assumed public Abridge hostname or event name.
5. Use `Write` or `Edit` to add the smallest focused tests and a redacted machine-readable test receipt.
6. Require an integration-owner review when the private contract, EHR template, or rollout cohort changes.

## Approval Boundaries

Do not connect CI to a live Abridge or EHR tenant. A contract-test update cannot authorize a production interface, disclose PHI, or replace clinical validation.

## Output

Return fixture scope, contract revision, tests added, negative paths exercised, redaction result, and an explicit statement of every live boundary not tested. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Fixture contains realistic patient data | Stop, quarantine the fixture, and replace it with synthetic content. |
| Private contract is unavailable | Mark the interface unverified and test only customer-owned invariants. |
| Mock diverges from approved schema | Fail CI and require contract-owner reconciliation. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
scope=note-review-handoff; fixtures=synthetic; negative-paths=4; live-calls=0; result=pass; contract=ICD-2026-04
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
