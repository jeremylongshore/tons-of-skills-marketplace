---
name: artifact-creator
description: |
  Create or revise Agent Skills, host plugins and subagents, MCP servers and
  client configurations, hooks, and marketplace catalogs against their actual
  specifications. Use when building reusable agent capabilities or consolidating
  creator tooling without inventing a universal host format. Trigger with
  "create an agent skill", "build a plugin", "create an MCP server", "add a
  subagent", or "scaffold an agent integration".
allowed-tools: Read,Write,Edit
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Agent Skills-compatible hosts; host-specific artifacts require their native specification
tags: [agent-skills, creation, plugins, agents, mcp, hooks]
---

# Artifact Creator

Create the smallest complete artifact that satisfies the user's requested
runtime and security boundary. Keep portable instructions separate from host
packaging.

## Overview

There is one portable Agent Skills contract, one open MCP protocol, and many
different plugin, agent, hook, permission, and marketplace formats. This skill
selects the correct authority before writing files and prevents host-specific
details from leaking into the portable core.

## When to use

Use for a new or substantially revised skill, subagent, plugin, MCP integration,
hook, or marketplace entry. For a production modernization involving research,
migration, security review, and release evidence, use `production-upgrade`
instead. For review without changes, use `artifact-validator`.

## Prerequisites

- The requested outcome and target repository or destination.
- Existing project instructions and the target host's current specification.
- Authorization for any local writes. Creation does not imply permission to
  install, publish, deploy, open a PR, or merge.

The pre-authorized `Read`, `Write`, and `Edit` capabilities apply only to local
files inside the user-selected target. Every network, shell, installation, and
external mutation capability remains behind host and project approval.

## Instructions

1. Read project instructions and inspect the target tree before choosing a
   format. Preserve generated-file ownership and existing public identifiers.
2. Classify the artifact using
   [references/artifact-contracts.md](references/artifact-contracts.md). If the
   request mixes a portable skill with host wiring, design the portable skill
   first and the host adapter second.
3. Establish the current authority:
   - Agent Skill: the open Agent Skills specification plus any declared local
     overlay.
   - MCP server: the Model Context Protocol specification and selected SDK.
   - Plugin, subagent, hook, command, or catalog: the target host's current
     specification.
   - This marketplace: repository instructions and its canonical validators.
4. Derive least privilege from the actual workflow. Do not copy a broad tool
   list from another artifact. Separate read-only analysis from mutations.
5. Create only useful files. A skill requires `SKILL.md`; add scripts when
   deterministic execution matters, references for conditional depth, assets
   for output material, and evals for behavior that needs proof.
6. For MCP work, define tools around bounded user outcomes. Validate every
   input, cap output and retries, redact secrets, separate reads from writes,
   and require explicit confirmation for high-impact mutations.
7. For host adapters, follow
   [references/host-adapters.md](references/host-adapters.md). Do not claim
   another runtime is supported merely because it can read Markdown.
8. Validate with `artifact-validator`, run focused tests, and report unresolved
   assumptions and operations that still require approval.

## Output

Return the created paths, the authority used for each artifact, validation
commands and results, support limitations, and the next authorization boundary.

## Error handling

- If the target host is unknown, create only the portable Agent Skill and leave
  host packaging unclaimed.
- If current official documentation conflicts with repository policy, stop and
  surface the conflict at the owning authority.
- If a secret, destructive default, unbounded retry, path escape, or unsupported
  runtime claim appears, fail closed and do not scaffold around it.
- If the destination already exists, preserve it and propose an update or
  migration; never overwrite without explicit authorization.

## Examples

- "Create a skill that audits release readiness" produces one portable skill
  and only the resources required by its checks.
- "Build a Goose skill" produces a portable Agent Skill and verifies Goose's
  native path before offering installation instructions.
- "Create an MCP server and Claude plugin" designs the server against MCP and
  treats the Claude plugin configuration as a separate adapter.

## Resources

- [Artifact contracts](references/artifact-contracts.md)
- [Host adapter rules](references/host-adapters.md)
