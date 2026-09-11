---
name: lucidchart-upgrade-migration
description: 'Plan and execute a reversible Lucid SDK, CLI, manifest, API-version, Standard Import, or connector migration. Use when a Lucid integration has dependency or contract drift. Trigger with "upgrade Lucid integration".'
argument-hint: "[project-path] [target-version]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, migration, upgrades, compatibility]
model: inherit
effort: high
compatibility: Designed for Claude Code; dependency mutation, API-version changes, data migration, installation, and production rollout require owner approval
---
# Reversible Lucid Upgrade and Migration

## Overview

Move one Lucid contract boundary at a time with an immutable baseline, representative fixtures, canary evidence, and tested rollback.

## Prerequisites

- Clean source revision, dependency lockfile, manifests, deployed artifact identity, and current production version
- Representative synthetic imports, documents, data, and connector events where applicable
- Owners for code, data, Lucid application, source system, and rollback

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for version and usage inventory, `WebFetch` for current official migration contracts, and `Write` or `Edit` only for approved local changes, tests, and receipts.

## Current Contract

The Standard Import format evolves and may render differently over time. Extension SDK/CLI and manifest behavior are versioned through project dependencies. REST resources may require `Lucid-Api-Version`. These are separate migration axes and must not be changed blindly together.

## Authentication

Preserve credential classes and least scopes unless a documented target contract requires change. Treat new scopes, redirect URIs, consent, account grants, and secret rotation as separate approved migrations.

## Instructions

1. Inventory current and target package/CLI versions, API-version headers, manifests/scopes, import fixtures, connector schemas, and deployment artifacts.
2. Capture a clean baseline: build, types, manifests, tests, fixture imports/exports, data reconciliation, and rollback.
3. Re-fetch exact official docs and inspect target installed types/changelogs; create a breaking-change matrix.
4. Split changes into reversible steps: tooling/dependencies, compile fixes, manifest/scopes, format/schema, API version, and deployment.
5. Present dependency edits and any auth/data contract changes for approval.
6. Apply one step, regenerate the lockfile with the project package manager, and run narrow then full affected gates.
7. Test old/new representative fixtures and compare rendering, data, identifiers, errors, and performance.
8. Deploy a bounded canary after approval; reconcile, monitor, and roll back on threshold breach before broader promotion.

## Approval Boundaries

Do not upgrade packages, change API versions/scopes, rewrite stored data, reinstall extensions, or deploy merely because a newer version exists.

## Output

Return baseline/target matrix, official evidence, changed files, dependency and scope diffs, tests, canary, rendering/data variance, approval, and rollback status.

## Error Handling

| Condition | Response |
|---|---|
| Target types remove a used API | Stop and redesign with supported primitives; do not conceal it with casts. |
| Import renders differently | Preserve both artifacts, quantify variance, and require owner acceptance. |
| Rollback changes data/schema | Test a forward repair and recovery copy before rollout. |

## Example

```text
axis=sdk; baseline=locked; target=reviewed; fixture-parity=pass; scope-delta=none; canary=not-approved
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Promote only after canary parity, explicit acceptance of known variance, and tested rollback from the exact artifact.
