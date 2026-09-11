---
name: abridge-rate-limits
description: "Analyze and control capacity, queueing, and backpressure for a tenant-specific Abridge integration without inventing public limits or headers. Use when handling concurrency or throttling requirements. Trigger with \"plan Abridge capacity\"."
argument-hint: "[interface] [peak-workload]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- capacity
- backpressure
- reliability
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Capacity and Backpressure Contract

## Overview

Derive limits from the signed tenant interface and observed approved responses, then protect clinical workflows with bounded queues, idempotency, retry budgets, and downtime procedures. Public product scale claims are not an API rate contract.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- The cited public Abridge materials do not define universal API quotas, concurrency tiers, reset headers, or retry semantics.
- Any limit or retry behavior must be tied to a versioned private interface contract or directly observed tenant evidence.
- Retries must not duplicate chart updates, note handoffs, or other clinical actions.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Freeze the interface, contract revision, workload units, peak model, delivery semantics, and clinical recovery objective.
2. Use `Read`, `Glob`, and `Grep` to inspect queues, retries, idempotency keys, timeouts, and dashboards.
3. Classify operations as safe to retry, conditionally retryable, or never automatic; bind each to evidence.
4. Design bounded exponential backoff with jitter only where the approved contract permits it, and cap total attempts and age.
5. Use `Write` or `Edit` to add tests for saturation, duplicates, stale work, poison messages, and manual recovery.
6. Use `WebFetch` only for current public workflow context; do not infer missing protocol details.

## Approval Boundaries

Do not load-test a live Abridge or EHR tenant, manufacture 429 responses, or replay clinical writes without written authorization.

## Output

Return authority revision, workload model, operation classes, queue bounds, retry budget, idempotency evidence, alerts, and downtime handoff. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Limit has no authoritative source | Mark it unknown and use a conservative configurable bound. |
| Operation is not idempotent | Require manual reconciliation instead of automatic retry. |
| Queue age exceeds clinical objective | Stop intake and invoke downtime procedure. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
interface=tenant-handoff; authority=ICD-r7; peak=contracted; retries=bounded; duplicate-test=pass; live-load-test=no
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
