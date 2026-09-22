---
name: vastai-multi-env-setup
description: >-
  Separate development, staging, and production Vast.ai identities, templates, labels, budgets, data, and evidence so one environment cannot mutate another. Use when establishing or auditing environment isolation. Trigger with: "set up Vast.ai environments", "separate Vast.ai prod and dev", "govern Vast.ai templates by environment".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environments-teams-and-promotion-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - environments
  - isolation
  - promotion
compatibility: 'Requires named environments, Teams or account contexts, scoped keys, immutable templates, secret stores, and cost ownership.'
---

# Vast.ai Environment Isolation

## Overview

Vast.ai does not turn naming conventions into isolation automatically. Build the boundary from team/account context, scoped keys, immutable template hashes, labels, data prefixes, budgets, and promotion evidence.

## Prerequisites

- Environment owners, sensitivity, workloads, regions, budgets, and approved accounts or teams
- Separate keys, SSH identities, storage prefixes, templates, registries, and alert routes
- Promotion, break-glass, rollback, and access-review procedures

## Instructions

### Step 1: Define environment identity

Assign each environment an explicit team/account context, key IDs, labels, data prefix, budget, and owner. Reject implicit current context.

### Step 2: Separate credentials

Create environment-specific scoped keys and dedicated SSH access. Production credentials must never be available to development jobs or forked CI.

### Step 3: Version templates and images

Use immutable image digests and template hashes. Promote the same bytes by recorded identity rather than rebuilding for each environment.

### Step 4: Constrain data and resources

Use distinct checkpoint/storage prefixes, resource labels, Serverless IDs, and notifications. Validate that a dev key cannot read or mutate production.

### Step 5: Promote through evidence

Require dev tests, staging canary, recovery, cost, and security receipts before a production role references the candidate identity.

### Step 6: Audit drift

Regularly compare members, roles, keys, templates, active resources, labels, budgets, and stale environment variables across contexts.

## Authentication

Environment isolation depends on distinct scoped credentials and explicit team/account context. Never infer environment only from a filename, branch, or mutable image tag.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Environment authority and resource map
- Cross-environment positive/negative access tests
- Promotion, drift, exception, and rollback receipt

Return environment contexts, role/key IDs, immutable release identity, data prefixes, access tests, budget owners, and promotion state.

## Examples

Staging and production use different team contexts and keys but promote the identical template hash; a staging key's attempted production instance read is retained as an expected denial.

## Error Handling

| Failure | Response |
| --- | --- |
| Current context is unknown | Stop before search or mutation and resolve the account/team explicitly. |
| One key spans unrelated environments | Replace it with scoped environment-specific identities. |
| Promotion rebuilds mutable bytes | Reject the release and promote an immutable digest/hash. |
| Cross-environment denial fails | Contain access, review audit logs, and repair roles before proceeding. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Teams overview](https://docs.vast.ai/guides/teams/teams-overview)
- [CLI permissions](https://docs.vast.ai/cli/permissions)
- [Managing templates](https://docs.vast.ai/guides/templates/managing-templates)
