---
name: abridge-common-errors
description: "Triage Abridge recording, note-review, Epic handoff, and access failures from observed evidence without inventing vendor error codes. Use when an Abridge clinical workflow is degraded. Trigger with \"diagnose this Abridge issue\"."
argument-hint: "[environment] [symptom] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- troubleshooting
- clinical-workflow
- support
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Workflow Failure Triage

## Overview

Classify the failure by user-visible stage, preserve a minimum-necessary timeline, and route it to the correct health-system, EHR, device, identity, network, or Abridge owner. Prefer observed messages and approved runbooks over generic HTTP guesses.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- The documented workflow spans patient selection, recording, note creation, Web Editor review, and optional Epic handoff.
- Linked Evidence is a review aid that connects note text to source transcript or audio; it is not an automatic clinical approval.
- Public support pages provide user workflows, not a canonical public list of partner API status codes.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Record the environment, affected cohort, first observed time, last known good time, and exact visible symptom.
2. Use `Read`, `Glob`, and `Grep` to locate the approved runbook, interface contract, recent configuration change, and feature-flag history.
3. Separate capture/device failures, upload or connectivity failures, note-generation delays, editor issues, and EHR handoff failures.
4. Check whether the problem follows one user, device, location, specialty, note type, or EHR workflow without collecting note content.
5. Use `WebFetch` only to compare the symptom with current official Abridge support guidance.
6. Use `Write` or `Edit` to produce a redacted escalation receipt and update a runbook only when evidence supports the change.

## Approval Boundaries

Do not replay a patient encounter, open a patient note, change an EHR template, or disable a security control solely to diagnose a failure. Escalate clinical-safety concerns immediately.

## Output

Return impact, stage, evidence, likely owning boundary, safe checks completed, stop conditions, and the exact redacted artifact needed for escalation. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Patient content appears in evidence | Stop collection and move to the approved protected support channel. |
| No exact timestamp or user-visible symptom | Request bounded evidence before assigning a cause. |
| Clinical note may be unsafe | Pause downstream use and invoke the clinical-safety escalation path. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
stage=epic-handoff; cohort=one-clinic; capture-and-review=healthy; owner=local-ehr-template; phi-in-receipt=no; status=escalate
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
