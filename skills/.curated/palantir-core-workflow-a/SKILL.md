---
name: palantir-core-workflow-a
description: >-
  Design and validate a Foundry Python transform pipeline with explicit datasets, compute choice, expectations, and incremental semantics. Use when building or changing batch data pipelines. Trigger with "Foundry transform" or "Palantir data pipeline".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[repository-and-output-dataset]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, transforms, data-pipelines]
---
# Palantir Python Transform Pipeline

## Overview

Create a pipeline whose inputs, outputs, engine, write behavior, and quality checks are explicit before the first production build. Prefer the simplest supported compute engine that satisfies data scale and feature requirements, then prove the choice with Foundry metrics.

## Prerequisites

- Identify the owning project, Code Repository, input and output datasets, schema contract, data classification, and build schedule.
- Confirm whether the workload requires Spark or can use a single-node engine such as Polars, pandas, or DuckDB.
- Read `references/official-docs.md` and inspect current input transaction history before selecting incremental semantics.
- Develop on a sandbox branch with representative but appropriately protected data.

## Current Contract

- Python transforms support batch and incremental pipelines, reusable libraries, expectations, and single-node or distributed engines.
- Input and output datasets must differ; using the same dataset creates a cyclic dependency.
- Incremental input modes and output write modes have precise transaction semantics; `modify` and `replace` are not interchangeable.
- A snapshot build may be needed when incremental transaction history becomes progressively slow or invalid.

## Instructions

1. Write the pipeline contract: owner, inputs, output, primary key or deduplication rule, schema, data-quality expectations, and recovery objective.

2. Choose the engine from required features and observed scale; document why single-node or Spark is appropriate.

3. Implement the transform with explicit input and output declarations and keep pure business logic separately testable.

4. If incremental processing is justified, define input read modes, output write mode, late-arrival behavior, and snapshot recovery.

5. Preview representative cases, run repository checks, build on the branch, inspect metrics and output transactions, then request review.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The data owner must approve new outputs, schema changes, marking changes, retention behavior, and production schedules. An incremental conversion also requires an approved snapshot and rollback plan.

## Output

A pipeline contract, reviewed transform change, test evidence, branch build, metrics, output validation, ownership record, and recovery procedure. Include the exact input transactions and output transaction used for acceptance.

## Error Handling

| Condition | Response |
|---|---|
| A cycle is detected | Separate the input and output datasets and redesign any feedback loop. |
| Incremental output duplicates rows | Stop promotion and correct keys, read modes, write mode, or late-arrival handling; rebuild from a controlled snapshot. |
| The build is memory-bound | Inspect Foundry metrics, then change engine or resources from measured evidence rather than a fixed size band. |
| Schema drifts unexpectedly | Fail the expectation, quarantine the output transaction, and resolve the producer contract. |

## Examples

### Example 1

Convert an append-only event transform to incremental processing by defining the `added` input behavior, deduplication key, `modify` output behavior, snapshot recovery, and parity check against a full rebuild.

### Example 2

Move a medium-scale production transform from Spark to Polars only after feature compatibility, branch-build duration, memory, and output parity demonstrate the single-node engine is appropriate.

## Validation

- Repository checks and unit tests pass on the exact branch commit.
- Preview and full build cover representative edge cases and protected-data rules.
- Incremental and snapshot outputs reconcile to the defined tolerance.
- Metrics support the selected engine and resource request.
- The output owner confirms schema, quality, lineage, and rollback.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
