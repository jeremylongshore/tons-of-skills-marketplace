---
name: coderabbit-data-handling
description: >-
  Define code, cache, retention, export, and sensitive-path controls for a repository or organization. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "audit CodeRabbit data handling".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, privacy, retention, data-governance]
---
# CodeRabbit Data Handling

## Overview

Map what CodeRabbit may read, retain, cache, and export before changing controls. Exclusions do not replace source-control secret prevention.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Cached data is documented as never used for training and expiring within one week.
- Cached data is encrypted except for open-source projects.
- Organizations can disable cache or data retention.
- Path filters change review surfaces, not Git history or provider access.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Classify repositories and paths by sensitivity and contractual requirements.

2. Record installation scope, filters, cache, retention, exports, and reports.

3. Design access minimization, secret prevention, exclusions, retention, and custody.

4. Pilot on synthetic data and confirm coverage and incident ownership.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require security and privacy approval before changing retention, exporting data, or expanding access. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A data-flow register, classification map, control matrix, patch, and residual-risk statement. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Disable cache for a regulated repository and verify effective settings.

### Example 2

Prove a fixture exclusion does not replace provider secret scanning.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
