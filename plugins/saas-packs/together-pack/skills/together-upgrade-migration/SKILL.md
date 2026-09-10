---
name: together-upgrade-migration
description: >-
  Migrate Together AI Python SDK v1, OpenAI-compatible clients, deprecated models, or legacy dedicated endpoints with inventory, contract tests, canaries, and rollback. Use when upgrading Together dependencies or provider resources. Trigger with "upgrade Together SDK", "Together model migration", or "migrate Together endpoint v1".
argument-hint: "[repository-path] [sdk|model|endpoint] [target]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.9.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- together-ai
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code; live migration verification requires authorized Together AI access
---
# Together AI Upgrade and Migration

## Overview

This skill moves one Together contract at a time while preserving response, model-quality, cost, and rollback evidence.

## Prerequisites

- An inventory of SDK versions, API calls, model IDs, and dedicated resources
- Current migration, model lifecycle, and deprecation documentation
- Golden requests/evaluations plus latency and cost baselines
- A rollback target and owners for traffic, data, billing, and teardown

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate dependencies, direct calls, model constants, response assumptions, and endpoint management. Use `WebFetch` for current migration and deprecation contracts. Use `Write` or `Edit` only after scope and rollback are agreed.

## Current Contract

- Python v1 is maintenance-only; new features target `together>=2.0.0` and may use changed method/response shapes.
- OpenAI-compatible migration requires Together's base URL, project key, and Together model IDs.
- Same-lineage model upgrades may redirect after notice; materially new models require explicit migration and evaluation.
- New dedicated capacity uses v2 DMI; legacy v1 create/restart paths are retired.

## Authentication

Preserve project-scoped `TOGETHER_API_KEY` injection while changing clients or endpoints. Never reuse development keys in production or expose a key during dual-run comparison.

## Instructions

1. Classify the migration as SDK, model, compatibility layer, or dedicated endpoint and freeze the baseline.
2. Inventory every call, parameter, response field, model, job, retry, and management resource in scope.
3. Build contract and golden-quality tests before changing dependencies or routing.
4. Implement the target behind a reversible configuration or traffic boundary.
5. Canary with sanitized requests; compare behavior, latency, usage, errors, limits, and cost.
6. Promote explicitly, monitor, remove obsolete resources only after retention/rollback approval, and update the runbook.

## Approval Boundaries

Do not accept silent model substitution, delete legacy endpoints, revoke keys, or shift production traffic without evaluated behavior and an executable rollback.

## Output

Return source/target contracts, inventory, test delta, canary metrics, model/deprecation evidence, traffic state, rollback proof, obsolete-resource disposition, and owners.

## Error Handling

| Condition | Response |
|---|---|
| SDK response shape changes | Adapt at the provider boundary and keep caller contracts stable. |
| Model quality regresses | Roll back routing and revisit the candidate. |
| Legacy endpoint cannot restart | Move to v2 DMI; do not rely on v1 recovery. |
| Redirect is detected | Record the effective model and run migration evaluations. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
source=python-v1; target=python-v2; contracts=pass; canary=pass; rollback=verified
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Python v2 migration](https://docs.together.ai/docs/pythonv2-migration-guide)
- [Deprecations](https://docs.together.ai/docs/deprecations)
- [Dedicated v1 migration](https://docs.together.ai/docs/dedicated-endpoints/migrate-from-v1)
