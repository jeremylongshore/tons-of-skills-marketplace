---
name: abridge-performance-tuning
description: "Measure and improve Abridge workflow latency and friction using privacy-safe health-system evidence. Use when clinicians report slow capture, note readiness, review, or EHR handoff. Trigger with \"measure Abridge performance\"."
argument-hint: "[cohort] [time-window] [workflow-stage]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- performance
- workflow-metrics
- clinical-operations
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Clinical Workflow Performance Study

## Overview

Measure the stages users experience instead of imposing invented API latency targets. Separate device and network conditions, capture duration, processing wait, review effort, and EHR handoff while protecting patient and clinician identity.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Official recording guidance identifies connectivity, microphone contention, device placement, and Bluetooth use as factors in capture quality and processing experience.
- Abridge's Redraft support page documents a user-visible regeneration workflow, but one published timing is not a universal service-level objective.
- Local baselines and signed service commitments control operational thresholds.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Define the cohort, stage boundaries, clock source, sampling policy, privacy threshold, and approved service objectives.
2. Use `Read`, `Glob`, and `Grep` to inspect instrumentation and dashboards for identifiers or note content that must be removed.
3. Measure stage distributions and failure rates, not only averages; stratify by device, location, care setting, and workflow version when safe.
4. Correlate slow paths with network and device conditions, review edits, downstream EHR behavior, and support events.
5. Use `WebFetch` only for current official workflow guidance; never convert marketing or support examples into an SLA.
6. Use `Write` or `Edit` to add bounded instrumentation or publish an experiment with rollback and success criteria.

## Approval Boundaries

Do not capture audio, transcript, note text, patient identifiers, or individual productivity rankings in performance telemetry.

## Output

Return stage definitions, percentile distributions, failure rates, cohort caveats, suspected boundary, experiment, rollback, and owner. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Stage clocks are incomparable | Repair instrumentation before drawing conclusions. |
| Small cohort risks identification | Aggregate or extend the window. |
| Optimization reduces review quality | Roll back immediately and notify the clinical owner. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
stage=note-ready-to-reviewed; cohort=outpatient-aggregate; p50=local-baseline; p95=regressed; phi=none; experiment=network-path-check
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
