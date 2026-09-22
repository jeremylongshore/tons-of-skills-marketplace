---
name: windsurf-data-handling
description: 'Govern data processed through Devin Desktop (formerly Windsurf).
  Use when mapping sensitive data, configuring context exclusions, reviewing vendor
  controls, or preparing regulated-workload evidence. Trigger with "windsurf data
  privacy", "windsurf PII", "GDPR", "data residency", or "AI data boundary".'
allowed-tools: Read, Write, Edit
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- privacy
- compliance
- data-handling
compatibility: Designed for Claude Code
---

# Devin Desktop Data Handling

## Overview

Build an evidence-backed data map for Devin Desktop. Do not infer retention, residency, training use, certification coverage, or zero-data-retention from plan names; verify mutable vendor claims against the current contract and security documentation.

## Prerequisites

- Data-classification policy and approved repository inventory
- Contract, DPA, or security evidence available to the authorized reviewer
- Named security, privacy, and legal decision owners

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Inventory data flows

For Cascade, autocomplete, indexing, remote indexing, MCP, Hooks, diagnostics, and App Deploys, record inputs, destination, purpose, identity, retention evidence, administrator, and applicable policy. Include metadata and logs, not only source files.

### Step 2: Minimize local context

Use `.gitignore` and repository `.codeiumignore` to exclude secrets, generated output, customer datasets, private keys, production exports, and irrelevant large files. Enterprise administrators may apply a global `.codeiumignore` under `~/.codeium/`.

Ignored paths are context controls. They do not revoke filesystem access, rotate secrets, satisfy least privilege, or prove a regulatory requirement.

### Step 3: Choose durable instructions

Put shared data-handling requirements in `AGENTS.md` or `.devin/rules/*.md`, for example:

```markdown
# Regulated data boundary
- Never paste customer records, access tokens, or production exports into prompts.
- Use synthetic fixtures in tests and examples.
- Require security review for changes under `src/payments/`.
- Stop and escalate if a requested artifact contains regulated data.
```

### Step 4: Review integrations

For every MCP server, Hook, deployment target, and analytics export, confirm an owner, authentication method, approved scopes, destination, log policy, revocation path, and incident contact. Disable integrations that lack an accountable owner.

### Step 5: Reconcile vendor evidence

Capture the URL or contract section, observation date, product/plan scope, and reviewer for each claim. Where public documentation and negotiated terms differ, label the applicable authority rather than blending them.

### Step 6: Test and approve

Use synthetic canaries to verify exclusions and policy behavior. Obtain the required security/privacy/legal approval before enabling regulated workloads, remote indexing, or external MCP access.

## Output

Produce a data-boundary record identifying data classes, indexed and excluded paths, integrations, organization controls, telemetry and logging decisions, retention or residency evidence, open questions, approvals, and validation results. Never reproduce sensitive values.

## Error Handling

| Issue | Response |
|---|---|
| Vendor claim lacks current evidence | Mark unverified and request contract/security review |
| Sensitive data entered Cascade | Stop, contain sharing, rotate affected secrets, and follow incident policy |
| Ignore test fails | Correct syntax or scope, refresh indexing through current controls, and retest |
| Integration owner is unknown | Disable or quarantine the integration until ownership is established |

## Examples

**Evidence row:** "Customer export; excluded by `.codeiumignore`; no MCP access; repository owner: Data Platform; retention claim pending DPA confirmation; synthetic canary passed during the recorded review run."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Ignore](https://docs.devin.ai/desktop/context-awareness/windsurf-ignore)
- [Windsurf security](https://windsurf.com/security)
- [Enterprise administration](https://docs.devin.ai/desktop/guide-for-admins)

## Related Skill

Continue with `windsurf-policy-guardrails` to turn approved data controls into enforceable repository, terminal, MCP, deployment, and organization policy.
