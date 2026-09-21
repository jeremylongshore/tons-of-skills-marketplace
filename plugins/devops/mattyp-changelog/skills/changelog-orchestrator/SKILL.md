---
name: changelog-orchestrator
description: Draft changelog PRs by collecting GitHub/Slack/Git changes, formatting
  with templates, running quality gates, and preparing a branch/PR. Use when generating
  weekly/monthly release notes or when the user asks to create a changelog from recent
  merges. Trigger with "changelog weekly", "generate release notes", "draft changelog",
  "create changelog PR".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git:*), Bash(gh:*), Bash(python:*),
  Bash(date:*)
version: 0.4.0
author: Mattyp
license: MIT
tags:
- automation
- changelog-orchestrator
compatibility: Designed for Claude Code
---
# Changelog Orchestrator

## Overview

This skill turns raw repo activity (merged PRs, issues, commits, optional Slack updates) into a publishable changelog draft and prepares a branch/PR for review.

## Prerequisites

- A project config file at `.changelog-config.json` in the target repo.
- Required environment variables set (at minimum `GITHUB_TOKEN` for GitHub source).
- Git available in PATH; `gh` optional (used for PR creation if configured).

## Instructions

1. Read `.changelog-config.json` from the repo root.
2. Validate it with `${CLAUDE_SKILL_DIR}/scripts/validate_config.py`.
3. Decide date range:
4. Load the configured markdown template (or fall back to `${CLAUDE_SKILL_DIR}/assets/weekly-template.md`).
5. Render the final markdown using `${CLAUDE_SKILL_DIR}/scripts/render_template.py`.
6. Ensure frontmatter contains at least `date` (ISO) and `version` (SemVer if known; otherwise `0.0.0`).
7. Run deterministic checks using `${CLAUDE_SKILL_DIR}/scripts/quality_score.py`.
8. If score is below threshold:
9. Write the changelog file to the configured `output_path`.
10. Create a branch `changelog-YYYY-MM-DD`, commit with `docs: add changelog for YYYY-MM-DD`.
11. If `gh` is configured, open a PR; otherwise, print the exact commands the user should run.

See `${CLAUDE_SKILL_DIR}/references/implementation.md` for detailed implementation guide.

## Output

- A markdown changelog draft (usually `CHANGELOG.md`), plus an optional PR URL.
- A quality report (score + findings) from `${CLAUDE_SKILL_DIR}/scripts/quality_score.py`.

## Error Handling

See `${CLAUDE_SKILL_DIR}/references/errors.md` for comprehensive error handling.

## Examples

See `${CLAUDE_SKILL_DIR}/references/examples.md` for detailed examples.

## Resources

- Validate config: `${CLAUDE_SKILL_DIR}/scripts/validate_config.py`
- Render template: `${CLAUDE_SKILL_DIR}/scripts/render_template.py`
- Quality scoring: `${CLAUDE_SKILL_DIR}/scripts/quality_score.py`
- Default templates:
  - `${CLAUDE_SKILL_DIR}/assets/default-changelog.md`
  - `${CLAUDE_SKILL_DIR}/assets/weekly-template.md`
  - `${CLAUDE_SKILL_DIR}/assets/release-template.md`
