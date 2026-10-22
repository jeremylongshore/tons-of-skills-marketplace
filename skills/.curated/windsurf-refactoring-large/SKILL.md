---
name: windsurf-refactoring-large
description: 'Manage large-scale refactoring with Cascade coordination. Activate when
  users mention

  "large refactoring", "codebase migration", "architecture refactor", "major refactoring",

  or "system-wide changes". Handles complex refactoring operations. Use when working
  with windsurf refactoring large functionality. Trigger with phrases like "windsurf
  refactoring large", "windsurf large", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*),Grep,Glob
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- migration
- scaling
compatibility: Designed for Claude Code
---
# Windsurf Refactoring Large

## Overview

This skill enables large-scale refactoring operations that span hundreds or thousands of files. It provides phased execution with checkpoints, comprehensive rollback capabilities, and AI-assisted planning.

## Prerequisites

- Windsurf IDE with Enterprise or Pro subscription
- Active Cascade AI connection
- Git repository with clean working state
- Comprehensive test suite for validation
- Backup strategy for critical code paths
- Team coordination for multi-developer codebases

## Instructions

1. **Analyze Scope**
2. **Create Plan**
3. **Prepare Environment**
4. **Execute with Cascade**
5. **Verify Completion**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Refactored codebase with all patterns migrated
- Phase completion reports with metrics
- Before/after performance comparison
- Updated documentation and API references
- Archived rollback artifacts (kept 30 days)

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Large Refactoring Guide](https://docs.windsurf.ai/features/large-refactoring)
- [Phased Execution Best Practices](https://docs.windsurf.ai/best-practices/phased-execution)
- [Rollback and Recovery](https://docs.windsurf.ai/features/rollback)
