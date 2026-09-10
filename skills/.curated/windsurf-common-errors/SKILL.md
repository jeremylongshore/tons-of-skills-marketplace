---
name: windsurf-common-errors
description: 'Diagnose and fix common Devin Desktop (formerly Windsurf) IDE and Cascade errors.

  Use when Cascade stops working, Supercomplete fails, indexing hangs,

  or encountering Windsurf-specific issues.

  Trigger with phrases like "windsurf error", "fix windsurf",

  "windsurf not working", "cascade broken", "windsurf slow".

  '
allowed-tools: Read, Grep, Bash(curl:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- debugging
- troubleshooting
compatibility: Designed for Claude Code
---
# Windsurf Common Errors

## Overview

Quick reference for the most common Windsurf IDE errors and their solutions. Covers Cascade failures, Supercomplete issues, indexing problems, and extension conflicts.

## Prerequisites

- Windsurf installed and previously working
- Access to Windsurf settings and logs

Reproduce the issue with a harmless workspace before changing shared configuration or collecting diagnostic data.

## Authentication

The public status page requires no authentication. Account, organization, and MCP diagnostics use the operator's existing Devin Desktop session plus provider-specific OAuth or environment-backed credentials; redact all values from logs and support bundles.

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Error 1: Cascade Not Responding

**Symptoms:** Cascade panel shows spinner indefinitely, no response to prompts.

**Solutions:**

1. Check internet connection -- Cascade requires cloud access
2. Check Windsurf status: https://status.windsurf.com
3. Check the usage meter and account state in Devin Desktop
4. Restart Cascade: Command Palette > "Cascade: Restart"
5. Restart Windsurf: Cmd/Ctrl+Shift+P > "Reload Window"

### Error 2: Supercomplete Not Showing Suggestions

**Symptoms:** No ghost text appears while typing.

**Solutions:**

1. Check if disabled: Click Windsurf widget (status bar) > verify autocomplete is ON
2. Check file type: Supercomplete may be disabled for certain languages
3. Check `.codeiumignore`: Current file might be excluded from indexing
4. Ensure not conflicting: Disable GitHub Copilot or TabNine if installed

```json
// Verify in settings.json
{
  "editor.inlineSuggest.enabled": true,
  "codeium.autocomplete.enable": true
}
```

### Error 3: Indexing Stuck or Slow

**Symptoms:** Status bar shows "Indexing..." for extended periods, Cascade lacks context.

**Solutions:**

1. Compare workspace file count and available memory with the current indexing guidance
2. Create or update `.codeiumignore`:

```gitignore
node_modules/
.git/
dist/
build/
.next/
coverage/
vendor/
__pycache__/
*.min.js
*.bundle.js
*.map
```

1. Open a subdirectory instead of monorepo root
2. Use the current indexing controls in Devin Desktop settings; preserve diagnostics before resetting

### Error 4: Extension Conflicts

**Symptoms:** Duplicate suggestions, slow editor, features not working.

**Known conflicts:**

```
GitHub Copilot — conflicts with Supercomplete (disable one)
TabNine — conflicts with Supercomplete
Cody (Sourcegraph) — conflicts with Cascade
IntelliCode — may interfere with completions
```

**Fix:** Disable conflicting extensions:

```
Extensions sidebar > Search "copilot" > Disable
```

### Error 5: Cascade Writes to Wrong Files

**Symptoms:** Cascade modifies files you didn't intend.

**Solutions:**

1. Be specific in prompts: name exact file paths
2. Add constraints: "Don't modify any files except src/services/auth.ts"
3. Use `.codeiumignore` to exclude sensitive directories from Cascade context
4. Review diffs before accepting -- use the Revert button per step
5. Always commit before Cascade sessions for safe rollback

### Error 6: "Model not available" or Quota Exhausted

**Symptoms:** The usage meter shows exhausted daily or weekly quota, or a selected model is unavailable.

**Solutions:**

- Check the displayed daily and weekly reset times.
- Use a currently available free or lower-cost SWE-family model for routine work.
- On eligible paid plans, use extra usage only within an approved spending limit.
- Confirm the current plan at `windsurf.com/subscription/manage-plan`.

### Error 7: MCP Server Not Connecting

**Symptoms:** MCP tools not appearing in Cascade, "server disconnected" errors.

**Solutions:**

1. Verify MCP is enabled: Settings > Cascade > MCP > Enable
2. Check config file: `~/.codeium/windsurf/mcp_config.json`
3. Verify command exists: Run the MCP command manually in terminal
4. Check environment variables: MCP config supports `${VAR}` interpolation
5. Restart: Command Palette > "Cascade: Restart MCP Servers"

### Error 8: Cascade Loses Context Mid-Conversation

**Symptoms:** Cascade forgets what it was doing, makes contradictory changes.

**Solutions:**

1. Keep conversations focused: one task per Cascade session
2. Start a new conversation for new tasks (Cmd/Ctrl+L, then + icon)
3. Use @ mentions to re-inject context: `@src/services/auth.ts`
4. Convert key decisions to Memories: "Remember that we're using JWT, not sessions"
5. For long tasks, use Workflows instead of multi-turn conversations

## Output

Return the observed symptom, likely cause, evidence gathered, smallest corrective action, and a verification step. If the issue remains unresolved, include a sanitized reproduction and the exact support channel or documentation page to use next.

## Error Handling

| Issue | Quick Fix | Root Cause |
|-------|-----------|------------|
| No AI features | Check auth in status bar | Token expired, re-sign-in |
| Cascade slow | Add `.codeiumignore` | Indexing too many files |
| Wrong suggestions | Update `.devin/rules/project.md` | Missing project context |
| Preview broken | Close and re-open Preview | Dev server disconnected |
| Terminal errors | Cmd/Ctrl+Shift+. | Auto-debug via Cascade |

## Examples

### Quick Health Check

```bash
# Check if Windsurf is installed
windsurf --version

# Check Codeium auth state
ls ~/.codeium/
```

### Reset Everything

```
Command Palette (Cmd/Ctrl+Shift+P):
1. Download diagnostics, then use the current indexing reset control.
2. "Cascade: Restart"
3. "Developer: Reload Window"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Status Page](https://status.windsurf.com)
- [Windsurf GitHub Issues](https://windsurf.com/support)
- [Windsurf Documentation](https://docs.devin.ai/desktop)

## Related Skill

Continue with `windsurf-debug-bundle` when the quick fixes do not resolve the issue and support-ready evidence must be collected safely.
