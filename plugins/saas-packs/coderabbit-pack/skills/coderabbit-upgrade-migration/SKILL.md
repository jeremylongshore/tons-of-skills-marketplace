---
name: coderabbit-upgrade-migration
description: >-
  Analyze and upgrade configuration, plan-enabled features, tools, or platform integration through schema validation and reversible rollout. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "upgrade CodeRabbit configuration".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, upgrade, configuration, change-management]
---
# CodeRabbit Configuration Upgrade

## Overview

Treat managed-SaaS upgrades as configuration and entitlement changes, not SDK versions. Revalidate docs because contracts evolve.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- The current schema URL is `https://coderabbit.ai/integrations/schema.v2.json`.
- The configuration reference is generated from that schema.
- The YAML validator checks proposed configuration.
- Plan, provider, early-access, and self-hosted changes are separate.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Capture resolved config, schema validity, plan, provider, features, metrics, and rollback.

2. Identify added, removed, renamed, defaulted, or gated behavior.

3. Apply the smallest feature-branch change and test eligible and excluded cases.

4. Canary, compare evidence, then promote or revert.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require owners before plan, early-access, self-hosted, override, or production changes. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

A contract diff, validated patch, entitlement check, canary evidence, rollback, and record. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Adopt an auto-review option after schema validation.

### Example 2

Remove an obsolete field and prove resolved behavior.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
