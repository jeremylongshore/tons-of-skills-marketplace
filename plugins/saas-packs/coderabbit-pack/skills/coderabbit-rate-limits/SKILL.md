---
name: coderabbit-rate-limits
description: >-
  Analyze PR, IDE, and CLI limits using the current per-developer hourly contract and usage evidence. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "check CodeRabbit rate limits".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, rate-limits, capacity, usage]
---
# CodeRabbit Review Rate Limits

## Overview

Use current dashboard and responses instead of stale concurrency tables. Separate CodeRabbit allowances, file limits, credits, and provider API limits.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- The current plan table defines reviews per developer per hour and files per review.
- Allowances refill under the documented model.
- `@coderabbitai rate limit` reports PR quota without a review.
- The usage-based add-on can continue eligible reviews with credits.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Capture user, org, plan, surface, time, response, Review Log, files, and allowance.

2. Classify allowance, file limit, credit state, provider limit, or service failure.

3. Reduce avoidable events or present a dated capacity decision.

4. Retry only after documented refill or approved change.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require billing approval before enabling usage billing or buying credits; never spam retries. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A limit record, classification, current contract, mitigation, spend impact, and verification. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Use the rate-limit command without consuming a review.

### Example 2

Separate a provider 403 from CLI allowance response.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
