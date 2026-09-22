---
name: agent-safety-preflight
description: |
  Generate a local repository risk receipt before Claude Code or other AI-agent edits.
  Use when the user asks to prepare a repository for agent changes, check for risky
  hooks or credential-writing automation, or run the /agent-preflight command.
  Trigger with "run agent preflight", "check this repo before agent edits", or
  "/agent-preflight".
argument-hint: "[repo-path]"
allowed-tools: Read, Bash(git:*), Bash(python3:*)
version: 1.2.0
author: Signal Loom Works <194151508+el-zachariah@users.noreply.github.com>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - agent-safety
  - claude-code
  - preflight
---

# Agent Safety Preflight

## Overview

Agent Safety Preflight helps Claude inspect a local repository before making AI-agent-assisted edits. It produces a compact Green, Yellow, or Red risk receipt from local files only, with special attention to destructive shell patterns, credential-writing automation, agent authority surfaces, uncommitted changes, and unavailable git state.

The skill pairs with the `/agent-preflight` command in this plugin. Prefer the bundled lightweight scanner when it is available from a trusted Claude install root, then explain the decision and next safe action before editing.

## Prerequisites

- A local repository or workspace path to inspect.
- Python 3 available for the bundled `agent_preflight_lite.py` scanner.
- Git available when the workspace is a git repository.
- Permission to read the target workspace locally.

Do not send source, secrets, tokens, private repository contents, payment credentials, or environment variables to external services while using this skill.

## Instructions

1. Confirm the target repository path. Use the current workspace unless the user supplied a path.
2. Use `Read` only for local documentation or configuration files that explain the workspace; do not copy private source into the response.
3. Run `/agent-preflight` when the command is installed, or invoke the bundled scanner from a trusted Claude install root.
4. If the scanner is unavailable, apply the same manual decision rules: destructive commands, credential-writing automation, risky agent authority, git state, and high-risk shell or network install chains.
5. Classify the workspace as Green, Yellow, or Red.
6. Report the decision, evidence, and next safe action before making edits.
7. For Yellow results, ask for a checkpoint or narrower scope before broad edits.
8. For Red results, stop and request human review before changing files.

## Output

Return a short receipt in Markdown that is safe to paste into the local work log or pull request notes:

```markdown
## Agent Safety Preflight Receipt

- Decision: Green | Yellow | Red
- Repository: <path>
- Git state: clean | dirty | unavailable
- Risk buckets: <bullets>
- Evidence: <file/path markers>
- Next safe action: proceed | checkpoint | stop
```

## Error Handling

- If the scanner cannot be found from a trusted install root, say that the automated scanner did not run and use the manual rules.
- If git status is unavailable, classify the workspace as Yellow rather than Green.
- If a file cannot be decoded, scan the readable prefix with tolerant UTF-8 decoding and include a note if relevant evidence may be incomplete.
- If a destructive or credential-writing marker appears in an agent-controlled path, classify the workspace as Red and stop.
- If the workspace is too large for a full pass, inspect high-signal paths first: `.claude/`, `.cursor/`, `.github/`, shell scripts, JSON/YAML/TOML config, package manifests, and environment files.

## Examples

### Example 1: Clean repo before routine edits

User request: "Run a preflight before you update this README."

The skill runs the scanner, sees a clean git state and no high-risk automation markers, then returns Green with the repository path and evidence summary.

### Example 2: Agent hooks present

User request: "Check this repo before the agent refactor."

The skill detects agent hook configuration or broad tool permissions, returns Yellow, and recommends a checkpoint or narrower edit scope before continuing.

### Example 3: Destructive automation found

User request: "Start editing this generated-project repo."

The skill finds a destructive recursive delete pattern in an automation file, returns Red, and stops until a human reviews the workflow.

## Resources

- Command: `plugins/security/agent-safety-preflight/commands/agent-preflight.md`
- Scanner: `plugins/security/agent-safety-preflight/scripts/agent_preflight_lite.py`
- Decision-rule reference: `references/decision-rules.md`
- Public source workflow: https://github.com/el-zachariah/ai-agent-safety-starter-pack
- Claude Code plugin reference: https://code.claude.com/docs/en/plugins
