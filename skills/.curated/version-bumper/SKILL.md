---
name: version-bumper
description: 'Execute automatically handles semantic version updates across plugin.json
  and marketplace catalog when user mentions version bump, update version, or release.
  ensures version consistency in AI assistant-code-plugins repository. Use when appropriate
  context detected. Trigger with relevant phrases based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Bash(cmd:*)
version: 2.20.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- version-bumper
compatibility: Designed for Claude Code
---
# Version Bumper

## Overview

Automates semantic version bumps across all version-bearing files in a Claude Code plugin. Ensures consistency between `plugin.json`, `marketplace.extended.json`, and the generated `marketplace.json` catalog.

## Prerequisites

- `jq` installed and available on PATH for JSON manipulation
- Read/write access to `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.extended.json`
- `pnpm run sync-marketplace` available at the repository root
- Git installed for optional tag creation

## Instructions

1. Identify the target plugin directory and read the current version from `.claude-plugin/plugin.json` using `jq -r '.version'`.
2. Determine the bump type (major, minor, or patch) from the user request. If unspecified, infer from the nature of changes: breaking changes warrant major, new features warrant minor, and fixes warrant patch.
3. Parse the current version into its `major.minor.patch` components and compute the new version according to semver rules (see `${CLAUDE_SKILL_DIR}/references/version-bump-process.md`).
4. Update the `"version"` field in `.claude-plugin/plugin.json` with the new version string.
5. Locate the plugin entry in `.claude-plugin/marketplace.extended.json` and update its `"version"` field to match (see `${CLAUDE_SKILL_DIR}/references/update-locations.md`).
6. Run `pnpm run sync-marketplace` at the repository root to regenerate `marketplace.json`.
7. Verify version consistency across all three files by reading each and confirming the version strings match.
8. Optionally create a git tag (`git tag -a "v<new_version>" -m "Release v<new_version>"`) and prepare a commit message following the `chore: Release v<version>` convention (see `${CLAUDE_SKILL_DIR}/references/release-workflow.md`).

## Output

A version bump execution summary containing:

- The computed transition (`old_version` to `new_version`)
- The exact files updated: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.extended.json`, and regenerated `.claude-plugin/marketplace.json`
- Validation confirmation that all files carry the same version
- Suggested next commands (`git add`, `git commit`, `git tag`, validation scripts)

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| `jq: command not found` | `jq` not installed | Install via `apt install jq` or `brew install jq` |
| Version format invalid | Non-semver string in plugin.json | Correct to `x.y.z` format before bumping |
| Plugin not found in marketplace | Missing catalog entry | Add the plugin to `marketplace.extended.json` first |
| Sync marketplace failure | Schema mismatch or missing fields | Run `jq empty` on both JSON files to locate syntax errors |
| Version mismatch after sync | `sync-marketplace` did not pick up changes | Verify the plugin name in `marketplace.extended.json` matches `plugin.json` exactly |

## Examples

**Patch bump for a specific plugin:**
Trigger: "Bump the security-scanner plugin to patch version"
Process: Read current version 1.2.3, compute 1.2.4, update `plugin.json` and `marketplace.extended.json`, run sync, verify consistency, report success.

**Explicit major release:**
Trigger: "Release version 2.0.0 of plugin-name"
Process: Set version to 2.0.0 in all files, sync marketplace, create git tag `v2.0.0`, prepare commit with `chore: Release v2.0.0`.

**Feature-based minor bump:**
Trigger: "Increment version for new feature"
Process: Detect minor bump, compute 1.2.3 to 1.3.0, update all version locations, sync, validate, report completion.

## Resources

- `${CLAUDE_SKILL_DIR}/references/version-bump-process.md` -- step-by-step bump algorithm
- `${CLAUDE_SKILL_DIR}/references/update-locations.md` -- all files requiring version updates
- `${CLAUDE_SKILL_DIR}/references/release-workflow.md` -- full release process including git tags
- `${CLAUDE_SKILL_DIR}/references/examples.md` -- additional usage scenarios
- [Semantic Versioning specification](https://semver.org/)
