---
name: coderabbit-install-auth
description: >-
  Analyze and implement platform installation plus interactive or headless CLI authentication with least privilege. Use when this operator task needs a current, evidence-backed
  CodeRabbit workflow. Trigger with "install CodeRabbit".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[target] [evidence-or-scope]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current CodeRabbit documentation and approved access for any live organization, repository, billing, or API change
tags: [saas, coderabbit, installation, authentication, platforms]
---
# CodeRabbit Installation and Authentication

## Overview

Route setup through the provider-specific flow and separate web-app installation from CLI auth. Never solicit or print credentials.

## Prerequisites

- Identify the CodeRabbit organization, Git provider, repository, plan, and accountable owner.
- Read `references/official-docs.md` and re-check any time-sensitive contract before execution.
- Use synthetic or read-only evidence until the approval boundary is satisfied.
- Preserve the repository's independent CI, security, and human-review requirements.

## Current Contract

- GitHub, GitLab, Azure DevOps, and Bitbucket use different authorization contracts.
- Organization access may require admin approval and explicit repo scope.
- Interactive and headless Agentic-key CLI auth are separate.
- Headless keys belong in a secret store, not repository config.

## Authentication

Treat Git-provider sessions, CodeRabbit web sessions, CLI credentials, and CodeRabbit API keys as separate credentials. Use only an already-approved session or secret-manager reference, never print a secret, and do not place credentials in `.coderabbit.yaml`, source files, logs, or deliverables.

## Instructions

1. Identify provider, hosting, owner, repositories, data class, plan, and surface.

2. Review permissions and choose the smallest installation scope.

3. Complete user-driven authorization or approved secret-store headless auth.

4. Verify one bounded review and record permissions and rotation owner.

## Tool Discipline

- Use **Glob** to locate candidate configuration and evidence files without widening scope.
- Use **Grep** to find relevant fields, commands, identifiers, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use these file tools as a substitute for authenticated CodeRabbit or provider operations.

## Approval Boundaries

Require organization-admin approval for installation and security approval for headless keys. Keep analysis and drafts local until approval is explicit, and record who approved the action and its scope.

## Output

An installation decision, scope, permission inventory, auth method, verification, and rotation owner. Include source dates, unknowns, and the exact boundary between observed fact and recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Current contract is unclear or docs disagree | Stop mutation, cite both sources, and request owner resolution. |
| Required access or approval is missing | Produce a draft and evidence plan only. |
| Validation or pilot behavior differs from expectation | Restore the prior state and retain the failed evidence. |
| Output contains secrets or private code | Stop, quarantine the artifact, redact it, and notify the data owner. |

## Examples

### Example 1

Install on one GitHub pilot repository.

### Example 2

Inject an Agentic API key from a runner secret manager.

## Validation

- Confirm every claim against the dated sources in `references/official-docs.md`.
- Verify the requested scope, owner, approval, happy path, failure path, and rollback.
- Re-read the effective configuration or provider state after any approved change.
- Report unsupported fields, undocumented endpoints, and unverified assumptions as failures.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
