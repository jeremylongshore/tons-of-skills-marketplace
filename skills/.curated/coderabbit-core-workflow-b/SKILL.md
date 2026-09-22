---
name: coderabbit-core-workflow-b
description: >-
  Tune review signal with current learnings, detected guideline files, path instructions, and measured feedback. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "tune CodeRabbit reviews".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, learnings, guidelines, review-quality]
---
# CodeRabbit Learnings and Guidelines

## Overview

Improve relevance using supported knowledge layers. Avoid invented configuration keys and judge changes against labeled real findings.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Learnings arise from natural-language interaction with review comments.
- Code guidelines can be detected from files such as `CLAUDE.md` and `AGENTS.md`.
- Path instructions guide review; path filters change scope.
- Configuration precedence can change the effective result.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Sample accepted, rejected, and unresolved findings.

2. Separate organization guidance, repository rules, path instructions, and temporary feedback.

3. Draft one supported measurable tuning change and validate resolved config.

4. Pilot comparable PRs and retain only improvements that preserve risky-path coverage.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require owner approval before changing shared learnings, global overrides, or exclusions. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A labeled sample, hypothesis, supported change, comparison metrics, and rollback decision. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Move a durable convention into `AGENTS.md` and verify detection.

### Example 2

Replace unsupported `custom_patterns` with documented path instructions.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
