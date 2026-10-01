---
name: plugin-validator
description: 'Validate automatically validates AI assistant code plugin structure,
  schemas, and compliance when user mentions validate plugin, check plugin, or plugin
  errors. runs comprehensive validation specific to AI assistant-code-plugins repository
  standards. Use when validating configurations or code. Trigger with phrases like
  ''validate'', ''check'', or ''verify''.

  '
allowed-tools: Read, Grep, Bash(cmd:*)
version: 2.20.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- compliance
- plugin-validator
compatibility: Designed for Claude Code
---
# Plugin Validator

## Overview

Validates Claude Code plugin structure, JSON schemas, frontmatter format, security compliance, and marketplace catalog consistency. Runs the same checks as the CI pipeline to catch issues before committing.

## Prerequisites

- Read access to the target plugin directory and repository-level `.claude-plugin/marketplace.extended.json`
- `jq` installed for JSON validation (`jq empty <file>`)
- `grep` and `find` available on PATH for pattern scanning
- `./scripts/validate-all-plugins.sh` available at the repository root

## Instructions

1. Identify the target plugin path from context or user request. Default to the current working directory if the path contains a `.claude-plugin/` subdirectory.
2. Validate required files exist (see `${CLAUDE_SKILL_DIR}/references/validation-checks.md`):
   - `.claude-plugin/plugin.json` present and valid JSON.
   - `README.md` present and non-empty.
   - `LICENSE` file present.
   - At least one component directory exists (`commands/`, `agents/`, `skills/`, `hooks/`, or `mcp/`).
3. Validate `plugin.json` schema:
   - Confirm all required fields: `name` (kebab-case), `version` (semver `x.y.z`), `description`, `author.name`, `author.email`, `license`, `keywords` (array, minimum 2).
   - Reject any fields not in the allowed set (`name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords`).
4. Validate frontmatter in all component files:
   - **Commands** (`commands/*.md`): require `name`, `description`, `model` (one of `sonnet`, `opus`, `haiku`).
   - **Agents** (`agents/*.md`): require `name`, `description`, `model`.
   - **Skills** (`skills/*/SKILL.md`): require `name`, `description`; `allowed-tools` optional but validated against the allowed tools list if present.
5. Validate directory structure matches the expected hierarchy (see `${CLAUDE_SKILL_DIR}/references/validation-checks.md` for the complete structure diagram).
6. Check script permissions: find all `.sh` files and verify they have execute permission. Report any that lack it with a fix command.
7. Run security scans: search for hardcoded secrets, AWS keys, private keys, dangerous commands, and suspicious URLs.
8. Validate marketplace compliance:
   - Confirm the plugin has an entry in `marketplace.extended.json`.
   - Verify version, name, category, and source path match between `plugin.json` and the catalog entry.
   - Check for duplicate plugin names.
9. Validate README content: confirm it contains installation, usage, and description sections.
10. Check hook path variables: verify hooks use `${CLAUDE_PLUGIN_ROOT}` instead of hardcoded absolute paths (`/home/`, `/Users/`).
11. Compile results into a validation report following the format in `${CLAUDE_SKILL_DIR}/references/validation-report-format.md`.

## Output

A structured validation report containing:

- Total checks passed and failed (e.g., "8/10 PASSED")
- Per-check results with pass/fail status
- For each failure: the specific issue, file location, and a ready-to-run fix command
- Warnings for non-critical issues (e.g., missing optional README sections)
- Overall verdict: PASSED or FAILED with critical issue count

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Plugin directory not found | Incorrect path provided | Verify path matches `plugins/[category]/[name]/` and the directory exists |
| `jq` parse error on JSON | Malformed JSON in `plugin.json` or catalog | Run `jq empty <file>` to locate the syntax error line |
| Frontmatter parse failure | Missing `---` delimiters or invalid YAML | Ensure YAML frontmatter is enclosed in `---` lines with valid key-value pairs |
| Version mismatch | `plugin.json` and `marketplace.extended.json` carry different versions | Update the stale version to match; run `pnpm run sync-marketplace` |
| Scripts not executable | `.sh` files missing execute permission | Run `chmod +x <script>` for each flagged file |
| Disallowed fields in plugin.json | Extra fields beyond the allowed set | Remove disallowed fields; only `name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords` are permitted |

## Examples

**Validate a specific plugin:**
Trigger: "Validate the skills-powerkit plugin."
Process: Run all 10 validation checks against `plugins/community/skills-powerkit/`. Identify 2 failures (script permissions, version mismatch). Provide fix commands: `chmod +x scripts/*.sh` and version update instruction. Report overall: FAILED (see `${CLAUDE_SKILL_DIR}/references/examples.md`).

**Pre-commit readiness check:**
Trigger: "Check if my plugin is ready to commit."
Process: Detect the plugin from working directory context. Run comprehensive validation including marketplace compliance. Report PASSED or list blocking issues with fixes.

**Debug CI failures:**
Trigger: "Why is my plugin failing CI?"
Process: Run the same validation checks that CI executes (`validate-all-plugins.sh`). Identify the exact failure (e.g., disallowed field in `plugin.json`). Provide the fix command and verify the fix resolves the issue.

## Resources

- `${CLAUDE_SKILL_DIR}/references/validation-checks.md` -- complete list of all 10 validation categories with specific checks
- `${CLAUDE_SKILL_DIR}/references/validation-report-format.md` -- report template with pass/fail formatting
- `${CLAUDE_SKILL_DIR}/references/examples.md` -- validation scenario walkthroughs
- `${CLAUDE_SKILL_DIR}/references/errors.md` -- error handling patterns
