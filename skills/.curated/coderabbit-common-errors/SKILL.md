---
name: coderabbit-common-errors
description: >-
  Triage missing, duplicate, noisy, or misconfigured reviews from observed pull-request and configuration evidence. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "debug CodeRabbit reviews".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, troubleshooting, configuration, reviews]
---
# CodeRabbit Common Errors

## Overview

Diagnose the first failing boundary instead of relying on fixed wait-time tables. Installation, feature-branch configuration, eligibility, limits, and service health require separate evidence.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- The reviewed `.coderabbit.yaml` comes from the feature branch under review.
- The default branch is always included; `base_branches` adds other targets.
- Draft, author, title, and label controls can exclude a pull request.
- The YAML validator and `@coderabbitai configuration` are contract checks.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Capture provider, PR, author, draft state, target branch, labels, and last response.

2. Read and validate feature-branch YAML plus central or organization overrides.

3. Classify installation, eligibility, configuration, limit, command-state, or service failure.

4. Apply one reversible correction and compare the response with baseline.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require owner approval before changing installation scope, organization settings, or pull-request state. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A redacted timeline, resolved-config evidence, fault classification, smallest fix, and verification result. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Explain a skipped release PR whose target pattern is absent.

### Example 2

Correct a runbook that says YAML must first be merged to the base branch.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
