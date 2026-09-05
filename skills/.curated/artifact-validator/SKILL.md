---
name: artifact-validator
description: |
  Discover and validate Agent Skills, host plugins and subagents, MCP servers
  and configurations, hooks, and marketplace catalogs against the correct
  authority. Use when performing pre-merge review, external submission checks,
  portability audits, security checks, or validation of mixed agent-system
  repositories. Trigger with "validate this skill", "audit this plugin", "check
  this agent", "review this MCP config", or "is this marketplace ready".
allowed-tools: Read
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Agent Skills-compatible hosts; validation depth depends on available authoritative tooling
tags: [agent-skills, validation, plugins, agents, mcp, security]
---

# Artifact Validator

Audit agent-system artifacts without changing them. Select authority by artifact
type, run the strongest available deterministic checks, and separate observed
facts from unsupported claims.

## Overview

This skill is an orchestrator, not another schema authority. In the Tons of
Skills repository it delegates to the repository's canonical validators. In
other projects it applies the open specification floor and the target host's
current contract, clearly labeling checks that could not be reproduced.

## When to use

Use for a single file, plugin directory, marketplace, contributor change, or
mixed repository. Use `artifact-creator` when changes are requested. Use
`production-upgrade` when the audit must lead through research, implementation,
migration, and release readiness.

## Prerequisites

- A target path or repository.
- Read access to project instructions and generated-file ownership rules.
- Network access only when current primary-source verification is necessary.
  Never transmit private artifacts to an external validator without approval.

## Instructions

1. Read project instructions, inspect repository status, and determine whether
   the target is generated, mirrored, canonical, or host-specific.
2. Run the offline inventory helper:

   ```bash
   python3 scripts/inventory_artifacts.py <target>
   ```

3. Use [references/validation-routing.md](references/validation-routing.md) to
   select the owner for each discovered artifact. Do not merge verdicts from
   different standards into one unexplained score.
4. In the Tons of Skills repository:
   - use `scripts/validate-skills-schema.py` for skill and agent authority;
   - use `scripts/validate-mcp-config.mjs` and the declared security gates for
     MCP configuration;
   - run catalog synchronization before judging generated projections;
   - keep kernel-shadow results advisory unless governance explicitly changes.
5. Validate structure, references, declared versus used capabilities, secret
   hygiene, path containment, bounded execution, provenance, license, and the
   evidence supporting every portability or production claim.
6. For behavior, require positive, negative, edge, and adversarial cases. A
   passing structural score does not prove runtime behavior or safety.
7. Reproduce automated-review findings independently. Reject or qualify any
   claim that lacks a command, primary source, fixture, or observable boundary.
8. Return a severity-ordered report with exact paths, evidence, authority,
   remediation options, and a PASS, FAIL, or NOT-VERIFIED verdict per artifact.

## Output

Report the inventory, checks executed, exact command results, blocking findings,
warnings, unverified surfaces, and overall claim ceiling. Do not collapse a
partially tested multi-component plugin into a stronger verdict than its weakest
component.

## Error handling

- Missing authoritative tooling: perform the open-spec floor, mark deeper
  checks `NOT-VERIFIED`, and do not invent a pass.
- Unknown host artifact: identify it as host-specific and request or locate the
  current native specification before grading.
- Dirty or generated target: report ownership and drift; do not auto-fix during
  an audit.
- Secret-like content: redact the value, identify only the path and field, and
  stop any command that could transmit it.

## Examples

- A valid `SKILL.md` with no behavioral evidence can pass structure while
  remaining `NOT-VERIFIED` for production behavior.
- A Claude plugin with five skills and one unchecked MCP server is capped by the
  MCP component's verdict.
- A portable skill claiming Pi, Hermes, or Goose support without registry-backed
  receipts is reported as compatible or unverified, not verified-native.

## Resources

- [Validation routing](references/validation-routing.md)
- `scripts/inventory_artifacts.py` performs read-only deterministic discovery.
