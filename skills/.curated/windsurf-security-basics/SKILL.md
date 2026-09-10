---
name: windsurf-security-basics
description: 'Secure Devin Desktop (formerly Windsurf) with context boundaries,
  repository controls, Rules, Hooks, and MCP review. Use when protecting secrets,
  hardening a workspace, or assessing AI-editor risk. Trigger with "windsurf
  security", "windsurf secrets", "codeiumignore", or "Cascade guardrails".'
allowed-tools: Read, Write, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- security
- privacy
- compliance
compatibility: Designed for Claude Code
---

# Devin Desktop Security Basics

## Overview

Devin Desktop is the current name for Windsurf. Secure it with layered controls: repository permissions and secret management are authoritative; `.codeiumignore`, Rules, and prompts reduce context exposure but do not replace access control.

## Prerequisites

- A version-controlled workspace and clean working tree
- The organization's data-classification and secret-handling policy
- Authorization to inspect configuration without collecting secret values

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.

## Instructions

### Step 1: Map trust boundaries

Record repository sensitivity, connected organizations, enabled models, MCP servers, Hooks, terminal permissions, remote indexing, and deployment integrations. Identify which controls are local, repository-owned, or centrally administered.

### Step 2: Configure context exclusions

Create `.codeiumignore` at the repository root using gitignore syntax. Include only project-relevant patterns, for example:

```gitignore
.env
.env.*
*.pem
*.key
credentials/
secrets/
customer-data/
dist/
node_modules/
```

Windsurf also honors `.gitignore`, and Enterprise administrators can add a global `.codeiumignore` under `~/.codeium/`. Verify behavior with a harmless canary filename; do not place a real secret in the test.

### Step 3: Enforce durable behavior

Use repository `AGENTS.md` or `.devin/rules/*.md` to require secure coding, validation, least privilege, and explicit approval for risky operations. Keep each workspace Rule within the documented 12,000-character limit and use the correct `trigger:` mode.

### Step 4: Review tools and automation

1. Disable unused MCP servers and tools.
2. Prefer provider OAuth or environment-backed secrets over literal values in `mcp_config.json`.
3. Review Hooks as executable policy code and fail closed where required.
4. Keep protected branches, code owners, CI, and deployment approvals outside the model's discretion.
5. Require human approval for production, destructive, identity, and billing mutations.

### Step 5: Respond to exposure

If a secret appears in a prompt, output, log, diff, or diagnostic bundle, treat it as exposed: stop sharing, revoke or rotate it through the provider, remove it from history where authorized, and document the incident. Adding an ignore rule alone is not remediation.

### Step 6: Verify

Confirm ignored paths are absent from context, protected branches still require review, MCP tools match policy, Hooks run on representative success and failure paths, and no configuration file contains credential material.

## Output

Deliver a security review with context boundaries, ignored paths, organization policy, MCP and Hook exposure, repository protections, detected secret locations without values, remediation owners, and verification evidence. Mark controls as preventive, detective, or corrective.

## Error Handling

| Issue | Response |
|---|---|
| Ignored file still appears | Check syntax, location, gitignore interaction, and current indexing state |
| MCP requires a token | Use provider OAuth or an approved secret store; never commit the value |
| Hook blocks legitimate work | Preserve the event, fix the narrow rule, and retest failure handling |
| Compliance claim is uncertain | Link first-party evidence and route the decision to security or legal |

## Examples

**Finding:** "`.env.production` was not excluded. Add `.env.*`, rotate any exposed credential, verify with a harmless canary, and retain protected-branch review as the enforcement boundary."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Ignore](https://docs.devin.ai/desktop/context-awareness/windsurf-ignore)
- [Rules and `AGENTS.md`](https://docs.devin.ai/desktop/cascade/memories)
- [Hooks](https://docs.devin.ai/desktop/cascade/hooks)
- [MCP](https://docs.devin.ai/desktop/cascade/mcp)

## Related Skill

Continue with `windsurf-data-handling` to build a regulated-data inventory, verify mutable vendor claims, and record control evidence without exposing sensitive values.
