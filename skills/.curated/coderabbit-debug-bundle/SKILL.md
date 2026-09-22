---
name: coderabbit-debug-bundle
description: >-
  Assemble a minimal redacted diagnostic package for configuration, review, CLI, or provider failures. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "build a CodeRabbit debug bundle".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, diagnostics, support, redaction]
---
# CodeRabbit Debug Bundle

## Overview

Collect only evidence needed to reproduce the failing boundary. Preserve timestamps and provenance while excluding code, credentials, private comments, and unrelated users.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- Feature-branch YAML, resolved config, eligibility, commands, and limit state are primary evidence.
- CLI failures have separate auth and network contracts.
- Provider permission state must be captured without tokens.
- Service health is evidence, not a substitute for local checks.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Define symptom, time window, surface, expected behavior, and reproduction boundary.

2. Collect redacted IDs, config hash, eligibility fields, timestamps, and CI state.

3. Remove source, secrets, emails, tokens, payloads, and unrelated comments.

4. Reproduce once safely and list included and excluded evidence.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require owner approval before reading private PR content, audit data, or transmitting a bundle. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A redacted manifest, timeline, config hash, reproduction, classification, and support summary. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Prepare skipped-draft evidence without exporting source.

### Example 2

Separate a CLI proxy failure from a rate-limit response.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
