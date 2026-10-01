---
name: janitor-swipe
description: "Tinder for your Claude Code skills. Reviews a sorted deck of every installed skill and lets you swipe keep / delete / skip on each one. Use when the user wants to bulk-clean their skill collection, triage unused skills, or do interactive skill cleanup. Trigger with '/janitor-swipe'."
allowed-tools: Read, Bash(bash:*)
argument-hint: "[--deck <file>] [--apply <decisions.json>]"
version: 1.7.0
author: Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>
license: MIT
compatibility: Designed for Claude Code. The TUI itself requires an interactive terminal (the user runs it with the '!' prefix); requires bash 3.2+ and a terminal of at least 50x22.
tags:
  - skills
  - triage
  - tui
  - cleanup
  - context-window
---

# Janitor Swipe — interactive skill triage

A bash TUI that puts every installed skill into a sorted deck and lets the user swipe keep / delete / skip on each card.

## Overview

The deck is sorted "most likely waste first" — heavy, never-used skills appear at the top, so most users hit `← delete` a few times and quit before reviewing the whole list. The swipe is scope-aware and honest about what it can delete: user-scope skills are actually removed (after confirmation), plugin skills are flagged for review instead.

## Prerequisites

- Claude Code with the skills-janitor plugin installed (provides `scripts/swipe.sh` and `swipe-build-deck.sh`)
- bash 3.2+ (the stock macOS bash works; no external dependencies)
- **An interactive terminal at least 50 columns x 22 rows** — the TUI reads single keypresses

## Instructions

### Step 1: Tell the user to run it via `!`

Inside Claude Code, the Bash tool's stdin is non-interactive, so the keypress reader can't work. The user must invoke it via the `!` prefix so the command runs in their actual shell:

```
!bash ~/.claude/skills/skills-janitor/scripts/swipe.sh
```

When the user asks for `/janitor-swipe`, tell them to run that command in their terminal. Do NOT try to run it yourself via the Bash tool — it will error with "needs an interactive terminal".

### Step 2: Explain the card and controls

Each card shows:

- Skill name + position in deck (e.g. `[3 / 47]`)
- Context cost split: `X always · Y on trigger` (description tokens are permanent; body loads only when the skill fires)
- Usage count and last invoked date
- Scope (`user`, `project`, `plugin · <plugin-name>`, etc.)
- 3-line truncated description
- Verdict label (e.g. *"Unused + heavy on trigger — prime delete candidate"*)

Controls:

- `←` / `h` / `d` — stage for delete
- `→` / `l` / `k` — keep
- `↓` / `j` / `s` / space — skip
- `u` — undo (back up one card, clear its decision)
- `i` — inspect (show full SKILL.md description)
- `q` / Esc — quit (still shows summary for decisions made so far)

### Step 3: Scope-aware deletion (the critical correctness point)

| Scope | What happens on swipe left |
|---|---|
| `user`, `project`, `codex-user`, `codex-project` | Path is staged for `rm -rf` (or unlink if symlink) |
| `plugin`, `plugin-source` | NOT deleted — flagged under "Plugins to review" at the apply screen, with a hint to run `/plugin uninstall <plugin>` if enough skills from that plugin were swiped |
| `mcp-user`, `mcp-project` (v1.7) | Server entry is removed from its config file (`~/.claude.json` / `.mcp.json`) with a timestamped `.bak` backup — reversible |
| `mcp-plugin` | NOT edited — flagged for plugin review like plugin skills |

MCP server cards show real call counts from session transcripts instead of token guesses (schemas live server-side). An unused connected server ranks high — its tool schemas load into context for nothing.

## Output

After the last card (or `q`), an apply screen shows keep/skip/delete counts, the deletion list with paths, the "frees X always-loaded + Y on-trigger" token summary, the plugin review breakdown, and a prompt:

- `y` — apply deletions immediately (logged to `~/.skills-janitor/log.jsonl` with path and frontmatter snapshot)
- `N` — cancel
- `save` — write decisions to `~/.skills-janitor/swipe-<timestamp>.json` for later application via `swipe.sh --apply <file>`

## Error Handling

1. **Error**: "Swipe needs an interactive terminal"
   **Solution**: The command was run through the Bash tool. Have the user run it with the `!` prefix in their own terminal.

2. **Error**: "Swipe needs at least 50 columns / 22 rows"
   **Solution**: The terminal window is too small — resize and retry.

3. **Error**: No skills to swipe
   **Solution**: Nothing is installed (exits 0 with a message) — suggest `/janitor-discover` to find skills.

4. **Error**: The user wants a non-interactive view instead
   **Solution**: Point them at `/janitor-report` or `/janitor-value` for the same data in list form.

Edge cases handled by the script: Ctrl-C mid-swipe restores the terminal; symlinks are unlinked, never followed; old saved decks without the v1.5 token-split fields still load.

## Examples

### Example 1: Standard triage

**Input**: "/janitor-swipe" or "help me clean up my skills interactively"

**Output**: Explain the flow in two sentences, then give the exact command to run: `!bash ~/.claude/skills/skills-janitor/scripts/swipe.sh` — and offer to review the results afterwards.

### Example 2: Resume saved decisions

**Input**: "I saved my swipe decisions yesterday — apply them."

**Output**: `!bash ~/.claude/skills/skills-janitor/scripts/swipe.sh --apply ~/.skills-janitor/swipe-<timestamp>.json` (list the files in `~/.skills-janitor/` to find the right one).

## Resources

- TUI script (plugin-relative): `{baseDir}/../../scripts/swipe.sh`; deck builder: `{baseDir}/../../scripts/swipe-build-deck.sh`
- Deletion log: `~/.skills-janitor/log.jsonl`
- `/janitor-report` — same data as a non-interactive list
- `/janitor-value` — the token + usage data underneath the swipe deck
- `/janitor-fix --prune` — automated broken-symlink cleanup, no interactive review
