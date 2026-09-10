---
name: windsurf-debug-bundle
description: 'Collect Devin Desktop (formerly Windsurf) diagnostic information for troubleshooting and support
  tickets.

  Use when encountering persistent issues, preparing support tickets,

  or collecting diagnostic data for Windsurf problems.

  Trigger with phrases like "windsurf debug", "windsurf support",

  "windsurf diagnostic", "windsurf logs", "windsurf not working".

  '
allowed-tools: Read, Bash(grep:*), Bash(ls:*), Bash(tar:*), Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- debugging
- support
compatibility: Designed for Claude Code
---
# Windsurf Debug Bundle

## Current State

Collect editor, runtime, and operating-system versions only after the user requests a diagnostic bundle; do not execute shell substitutions while loading this skill.

## Overview

Collect a minimal, redacted diagnostic package for troubleshooting Devin Desktop issues or preparing an effective support request without sweeping unrelated user data.

## Prerequisites

- Windsurf installed (even if malfunctioning)
- Terminal access
- Permission to read Windsurf config directories

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Collect Windsurf Configuration State

```bash
#!/bin/bash
set -euo pipefail

BUNDLE="windsurf-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE"/{config,logs,workspace}

echo "=== Windsurf Debug Bundle ===" > "$BUNDLE/summary.txt"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BUNDLE/summary.txt"

# 1. Windsurf version and environment
echo "--- Environment ---" >> "$BUNDLE/summary.txt"
windsurf --version >> "$BUNDLE/summary.txt" 2>&1 || echo "windsurf CLI not found" >> "$BUNDLE/summary.txt"
node --version >> "$BUNDLE/summary.txt" 2>&1
echo "OS: $(uname -srm)" >> "$BUNDLE/summary.txt"

# 2. Codeium config (redacted)
echo "--- Codeium Config ---" >> "$BUNDLE/summary.txt"
ls -la ~/.codeium/ >> "$BUNDLE/config/codeium-dir.txt" 2>&1 || echo "No ~/.codeium/" >> "$BUNDLE/config/codeium-dir.txt"

# 3. MCP server config (redacted)
if [ -f ~/.codeium/windsurf/mcp_config.json ]; then
  sed 's/"[A-Za-z0-9_-]\{20,\}"/"***REDACTED***"/g' ~/.codeium/windsurf/mcp_config.json > "$BUNDLE/config/mcp-config-redacted.json"
fi

# 4. Workspace config
cp .devin/rules/project.md "$BUNDLE/workspace/" 2>/dev/null || true
cp .codeiumignore "$BUNDLE/workspace/" 2>/dev/null || true
ls -la .windsurf/ >> "$BUNDLE/workspace/windsurf-dir.txt" 2>/dev/null || true
ls -la .devin/rules/ >> "$BUNDLE/workspace/rules-dir.txt" 2>/dev/null || true

# 5. Extension list
windsurf --list-extensions > "$BUNDLE/config/extensions.txt" 2>/dev/null || echo "Cannot list extensions" > "$BUNDLE/config/extensions.txt"
```

### Step 2: Collect Logs

```bash
# Windsurf logs location varies by OS:
# macOS: ~/Library/Application Support/Windsurf/logs/
# Linux: ~/.config/Windsurf/logs/
# Windows: %APPDATA%/Windsurf/logs/

LOG_DIR="${HOME}/.config/Windsurf/logs"
[ -d "$LOG_DIR" ] || LOG_DIR="${HOME}/Library/Application Support/Windsurf/logs"

if [ -d "$LOG_DIR" ]; then
  # Copy last 1000 lines of each log (redacted)
  for log in "$LOG_DIR"/*.log; do
    tail -1000 "$log" 2>/dev/null | sed 's/Bearer [^ ]*/Bearer ***REDACTED***/g' > "$BUNDLE/logs/$(basename "$log")"
  done
fi

# Codeium-specific logs
if [ -d ~/.codeium/windsurf/logs ]; then
  cp ~/.codeium/windsurf/logs/*.log "$BUNDLE/logs/" 2>/dev/null || true
fi
```

### Step 3: Check Workspace Health

```bash
# Workspace analysis
echo "--- Workspace Health ---" >> "$BUNDLE/summary.txt"
echo "File count: $(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l)" >> "$BUNDLE/summary.txt"
echo "Has .devin/rules/project.md: $([ -f .devin/rules/project.md ] && echo 'YES' || echo 'NO')" >> "$BUNDLE/summary.txt"
echo "Has .codeiumignore: $([ -f .codeiumignore ] && echo 'YES' || echo 'NO')" >> "$BUNDLE/summary.txt"
echo "Has .devin/rules/: $([ -d .devin/rules ] && echo 'YES' || echo 'NO')" >> "$BUNDLE/summary.txt"

# Check for common issues
if [ ! -f .codeiumignore ] && [ -d node_modules ]; then
  echo "WARNING: No .codeiumignore but node_modules exists -- indexing will be slow" >> "$BUNDLE/summary.txt"
fi
```

### Step 4: Package and Submit

```bash
tar -czf "$BUNDLE.tar.gz" "$BUNDLE"
echo "Debug bundle created: $BUNDLE.tar.gz"
echo "Review for sensitive data before submitting to support."
```

## Support Ticket Template

Populate the template only from reviewed bundle evidence, and replace every bracketed field before sharing it with support.

```markdown
## Windsurf Support Request

**Windsurf Version:** [from debug bundle]
**OS:** [macOS/Linux/Windows + version]
**Plan:** [Free/Pro/Teams/Enterprise]

### Issue
[One paragraph description]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]

### Expected vs Actual
- Expected: [behavior]
- Actual: [behavior]

### Attachments
- [ ] Debug bundle (windsurf-debug-*.tar.gz)
- [ ] Screenshot of error (if visual)
- [ ] Relevant .devin/rules/project.md (if context-related)

### Already Tried
- [ ] Restart Cascade
- [ ] Reload Window
- [ ] Reset Indexing
- [ ] Disable conflicting extensions
```

## Output

Create a sanitized diagnostic bundle plus a manifest listing included files, redactions, collection time, editor version, operating system, and reproduction steps. Do not include source code, tokens, cookies, environment secrets, or unreviewed MCP configuration values.

## Error Handling

| Item | Purpose | Included |
|------|---------|----------|
| Windsurf version | Compatibility check | Yes |
| Extension list | Conflict detection | Yes |
| Workspace config | Context issues | Yes |
| Log files (redacted) | Error analysis | Yes |
| MCP config (redacted) | Integration issues | Yes |

## Examples

### ALWAYS REDACT

- API keys and tokens
- Passwords and secrets
- Personal file paths (replace with ~/)
- Customer data

### Quick Single-Command Health Check

```bash
echo "Windsurf: $(windsurf --version 2>/dev/null || echo 'N/A')" && \
echo "Rules: $([ -f .devin/rules/project.md ] && wc -c < .devin/rules/project.md || echo 'none')" && \
echo "Ignore: $([ -f .codeiumignore ] && wc -l < .codeiumignore || echo 'none')"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf GitHub Issues](https://windsurf.com/support)
- [Windsurf Status](https://status.windsurf.com)

## Related Skill

Continue with `windsurf-rate-limits` when the bundle shows quota exhaustion, reset-window confusion, or unexpectedly expensive session behavior.
