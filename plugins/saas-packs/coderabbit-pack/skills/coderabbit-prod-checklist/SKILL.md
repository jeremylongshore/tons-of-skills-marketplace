---
name: coderabbit-prod-checklist
description: >-
  Make an evidence-backed go-live decision for installation, configuration, governance, security, continuity, and operations. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "review CodeRabbit go-live".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, production-readiness, go-live, governance]
---
# CodeRabbit Production Readiness

## Overview

Turn a pilot into an explicit production decision. Each gate needs an owner, evidence, failure criterion, and rollback.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Configuration may resolve from multiple authorities.
- Provider permissions, roles, seats, and plans are distinct.
- Review state must coexist with independent CI and security.
- Retention, exports, keys, and support need owners.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Verify scope, ownership, permissions, config, plan, seats, roles, and data.

2. Exercise happy, skipped, invalid-config, limit, provider-failure, and rollback paths.

3. Confirm dashboards, incident ownership, continuity, and recertification.

4. Record GO, CONDITIONAL GO, or NO-GO with evidence.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Named repository, security, privacy, billing, and operations owners approve their own gates. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A readiness matrix, receipts, risks, continuity plan, rollback, and decision. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Issue conditional go-live limited to pilots.

### Example 2

Reject enforcement when manual continuity is untested.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
