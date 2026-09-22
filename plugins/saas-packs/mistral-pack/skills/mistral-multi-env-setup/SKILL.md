---
name: mistral-multi-env-setup
description: >-
  Isolate Mistral development, staging, and production by workspace, credential, data, budget, and routing policy. Use when configuring multiple environments. Trigger with "separate Mistral environments", "configure Mistral staging", or "audit Mistral environment isolation".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environments> <workspace-policy> <promotion-path>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, environments]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Multi-Environment Isolation

## Overview

Prevent development changes from consuming production data, budget, capacity, or state. Make environment identity explicit in secrets, resources, telemetry, artifacts, and promotion evidence.

## Prerequisites

- An environment inventory and accountable owners.
- Secret, budget, data, model, endpoint, and state isolation requirements.
- A promotion path with synthetic staging tests and production rollback.

## Current Contract

Limits are workspace-shared across keys, so extra keys do not guarantee capacity isolation. Organization/workspace, role, limit, and billing controls must be inspected.

## Authentication

Use distinct environment secret references and narrow workspace identity. Fail closed if runtime environment and secret metadata disagree.

## Instructions

1. Inventory each environment's workspace, key owner, secret, data class, models, endpoints, and state.
2. Decide separate-workspace needs from capacity, spend, admin, and data isolation.
3. Encode non-secret environment identity and allowed surfaces in reviewed config.
4. Block production identifiers, files, workflow IDs, and overrides from non-production.
5. Promote one immutable artifact through offline, staging, and approved canary evidence.
6. Test rotation, wrong-environment denial, cap exhaustion, rollback, and orphan reconciliation.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Workspace or key creation, roles, budget or limit changes, production secret access, promotion, and deletion require administration approval. Record each mutation against its environment owner.

## Error Handling

- Multiple keys in one workspace still share rate boundaries.
- Production fixtures in staging can violate data policy.
- Mutable deployment artifacts invalidate promotion evidence.

## Output

Return environment matrix, workspace/secret mapping, allowed surfaces, caps, promotion state, isolation tests, owners, and rollback.

## Examples

- Use separate production capacity while development uses synthetic fixtures.
- Reject a staging runtime resolving a production-labeled secret.

## Validation

Attempt cross-environment secret, model, file, workflow, and telemetry access; prove denial, rotation, promotion, and rollback.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
