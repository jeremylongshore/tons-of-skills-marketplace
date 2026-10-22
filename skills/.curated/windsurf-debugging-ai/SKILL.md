---
name: windsurf-debugging-ai
description: 'Execute use Cascade for intelligent debugging and error analysis. Activate
  when users mention

  "debug with ai", "error analysis", "cascade debug", "find bug",

  or "troubleshoot code". Handles AI-assisted debugging workflows. Use when debugging
  issues or troubleshooting. Trigger with phrases like "windsurf debugging ai", "windsurf
  ai", "windsurf".

  '
allowed-tools: Read,Grep,Glob,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- debugging
- workflow
compatibility: Designed for Claude Code
---
# Windsurf Debugging Ai

## Overview

This skill enables AI-assisted debugging within Windsurf. Cascade analyzes error messages, stack traces, and code context to identify root causes and suggest fixes.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Application with reproducible issues
- Debug configuration set up
- Error logs accessible
- Understanding of application architecture

## Instructions

1. **Capture Error Context**
2. **Analyze with Cascade**
3. **Investigate Root Cause**
4. **Apply Fix**
5. **Document for Prevention**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Root cause analysis
- Fix recommendations
- Debug session logs
- Prevention strategies

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Debugging Guide](https://docs.windsurf.ai/features/debugging)
- [AI-Assisted Debugging](https://docs.windsurf.ai/cascade/debugging)
- [Debug Configuration Reference](https://docs.windsurf.ai/reference/debug-config)
