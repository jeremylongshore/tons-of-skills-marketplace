---
name: coderabbit-webhooks-events
description: >-
  Build customer-owned automation around Git-provider events containing CodeRabbit reviews without claiming a separate CodeRabbit webhook contract. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "automate CodeRabbit review events".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, events, webhooks, automation]
---
# CodeRabbit Review Event Automation

## Overview

Use the Git provider as event authority for normal PR review automation. Reviewed CodeRabbit docs do not establish a general outgoing CodeRabbit webhook and secret.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- CodeRabbit uses walkthrough comments, inline comments, reviews, and commands.
- Customer receivers validate the Git provider signature and delivery.
- Bot identity, repo, PR, action, and event type require allowlists.
- Slack or Discord automations are separate product surfaces.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Define provider event, identity evidence, repositories, action, idempotency, and replay window.

2. Verify provider signature over raw body before parsing.

3. Normalize required fields and queue an idempotent event behind a policy gate.

4. Test valid, invalid, replay, wrong-identity, duplicate, and out-of-order fixtures.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require security approval for webhook secrets and owner approval before any live mutation. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

An event contract, trust boundary, validation, fixtures, dead-letter policy, and mutation gate. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Notify on a verified CodeRabbit changes-requested review.

### Example 2

Reject a forged comment that merely mentions `@coderabbitai`.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
