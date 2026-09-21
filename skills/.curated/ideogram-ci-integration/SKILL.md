---
name: ideogram-ci-integration
description: >-
  Build deterministic CI for Ideogram adapters with sanitized schemas, fixtures, secret isolation, and a trusted optional live lane. Use when adding or auditing automated integration tests. Trigger with "test Ideogram in CI", "build Ideogram contract tests", or "secure an Ideogram GitHub workflow".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<ci-provider> <test-command> <trusted-live-policy>"
version: 1.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, ideogram, ci]
model: inherit
effort: high
compatibility: "Designed for Claude Code; normal CI runs entirely offline"
---
# Ideogram Continuous Integration

## Overview

Make Ideogram integration quality reproducible without granting untrusted changes a paid credential. Use fixtures and schema checks for every pull request, then isolate any live smoke test behind trusted-branch, synthetic-content, spend, and concurrency controls.

## Prerequisites

- CI trust model, branch policy, test runner, adapter seam, and secret provider.
- Sanitized fixtures covering sync, async, safety, errors, webhook, polling, and storage.
- Named owners for schema refresh, live-smoke spend, and failed-run cleanup.

## Current Contract

The first-party OpenAPI is machine-readable, while endpoint pages carry important behavioral details such as multipart requirements, unsafe empty URLs, and current V4 rendering constraints. CI must preserve both schema and documented semantic assertions.

## Authentication

Pull-request jobs must run without `IDEOGRAM_API_KEY`. A separately approved live job may receive a short-lived or environment-scoped secret server-side and send it only as `Api-Key` to `https://api.ideogram.ai`.

## Instructions

1. Inventory workflows, fork behavior, secret exposure, cache artifacts, and existing paid calls.
2. Add offline tests for multipart field names, mutually exclusive prompts, typed errors, safety outcomes, async terminal states, signature verification, download limits, and storage cleanup.
3. Pin a reviewed OpenAPI snapshot or hash and report drift without blindly replacing owned contracts.
4. Scan fixtures and artifacts for keys, prompts, URLs, image bytes, and customer identifiers.
5. Gate any live smoke to a trusted protected context with manual or environment approval, one synthetic request, strict timeout, output count, and cost ceiling.
6. Persist no vendor URL, delete generated test assets, and publish only content-free status evidence.
7. Require offline tests for merge; keep vendor availability from making normal pull requests flaky.

## Tool Discipline

Use Read, Glob, and Grep to inspect workflows and tests. Use Write and Edit for approved CI, fixture, and documentation changes. Do not add secrets, enable paid fork jobs, or change required checks without repository authority.

## Approval Boundaries

Require approval for workflow permissions, new secret access, live spend, external artifact upload, required-check changes, and branch-protection changes. Fork-originated code must never receive the Ideogram key.

## Error Handling

- Fail on fixture secrets, undocumented schema changes, unsafe-output bypass, or retained image artifacts.
- Quarantine vendor outage in the optional live lane; do not weaken deterministic merge gates.
- Cancel timed-out jobs and reconcile any accepted async generation before retrying.

## Output

Return workflow and test paths, trust boundaries, assertion counts, OpenAPI hash, secret-scan result, offline gate status, live-lane status and spend, cleanup receipt, and rollback plan.

## Examples

- Run multipart and webhook fixtures on every pull request; run one V4 smoke only after protected-environment approval.
- Report `offline=pass; secrets=0; live=skipped-untrusted-fork; required_gate=pass`.

## Validation

Test trusted and untrusted event paths, inspect effective permissions, rerun the offline suite, and verify artifacts contain no content. Exercise cancellation and confirm any live-created object is deleted.

## Resources

- [Current first-party evidence map](references/official-docs.md) — use the dated endpoint, webhook, billing, team, and training links as the contract index for this workflow.
- Recheck the endpoint-specific page and current OpenAPI description before relying on an enum, limit, beta feature, or lifecycle claim.
- Record live observations as environment-specific evidence, not as universal vendor guarantees.
