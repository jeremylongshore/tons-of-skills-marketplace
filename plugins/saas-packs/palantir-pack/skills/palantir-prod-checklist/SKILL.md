---
name: palantir-prod-checklist
description: >-
  Run a fail-closed production-readiness review for a Foundry pipeline, OSDK application, DevOps product, or Compute Module. Use when preparing a first release or high-risk promotion. Trigger with "Palantir production checklist".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[product-application-pipeline-or-module]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, production-readiness, release]
---
# Palantir Production Readiness Gate

## Overview

Prove the exact artifact, data contract, access model, observability, failure path, and rollback before promotion. A collection of green local tests is insufficient without Foundry checks and target-environment evidence.

## Prerequisites

- Identify the accountable product, application, data, security, and operations owners.
- Freeze the candidate commit, generated OSDK/package, product version, or container digest.
- Read `references/official-docs.md` and collect non-production receipts for every required gate.
- Name the release window, maintenance constraints, rollback target, and recovery objective.

## Current Contract

- Code Repository checks and unit tests validate supported repository and transform contracts.
- DevOps and Marketplace provide versioned product installation and release management across environment spaces.
- Compute Modules require compatible immutable container images and produce active-replica usage and operational telemetry.
- OAuth scopes, Developer Console restrictions, Foundry permissions, and mandatory controls all participate in effective access.

## Authentication

Verify the production grant type, acting principal, requested scopes, Developer Console restrictions, secret storage, rotation, and revocation. Never copy a non-production secret into production or log a production token during validation.

## Instructions

1. Freeze and inventory the candidate artifact, dependencies, datasets, Ontology entities, Actions, external systems, parameters, schedules, and owners.

2. Verify tests, Foundry checks, representative builds or application flows, data expectations, and positive/negative access.

3. Verify production parameters, secrets, restrictions, markings, log policy, metrics, alerts, runbooks, capacity, and limits.

4. Rehearse failed deployment, bad data, auth denial, throttling, dependency outage, and prior-version rollback in non-production.

5. Obtain independent approvals, promote the exact artifact, observe the defined window, and record post-release evidence.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Production owners approve promotion; data/security owners approve data and access controls; operations owners approve monitoring and rollback. The executor must not self-approve a high-risk release where policy requires independence.

## Output

A signed readiness matrix with exact artifact, dependencies, test/build receipts, data and access controls, environment parameters, telemetry, failure rehearsals, approvals, promotion receipt, observation results, and rollback target.

## Error Handling

| Condition | Response |
|---|---|
| Candidate changes after approval | Invalidate approvals and rerun affected gates on the new exact artifact. |
| Negative-access test succeeds | Block release and correct permissions or application restrictions. |
| Rollback cannot be rehearsed | Do not promote until a restorable prior version and dependency set exist. |
| Post-release data checks fail | Stop consumers or schedules as approved, restore the prior version, and isolate affected outputs. |

## Examples

### Example 1

Gate a transforms product by freezing the branch commit, passing repository checks and a representative test build, validating dataset controls and alerts, then promoting one DevOps version.

### Example 2

Gate a Compute Module by pinning an image digest, testing non-root/platform/port requirements, OAuth restrictions, scale and failure behavior, logs, and prior-image rollback.

## Validation

- All evidence refers to the exact promoted artifact.
- Foundry checks and target-environment tests pass.
- Data correctness and positive/negative access are explicitly proven.
- Alerts and runbooks are exercised, not merely present.
- Rollback restores the prior healthy workflow within the objective.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
