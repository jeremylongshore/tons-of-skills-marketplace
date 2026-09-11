---
name: abridge-hello-world
description: "Run a bounded Abridge smoke test through the documented user workflow using an approved test encounter and no invented API. Use when validating a new tenant or pilot cohort. Trigger with \"smoke test Abridge\"."
argument-hint: "[environment] [test-encounter-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- smoke-test
- consent
- note-review
model: inherit
effort: medium
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Consent-to-Note Pilot Smoke Test

## Overview

Prove the smallest useful path: authorized user, designated test patient or synthetic scenario, consent handling, recording, note creation, Web Editor review, Linked Evidence check, and approved final disposition.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge's documented entry path uses its clinician application and Web Editor rather than a public create-session REST tutorial.
- Recording guidance requires following the organization's consent policy.
- The clinician reviews and edits the generated draft before sending or otherwise finalizing it.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Confirm the environment, authorized user, approved test-record procedure, consent script, and expected note destination.
2. Use `Read`, `Glob`, and `Grep` to inspect the local test plan, tenant labels, and expected configuration without opening credentials.
3. Run the documented application workflow with synthetic dialogue or the health system's designated non-production encounter.
4. Verify note creation, visible sections, editability, and a sample of Linked Evidence; record outcomes without clinical text.
5. Exercise one safe failure path such as interrupted capture or withheld send, then confirm no unintended chart update.
6. Use `Write` or `Edit` to record the receipt; use `WebFetch` only for current official Abridge instructions.

## Approval Boundaries

Do not use a real patient or send content to a production chart unless the health system's controlled test protocol explicitly authorizes it.

## Output

Return environment, test identity class, consent path, workflow stages, evidence sample result, chart-write count, failure-path result, and go/no-go. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| No designated test encounter exists | Stop and obtain one through the EHR test-data process. |
| Patient identity does not match | Stop before recording. |
| Draft cannot be reviewed | Do not send or finalize it. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
environment=nonprod; encounter=designated-test; consent=scripted; draft=reviewable; evidence=sample-pass; chart-writes=0; result=pass
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
