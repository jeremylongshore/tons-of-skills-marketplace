---
title: "Fixing Claude Code Hooks: The New Matcher Format"
description: "Fixing Claude Code Hooks: The New Matcher Format"
date: "2026-02-04"
tags: ["claude-code", "debugging", "configuration", "hooks"]
featured: false
canonical: "https://startaitools.com/posts/fixing-claude-code-hooks-the-new-matcher-format/"
---

*Correction, 2026-10-03: An earlier version of this post said `matcher` must be a valid regex and that an empty string does not work, and its fixed example put a matcher on a `Stop` hook. The current [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) (checked 2026-10-03) says `"*"`, `""` or an omitted matcher all match every occurrence, and that `Stop` does not support matchers: a matcher there is silently ignored. The matcher rule and the example below have been corrected.*

Claude Code recently changed their hooks format, and if you haven't updated your project settings, you'll see this cryptic error:

```
hooks: Expected array, but received undefined
Files with errors are skipped entirely, not just the invalid settings.
```

## The Problem

The old hook format put `command` at the top level:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "command": "bash .claude/hooks/my-script.sh"
      }
    ]
  }
}
```

This silently breaks - your entire settings file gets skipped.

## The Fix

The new format requires a nested `hooks` array with explicit `type`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/my-script.sh"
          }
        ]
      }
    ]
  }
}
```

Key changes:
1. **`matcher`** - Filters when the hook fires. `"*"`, `""` or leaving it out matches everything. A plain tool name such as `Bash`, or a list such as `Edit|Write`, matches exactly. Anything with other characters is treated as a regex. `Stop` and several other events ignore the matcher, so the example above leaves it out; it matters on tool events such as `PreToolUse` and `PostToolUse`
2. **`hooks`** - Now an array inside the matcher object
3. **`type`** - Required field, set to `"command"` for shell commands

## Quick Migration

Find all your `.claude/settings.json` files and update them:

```bash
# Find all Claude settings files
find ~/projects -name "settings.json" -path "*/.claude/*" 2>/dev/null
```

Then update each one to the new format.

## Related

- [Fixing Claude Code EACCES Multi-User Linux Permissions](/posts/fixing-claude-code-eacces-multi-user-linux-permissions/)
- [Debugging Claude Code Slash Commands](/posts/debugging-claude-code-slash-commands-silent-deployment-failures/)
