---
title: 'Slash Commands and Hooks'
description: 'Skills and legacy slash commands, plus real lifecycle hook configuration, stdin input, and failure-handling boundaries.'
section: 'concepts'
order: 4
keywords:
  - 'Claude Code commands'
  - 'slash commands'
  - 'Claude Code hooks'
  - 'PreToolUse'
  - 'PostToolUse'
  - 'lifecycle hooks'
  - 'commands/*.md'
  - 'CLAUDE_PLUGIN_ROOT'
officialLinks:
  - title: 'Claude Code Custom Slash Commands'
    url: 'https://code.claude.com/docs/en/slash-commands'
  - title: 'Claude Code Hooks'
    url: 'https://code.claude.com/docs/en/hooks'
  - title: 'Claude Code Plugins Overview'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'concepts/plugins'
  - 'concepts/skills'
  - 'concepts/agents'
  - 'reference/skill-frontmatter'
---

## Overview

Skills and legacy command files can both provide explicit slash invocations. Hooks react to lifecycle events. They solve different problems: an invocation requests work; a hook runs at a defined point in the session or tool lifecycle.

Plugin invocations are namespaced, such as `/example-plugin:review`. The exact name depends on the installed artifact. Do not assume every plugin provides `/review` or `/deploy`.

## Skills and legacy commands

New reusable instructions should generally use `skills/<name>/SKILL.md`. Files in `commands/<name>.md` remain supported; they are not declared deprecated by the native skills reference. Their name comes from the filename, and they support the same frontmatter as skills except `name` and `paths`.

A skill can be invoked by the user without `argument-hint`. That field documents expected input; it does not enable manual invocation. `user-invocable: false` blocks explicit user invocation. Claude can still invoke the skill unless `disable-model-invocation: true` also restricts model invocation.

This is an illustrative legacy command, not a marketplace-ready skill file:

````markdown
---
description: Review the user-supplied diff without modifying files.
argument-hint: '[review focus]'
allowed-tools: Read, Grep, Glob
---

Review the supplied diff with this focus: $ARGUMENTS.

Return concrete findings and uncertainties. Do not execute repository scripts
or claim that tests passed without corresponding evidence.

Example output format:

```text
Finding: path/to/file.ts — explanation and suggested test
Uncertainty: behavior requiring execution or provider access
```
````

`allowed-tools` preapproves tools for an invocation; it is not an exclusive tool sandbox. Marketplace skills still require all eight repository-required fields. See [skills](/docs/concepts/skills/) for that separate contract.

## Hook configuration

Use the actual lifecycle event names, such as `PreToolUse`, `PostToolUse`, and `SessionStart`. The event allowlist is larger than those examples; the [hook reference](https://code.claude.com/docs/en/hooks) owns it.

A plugin's `hooks/hooks.json` nests command hooks beneath an event and matcher:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/check-write.py\""
          }
        ]
      }
    ]
  }
}
```

The following complete Python handler refuses a requested write whose basename is `.env`, and refuses malformed input. It is a narrow filename check, **not** a complete secret, symlink, path, or authorization policy:

```python
import json
import sys
from pathlib import PurePosixPath, PureWindowsPath


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("Expected an event object")
        if event.get("tool_name") not in {"Write", "Edit"}:
            raise ValueError("Unexpected tool")
        tool_input = event.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("Expected tool_input object")
        path = tool_input.get("file_path")
        if not isinstance(path, str) or not path or "\x00" in path:
            raise ValueError("Expected a nonempty file_path")
        names = {PurePosixPath(path).name, PureWindowsPath(path).name}
        if ".env" in names:
            raise ValueError("Direct .env writes require separate review")
    except (ValueError, TypeError) as error:
        print(f"Write check refused: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The event arrives as JSON on **stdin**. There is no established `CLAUDE_TOOL_INPUT_FILE` environment variable in this hook contract. For Bash events, inspect `tool_input.command`, not a fabricated file-path variable. Never evaluate untrusted event JSON as shell code.

## Blocking, errors, and output

For this `PreToolUse` command hook, exit code **2** is the documented blocking signal. Do not generalize every nonzero exit to “the tool was blocked”: behavior depends on the event and hook configuration. `PostToolUse` runs after the operation and cannot undo it.

A real validation gate must propagate operational failures. Do not append `2>/dev/null || true` to a gate or hide a test failure behind a successful `tail` process. When intentionally showing the end of a test log, Bash needs `set -o pipefail` and a documented failure policy. An optional formatter can be advisory, but label that role explicitly rather than silently turning a failed gate green.

Avoid logging every raw Bash command or full tool payload. Commands, file content, and arguments may contain secrets. If evidence is required, collect only necessary redacted fields in access-controlled storage with a defined retention policy.

## Test and install boundaries

Test handlers with isolated stdin fixtures before enabling them. A passing narrow filename fixture does not certify a complete security policy. Quote `${CLAUDE_PLUGIN_ROOT}` and any paths passed to interpreters. A Python script launched through `python3` does not need to be directly executable; the interpreter must exist in the target environment.

Use the native hook reference and this repository's canonical hook validator for the full event/schema contract. This page does not change the allowed event set or promote advisory checks into required policy.
