---
name: attio-upgrade-migration
description: >-
  Migrate an Attio integration through a contract-led inventory, OpenAPI and documentation diff, shadow validation, canary rollout, reconciliation, and tested rollback. Use when endpoint assumptions, client versions, schemas, or integration architecture must change. Trigger with "upgrade Attio integration", "Attio migration", or "Attio API contract change".
argument-hint: "[repository-path] [change-target]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.7.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- attio
- migration
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Attio Contract Migration

## Overview

This skill migrates the integration that actually exists. It does not assume a generic historical version jump; it proves every affected endpoint and data shape against current Attio contracts.

## Prerequisites

- Current integration commit, dependencies, and deployment topology
- Endpoint, scope, pagination, data-shape, and webhook inventory
- Representative redacted fixtures and reconciliation queries
- Canary cohort, rollback owner, and recovery objective

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inventory current assumptions and tests. Use `WebFetch` only for current official Attio documentation and OpenAPI. Use `Write` or `Edit` after the contract diff, rollout boundary, and rollback point are documented.

## Current Contract

- Validate method, path, scopes, request fields, response fields, value shapes, and pagination per endpoint.
- Treat official OpenAPI as an input to the diff, not a substitute for behavioral fixtures and endpoint documentation.
- Record and entry queries may use offset pagination and score-based rate accounting; other endpoints can expose cursors.
- Webhook changes must preserve raw-body signature verification and at-least-once idempotency.

## Authentication

Preserve tenant-to-token binding and least privilege throughout the migration. Any new scope requires explicit justification, administrator approval, and a reversible credential plan.

## Instructions

1. Freeze a baseline of call sites, dependencies, contracts, fixtures, metrics, and current production behavior.
2. Diff each affected endpoint against official documentation and OpenAPI.
3. Classify changes as compatible, additive, behavior-sensitive, or breaking.
4. Add compatibility adapters and tests for pagination, value shapes, errors, idempotency, and redaction.
5. Run shadow reads or dry-run comparisons and reconcile mismatches without customer-facing mutations.
6. Canary one bounded workspace or workload with explicit health and rollback thresholds.
7. Expand in stages, retain rollback until reconciliation passes, then remove obsolete paths deliberately.

## Approval Boundaries

Do not add scopes, alter destructive mutations, switch all tenants, or remove the rollback path without owner approval and recorded evidence.

## Output

Return the before-and-after contract matrix, risk classification, adapter plan, test evidence, shadow or canary results, reconciliation status, and rollback decision.

## Error Handling

| Condition | Response |
|---|---|
| Official sources disagree | Pause the affected endpoint and preserve both references. |
| Shadow results diverge | Classify the mismatch and keep production on the old path. |
| Canary error budget fails | Roll back and retain captured redacted evidence. |
| Rollback cannot restore state | Stop before rollout and repair recovery first. |

## Examples

Input:

```text
change=replace hand-written record client; cohort=one test workspace
```

Expected handoff:

```text
contract-diff=complete; shadow=matched; canary=pass; rollback=retained
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [OpenAPI specification](https://docs.attio.com/rest-api/endpoint-reference/openapi)
- [REST API overview](https://docs.attio.com/rest-api/overview)
- [Pagination](https://docs.attio.com/rest-api/guides/pagination)
