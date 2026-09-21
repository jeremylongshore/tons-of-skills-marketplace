---
name: abridge-core-workflow-b
description: "Verify the approved handoff of clinician-reviewed Abridge note sections into Epic templates and downstream workflows. Use when configuring or auditing Abridge-to-Epic documentation flow. Trigger with \"verify the Abridge Epic handoff\"."
argument-hint: "[department] [epic-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- epic
- ehr-handoff
- templates
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Epic Note Handoff Assurance

## Overview

Prove that reviewed content reaches the intended Epic note sections through the tenant's supported workflow, with clear handling for manual patients, template differences, and patient-facing content. Do not substitute a generic FHIR push for the documented integration.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge documents a Send Now workflow and Epic SmartLinks for several note sections.
- Its support guidance states that manually added patients may require copy and paste, and Patient Visit Summaries are not sent directly into Epic in that documented flow.
- Epic-integrated product behavior varies by licensed deployment, care setting, and implementation phase.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze the Epic environment, department, note type, template owner, SmartLink mapping, and approved test-patient procedure.
2. Use `Read`, `Glob`, and `Grep` to inspect configuration and test scripts while excluding patient content and production credentials.
3. Trace each reviewed Abridge section to its intended Epic destination and identify manual or unsupported paths.
4. Test with approved synthetic or designated test records; verify omission, duplication, stale-draft, and wrong-chart failure paths.
5. Use `WebFetch` only for current official Abridge and Epic-facing guidance; private build documents control tenant specifics.
6. Use `Write` or `Edit` to record the mapping, evidence, rollback, and owner sign-off.

## Approval Boundaries

Do not post to a live chart, alter a shared Epic template, or enable a new care setting without the EHR change authority and clinical owner present.

## Output

Return the section-to-destination map, test-record evidence, exceptions, template owner, rollback, and go/no-go decision. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Section lands in the wrong template location | Disable the handoff for that cohort and restore the last approved mapping. |
| Manual-patient path differs | Document and train the manual path; do not silently automate it. |
| Patient-facing summary is assumed to transfer | Treat it as unsupported until tenant evidence proves otherwise. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
department=cardiology-test; sections=4/4-mapped; manual-patient-path=documented; live-chart-writes=0; decision=go-pilot
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
