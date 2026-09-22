---
name: coderabbit-observability
description: >-
  Measure review adoption, latency, findings, usage, and outcomes from documented dashboards, exports, reports, or API data. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "measure CodeRabbit reviews".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, observability, metrics, reporting]
---
# CodeRabbit Observability

## Overview

Use documented metric definitions and preserve denominators. Avoid scraping bot comments as a substitute for authoritative reporting.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Git-platform and IDE or CLI metrics have separate definitions.
- The Usage dashboard explains events, limits, and the Review Log.
- Data export supports offline analysis.
- Authenticated metrics APIs depend on plan and permissions.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Define decision, population, provider, repositories, UTC window, and metrics.

2. Export with timestamps, filters, pagination, and exclusions.

3. Compute coverage, response, resolution, and usage with denominators.

4. Compare cohorts and publish thresholds only after baseline evidence.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require data-owner approval before user-level exports, scheduled reports, or API credentials. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A reproducible metric spec, source receipt, dataset summary, dashboard, anomalies, and actions. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Compare coverage before and after central config rollout.

### Example 2

Reconcile CLI use with Review Log before buying credits.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
