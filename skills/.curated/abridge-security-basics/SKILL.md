---
name: abridge-security-basics
description: "Review Abridge deployment controls across data handling, identity, devices, EHR workflows, support, auditability, and incident response. Use when conducting a security assessment or control renewal. Trigger with \"audit Abridge security\"."
argument-hint: "[environment] [control-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- security
- privacy
- hipaa
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Privacy and Security Control Review

## Overview

Map public posture claims, Trust Center evidence, signed agreements, tenant configuration, and customer controls without overclaiming HIPAA compliance from a checklist. Focus on responsibility boundaries and evidence freshness.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge states that data is handled through secure channels and stored and processed in HIPAA-secure US-based data centers.
- Its Trust Center describes SOC 2 Type 2 coverage and provides controlled access to additional reports.
- Vendor posture does not replace the health system's risk analysis, access governance, consent, device, EHR, logging, and incident duties.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Define scope, data classes, environments, care settings, regulatory owners, vendor evidence date, and inherited controls.
2. Use `Read`, `Glob`, and `Grep` to inspect the data-flow, access model, device policy, audit configuration, support route, and incident plan.
3. Verify contract and Trust Center evidence for storage, processing, subprocessors, retention, deletion, resilience, and incident obligations.
4. Test joiner-mover-leaver, wrong-patient prevention, least privilege, session handling, protected support, and audit review with non-PHI evidence.
5. Use `WebFetch` only for current official Abridge and HHS guidance, recording evidence dates and access limits.
6. Use `Write` or `Edit` to publish findings with owner, severity, evidence, compensating control, and due date.

## Approval Boundaries

Do not declare a system HIPAA compliant, waive a control, or disclose protected reports based only on this workflow. Authorized privacy, security, and legal owners decide.

## Output

Return responsibility matrix, evidence inventory, control findings, inherited and customer controls, gaps, expiries, owners, and residual-risk decision. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Evidence is expired or inaccessible | Mark the control unverified. |
| Public claim conflicts with contract | Escalate to legal and vendor management. |
| Potential breach is identified | Activate the approved incident and breach-assessment process. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
scope=prod-tenant; evidence-date=2026-09-10; controls=18; verified=15; gaps=3; phi-exported=0; decision=remediate-before-expansion
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
