---
name: plugin-auditor
description: 'Audit automatically audits AI assistant code plugins for security vulnerabilities,
  best practices, AI assistant.md compliance, and quality standards when user mentions
  audit plugin, security review, or best practices check. specific to AI assistant-code-plugins
  repositor... Use when assessing security or running audits. Trigger with phrases
  like ''security scan'', ''audit'', or ''vulnerability''.

  '
allowed-tools: Read, Grep, Bash(cmd:*)
version: 2.20.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- security
- compliance
- audit
compatibility: Designed for Claude Code
---
# Plugin Auditor

## Overview

Audits Claude Code plugins for security vulnerabilities, best practices compliance, CLAUDE.md standards adherence, and marketplace readiness. Produces a scored audit report covering eight categories: security, best practices, CLAUDE.md compliance, marketplace compliance, git hygiene, MCP-specific checks, performance, and UX.

## Prerequisites

- Read access to the target plugin directory and repository-level `.claude-plugin/marketplace.extended.json`
- `jq` installed for JSON schema validation
- `grep` and `find` available on PATH for pattern scanning
- Familiarity with the plugin structure defined in CLAUDE.md (`.claude-plugin/plugin.json`, `README.md`, `LICENSE`, component directories)

## Instructions

1. Identify the target plugin path (e.g., `plugins/security/plugin-name/`). Confirm the directory exists and contains `.claude-plugin/plugin.json`.
2. Run a security scan across all plugin files (see `${CLAUDE_SKILL_DIR}/references/audit-categories.md` for full pattern list):
   - Search for hardcoded secrets, API keys, AWS access keys (`AKIA...`), and private key headers.
   - Detect dangerous commands (`rm -rf /`, `eval()`, `exec()`) and command injection vectors.
   - Flag suspicious URLs (non-HTTPS, raw IP addresses) and obfuscated code (base64 decode, hex encoding).
3. Validate plugin structure and best practices (see `${CLAUDE_SKILL_DIR}/references/audit-process.md`):
   - Confirm required files exist: `plugin.json`, `README.md`, `LICENSE`.
   - Verify semantic versioning format in `plugin.json`.
   - Check that all `.sh` scripts have execute permissions.
   - Scan for `TODO`/`TODO` comments without linked issues and `console.log()` in production code.
4. Check CLAUDE.md compliance:
   - Verify the plugin follows the directory structure specified in the repository CLAUDE.md.
   - Confirm `plugin.json` contains only allowed fields (`name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords`).
   - Validate that hooks use `${CLAUDE_PLUGIN_ROOT}` instead of hardcoded paths.
5. Verify marketplace compliance:
   - Confirm the plugin has an entry in `marketplace.extended.json` with matching name, version, category, and source path.
   - Check for duplicate plugin names in the catalog.
6. Assess git hygiene: no committed `node_modules/`, `.env` files, large binaries, or merge conflict markers.
7. For MCP plugins: validate `package.json` dependencies, TypeScript configuration, `dist/` in `.gitignore`, and build scripts.
8. Generate a scored audit report following the format in `${CLAUDE_SKILL_DIR}/references/audit-report-format.md`, with per-category scores out of 10 and an overall quality rating.

## Output

A structured audit report containing:

- Plugin identification (name, version, category, audit date)
- Per-category results: passed checks, failed checks with fix commands, warnings with recommendations
- Numeric quality scores: Security (x/10), Best Practices (x/10), Compliance (x/10), Documentation (x/10)
- Overall score and rating (Excellent / Good / Needs Work / Failed)
- Prioritized recommendations list with estimated fix time

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Plugin directory not found | Incorrect path or plugin does not exist | Verify the path matches `plugins/[category]/[name]/` structure |
| `plugin.json` missing or invalid | File absent or malformed JSON | Create from template or fix JSON syntax with `jq empty .claude-plugin/plugin.json` |
| Marketplace entry missing | Plugin not yet added to catalog | Add entry to `marketplace.extended.json` and run `pnpm run sync-marketplace` |
| Version mismatch detected | `plugin.json` and `marketplace.extended.json` carry different versions | Update the stale file to match the authoritative version |
| Permission denied during scan | Restricted file access | Request read permissions on the plugin directory tree |

## Examples

**Full audit before publishing:**
Trigger: "Audit the security-scanner plugin."
Process: Run all eight audit categories against `plugins/security/security-scanner/`. Generate a comprehensive report with per-category scores. Report overall rating and prioritized fix list (see `${CLAUDE_SKILL_DIR}/references/examples.md`).

**Publish readiness check:**
Trigger: "Is this plugin safe to publish?"
Process: Prioritize security audit (critical), then marketplace compliance and quality scoring. Produce a publish readiness assessment with pass/fail verdict.

**Featured status review:**
Trigger: "Quality review before featured status."
Process: Run full audit with elevated quality thresholds. Apply featured plugin requirements (higher documentation and test coverage standards). Recommend approve or reject.

## Resources

- `${CLAUDE_SKILL_DIR}/references/audit-categories.md` -- all eight audit categories with specific checks
- `${CLAUDE_SKILL_DIR}/references/audit-process.md` -- step-by-step audit execution procedures
- `${CLAUDE_SKILL_DIR}/references/audit-report-format.md` -- report template with scoring rubric
- `${CLAUDE_SKILL_DIR}/references/examples.md` -- audit scenario walkthroughs
- `${CLAUDE_SKILL_DIR}/references/errors.md` -- error handling patterns
