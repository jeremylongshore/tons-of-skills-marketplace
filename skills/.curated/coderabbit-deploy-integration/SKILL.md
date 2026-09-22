---
name: coderabbit-deploy-integration
description: >-
  Roll out CodeRabbit with staged installation, central configuration, ownership, evidence, and rollback. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "deploy CodeRabbit organization-wide".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, deployment, central-configuration, onboarding]
---
# CodeRabbit Organization Rollout

## Overview

Treat rollout as controlled policy deployment. Central configuration, repository config, organization settings, and global overrides have distinct precedence.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- A dedicated `coderabbit` repository can provide central configuration.
- CodeRabbit must be installed on that repository.
- Repository files can override central config; global overrides apply last.
- Provider permissions and features vary by platform and plan.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Inventory providers, repositories, owners, data classes, and current gates.

2. Choose a representative pilot with success, failure, and rollback criteria.

3. Install least scope and deploy defaults without hard enforcement.

4. Measure, train maintainers, and expand in reversible cohorts.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require organization-admin approval for installation, overrides, central config, and enforcement cohorts. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A rollout inventory, precedence map, pilot plan, owners, cohort schedule, and rollback runbook. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Pilot `coderabbit/.coderabbit.yaml` for three repositories.

### Example 2

Pause rollout and restore prior settings when coverage regresses.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
