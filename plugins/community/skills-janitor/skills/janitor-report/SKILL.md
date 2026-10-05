---
name: janitor-report
description: "Full health check of all your skills in one report. Use when the user wants to check for errors, find duplicates, detect broken skills, or get a complete overview of skill health. Pass --brief for inventory only. Trigger with '/janitor-report'."
allowed-tools: Read, Bash(bash:*)
argument-hint: "[--brief]"
version: 1.7.0
author: Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>
license: MIT
compatibility: Designed for Claude Code. Requires bash 3.2+ (macOS default works). Reads local Claude Code data only (~/.claude/skills, ~/.claude/agents, installed plugin metadata).
tags:
  - skills
  - health-check
  - duplicates
  - maintenance
  - inventory
---

# Health Report

Generate a comprehensive health report combining inventory, quality checks, duplicate detection, and broken skill findings.

## Overview

One report covering every place a skill lives: user, project, codex, plugin, and source scopes. Plugin skills appear with their full invocation name (e.g. `marketing-skills:image`, `figma:figma-use`) — these were invisible to the v1.2 report. The scan JSON also includes an `agents` array (subagents from `~/.claude/agents` — their descriptions are always-loaded too) and per-plugin `update_available` (installed commit vs marketplace HEAD) — surface stale plugins and heavy agents in the report.

Modes:

- **`/janitor-report`** (default) — full health check: inventory + lint + duplicates + broken
- **`/janitor-report --brief`** — inventory only (replaces the old `/janitor-audit`)

## Prerequisites

- Claude Code with the skills-janitor plugin installed (provides `scripts/scan.sh`, `lint.sh`, `detect_dupes.sh`)
- bash 3.2+ (the stock macOS bash works; no external dependencies)
- Read access to `~/.claude/skills`, `~/.claude/agents`, and installed plugin metadata
- No authentication or API keys required — the scripts read local files only

## Instructions

### Step 1: Run the scripts

Full report:

```bash
bash ~/.claude/skills/skills-janitor/scripts/scan.sh
bash ~/.claude/skills/skills-janitor/scripts/lint.sh
bash ~/.claude/skills/skills-janitor/scripts/detect_dupes.sh
```

Brief mode (inventory only):

```bash
bash ~/.claude/skills/skills-janitor/scripts/scan.sh
```

### Step 2: What each script covers

- **Inventory (scan.sh)** — all skills across scopes, symlink status, frontmatter fields, line counts; `agents` and `plugins` (with `update_available`) arrays; `broken_symlinks` count.
- **Quality checks (lint.sh)** — Critical: broken symlinks, missing SKILL.md, missing frontmatter. Warning: missing/empty name or description, description too short/long, missing version. Info: no body content, no Gotchas section, large files.
- **Duplicate detection (detect_dupes.sh)** — name collisions (two distinct skills with the same qualified name at different paths) and description overlap (Jaccard similarity >30%), with cross-scope user-vs-plugin pairs explicitly surfaced (e.g. `marketing-seo-audit` (user) ↔ `marketing-skills:seo-audit` (plugin)).

### Step 3: Present a unified report

Merge the three outputs into one table with severity levels, then recommend actions.

## Output

```
| Skill                            | Scope    | Status      | Issues                                   |
|----------------------------------|----------|-------------|------------------------------------------|
| marketing-copywriting            | user     | DUPLICATE?  | 90% overlap with marketing-skills:copywriting |
| seo-audit                        | user     | WARNING     | Description too short                    |
| old-deploy-helper                | user     | CRITICAL    | Broken symlink                           |
| figma:figma-use                  | plugin   | OK          | -                                        |
```

Recommended actions per issue type:

- Broken symlinks → `/janitor-fix --prune`
- Quality issues → `/janitor-fix`
- User-vs-plugin duplicates → uninstall the user-scope copy and rely on the plugin (or vice versa)
- Stale plugins (`update_available: true`) → `/plugin update <name>`
- Token waste → `/janitor-value`
- Suspicious content (injection phrases, dangerous scripts) → `/janitor-security`
- Unused MCP servers (run `scripts/mcp.sh` for the inventory) → remove the config entry or `/janitor-swipe`

## Error Handling

1. **Error**: `scan.sh: No such file or directory`
   **Solution**: The plugin is installed under a different root. Locate it with `ls ~/.claude/skills` or check the plugin cache, then run the scripts from their actual location.

2. **Error**: Scan output is not valid JSON
   **Solution**: Re-run with stderr visible (drop any `2>/dev/null`) and report the failing line; a skill directory with unusual characters is the usual cause.

3. **Error**: `plugins` array is empty despite installed plugins
   **Solution**: `~/.claude/plugins/installed_plugins.json` is missing or in an unknown format — report which Claude Code version is in use.

## Examples

### Example 1: Full health check

**Input**: "Check my skills for problems."

**Output**: Run all three scripts, merge into the severity table, and lead with counts: "175 skills scanned: 2 critical (broken symlinks), 5 warnings, 3 likely duplicates, 2 plugins have updates available."

### Example 2: Inventory only

**Input**: "/janitor-report --brief"

**Output**: Run `scan.sh` only and present the inventory grouped by scope with per-scope counts.

## Resources

- Scripts (plugin-relative): `{baseDir}/../../scripts/scan.sh`, `lint.sh`, `detect_dupes.sh`
- `/janitor-fix` — auto-fix the issues this report finds
- `/janitor-value` — token cost + usage (combined)
- `/janitor-discover` — find or evaluate new skills
