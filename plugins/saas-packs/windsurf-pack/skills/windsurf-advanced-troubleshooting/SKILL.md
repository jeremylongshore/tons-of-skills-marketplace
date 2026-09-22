---
name: windsurf-advanced-troubleshooting
description: 'Advanced Devin Desktop (formerly Windsurf) debugging for hard-to-diagnose IDE, Cascade, and indexing
  issues.

  Use when standard troubleshooting fails, Cascade produces consistently wrong output,

  or investigating deep configuration problems.

  Trigger with phrases like "windsurf deep debug", "windsurf mystery error",

  "windsurf impossible to fix", "cascade keeps failing", "windsurf advanced debug".

  '
allowed-tools: Read, Grep, Bash(ls:*), Bash(curl:*), Bash(find:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- debugging
- advanced
- troubleshooting
compatibility: Designed for Claude Code
---
# Windsurf Advanced Troubleshooting

## Overview

Deep debugging techniques for Windsurf issues that resist standard troubleshooting. Covers Cascade context corruption, indexing engine problems, extension conflicts, MCP failures, and workspace configuration debugging.

## Prerequisites

- Standard troubleshooting attempted (see `windsurf-common-errors`)
- Terminal access
- Understanding of Devin Desktop's editor, Cascade, indexing, extension, and MCP layers

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Isolate Windsurf Layer vs VS Code Layer

```
Devin Desktop = editor shell + Cascade + indexing/context + extension/MCP layers

If the issue is:
- Editor crashes, rendering, file system → VS Code layer
- AI suggestions wrong, Cascade fails, indexing stuck → Cascade or context/indexing layer
- Extension not working → Extension compatibility layer

Test VS Code layer:
  windsurf --disable-extensions  # Run without extensions
  # If issue persists → VS Code layer problem

Test AI and extension layers:
  # Start with extensions disabled using the documented troubleshooting flow.
  # If the issue resolves, re-enable extensions incrementally to isolate the conflict.
```

### Step 2: Debug Cascade Context Issues

When Cascade consistently gives wrong or irrelevant suggestions:

```bash
set -euo pipefail
echo "=== Cascade Context Debug ==="
readonly WORKSPACE_RULE_LIMIT=12000 # Current documented maximum for one workspace rule.
readonly GLOBAL_RULE_LIMIT=6000 # Current documented maximum for the global rule.

# 1. Check rules file
echo "--- .devin/rules/project.md ---"
if [ -f .devin/rules/project.md ]; then
  CHARS=$(wc -c < .devin/rules/project.md)
  echo "Size: $CHARS chars (workspace rule limit: $WORKSPACE_RULE_LIMIT)"
  [ "$CHARS" -gt "$WORKSPACE_RULE_LIMIT" ] && echo "WARNING: Workspace rule exceeds its limit"
else
  echo "MISSING — Cascade has no project context"
fi

# 2. Check workspace rules
echo "--- Workspace Rules ---"
TOTAL_RULE_CHARS=0
if [ -d .devin/rules ]; then
  for rule in .devin/rules/*.md; do
    [ -f "$rule" ] || continue
    CHARS=$(wc -c < "$rule")
    TOTAL_RULE_CHARS=$((TOTAL_RULE_CHARS + CHARS))
    HAS_TRIGGER=$(grep -c "^trigger:" "$rule" || true)
    echo "  $(basename "$rule"): $CHARS chars, trigger: $([[ $HAS_TRIGGER -gt 0 ]] && echo 'YES' || echo 'MISSING')"
  done
  echo "Total: $TOTAL_RULE_CHARS chars"
else
  echo "No .devin/rules/ directory"
fi

# 3. Check independent rule limits
RULES_CHARS=$(wc -c < .devin/rules/project.md 2>/dev/null || echo 0)
GLOBAL_CHARS=$(wc -c < ~/.codeium/windsurf/memories/global_rules.md 2>/dev/null || echo 0)
echo "--- Rule Limits ---"
echo "Workspace rule: $RULES_CHARS/$WORKSPACE_RULE_LIMIT chars; global rule: $GLOBAL_CHARS/$GLOBAL_RULE_LIMIT chars"
[ "$RULES_CHARS" -gt "$WORKSPACE_RULE_LIMIT" ] && echo "WARNING: Workspace rule exceeds its limit"
[ "$GLOBAL_CHARS" -gt "$GLOBAL_RULE_LIMIT" ] && echo "WARNING: Global rule exceeds its limit"

# 4. Check memories
echo "--- Memories ---"
MEMORY_DIR="$HOME/.codeium/windsurf/memories"
if [ -d "$MEMORY_DIR" ]; then
  MEMORY_COUNT=$(find "$MEMORY_DIR" -type f | wc -l)
  echo "Memory files: $MEMORY_COUNT"
  [ "$MEMORY_COUNT" -gt 50 ] && echo "WARNING: Many memories — may cause conflicting context"
else
  echo "No memories directory"
fi
```

### Step 3: Debug Indexing Problems

```bash
set -euo pipefail
echo "=== Indexing Debug ==="

# Count files that would be indexed
readonly LARGE_WORKSPACE_HEURISTIC=10000 # Diagnostic threshold, not a vendor limit.
TOTAL_FILES=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l)
echo "Total files (excluding node_modules, .git): $TOTAL_FILES"

# Check for large files that slow indexing
echo "--- Large files (>1MB, not in node_modules) ---"
find . -type f -size +1M -not -path '*/node_modules/*' -not -path '*/.git/*' | head -10

# Check .codeiumignore effectiveness
if [ -f .codeiumignore ]; then
  echo "--- .codeiumignore patterns ---"
  wc -l < .codeiumignore
  echo "patterns defined"
else
  echo "WARNING: No .codeiumignore — indexing everything"
fi

# Recommendations
if [ "$TOTAL_FILES" -gt "$LARGE_WORKSPACE_HEURISTIC" ]; then
  echo ""
  echo "RECOMMENDATION: >10K files. Open a subdirectory instead of root."
  echo "RECOMMENDATION: Add more patterns to .codeiumignore"
fi
```

### Step 4: Debug Extension Conflicts

```bash
set -euo pipefail
echo "=== Extension Conflict Check ==="

# List all installed extensions
windsurf --list-extensions 2>/dev/null | while read ext; do
  # Check for known conflicts
  case "$ext" in
    *copilot*|*tabnine*|*cody*|*intellicode*|*aws-toolkit*codewhisperer*)
      echo "CONFLICT: $ext — competes with Supercomplete/Cascade"
      ;;
    *remote*|*liveshare*|*container*)
      echo "OK: $ext — compatible but may affect performance"
      ;;
    *)
      echo "OK: $ext"
      ;;
  esac
done

echo ""
echo "Resolution: Disable conflicting extensions or run:"
echo "  windsurf --disable-extensions  # Test in clean mode"
```

### Step 5: Debug MCP Server Issues

```bash
set -euo pipefail
echo "=== MCP Debug ==="

MCP_CONFIG="$HOME/.codeium/windsurf/mcp_config.json"
if [ -f "$MCP_CONFIG" ]; then
  echo "MCP config exists"
  # Validate JSON
  python3 -c "import json; json.load(open('$MCP_CONFIG'))" 2>&1 && echo "JSON: valid" || echo "JSON: INVALID"

  # Check each server command
  python3 -c "
import json
config = json.load(open('$MCP_CONFIG'))
for name, server in config.get('mcpServers', {}).items():
    cmd = server.get('command', 'N/A')
    print(f'  {name}: command={cmd}')
  "
else
  echo "No MCP config at $MCP_CONFIG"
fi
```

### Step 6: Nuclear Reset Options

When nothing else works:

```markdown
## Progressive Reset (least to most destructive)

1. Restart Cascade
   Command Palette > "Cascade: Restart"

2. Reset Indexing
   Download diagnostics, then use the current indexing control in Settings.

3. Reload Window
   Cmd/Ctrl+Shift+P > "Developer: Reload Window"

4. Review Memories and Rules
   Export or record needed customizations, then remove only the confirmed bad item through the UI.

5. Re-authenticate
   Sign out and back in only after preserving diagnostics and confirming the organization.

6. Clean Install
   Follow the current support instructions for the operating system. Back up settings first; do not recursively delete the entire Codeium/Devin state tree from a generic runbook.
```

## Output

Return a diagnostic report with the isolated failing layer, commands and evidence collected, the least-destructive corrective action, validation results, and any remaining escalation data. Redact credentials, tokens, repository content, and personal paths before sharing the report.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Cascade gives contradictory advice | Conflicting memories | Clear old memories |
| Rules ignored | Over 12K combined chars | Trim rules, check total budget |
| Wrong file suggestions | Stale index | Reset indexing |
| Slow after update | Extension incompatibility | Test with `--disable-extensions` |
| MCP tools missing | Config JSON invalid | Validate with python3 json parser |
| Everything broken | Corrupted state | Progressive reset (Step 6) |

## Examples

### Quick Diagnostic One-Liner

```bash
echo "WS files: $(find . -not -path '*/node_modules/*' -not -path '*/.git/*' -type f | wc -l) | Rules: $(wc -c < .devin/rules/project.md 2>/dev/null || echo 0)c | Ignore: $(wc -l < .codeiumignore 2>/dev/null || echo 0) patterns | Exts: $(windsurf --list-extensions 2>/dev/null | wc -l)"
```

### Submit Support Ticket

```markdown
Attach:
1. Output from all diagnostic scripts above
2. Debug bundle from windsurf-debug-bundle
3. Exact prompts that produce wrong results
4. Expected vs actual Cascade behavior
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf GitHub Issues](https://windsurf.com/support)
- [Windsurf Status Page](https://status.windsurf.com)

## Related Skill

Continue with `windsurf-load-scale` when the diagnosis shows workspace size, indexing scope, or organization rollout is the limiting factor.
