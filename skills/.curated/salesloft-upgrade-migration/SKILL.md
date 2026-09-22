---
name: salesloft-upgrade-migration
description: >-
  Migrate an existing Salesloft integration through an evidence-backed endpoint, auth, schema, scope, and behavior diff with shadow validation and rollback. Use when current contracts or application assumptions change. Trigger with "Salesloft migration", "upgrade Salesloft integration", or "Salesloft API contract change".
argument-hint: "[repository-path] [migration-scope]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- migration
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Contract Migration

## Overview

This skill migrates the integration that actually exists. It does not assume a generic v1-to-v2 journey, API-key deprecation, or universal endpoint rename.

## Prerequisites

- Current integration commit, dependencies, deployment topology, and owners
- Complete method/path/scope/request/response inventory
- Target official documentation and migration reason
- Sanitized fixtures, shadow environment, rollback, and reconciliation plan

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inventory callers, auth, schemas, and compatibility code. Use `WebFetch` only for current official Salesloft documentation. Use `Write` or `Edit` after the migration boundary is approved.

## Current Contract

- The current public reference exposes v2 and historical v1 surfaces; compatibility is endpoint-specific.
- Resource paths are documented without a universal `.json` requirement.
- Auth flow choice depends on integration type; API keys remain a customer path and client credentials remain private-use only.
- Rate costs and endpoint schemas can change independently of URL versioning.
- Cadence import, export, and membership contracts must be verified from their own endpoint pages.

## Authentication

Treat auth migration as a separate reversible workstream. Preserve tenant binding and least privilege, and do not disable the old credential until the new path is proven and rollback is viable.

## Instructions

1. Inventory every live method, path, query, content type, scope, response field, and retry assumption.
2. Diff each used contract against current official documentation and classify required changes.
3. Add failing fixtures for every intentional schema or behavior delta.
4. Implement an adapter or dual-read path instead of changing all callers at once.
5. Shadow reads and compare normalized results without duplicating writes.
6. Canary approved mutations with read-after-write and reconciliation evidence.
7. Cut over gradually, monitor rate and error signals, then remove compatibility code only after rollback expiry.

## Approval Boundaries

Do not automatically fall back between API versions, convert auth flows, import cadences, or replay writes. Each live mutation and irreversible cleanup needs explicit approval.

## Output

Return contract diff, affected callers, fixture results, shadow comparison, canary evidence, cutover state, rollback trigger, and cleanup date.

## Error Handling

| Condition | Response |
|---|---|
| Undocumented behavior | Stop and obtain provider or support confirmation. |
| Shadow mismatch | Keep old reads authoritative and isolate the field delta. |
| Canary uncertainty | Reconcile before retry or wider rollout. |
| Rate regression | Halt expansion and compare endpoint/page cost. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
contracts=14; changed=3; shadow-match=100%; canary=pending; rollback=ready
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Salesloft API reference](https://developers.salesloft.com/docs/api/salesloft-platform/)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
