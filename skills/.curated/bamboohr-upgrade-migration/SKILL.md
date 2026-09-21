---
name: bamboohr-upgrade-migration
description: >-
  Migrate a BambooHR integration across SDK, OpenAPI, auth, dataset, or endpoint
  changes with pinned evidence, dual-read comparison, and rollback. Use when
  replacing legacy report/dataset calls or upgrading an official SDK. Trigger
  with "upgrade BambooHR", "BambooHR migration", or "BambooHR deprecated API".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<current-contract> <target-contract>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, migration, upgrade]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Upgrade and Migration

## Overview

Move one contract boundary at a time and prove semantic parity on authorized
data. A repository default branch is not a released package; a README install
line is not registry evidence; and a `v1` URL does not mean the operation is
free from deprecation.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

- Dataset v1 data retrieval is deprecated in favor of
  `POST /api/v2/datasets/{datasetName}/data`.
- Saved/custom report operations carry replacement notices in the current SDK docs.
- Official Python and PHP SDK repositories were updated 2026-08-31. PHP package
  `bamboohr/api` 2.0.1 is on Packagist. Python `bamboohr-sdk` 1.0.0 is described
  in source but was absent from public PyPI and had no tag/release on 2026-09-11.

## Authentication

Preserve the existing identity during endpoint/SDK migration unless auth change
is the explicit workstream. If migrating API key to OAuth, treat registration,
state validation, token storage, refresh, permission equivalence, and revocation
as a separate staged migration with independent rollback.

## Instructions

1. Freeze the current adapter, dependency lock, endpoint inventory, auth mode,
   fields, filters, pagination, error mapping, retry policy, and production metrics.
2. Pin target OpenAPI/SDK evidence to an immutable commit, tag, or registry
   artifact. Verify package availability, integrity, license, and runtime support.
3. Diff operations, required parameters, auth scopes, status codes, response
   shapes, deprecations, pagination, retry behavior, and model return types.
4. Put old and new implementations behind the same application adapter. Keep
   writes on the old path while dual-reading a minimized approved cohort.
5. Compare record identities, field semantics, null/absent/redacted values,
   inactive/future cases, ordering, page completion, and error behavior. Do not
   log differing employee values; report aliases and counts.
6. Canary the new read path, then separately stage any idempotent write path with
   before/after verification and explicit approval.
7. Maintain checkpoints that both versions understand or define a reversible
   conversion. Do not let rollback replay completed HR mutations.
8. Remove old code only after the observation window, reconciliation, dependency
   scan, runbook update, and rollback retirement approval.

## Tool Discipline

Use Read, Glob, and Grep to inventory current contracts and versions. Use
Write/Edit only for approved adapters, migrations, tests, and docs. This skill
does not install packages, access a tenant, deploy, or delete legacy code.

## Approval Boundaries

Require approval for dependency/source pins, auth changes, production dual-read,
write canary, checkpoint conversion, cutover, rollback, and legacy removal.

## Output

Return source/target evidence, contract diff, package provenance, compatibility
matrix, dual-read reconciliation, canary metrics, checkpoint/rollback plan,
cutover decision, and deprecated code remaining.

## Error Handling

- Target package cannot be reproduced: stop and use a reviewed source pin or direct HTTP.
- Semantic mismatch: quarantine the field/operation; do not normalize silently.
- Ambiguous write during canary: read current state and halt further writes.

## Examples

- "Upgrade to the Python SDK" first verifies the distribution or pins source.
- "Move custom reports to datasets" produces a field-by-field dual-read migration.

## Resources

Read [official evidence](references/official-docs.md) for migration authority.
