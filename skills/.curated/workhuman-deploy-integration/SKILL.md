---
name: workhuman-deploy-integration
description: 'Deploy a customer-owned Workhuman adapter or supported managed integration through preview, canary, reconciliation, and rollback. Use when releasing integration changes. Trigger with "deploy a Workhuman integration".'
argument-hint: "[release-id] [target-environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, deployment, integration, rollback]
model: inherit
effort: high
compatibility: Designed for Claude Code; production deployment, managed-connector enablement, and tenant mutations require explicit accountable-owner approval
---
# Workhuman Integration Deployment

## Overview

Release an exact reviewed adapter or managed-connector configuration without confusing code deployment with authorization to change customer data or programs.

## Prerequisites

- An immutable release and passing `workhuman-prod-checklist` decision
- Current tenant contract, secretless configuration, principals, topology, and field authority map
- Canary, observability, reconciliation, abort, rollback, communications, and support plans

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to verify release artifacts, `WebFetch` for current vendor context, and `Write` or `Edit` only for deployment configuration, manifests, and redacted receipts.

## Current Contract

Workhuman offers managed integrations for workplace and HCM systems plus an open API. The customer contract determines whether the deployable unit is customer code, vendor configuration, or both; no public generic deployment endpoint should be assumed.

## Authentication

Bind runtime principals to one tenant, environment, direction, and approved capability. Acquire secrets from the approved store at runtime and verify rotation and revocation before cutover.

## Instructions

1. Verify the release identifier, approvals, contract digest, image or package digest, configuration digest, and dependency versions.
2. Diff current and target topology, principals, hosts, mappings, schedules, data classes, observability, and network policy.
3. Produce a mutation preview with exact services, tenant settings, records at risk, financial exposure, and expected downtime.
4. Rehearse deployment, disablement, rollback, checkpoint recovery, and reconciliation in a safe environment.
5. Confirm canary cohort, traffic or schedule, abort thresholds, support coverage, communications, and decision owners.
6. After explicit approval, deploy only the immutable candidate and keep business mutations disabled until separately authorized.
7. Canary the approved flow, observe safe service and business signals, and reconcile authoritative records.
8. Expand only on passing thresholds; otherwise halt and execute rollback, then retain a redacted receipt.

## Approval Boundaries

Do not enable production traffic, change a managed connector, alter schedules, migrate workers, create recognition, approve awards, or send notifications without explicit scope-specific approval.

## Output

Return release and configuration identities, deployment diff, mutation preview, rehearsal, approvals, canary evidence, reconciliation, final state, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Runtime differs from reviewed artifact | Abort before traffic and restart approval with the actual digest. |
| Canary violates a threshold | Halt expansion and execute the tested rollback. |
| Write outcome is ambiguous | Freeze the checkpoint and reconcile before replay. |

## Example

A redacted completion receipt might look like this:

```text
release=sha256:...; target=customer-prod; config=sha256:...; canary=20; thresholds=pass; reconciliation=exact; state=expanded
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman for Microsoft Teams](https://www.workhuman.com/capabilities/integrations/microsoft-teams/)

## Next Steps

Complete post-release review and keep rollback available until the agreed stability window closes.
