---
name: cursor-common-errors
description: 'Troubleshoot common Cursor IDE errors: authentication, completion, indexing,
  API, and performance

  issues. Triggers on "cursor error", "cursor not working", "cursor issue", "cursor
  problem",

  "fix cursor", "cursor crash".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-common
compatibility: Designed for Claude Code
---
# Cursor Common Errors

## Overview

Diagnose Cursor startup, authentication, extension, indexing, and workspace errors with reversible, user-scoped steps before resetting local state.

## Prerequisites

- A reproduction, Cursor version, affected operating system, and an approved backup location for user settings.
- Authorization to inspect local logs; redact project paths, prompts, and credentials from support evidence.

## Instructions

1. Reproduce the issue with extensions disabled or in a disposable profile when possible.
2. Capture the smallest relevant status/log evidence and try the least-destructive documented remedy.
3. Back up settings before clearing caches or resetting state, then validate recovery with a non-sensitive workspace.
4. Escalate persistent issues with a redacted reproduction instead of sharing workspace data.

## Output

- A classified issue, reversible remediation, and redacted verification result.

## Error Handling

| Condition | Safe response |
|---|---|
| Reset would erase user settings | Create and verify a backup before proceeding. |
| Logs contain sensitive code or tokens | Redact them and use the approved secure support route. |
| Error persists after safe remediation | Stop destructive retries and escalate with the minimal reproduction. |

## Examples

When Cursor will not start, launch once with extensions disabled, record the version and outcome, then re-enable extensions individually in a disposable profile. Clear only cache folders after backing up settings; do not delete the full profile to diagnose a single extension.

Diagnostic and resolution guide for the most frequent Cursor IDE issues. Organized by error category with specific symptoms, causes, and fixes.

## Authentication Errors

### "Sign-in failed" / OAuth Loop

**Symptoms:** Browser opens for auth, redirects back, Cursor still shows "Sign In".

**Fix:**

1. Clear browser cookies for `cursor.com` and `auth.cursor.com`
2. Try incognito/private window for the OAuth flow
3. Check if browser is blocking popups from cursor.com
4. Try a different auth method (GitHub vs Google vs email)

### "License not found" / "No active subscription"

**Symptoms:** Signed in but AI features are disabled.

**Fix:**

1. Verify subscription at [cursor.com/settings](https://cursor.com/settings)
2. Confirm the email address matches your Cursor account
3. Sign out (`Cmd+Shift+P` > `Sign Out`) then sign back in
4. If on a team plan, ask admin to verify your seat is assigned

### "Session expired"

**Symptoms:** Features stop working mid-session.

**Fix:** `Cmd+Shift+P` > `Cursor: Sign Out` > Sign back in. This refreshes the auth token.

## AI Completion Errors

### Tab Suggestions Not Appearing

**Symptoms:** No ghost text while typing.

**Causes and fixes:**

| Cause | Fix |
|-------|-----|
| Tab completion disabled | `Cursor Settings` > `Tab` > enable |
| Conflicting extension (Copilot/TabNine) | Disable other completion extensions |
| File type not supported | Check file is a recognized language |
| Rate limited (Free plan) | Wait or upgrade to Pro |
| Large file (>10K lines) | Split file or use Cmd+K for specific sections |

### "Request failed" / "Model unavailable"

**Symptoms:** Chat or Composer returns an error instead of a response.

**Fix:**

1. Check [status.cursor.com](https://status.cursor.com) for outages
2. Switch to a different model (model dropdown in Chat/Composer)
3. If using BYOK, verify API key is valid and has credits
4. Try a shorter prompt (may have hit context limit)

### Poor Quality Suggestions

**Symptoms:** AI generates irrelevant, outdated, or incorrect code.

**Fix:**

1. Add context: use `@Files` to reference relevant code
2. Add project rules: create `.cursor/rules/*.mdc` with your patterns
3. Switch model: try Claude Opus or GPT-5 for complex tasks
4. Start a new chat: long conversations degrade quality
5. Be more specific: "Add Zod validation to the user endpoint" beats "fix validation"

## Indexing Errors

### "Indexing stuck" / Never Completes

**Symptoms:** Status bar shows "Indexing..." indefinitely.

**Fix:**

1. Check `.cursorignore` -- exclude `node_modules/`, `dist/`, large data files
2. `Cmd+Shift+P` > `Cursor: Resync Index`
3. Close and reopen the workspace
4. Delete index cache:

   ```
   macOS: rm -rf ~/Library/Application\ Support/Cursor/Cache/
   Linux: rm -rf ~/.config/Cursor/Cache/
   ```

5. Restart Cursor

### "@Codebase returns no results"

**Symptoms:** Codebase search finds nothing, even for known code.

**Fix:**

1. Wait for indexing to complete (check status bar)
2. Verify the file is not in `.cursorignore` or `.gitignore`
3. Resync the index
4. Check network connectivity (embeddings require API access)

## Performance Errors

### Cursor is Slow / Freezing

**Symptoms:** Editor lags, typing delays, UI freezes.

**Diagnosis and fixes:**

```
Step 1: Open Process Explorer
  Cmd+Shift+P > "Developer: Open Process Explorer"
  Identify which process uses most CPU/memory

Step 2: Extension audit
  Disable extensions one-by-one to find the culprit
  Common offenders: GitLens (large repos), Prettier (on save), ESLint

Step 3: Reduce indexed scope
  Add large directories to .cursorignore

Step 4: Clear chat history
  Long chat sessions consume memory. Start new chats frequently.

Step 5: Increase memory limit
  settings.json: "files.maxMemoryForLargeFilesMB": 4096
```

### High CPU After Startup

**Symptoms:** CPU spikes for minutes after opening a project.

**Cause:** Initial indexing + extension loading.

**Fix:** Wait for indexing to complete. Add aggressive `.cursorignore` patterns. Close unused workspace folders.

## Extension Errors

### Extension Not Found / Install Failed

**Symptoms:** Extension from VS Code Marketplace not available.

**Cause:** Cursor uses Open VSX Registry, not Microsoft's marketplace.

**Fix:**

1. Search the extension on [open-vsx.org](https://open-vsx.org)
2. If not on Open VSX, download `.vsix` from VS Code Marketplace website
3. `Cmd+Shift+P` > `Extensions: Install from VSIX...`

### Extension Conflicts with AI Features

**Common conflicts:**

| Extension | Conflict | Resolution |
|-----------|----------|------------|
| GitHub Copilot | Duplicate Tab suggestions | Disable Copilot in Cursor |
| TabNine | Duplicate completions | Disable TabNine |
| IntelliCode | Suggestion conflicts | Disable IntelliCode |
| Vim | Ctrl+K/L/I conflicts | Remap AI shortcuts (see cursor-keybindings skill) |

## Network Errors

### "Connection refused" / "Timeout"

**Symptoms:** AI features fail but editor works fine.

**Fix:**

1. Check internet connectivity
2. Check if corporate firewall/proxy blocks `*.cursor.com`
3. Required domains to allowlist:

   ```
   api.cursor.com
   api2.cursor.com
   auth.cursor.com
   *.turbopuffer.com (for indexing)
   ```

4. If using VPN, try disconnecting temporarily

## Crash Recovery

### Cursor Won't Start

```bash
# Start with extensions disabled
cursor --disable-extensions

# Start with GPU disabled (Linux/Windows)
cursor --disable-gpu

# Reset to defaults (nuclear option -- backs up settings first)
# macOS:
cp -r ~/Library/Application\ Support/Cursor ~/cursor-backup
rm -rf ~/Library/Application\ Support/Cursor/Cache
rm -rf ~/Library/Application\ Support/Cursor/CachedData
```

### Recovering Unsaved Work

Cursor auto-saves by default. Check:

- `File` > `Open Recent` for recent files
- Hot exit preserves unsaved buffers between sessions
- Git reflog if changes were staged: `git reflog`

## Enterprise Considerations

- **Centralized troubleshooting**: Document common errors and fixes in team wiki
- **Proxy configuration**: Enterprise proxy settings via `settings.json`:

  ```json
  { "http.proxy": "http://proxy.corp.com:8080" }
  ```

- **Support escalation**: Business/Enterprise plans include priority support via Cursor dashboard
- **Telemetry for diagnostics**: Anonymous telemetry helps Cursor diagnose widespread issues (can be disabled)

## Resources

- [Cursor Status Page](https://status.cursor.com)
- [Cursor Community Forum](https://forum.cursor.com)
- [Cursor GitHub Issues](https://github.com/getcursor/cursor/issues)
