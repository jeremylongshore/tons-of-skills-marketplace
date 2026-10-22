---
name: windsurf-workspace-setup
description: 'Initialize Windsurf workspace with project-specific AI rules. Activate
  when users mention

  "create windsurfrules", "setup workspace", "configure project ai", "initialize windsurf
  workspace",

  or "migrate to windsurf". Handles workspace configuration and team standardization.
  Use when working with windsurf workspace setup functionality. Trigger with phrases
  like "windsurf workspace setup", "windsurf setup", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- migration
compatibility: Designed for Claude Code
---
# Windsurf Workspace Setup

## Overview

This skill enables rapid workspace setup for Windsurf projects. It covers creating .windsurfrules for AI behavior, configuring editor settings, establishing team conventions, and setting up multi-root workspaces.

## Prerequisites

- Windsurf IDE installed
- Project repository cloned
- Understanding of project architecture
- Team conventions documented
- Admin access for team-wide settings (optional)

## Instructions

1. **Create .windsurfrules**
2. **Configure Editor Settings**
3. **Set Up Extensions**
4. **Configure Cross-Editor Consistency**
5. **Establish Team Standards**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Configured .windsurfrules file
- Editor settings.json
- Extension recommendations
- Cross-editor configuration files
- Workspace configuration for monorepos

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Workspace Guide](https://docs.windsurf.ai/features/workspace)
- [.windsurfrules Reference](https://docs.windsurf.ai/reference/windsurfrules)
- [Multi-Root Workspaces](https://docs.windsurf.ai/features/multi-root)
