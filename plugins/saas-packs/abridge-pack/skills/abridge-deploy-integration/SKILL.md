---
name: abridge-deploy-integration
description: "Plan and control a staged Abridge rollout across clinical cohorts and EHR workflows without pretending to deploy vendor infrastructure. Use when preparing an Abridge pilot or expansion. Trigger with \"plan the Abridge rollout\"."
argument-hint: "[care-setting] [cohort]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- deployment
- change-management
- pilot
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Staged Enterprise Rollout

## Overview

Coordinate readiness, training, tenant configuration, EHR change control, support coverage, measurement, and rollback for a bounded cohort. Customer operators configure their environment and workflow; Abridge operates its platform.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge documents integrated workflows across outpatient, emergency, and inpatient settings, with features varying by setting and rollout phase.
- Published rollout examples emphasize pilots, clinician demand, peer support, and phased expansion.
- Public product material does not authorize customers to self-deploy Abridge backend services or generic containers.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Name the executive, clinical, privacy, security, EHR, training, support, and vendor owners.
2. Freeze cohort eligibility, care setting, licensed capabilities, consent policy, training, success measures, and stop criteria.
3. Use `Read`, `Glob`, and `Grep` to inspect the local rollout plan and configuration artifacts without patient data.
4. Rehearse patient selection, recording, note review, EHR handoff, downtime, support, and opt-out paths with approved test records.
5. Use `WebFetch` only for current official Abridge workflow and rollout context; tenant build documents remain authoritative.
6. Use `Write` or `Edit` to publish the staged checklist, responsibility matrix, decision log, and rollback trigger.

## Approval Boundaries

Do not expand the cohort, care setting, note type, or EHR workflow without the corresponding clinical and change-control approval.

## Output

Return cohort, capabilities, owners, rehearsal evidence, training state, support coverage, metrics, stop criteria, and go/no-go authority. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Licensed capability is uncertain | Hold it out of scope until the vendor owner confirms it. |
| Rollback owner is absent | Do not launch. |
| Pilot metrics omit safety | Add clinical-quality and incident measures before approval. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
setting=outpatient; cohort=25-volunteers; training=complete; test-records=pass; support=covered; rollback=owned; decision=go
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
