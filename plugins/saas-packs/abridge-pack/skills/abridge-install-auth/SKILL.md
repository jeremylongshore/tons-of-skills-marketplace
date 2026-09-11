---
name: abridge-install-auth
description: "Establish Abridge tenant access, identity ownership, and approved EHR integration prerequisites without fabricating public credentials or endpoints. Use when onboarding an Abridge implementation. Trigger with \"configure Abridge access\"."
argument-hint: "[environment] [identity-owner]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- access
- identity
- onboarding
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Access and Integration Readiness

## Overview

Build an authority map for contracted capabilities, user provisioning, SSO, administrative roles, EHR integration, support, and secrets. Treat vendor-issued implementation documents as tenant-scoped evidence, not reusable public API facts.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge publicly describes enterprise SSO, governance, analytics, secure cloud handling, and EHR-integrated workflows.
- The cited public documentation does not publish a self-service API-key flow, universal partner hostname, or generic SMART-on-FHIR setup for Abridge customers.
- Identity, integration, and support details must come from the signed agreement and approved implementation workbook.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Identify contract owner, tenant administrator, identity owner, EHR owner, privacy and security contacts, and vendor implementation lead.
2. Inventory licensed products, environments, cohorts, roles, SSO requirements, support routes, and tenant-specific interfaces.
3. Use `Read`, `Glob`, and `Grep` to locate configuration templates and secret references without exposing secret values.
4. Verify least-privilege provisioning, joiner-mover-leaver handling, break-glass ownership, and audit evidence.
5. Use `WebFetch` only for current official Abridge public context; reconcile private setup steps with their document revision.
6. Use `Write` or `Edit` to create the readiness matrix and unresolved-dependency log.

## Approval Boundaries

Do not invent or probe Abridge endpoints, place vendor secrets in repository files, or authorize a user outside the health system's identity process.

## Output

Return environment and capability inventory, authority owners, role model, secret locations by reference, support route, evidence revisions, and readiness gaps. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Credential source is informal | Reject it and request vendor-issued or identity-owner evidence. |
| Role scope is unclear | Provision nothing until least privilege is defined. |
| Environment cannot be distinguished | Hold all live actions. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
tenant=contracted; environments=2; sso-owner=iam; ehr-owner=clinical-apps; secrets=references-only; unresolved=vendor-interface-revision
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
