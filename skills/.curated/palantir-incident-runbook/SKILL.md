---
name: palantir-incident-runbook
description: >-
  Triage and stabilize Foundry API, pipeline, application, or Compute Module incidents with evidence-preserving rollback. Use when degraded service, failed builds, access failures, or release regressions require response. Trigger with "Foundry incident" or "Palantir outage".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[incident-or-resource-id]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, incident-response, reliability]
---
# Palantir Foundry Incident Response

## Overview

Protect data integrity and access controls while restoring service. Classify the failing Foundry surface, preserve request/build/release evidence, apply the least risky reversible mitigation, and validate recovery before closing.

## Prerequisites

- Name the incident commander, technical owner, data owner, communications owner, severity, affected resources, and start time.
- Capture request IDs, build IDs, branch/commit, product or artifact version, module state, and recent approved changes.
- Read `references/official-docs.md` and the target enrollment's operational procedures.
- Confirm the rollback authority and protected-data handling rules before collecting logs.

## Current Contract

- API `429` or `503` can represent rate or concurrency limiting and should receive bounded backoff rather than an unbounded retry storm.
- Transform build reports and metrics distinguish queue, CPU, memory, dependency, and data-related failures.
- DevOps/Marketplace release management can retain prior versions and support controlled upgrades or rollback.
- Logs may expose sensitive content and require explicit log access plus appropriate markings.

## Authentication

Record grant type, principal, scope names, and application restrictions for API incidents, never token values. Do not rotate credentials until evidence distinguishes an authentication failure from permissions, restrictions, mandatory controls, throttling, or platform availability.

## Instructions

1. Declare severity, impacted workflow, current data-integrity risk, access-control risk, and the last known healthy version or build.

2. Classify the incident as API/auth, transform/build, OSDK/application, Compute Module, data quality, permissions, or release regression.

3. Preserve bounded evidence and freeze unrelated changes; restrict retries and writeback when integrity is uncertain.

4. Choose the safest reversible mitigation: reduce concurrency, pause a schedule, disable a failing consumer, restore an artifact/product version, or isolate a bad output.

5. Verify recovery through service health plus data correctness and permission checks, then publish a timeline and corrective actions.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Only authorized owners may pause production schedules, change access, roll back products, alter module scaling, rotate credentials, or suppress outputs. Emergency authority must be recorded with scope and expiry.

## Output

An incident record with severity, owners, timeline, evidence IDs, classification, customer/data impact, mitigation, approval, recovery validation, rollback outcome, and assigned corrective actions.

## Error Handling

| Condition | Response |
|---|---|
| Evidence collection could expose protected data | Use identifiers and selected redacted excerpts; involve the data/security owner before accessing logs. |
| The last healthy version is unknown | Stop forward changes and reconstruct artifact/product/build history first. |
| Mitigation restores HTTP success but data is wrong | Keep the incident open, isolate outputs, and validate lineage and transactions. |
| Repeated retries worsen impact | Cancel automation, reduce concurrency, and honor rate/concurrency guidance. |

## Examples

### Example 1

Stabilize a backend integration returning `429` and `503` by halting duplicate workers, applying bounded backoff, checking current limits, and validating both request success and downstream object consistency.

### Example 2

Roll back a DevOps product installation after an application release regression, verify the previous product version and OAuth/resource restrictions, and preserve the failed release evidence for follow-up.

## Validation

- Recovery is proven on the affected user or data workflow, not only a health endpoint.
- Data integrity, access controls, and pending writeback are explicitly checked.
- The exact mitigation and approval receipt are recorded.
- Temporary emergency access or settings have been removed or assigned an expiry.
- Corrective actions have owners and verification criteria.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
