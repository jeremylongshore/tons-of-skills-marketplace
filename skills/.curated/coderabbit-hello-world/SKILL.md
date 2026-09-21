---
name: coderabbit-hello-world
description: >-
  Run a bounded first pull-request review with minimal supported configuration and explicit cleanup. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "smoke test CodeRabbit".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, quickstart, smoke-test, pull-requests]
---
# CodeRabbit First Review

## Overview

Prove installation and review behavior with a synthetic reversible PR. Avoid production secrets, branch-rule changes, and timing promises.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- CodeRabbit works with defaults; YAML is optional customization.
- Repository YAML belongs at root and is read from the feature branch.
- Draft reviews are disabled by default.
- Configuration and review commands expose or control review state.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Choose an approved test repository and verify installation scope.

2. Create one harmless feature-branch change and optional minimal schema-linked YAML.

3. Open a non-draft PR and observe walkthrough, findings, and CI.

4. Respond once, then close or merge under normal policy and clean up.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require owner approval before installation, a production-repository test PR, or merge. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A receipt with repository, branch, PR, config hash, review surfaces, CI, and cleanup. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Validate a private-repository installation with a docs-only PR.

### Example 2

Confirm a `chill` profile change is read before merge.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
