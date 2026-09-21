---
name: palantir-cost-tuning
description: >-
  Reduce Foundry compute usage through measured engine, resource, incremental, schedule, and Compute Module decisions. Use when build or application usage is high or unpredictable. Trigger with "Foundry cost tuning" or "Palantir compute usage".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[pipeline-or-compute-module]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, cost, compute]
---
# Palantir Compute and Usage Optimization

## Overview

Optimize from measured Foundry usage and telemetry, not invented data-volume bands. Separate transform-build consumption from interactive Compute Module replica consumption because they have different controls and failure modes.

## Prerequisites

- Identify the pipeline, build jobs, Compute Modules, schedules, owners, service objectives, and current usage window.
- Capture build duration, requested and observed CPU/memory, queue time, input change rate, output volume, and module replica activity.
- Read `references/official-docs.md` and confirm contract-specific pricing or usage questions with the account owner or Palantir representative.
- Define correctness and latency constraints that cannot be traded away.

## Current Contract

- Python transforms can use single-node engines or Spark; required feature support constrains the choice.
- Foundry build metrics expose requested and observed CPU and memory, enabling evidence-based resource changes.
- Incremental transforms can reduce repeated work only when their transaction semantics remain correct.
- Compute Module usage is measured while replicas are starting or active, including predictive autoscaling behavior.

## Instructions

1. Build a baseline that separates transform jobs, schedules, previews, retries, snapshots, and Compute Module replicas.

2. Rank usage drivers by measured consumption and business criticality.

3. Test one change at a time: engine, resource request, incremental mode, schedule, batch shape, property selection, or replica policy.

4. Compare output parity, latency, failure rate, queue time, and consumption against the baseline.

5. Promote the smallest validated change and monitor one full representative operating window.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The pipeline owner approves transform and schedule changes; the application owner approves module scaling changes; the commercial owner approves interpretations of contract pricing. Never shut down production compute or relax correctness controls solely to reduce usage.

## Output

A measured baseline, ranked drivers, experiment plan, before/after telemetry, correctness evidence, approved change, savings estimate with assumptions, and rollback threshold.

## Error Handling

| Condition | Response |
|---|---|
| Usage cannot be attributed | Add ownership and telemetry first; do not optimize from an aggregate bill alone. |
| Incremental results diverge | Revert to the prior snapshot behavior and fix transaction semantics before continuing. |
| Lower resources increase queueing or failures | Restore the prior request and evaluate engine choice or data-shape changes. |
| Replica usage persists without requests | Inspect minimum replicas and predictive autoscaling; verify behavior before changing availability. |

## Examples

### Example 1

Compare a Spark transform with a Polars implementation on representative branch builds, accepting the change only if required features, output parity, memory, duration, and reliability all pass.

### Example 2

Reduce Compute Module consumption by reviewing active and starting replica time, minimum-replica requirements, autoscaling behavior, and the application's cold-start objective.

## Validation

- Every recommendation points to a measured driver.
- Correctness and security controls remain unchanged or improve.
- Transform and Compute Module usage are reported separately.
- A representative post-change window meets latency and reliability objectives.
- Rollback thresholds and owners are explicit.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
