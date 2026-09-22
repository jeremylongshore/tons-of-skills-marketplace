---
name: coderabbit-incident-runbook
description: >-
  Coordinate a review outage, harmful-output wave, access incident, or merge-policy failure without silently bypassing safeguards. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "handle a CodeRabbit incident".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, incident-response, continuity, rollback]
---
# CodeRabbit Incident Runbook

## Overview

Contain impact while preserving independent security and CI. Separate provider health, service health, config, permissions, limits, and harmful output.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- CodeRabbit can fail independently from repository CI.
- Limits and exclusions can resemble an outage.
- Bypass authority belongs to repository governance.
- Status evidence needs timestamps and local corroboration.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Declare scope, severity, owner, repositories, and exposure risk.

2. Freeze risky rollout changes and preserve independent controls.

3. Classify using health, installation, eligibility, config, limit, and provider evidence.

4. Restore, use an approved manual-review continuity path, or remain fail-closed.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Only documented repository authority may relax a CodeRabbit-related gate; unrelated controls remain required. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A timeline, impact, containment, continuity control, recovery proof, and follow-up actions. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Use two named human reviewers during a confirmed outage.

### Example 2

Stop a faulty global override and prove restored config.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
