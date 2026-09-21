---
name: abridge-upgrade-migration
description: "Plan a reversible Abridge tenant, care-setting, note-template, or EHR workflow change from authoritative release evidence. Use when migrating an Abridge implementation. Trigger with \"plan the Abridge migration\"."
argument-hint: "[change-type] [source-state] [target-state]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- migration
- change-control
- rollback
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Tenant and EHR Change Migration

## Overview

Treat every material workflow change as a clinical and EHR migration, not a generic API-version bump. Pin source and target behavior, identify affected cohorts and templates, test with designated records, and preserve a workable rollback.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge capabilities differ across outpatient, emergency, inpatient, orders, note types, and integration modes.
- Note-setting changes can affect future notes without retroactively changing prior notes.
- Public announcements describe capability direction; the tenant's approved release and implementation documents control availability.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze source and target tenant states, release evidence, care settings, cohorts, note types, EHR templates, owners, and maintenance window.
2. Use `Read`, `Glob`, and `Grep` to inventory configuration, mappings, training, tests, dashboards, and downstream dependencies.
3. Classify changes by patient-selection, capture, generation, review, evidence, note-template, EHR handoff, access, and support impact.
4. Test source and target side by side with approved test records; include rollback, partial migration, and in-flight encounter cases.
5. Use `WebFetch` only for current official product context; require tenant release notes for actual change semantics.
6. Use `Write` or `Edit` to publish the migration map, evidence, communications, cutover checks, and rollback authority.

## Approval Boundaries

Do not cut over active clinical cohorts, change shared templates, or assume a newly announced feature is licensed and enabled without owner confirmation.

## Output

Return source and target states, affected assets, test evidence, in-flight handling, training, cutover steps, rollback trigger, and decision owners. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Target behavior is not documented for the tenant | Delay migration. |
| Prior note behavior is assumed to change | Separate prospective settings from historical content. |
| Rollback changes patient workflow | Rehearse and communicate it before cutover. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
change=inpatient-note-type; cohort=pilot; source=approved-r4; target=approved-r5; test-records=8; rollback=pass; decision=scheduled
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
