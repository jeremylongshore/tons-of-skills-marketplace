---
name: workhuman-prod-checklist
description: 'Gate a Workhuman integration or program change for production with contract, data, security, financial, support, canary, and rollback evidence. Use when preparing for go-live. Trigger with "review Workhuman production readiness".'
argument-hint: "[release-id] [tenant]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, production, readiness, release]
model: inherit
effort: high
compatibility: Designed for Claude Code; production deployment and tenant mutations require release, program, HCM, payroll, security, and vendor-owner approval as applicable
---
# Workhuman Production Readiness Gate

## Overview

Issue a fail-closed production decision from exact evidence, with no deployment or program mutation implied by a `READY` result.

## Prerequisites

- Immutable release or configuration identifier and complete scope
- Current tenant contracts, field authority map, program policy, security review, and support plan
- Synthetic test results, canary design, reconciliation, abort thresholds, and rollback owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect the candidate and evidence, `WebFetch` to re-check current vendor context, and `Write` or `Edit` only for the readiness record and approved release artifacts.

## Current Contract

Workhuman capabilities and managed integrations are customer-configured. Readiness must be evaluated against the subscribed products, current implementation documents, program controls, and dependent HCM or collaboration systems—not a generic public endpoint list.

## Authentication

Verify every human, administrator, managed connector, and API principal for least privilege, environment isolation, rotation, revocation, and support ownership.

## Instructions

1. Freeze release identity, tenant, products, data flows, mutations, excluded scope, deployment window, and owners.
2. Verify contract versions, entitlements, field authority, schemas, configuration, and dependency compatibility.
3. Require passing unit, contract, fixture, security, privacy, duplicate, partial-failure, capacity, and recovery tests.
4. Confirm audience and worker reconciliation, recognition policy, award controls, spend and financial ownership, reporting, and Store implications.
5. Review observability for safe correlation, latency, failures, queue age, reconciliation lag, spend anomalies, and misuse signals.
6. Exercise rollback or disablement and prove checkpoint preservation without losing authoritative records.
7. Present the canary cohort, mutation counts, approvals, abort thresholds, communications, support coverage, and rollback.
8. Return `BLOCKED` for any missing owner, stale contract, unresolved financial effect, failed gate, or untested recovery.

## Approval Boundaries

A readiness decision does not authorize deployment, connector changes, worker mutations, recognition, awards, communications, or spend.

## Output

Return the immutable scope, gate matrix, evidence links, principal review, canary and rollback plan, approvals, blockers, and `READY` or `BLOCKED` decision.

## Error Handling

| Condition | Response |
|---|---|
| Candidate changes during review | Invalidate evidence and restart from the new immutable identifier. |
| Rollback is untested | Return `BLOCKED` regardless of other passing checks. |
| Financial or worker impact is unclear | Return `BLOCKED` and route to payroll, HCM, or program ownership. |

## Example

A redacted completion receipt might look like this:

```text
release=sha256:...; tenant=customer-prod; gates=14/14; canary=25-workers; rollback=exercised; decision=READY; deploy=not-authorized
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Obtain execution approval for the exact reviewed identifier and preserve the readiness record with the release receipt.
