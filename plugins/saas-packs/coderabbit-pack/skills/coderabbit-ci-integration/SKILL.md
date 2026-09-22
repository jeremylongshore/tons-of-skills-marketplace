---
name: coderabbit-ci-integration
description: >-
  Design a fail-closed merge policy that combines CodeRabbit review state with provider checks without inventing a CodeRabbit status-check name. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "gate merges with CodeRabbit".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, ci-cd, github, merge-policy]
---
# CodeRabbit CI Integration

## Overview

Build a merge policy from observable provider state. CodeRabbit review state, GitHub Checks ingestion, and branch protection are separate contracts.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- `reviews.request_changes_workflow` controls whether CodeRabbit can submit a changes-requested review.
- The GitHub Checks tool reads existing CI results; it does not prove CodeRabbit publishes a stable check name.
- Branch rules must use check names observed in the target repository.
- Emergency paths must retain independent tests, security checks, and audit evidence.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Inspect current branch rules, recent CodeRabbit reviews, and actual check-run names.

2. Choose whether review state is advisory or required, and list independent CI authorities.

3. Pilot the smallest YAML and branch-rule change without enabling enforcement.

4. Prove clean, failing, and rollback paths before enabling the policy.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require repository-owner approval before changing branch rules, request-changes behavior, or bypass procedures. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A merge-policy record, observed check inventory, reviewed patch, pilot evidence, and rollback procedure. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Replace a guessed `coderabbitai` required check with observed review and check evidence.

### Example 2

Pilot request-changes behavior while retaining required tests and secret scanning.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
