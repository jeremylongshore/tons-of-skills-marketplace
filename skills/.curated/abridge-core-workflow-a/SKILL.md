---
name: abridge-core-workflow-a
description: "Design and verify the clinician workflow from consent through recording, draft review, Linked Evidence, and final note disposition. Use when implementing or auditing an Abridge clinical documentation pathway. Trigger with \"map the Abridge note workflow\"."
argument-hint: "[care-setting] [note-type]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- clinical-workflow
- note-review
- consent
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Encounter-to-Reviewed-Note Workflow

## Overview

Define a clinician-in-the-loop path that keeps consent, patient selection, capture quality, draft verification, edits, and finalization explicit. Treat generated content as a draft until the authorized clinician completes the health system's review process.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge's recording guidance tells clinicians to follow organizational consent policy before recording.
- The Web Editor supports reviewing and editing generated notes, and Linked Evidence supports source verification.
- A generated note remains subject to clinician review and the health system's documentation policy.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Identify care setting, authorized user, patient-selection source, consent rule, note type, and final record destination.
2. Map the happy path and failure exits from patient selection through recording, note creation, review, editing, and submission.
3. Use `Read`, `Glob`, and `Grep` to inspect local policies, templates, training, and integration configuration without reading patient data.
4. Add checks for wrong-patient risk, interrupted capture, missing source support, unsupported statements, and unsigned drafts.
5. Use `WebFetch` only for current official Abridge workflow documentation and label tenant-specific behavior separately.
6. Use `Write` or `Edit` to update the workflow artifact, acceptance script, and rollback handoff after owner confirmation.

## Approval Boundaries

Do not automate consent, clinical verification, note signing, or chart submission beyond the explicitly approved tenant workflow. A clinician must retain final review authority.

## Output

Return actors, states, handoffs, evidence checks, failure exits, clinical owner, and the boundary between generated draft and finalized record. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Patient identity is ambiguous | Stop before recording or opening the draft. |
| Evidence does not support a statement | Correct or remove it before finalization. |
| Destination workflow differs from the map | Hold submission and reconcile the tenant configuration. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
setting=outpatient; consent=confirmed; draft=reviewed; linked-evidence=sampled; clinician-signoff=required; ehr-handoff=approved
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
