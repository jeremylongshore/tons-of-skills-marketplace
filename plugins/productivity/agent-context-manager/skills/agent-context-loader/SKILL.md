---
name: agent-context-loader
description: 'Execute proactive auto-loading: automatically detects and loads agents.md
  files.

  Use when appropriate context detected. Trigger with relevant phrases based on skill
  purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(general:*), Bash(util:*)
version: 1.24.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- productivity
- agent-context
compatibility: Designed for Claude Code
---
# Agent Context Loader

## Overview

Automatic discovery and loading of `AGENTS.md` files across project hierarchies for AI coding agents. This skill scans the current workspace and its parent directories to locate agent instruction files, then surfaces their contents so the active agent session has full operational context.

## Prerequisites

- A project workspace containing one or more `AGENTS.md` files at any directory depth
- Read and Glob permissions to traverse the directory tree
- Grep access for searching file contents when multiple candidates exist

## Instructions

1. Scan the current working directory and all ancestor directories (up to the filesystem root or repository root) for files named `AGENTS.md` or `agents.md`.
2. Search subdirectories of the current workspace for additional `AGENTS.md` files that may apply to sub-projects or modules.
3. Determine load order: files closer to the repository root load first (global context), files in deeper directories load later (override or supplement).
4. Read each discovered `AGENTS.md` file and extract its instruction blocks, workflow definitions, and constraint declarations.
5. Merge instructions into a unified context, noting any conflicts between levels (e.g., a subdirectory agent overriding a root-level rule).
6. Present the loaded context as a structured summary: source file path, instruction count, and any detected conflicts.
7. Cache the discovery results for the current session to avoid redundant filesystem scans on subsequent activations.

## Output

- Ordered list of discovered `AGENTS.md` file paths with their directory depth
- Merged instruction set combining all discovered agent contexts
- Conflict report highlighting any contradictory directives between levels
- Session cache status indicating whether results are fresh or reused

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No `AGENTS.md` found | Workspace has no agent instruction files | Confirm the correct working directory; create an `AGENTS.md` at the project root if needed |
| Permission denied on directory traversal | Restricted parent directories above the workspace | Limit scan depth to the repository root (detected via `.git/` presence) |
| Circular symlink detected | Symlinked directories create an infinite traversal loop | Skip symlinked directories during the scan; log a warning with the symlink path |
| Conflicting instructions across levels | A subdirectory `AGENTS.md` contradicts the root-level file | Flag the conflict in the output; apply the more specific (deeper) instruction by default |
| File encoding error | `AGENTS.md` uses a non-UTF-8 encoding | Attempt latin-1 fallback; report the file path and encoding issue |

## Examples

**Example 1: Monorepo with per-package agent instructions**

- Structure: Root `AGENTS.md` sets global conventions; `packages/api/AGENTS.md` adds API-specific tooling rules.
- Result: Both files loaded in order. The API-specific rules supplement the global context without conflict.

**Example 2: Nested workspace with conflicting commit policies**

- Structure: Root `AGENTS.md` says "always sign commits"; `services/legacy/AGENTS.md` says "skip commit signing."
- Result: Conflict detected and reported. The deeper (legacy) directive is applied with a warning noting the override.

**Example 3: First-time setup with no agent files**

- Structure: A freshly cloned repository with no `AGENTS.md` anywhere.
- Result: Scan completes with zero files found. Output includes a suggestion to create `AGENTS.md` at the repository root with a minimal template.

## Resources

- AGENTS.md open specification: https://agents.md/
- Monorepo workspace patterns for agent configuration: https://code.claude.com/docs
- File discovery best practices for hierarchical configuration loading
