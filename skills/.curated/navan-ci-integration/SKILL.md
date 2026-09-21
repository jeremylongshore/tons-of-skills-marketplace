---
name: navan-ci-integration
description: >-
  Gate Navan integration changes with deterministic fixtures and an isolated optional live smoke. Use when adding CI checks for adapters or data pipelines. Trigger with "test Navan in CI", "Navan contract tests", or "secure Navan CI".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<ci-provider> <required-suite> <live-policy>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Offline-First CI Contract

## Overview

Gate Navan integration changes with deterministic fixtures and an isolated optional live smoke. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Required pull-request checks must not depend on a Navan tenant, credentials, paid services, or private traveler data. A live smoke belongs only in a trusted event with protected secrets and a fixed read-only budget.

## Authentication

Run required jobs without Navan secrets and deny network access. Resolve a non-production credential only inside the separately approved live environment; never expose it to fork code.

## Instructions

1. Enumerate contract, mapping, privacy, and side-effect regressions.
2. Add sanitized fixtures for each enabled surface and failure class.
3. Require schema, mapping, redaction, reconciliation, and rollback tests.
4. Deny sockets and assert no secret is available in ordinary jobs.
5. Define an optional trusted live smoke with one bounded read and no retry.
6. Publish content-free receipts and preserve artifacts without sensitive payloads.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Protected secrets, network, live tenant reads, fixture refreshes, and required-check changes need explicit repository and data-owner approval.

## Error Handling

- A skipped required test is not a pass.
- Never combine untrusted checkout with privileged pull-request secrets.
- Do not snapshot a live traveler response into CI.

## Output

Return job names, trust matrix, fixture coverage, network policy, live budget, artifact policy, and rollback. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Run booking schema fixtures on every pull request.
- Schedule one synthetic non-production metadata read after merge.

## Validation

Test fork PRs, missing secrets, attempted network, malformed fixtures, vendor outage, and artifact scanning. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
