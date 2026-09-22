---
name: abridge-reference-architecture
description: "Define an Abridge reference architecture that separates vendor, EHR, identity, device, customer, and clinical authority boundaries. Use when reviewing an enterprise Abridge design. Trigger with \"design the Abridge architecture\"."
argument-hint: "[care-settings] [ehr-landscape]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- architecture
- ehr
- governance
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Health-System Integration Architecture

## Overview

Produce a tenant-grounded component and trust-boundary model for clinician capture, Abridge processing, review, Linked Evidence, EHR handoff, identity, support, telemetry, and downtime. Show unknown private interfaces explicitly instead of filling them with generic REST or FHIR assumptions.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge publicly documents application and Epic-integrated user workflows across multiple care settings.
- Linked Evidence supports review by relating generated text to source material.
- Exact data flows, retention, interfaces, identity protocols, and EHR mappings require tenant and vendor evidence.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Inventory actors, care settings, devices, Abridge tenant capabilities, EHR modules, identity systems, networks, support channels, and owners.
2. Use `Read`, `Glob`, and `Grep` to locate interface control documents, data-flow diagrams, retention decisions, and threat models.
3. Draw data and control flows with classification, system of record, trust boundary, authorization, retention, and failure owner on each edge.
4. Model consent, wrong-patient prevention, clinician review, downtime, rollback, and protected support evidence as first-class paths.
5. Use `WebFetch` only for current official Abridge product context and label all tenant-specific facts by source revision.
6. Use `Write` or `Edit` to update the architecture record and unresolved evidence register.

## Approval Boundaries

Do not label an inferred interface, FHIR resource, webhook, hosting model, or retention period as implemented without authoritative evidence.

## Output

Return component map, flows, trust boundaries, data classes, systems of record, owners, failure paths, evidence revisions, and open assumptions. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Edge lacks an owner | Keep the design unapproved. |
| PHI crosses an undocumented boundary | Stop and escalate to privacy and security review. |
| Diagram conflicts with tenant evidence | Update the diagram and record the superseded assumption. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
settings=outpatient+ed; ehr=epic; boundaries=7; undocumented-edges=2; phi-flows=owner-reviewed; status=design-review
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
