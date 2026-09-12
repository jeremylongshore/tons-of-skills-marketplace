---
name: mistral-ci-integration
description: >-
  Gate Mistral integrations with offline contract tests and a protected optional live smoke lane. Use when adding provider checks to CI. Trigger with "test Mistral in CI", "add a Mistral quality gate", or "secure Mistral GitHub Actions".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<ci-provider> <required-suite> <live-lane-policy>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Mistral Offline-First CI Contract

## Overview

Make deterministic contract and safety tests required while isolating network evidence. Provider outage or missing fork secrets must not block ordinary review, and untrusted changes never receive credentials.

## Prerequisites

- A locked dependency graph and application-owned adapter.
- Synthetic fixtures for success, streams, tools, throttling, malformed data, and cancellation.
- A protected CI environment for a separately approved live smoke.

## Current Contract

Client and endpoint schemas can drift, but CI can validate the application contract offline. Live checks consume capacity and belong in a trusted branch, schedule, or approved lane with a strict budget.

## Authentication

Required jobs run without `MISTRAL_API_KEY` and deny unexpected network. The live job resolves a protected secret only after trust, branch, and approval guards pass.

## Instructions

1. Enumerate provider regressions affecting users, data, spend, or side effects.
2. Add fixture tests for normalized results, errors, streams, usage, and tool denial.
3. Check secret-bearing files, browser exposure, unpinned dependencies, and unsafe logs.
4. Run required jobs without provider secrets and deny networking where possible.
5. Create a named live smoke with trusted-event guards, one synthetic request, fixed output, and no retry.
6. Publish content-free receipts and document how to disable live checks without weakening required gates.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Require approval for secrets, network, paid smoke, live-derived snapshots, or required-check changes. Fork-origin code never receives the key.

## Error Handling

- A skipped required test is not a pass.
- Privileged pull-request events plus untrusted checkout can leak secrets.
- A flaky live check does not belong inside a required offline job.

## Output

Return job names, trust conditions, secret matrix, test inventory, network policy, live budget, artifact exclusions, and rollback.

## Examples

- Run fixtures on every PR and a synthetic live call only after merge.
- Fail if the key is mapped to a client-prefixed variable.

## Validation

Test fork PR, missing secret, outage, malformed fixture, accidental network, and live cancellation; scan artifacts.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.
