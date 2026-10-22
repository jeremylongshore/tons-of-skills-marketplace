---
name: janitor-value
description: "Show whether each skill is earning its context-window cost — combined tokens-used view sorted by waste. Use when the user asks 'are my skills worth it', 'what's my context budget', 'which skills are dead weight', or wants to audit skill value, token cost, or usage. Trigger with '/janitor-value'."
allowed-tools: Read, Bash(bash:*)
argument-hint: "[--weeks N] [--budget N] [--json]"
version: 1.7.0
author: Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>
license: MIT
compatibility: Designed for Claude Code. Requires bash 3.2+ (macOS default works). Reads local Claude Code data only (~/.claude/skills, ~/.claude/agents, session history).
tags:
  - skills
  - context-window
  - token-budget
  - usage-tracking
  - maintenance
---

# Skill Value Report

Show whether each installed skill is earning the context-window tokens it costs.

## Overview

Combine token cost and usage tracking into a single view of every installed skill, sorted with the heaviest unused skills at the top. The report splits each skill's cost into what is permanently loaded (the description) and what only loads on demand (the body), then cross-references recent invocations so the user can see which skills are dead weight.

Replaces the v1.2 split between `/janitor-tokens` (cost only) and `/janitor-usage` (usage only).

## Prerequisites

- Claude Code with the skills-janitor plugin installed (provides `scripts/value.sh`)
- bash 3.2+ (the stock macOS bash works; no external dependencies)
- Read access to `~/.claude/skills`, `~/.claude/agents`, and local Claude Code session history
- No authentication or API keys required — the script reads local files only

## Instructions

### Step 1: Run the value script

```bash
bash ~/.claude/skills/skills-janitor/scripts/value.sh [--weeks N] [--budget N] [--json]
```

- `--weeks N` — usage lookback window (default: 4)
- `--budget N` — context window size for % calculations (default: 200000)
- `--json` — emit raw JSON

### Step 2: Present the results

Show the table and summary to the user. When explaining results, do NOT describe body tokens as permanent context cost — only descriptions are always loaded. Plugin-namespaced skills appear with their full invocation name (e.g., `marketing-skills:image`, `figma:figma-use`).

### Step 3: Suggest action when waste is high

If "unused skill cost" exceeds 20% of the budget, recommend the user run `/janitor-report` for a full health check or (in v1.4+) `/janitor-swipe` to triage interactively.

## Output

A table of every installed skill with:

- **Always** — description tokens, permanently in the system prompt (the real context rent)
- **Body** — the rest of SKILL.md, loaded only when the skill triggers (progressive disclosure)
- **Used?** — `yes` if invoked in the lookback window, else `NO`
- **Last Used** — date of most recent invocation

Followed by a summary:

- Total tokens loaded into context (the always-loaded TOTAL includes skills plus subagent descriptions from `~/.claude/agents`, reported as % of budget)
- Active vs. unused split
- Top wasters: heavy skills with zero usage

## Error Handling

1. **Error**: `value.sh: No such file or directory`
   **Solution**: The plugin is installed under a different root. Locate it with `ls ~/.claude/skills` or check the plugin cache, then run the script from its actual location.

2. **Error**: Every skill shows `NO` in the Used? column
   **Solution**: The lookback window may be too short or session history is empty. Re-run with a longer window, e.g. `--weeks 12`.

3. **Error**: A skill shows 0 tokens
   **Solution**: Its SKILL.md is missing or unreadable. Run `/janitor-report` to surface broken skills, then `/janitor-fix --prune` to clean them up.

4. **Error**: Percentages look wrong for a non-default model
   **Solution**: Pass the correct context size explicitly, e.g. `--budget 500000`.

## Examples

### Example 1: Standard value check

**Input**: "Are my skills worth their token cost?"

**Output**: Run `bash ~/.claude/skills/skills-janitor/scripts/value.sh`, then present the table sorted by waste and the summary line, e.g. "Always-loaded total: 8,420 tokens (4.2% of 200k budget). 6 of 31 skills unused in 4 weeks; top waster: `heavy-skill` (1,900 tokens, never used)."

### Example 2: Longer lookback, custom budget

**Input**: "Check skill usage over the last quarter against a 500k window."

**Output**: Run `bash ~/.claude/skills/skills-janitor/scripts/value.sh --weeks 12 --budget 500000` and present the same table with the adjusted lookback and percentages.

### Example 3: Machine-readable output

**Input**: "Give me the raw skill value data."

**Output**: Run the script with `--json` and return the JSON payload unmodified.

### MCP servers (v1.7)

For the MCP side of context cost, run `bash {baseDir}/../../scripts/mcp.sh [--weeks N]` — inventories every configured server (user, project, plugin) with REAL call counts from session transcripts, and lists servers unused in the window. No token guesses: schemas live server-side, so the janitor reports calls, distinct tools used, and last-used instead.

## Resources

- Report script (plugin-relative): `{baseDir}/../../scripts/value.sh`
- `/janitor-report` — full health check including duplicates and broken skills
- `/janitor-fix --prune` — remove broken symlinks and empty skill dirs
- `/janitor-discover` — find new skills or check one before installing
