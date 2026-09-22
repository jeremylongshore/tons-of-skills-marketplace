---
name: algolia-multi-env-setup
description: >-
  Design isolated Algolia development, staging, preview, and production targets with explicit promotion rules. Use when environments share credentials or index names, or previews need bounded search data. Trigger with "Algolia environments", "Algolia staging setup", or "preview index".
argument-hint: "[repository-path] [environment-map]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- environments
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia Multi-Environment Setup

## Overview

This skill makes environment isolation an application-owned contract. It does not assume one provider topology: separate applications, index namespaces, or a combination may be selected from security, data, cost, and operational requirements.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Map every runtime environment to an explicit application ID, index namespace, credential owner, and data classification.
- Prevent preview or branch input from selecting an arbitrary production index.
- Promote versioned settings and transforms through review rather than copying unknown live state.
- Define lifecycle and cleanup for ephemeral indices before creating them.

## Authentication

Use separate custom keys and secret scopes for each environment. Browser builds receive only the search credential for their resolved environment.

## Instructions

1. Inventory applications, indices, replicas, keys, deployment environments, data sources, and retention rules.
2. Choose isolation boundaries based on blast radius, data policy, feature parity, and verified current commercial terms.
3. Implement an allowlisted environment resolver with no production fallback for unknown values.
4. Define reproducible record, settings, synonym, and rule promotion artifacts.
5. Test cross-environment denial, preview naming, cleanup, and production-selection safeguards.
6. Document owners, rotation, promotion, rollback, retention, and orphan-index review.

## Approval Boundaries

Do not create applications, copy production data, share keys, or delete preview indices until topology and data-policy owners approve.

## Output

Return the environment matrix, selected topology and tradeoffs, configuration resolver, key scopes, promotion flow, isolation tests, and lifecycle controls.

## Error Handling

| Condition | Response |
|---|---|
| Unknown environment | Fail closed instead of selecting production. |
| Preview requests production data | Reject unless an explicit approved sanitized source exists. |
| Settings drift | Rebuild from versioned artifacts and review the diff. |
| Orphan cleanup uncertain | Report candidates without deleting them. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
env=preview-482; app=nonprod; index=preview_482_products; data=synthetic
```

Expected handoff:

```text
resolver=allowlisted; prod-fallback=none; cleanup-after=reviewed-policy
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [Sending and managing data](https://www.algolia.com/doc/guides/sending-and-managing-data)
- [Algolia pricing](https://www.algolia.com/pricing/)
