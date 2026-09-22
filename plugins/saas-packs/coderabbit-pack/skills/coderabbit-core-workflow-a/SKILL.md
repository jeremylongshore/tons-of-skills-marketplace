---
name: coderabbit-core-workflow-a
description: >-
  Run the primary CodeRabbit review loop from eligibility through finding disposition and verification. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "run a CodeRabbit PR review".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, pull-requests, code-review, workflow]
---
# CodeRabbit Pull Request Review

## Overview

Operate one evidence-backed review cycle. Separate walkthroughs, inline findings, incremental review, full review, CI, and human merge ownership.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Eligible pull requests are reviewed automatically unless configuration excludes them.
- The walkthrough is separate from inline findings.
- Incremental and full reviews are distinct commands.
- CodeRabbit supplements rather than replaces required CI and human judgment.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Verify installation, eligibility, feature-branch config, and independent CI.

2. Group walkthrough and inline findings by severity, file, and evidence.

3. Resolve valid findings in bounded commits and explain declined findings.

4. Request the appropriate documented review and confirm closure before handoff.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require human approval before pushing fixes, dismissing security findings, requesting approval, or merging. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A finding ledger with evidence, dispositions, commits, residual risk, and merge recommendation. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Process an incremental review after a narrow bug fix.

### Example 2

Decline a false positive with repository evidence retained in the PR thread.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
