---
name: windsurf-migration-deep-dive
description: 'Migrate to Devin Desktop (formerly Windsurf) from VS Code, Cursor, or other AI IDEs with full
  configuration transfer.

  Use when migrating a team to Windsurf, transferring Cursor rules,

  or evaluating Windsurf against other AI editors.

  Trigger with phrases like "migrate to windsurf", "switch to windsurf",

  "windsurf from cursor", "windsurf from copilot", "windsurf evaluation".

  '
argument-hint: "[source editor and migration scope]"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*)
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- migration
- cursor
- vscode
compatibility: Designed for Claude Code
---
# Windsurf Migration Deep Dive

## Current State

Collect source and target editor versions during the inventory step; do not execute shell substitutions while loading this skill.

## Overview

Comprehensive guide for migrating teams to Windsurf from VS Code + Copilot, Cursor, or other AI editors. Covers settings transfer, concept mapping, team rollout planning, and rollback strategy.

## Prerequisites

- Current editor still installed (for config export)
- Target repositories identified
- Team buy-in for evaluation period

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Feature Comparison Matrix

| Feature | VS Code + Copilot | Cursor | Windsurf |
|---------|------------------|--------|----------|
| Inline completions | Copilot | Tab | Supercomplete |
| Agentic AI chat | N/A | Composer | Cascade Write |
| AI Q&A | Copilot Chat | Chat | Cascade Chat |
| Inline edit | Copilot Edit | Cmd+K | Cmd+I (Command) |
| Project rules | N/A | .cursorrules | .devin/rules/project.md |
| AI ignore file | N/A | .cursorignore | .codeiumignore |
| Workspace rules | N/A | .cursor/rules/ | .devin/rules/ |
| Reusable workflows | N/A | N/A | .windsurf/workflows/ |
| Persistent memories | N/A | Notepad | Memories |
| MCP support | Via extension | Built-in | Built-in |
| In-IDE preview | N/A | N/A | Previews |
| Terminal AI | N/A | Limited | Full (Turbo mode) |
| Deploy from IDE | N/A | N/A | Netlify native |
| Pricing | Verify current vendor plan | Verify current vendor plan | Verify current Devin plan |

### Step 2: Migrate from Cursor

```bash
#!/bin/bash
set -euo pipefail
echo "=== Migrating Cursor → Windsurf ==="

# 1. Convert rules files
if [ -f .cursorrules ]; then
  mkdir -p .devin/rules
  cp .cursorrules .devin/rules/project.md
  echo "Converted .cursorrules → .devin/rules/project.md"
fi

# 2. Convert ignore file
if [ -f .cursorignore ]; then
  cp .cursorignore .codeiumignore
  echo "Converted .cursorignore → .codeiumignore"
fi

# 3. Convert workspace rules
if [ -d .cursor/rules ]; then
  mkdir -p .devin/rules
  for rule in .cursor/rules/*.md; do
    [ -f "$rule" ] || continue
    BASENAME=$(basename "$rule")
    cp "$rule" ".devin/rules/$BASENAME"
    echo "Copied rule: $BASENAME"
  done
  echo ""
  echo "NOTE: Review .devin/rules/ files."
  echo "Windsurf uses frontmatter with 'trigger:' field:"
  echo "  trigger: always_on | glob | model_decision | manual"
  echo "  globs: **/*.test.ts (for glob trigger)"
fi

# 4. Migrate extensions
if command -v cursor &>/dev/null; then
  cursor --list-extensions > /tmp/cursor-extensions.txt
  echo ""
  echo "Extensions to install in Windsurf:"
  grep -v "cursor\|anysphere" /tmp/cursor-extensions.txt | while read ext; do
    echo "  windsurf --install-extension $ext"
  done
fi

echo ""
echo "Migration complete. Remove Cursor-specific references from .devin/rules/project.md"
```

### Step 3: Migrate from VS Code + Copilot

```bash
#!/bin/bash
set -euo pipefail
echo "=== Migrating VS Code + Copilot → Windsurf ==="

# 1. Export and install extensions
code --list-extensions > /tmp/vscode-extensions.txt
echo "Installing $(wc -l < /tmp/vscode-extensions.txt) extensions..."
grep -v "github.copilot" /tmp/vscode-extensions.txt | while read ext; do
  windsurf --install-extension "$ext" 2>/dev/null || echo "  SKIP: $ext"
done

# 2. Copy settings
SRC="$HOME/.config/Code/User/settings.json"
DST="$HOME/.config/Windsurf/User/settings.json"
[ -f "$SRC" ] && cp "$SRC" "$DST" && echo "Settings copied"

# 3. Copy keybindings
SRC_KB="$HOME/.config/Code/User/keybindings.json"
DST_KB="$HOME/.config/Windsurf/User/keybindings.json"
[ -f "$SRC_KB" ] && cp "$SRC_KB" "$DST_KB" && echo "Keybindings copied"

# 4. Create new Windsurf-specific config (no equivalent in VS Code)
echo ""
echo "NEW: Create these files for Windsurf AI features:"
echo "  .devin/rules/project.md   — project context for Cascade AI"
echo "  .codeiumignore   — exclude files from AI indexing"
echo "  .devin/rules/ — triggered workspace rules"
```

### Step 4: Team Rollout Plan

```yaml
# Phased rollout strategy
migration_plan:
  week_1_pilot:
    participants: "2-3 senior developers"
    goals:
      - "Install Windsurf, import VS Code settings"
      - "Create .devin/rules/project.md for 1-2 main repos"
      - "Use Cascade for real tasks, document experience"
    success_criteria: "Pilot devs productive in Windsurf"

  week_2_expand:
    participants: "Full team (keep old editor available)"
    goals:
      - "All team members install Windsurf"
      - "Run setup-windsurf.sh for each repo"
      - "Training session: Cascade, Supercomplete, Workflows"
    success_criteria: ">70% team using Windsurf daily"

  week_3_optimize:
    participants: "Full team"
    goals:
      - "Refine .devin/rules/project.md based on team feedback"
      - "Create team workflows for common tasks"
      - "Configure Turbo mode allow/deny lists"
    success_criteria: "Acceptance rate >25%, team satisfied"

  week_4_commit:
    participants: "Full team"
    goals:
      - "Remove old editor from default toolchain"
      - "Decommission Copilot/Cursor licenses"
      - "Document final configuration"
    success_criteria: "100% team on Windsurf, licenses cancelled"
```

### Step 5: Rollback Plan

```yaml
rollback:
  trigger: "Team productivity drops or critical issues discovered"
  steps:
    1. "Keep old editor installed during evaluation (don't uninstall)"
    2. "Git config files (.devin/rules/project.md, .codeiumignore) don't affect other editors"
    3. "VS Code settings already backed up during migration"
    4. "Cancel Windsurf subscription within trial period"
  note: "Windsurf config files are safe to leave in repo — they're ignored by other editors"
```

## Output

Deliver a migration inventory, feature mapping, converted configuration, unsupported-item list, validation evidence, user communication, and rollback path. Preserve the source editor configuration until the target cohort signs off on the migrated workflow.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Extension doesn't work in Windsurf | VS Code API incompatibility | Check Windsurf marketplace for alternative |
| Settings cause errors | Windsurf-specific settings format | Remove Cursor/Copilot-specific settings |
| Team resistance | Unfamiliar with Cascade | Demo session with real project tasks |
| .cursorrules not working | Wrong filename | Must be `.devin/rules/project.md` in Windsurf |
| Missing features | Specific Cursor/Copilot feature | Check if Windsurf has equivalent (often different name) |

## Examples

### Quick Evaluation Script

```bash
# Install Windsurf alongside existing editor
brew install --cask windsurf  # macOS

# Import settings
windsurf --list-extensions  # Check what's already imported

# Open same project in both editors, compare AI quality
windsurf /path/to/project
cursor /path/to/project  # or: code /path/to/project
```

### Concept Quick Reference

```
Copilot → Supercomplete (Tab completions)
Copilot Chat → Cascade Chat (Cmd+L, Chat mode)
Copilot Edit → Cascade Write (Cmd+L, Code mode)
Composer (Cursor) → Cascade Write
Cmd+K (Cursor) → Cmd+I (Windsurf Command)
.cursorrules → .devin/rules/project.md
.cursorignore → .codeiumignore
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Download](https://windsurf.com/download)
- [Windsurf vs Cursor Comparison](https://windsurf.com/compare/windsurf-vs-cursor)
- [Windsurf Changelog](https://windsurf.com/changelog)

## Related Skill

Continue with `windsurf-advanced-troubleshooting` when migration validation exposes indexing, extension, MCP, authentication, persistent workspace-state, or editor-runtime failures.
