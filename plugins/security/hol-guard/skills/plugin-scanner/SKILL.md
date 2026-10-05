---
name: plugin-scanner
description: Scan AI agent skills, plugins, MCP servers, and agent tooling for prompt injection, unsafe commands, secret exposure, and supply-chain risks before installing or trusting them. Use when evaluating agent ecosystem content before installation, publication, or use. Trigger with "scan this skill", "check this MCP server", "audit this agent plugin", or "verify this AI tool".
allowed-tools: "Bash(command -v plugin-scanner) Bash(pipx install plugin-scanner==3.0.123) Bash(plugin-scanner scan:*) Bash(plugin-scanner lint:*) Bash(plugin-scanner verify:*)"
version: 0.1.0
author: Hashgraph Online
license: Apache-2.0
compatibility: Requires a local Python CLI environment with pipx for optional installation; scans local agent skills, plugins, MCP servers, packages, and repositories without executing the target.
tags: [security, ai-agents, supply-chain, prompt-injection, mcp]
---

# Plugin Scanner

## Overview

Use HOL's local `plugin-scanner` when a user asks to inspect an AI agent skill, plugin, MCP server, agent package, or repository before installation or use. The scanner is shipped by the open-source `plugin-scanner` Python distribution. It is built from the same HOL Guard source repository, but it is intentionally packaged separately from the `hol-guard` runtime CLI.

Scanning runs locally and does not require Guard Cloud. Treat scanner findings as evidence about the covered checks, not as a guarantee that a target is safe.

## Prerequisites

- A local path or repository the user has chosen to inspect.
- `pipx` only when `plugin-scanner` is not already installed and the user approves installation.
- Do not execute the target repository, its install scripts, package lifecycle hooks, or arbitrary shell commands to prepare a scan.
- Never read `.env` files, credential stores, private keys, or unrelated user secrets.

## Instructions

1. **Check for the scanner.** Run the read-only availability check:

   ```bash
   command -v plugin-scanner
   ```

   If it is unavailable, explain that `plugin-scanner` is a separate open-source CLI distribution from the HOL Guard repository. Install only after the user explicitly approves setup, using the exact reviewed package version:

   ```bash
   pipx install plugin-scanner==3.0.123
   ```

   Do not assume an existing `hol-guard` installation also provides the scanner command. If `pipx` is unavailable, point the user to the plugin-scanner installation instructions rather than silently changing their Python environment.

2. **Scan the target without executing it.** For a repository or directory:

   ```bash
   plugin-scanner scan PATH --format markdown
   ```

   For machine-readable results:

   ```bash
   plugin-scanner scan PATH --format json
   ```

   For Agent Skill or plugin structure validation:

   ```bash
   plugin-scanner lint PATH
   plugin-scanner verify PATH
   ```

   Use the narrowest local target path that contains the material the user asked to inspect.

3. **Interpret findings.** Identify the highest-severity result, the concrete files or rules involved, and whether the scanner found prompt-injection, secret/exfiltration, command-execution, dependency/install, or MCP-specific risks. Recommend the smallest next action supported by the evidence.

## Output

Return a concise result containing:

- the local target that was scanned;
- whether `plugin-scanner` was already available or installed with explicit user approval;
- the command and output format used;
- the highest-severity finding and concrete files or rule identifiers involved;
- the relevant risk category or categories;
- the recommended next action.

Do not claim a target is safe solely because no finding was returned. Say that no covered issue was detected by the current scan.

## Error Handling

If `plugin-scanner` is missing, stop before scan commands and offer the pinned `pipx` installation only when installation is within the user's request. If `pipx` is unavailable, recommend an isolated Python CLI installation approach instead of silently changing the system Python environment.

If `scan`, `lint`, or `verify` fails, preserve the command output needed for diagnosis. Do not execute the target or weaken scanner checks to force a pass. If the target path is ambiguous, ask the user to identify the intended local artifact rather than scanning unrelated directories.

## Examples

**Scan a skill before installation**

Input: `scan this skill before I install it`

Workflow:

```bash
command -v plugin-scanner
plugin-scanner scan PATH --format markdown
```

Output: report the highest-severity covered finding, affected files or rules, and the next action.

**Validate an Agent Skill or plugin structure**

Input: `verify this AI tool`

Workflow:

```bash
plugin-scanner lint PATH
plugin-scanner verify PATH
```

Output: report validation failures without executing the target.

**Produce machine-readable scan evidence**

Input: `scan this plugin and return structured results`

Workflow:

```bash
plugin-scanner scan PATH --format json
```

Output: summarize the JSON result while preserving concrete rule identifiers and severity.

## Resources

- Plugin Scanner source: https://github.com/hashgraph-online/hol-guard
- Plugin Scanner package: https://pypi.org/project/plugin-scanner/
- Distribution companion: https://github.com/hashgraph-online/hol-guard-plugin
