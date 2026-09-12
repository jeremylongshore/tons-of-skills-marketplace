---
name: mistral-upgrade-migration
description: >-
  Migrate a pinned Mistral client or deprecated API surface through characterization, contract diffing, and staged rollback. Use when upgrading SDKs or moving API generations. Trigger with "upgrade Mistral SDK", "migrate Mistral Agents", or "fix Mistral deprecations".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<from-version-or-surface> <to-version-or-surface> <scope>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral SDK and API Surface Upgrade

## Overview

Upgrade from evidence, not search-and-replace. Characterize the current adapter, compare exact target contracts, and isolate Public Preview migrations from dependency maintenance.

## Prerequisites

- A clean branch, pinned source/target versions, and adapter inventory.
- Characterization tests for requests, streams, errors, usage, and state.
- A canary, compatibility window, and rollback owner.

## Current Contract

Current docs expose Public Preview beta Agents and Conversations plus Workflows, while deprecated Agents remains documented. Choose the target per workload; this is not a one-to-one rename.

## Authentication

Use offline characterization where possible. Live comparison uses the server-side key, synthetic content, fixed budget, and content-free evidence.

## Instructions

1. Inventory imports, types, endpoints, models, options, parsing, retries, and state IDs.
2. Lock characterization tests before changing dependencies.
3. Diff releases, schemas, preview labels, and unsupported features.
4. Choose per workload: stable chat, Workflows, or explicitly accepted beta Agents/Conversations.
5. Migrate one adapter path at a time without leaking target SDK objects.
6. Run offline regression and approved canary; remove compatibility only after rollback expiry.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for dependencies, preview adoption, endpoint changes, live comparison, state migration, or compatibility removal.

## Error Handling

- Compiling can still hide stream, error, usage, or pagination changes.
- Deprecated-to-beta Agents may require redesigned state lifecycle.
- Automatic model substitution invalidates quality, price, and safety baselines.

## Output

Return source/target pins, contract diff, destination per workflow, changed call sites, tests/canary, preview risks, rollback, and removal date.

## Examples

- Upgrade the TypeScript client behind an unchanged app adapter.
- Keep stable chat while separately evaluating Workflows.

## Validation

Test both adapters with identical fixtures, malformed responses, cancellation, retry classes, usage, and rollback drill.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
