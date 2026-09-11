---
name: mindtickle-deploy-integration
description: 'Deploy a tenant-scoped Mindtickle adapter through a canary, reconciliation, and rollback workflow. Use when promoting an approved integration build. Trigger with "deploy Mindtickle integration".'
argument-hint: "[release-id] [environment]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, deployment, canary, rollback]
model: inherit
effort: high
compatibility: Designed for Claude Code; deployment, secrets, network policy, and production enablement require service and tenant-owner approval
---
# Controlled Mindtickle Adapter Deployment

## Overview

Promote a verified adapter without assuming a deployment platform, then prove tenant binding, safe behavior, and rollback from production evidence.

## Prerequisites

- An immutable build, passing CI receipt, contract digest, and dependency inventory
- Environment owners, secret references, tenant mapping, observability, and on-call coverage
- A canary workload, success thresholds, abort criteria, and tested rollback

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect manifests and receipts, `WebFetch` for current authorized contracts, and `Write` or `Edit` for deployment configuration, runbooks, and redacted evidence.

## Current Contract

Deployment architecture is customer-controlled. The adapter must use the exact tenant API or managed-connector contract already approved; health checks must prove local readiness separately from optional external dependency readiness.

## Authentication

Resolve secrets at runtime from the approved provider, bind them to one environment and tenant, deny shell or log exposure, and verify rotation and revocation ownership before rollout.

## Instructions

1. Freeze build identity, contract digest, configuration digest, tenant map, dependencies, and data-flow classification.
2. Validate least-privilege runtime identity, egress allowlist, encryption, secret references, resource limits, and log redaction.
3. Separate liveness, local readiness, and external dependency signals so a vendor outage does not cause uncontrolled restart storms.
4. Present the deployment diff, canary population, expected operations, alert thresholds, approvers, and rollback command.
5. After approval, deploy the canary and observe latency, errors, throttling, backlog, duplicate prevention, and reconciliation.
6. Expand only when the evidence window passes; stop automatically on an abort threshold.
7. Reconcile expected versus actual tenant state and retain deployment and rollback receipts without sensitive payloads.
8. Confirm the previous build and compatible contract fixtures remain deployable until the observation window closes.

## Approval Boundaries

Do not alter tenant configuration, inject credentials, enable production writes, expand the canary, or destroy the rollback build without named approvals.

## Output

Return build and contract identities, configuration review, deployment preview, approvals, canary metrics, reconciliation, promotion decision, and rollback readiness.

## Error Handling

| Condition | Response |
|---|---|
| Tenant binding is ambiguous | Block startup and repair configuration; never select a default tenant. |
| Canary crosses an abort threshold | Halt expansion and roll back using the approved procedure. |
| External health is unavailable | Preserve local service stability, pause work, and drain or queue within policy. |

## Example

```text
build=sha256:...; contract=...; tenant-map=exact; canary=5-percent; thresholds=pass; reconciliation=exact; rollback=ready
```

## Resources

- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)
- [Mindtickle Service Level Agreement](https://www.mindtickle.com/legal/service-level-agreement/)

## Next Steps

Close the observation window only after scheduled reconciliation and a current rollback rehearsal.
