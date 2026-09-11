---
name: abridge-cost-tuning
description: "Evaluate Abridge adoption, workflow value, and avoidable operational friction without inventing prices or vendor billing meters. Use when reviewing an Abridge rollout or renewal. Trigger with \"analyze Abridge value\"."
argument-hint: "[cohort] [measurement-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- adoption
- value
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Adoption and Value Review

## Overview

Join contract-approved commercial facts with health-system telemetry and clinician feedback. Separate licensed access, eligible clinicians, active adoption, workflow completion, note-quality feedback, and downstream outcomes so cost decisions remain auditable.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge is sold and deployed as an enterprise clinical platform; public pages do not define a universal self-service price or API usage meter.
- Abridge case studies describe phased adoption and clinician-led scaling, but another organization's outcomes are not a local ROI guarantee.
- Clinical quality and safety outcomes must not be reduced to note volume or minutes saved.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze the cohort, contract period, eligible-user denominator, cost authority, and outcome definitions.
2. Use `Read`, `Glob`, and `Grep` to locate contract-approved fields, local utilization exports, training records, and prior decisions.
3. Calculate adoption and completion with explicit denominators; stratify by care setting without exposing clinician or patient identity.
4. Pair quantitative trends with note-quality feedback, support burden, after-hours work, and safety signals.
5. Use `WebFetch` only to contextualize with current official Abridge product and rollout materials; label external results as non-comparable.
6. Use `Write` or `Edit` to produce a decision table with evidence gaps and owner-approved actions.

## Approval Boundaries

Do not infer contract prices, penalize individual clinicians, or recommend expansion based solely on volume. Commercial and clinical owners must approve conclusions.

## Output

Return denominators, adoption funnel, workflow outcomes, support burden, contract-sourced cost fields, limitations, and expand/hold/remediate options. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Contract metric is undefined | Exclude it and request the signed commercial definition. |
| Cohorts are not comparable | Stratify or stop the comparison. |
| Small cells risk re-identification | Suppress or aggregate them under policy. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
window=90d; eligible=420; activated=301; sustained-users=244; contract-fields=verified; patient-data=none; recommendation=targeted-training
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
