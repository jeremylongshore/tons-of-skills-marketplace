---
name: windsurf-performance-profiling
description: 'Profile and optimize code with AI-assisted analysis. Activate when users
  mention

  "performance profiling", "optimize performance", "bottleneck analysis", "profiling",

  or "performance tuning". Handles performance analysis and optimization. Use when
  working with windsurf performance profiling functionality. Trigger with phrases
  like "windsurf performance profiling", "windsurf profiling", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*),Grep
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- performance
compatibility: Designed for Claude Code
---
# Windsurf Performance Profiling

## Overview

This skill enables AI-assisted performance profiling within Windsurf. Cascade analyzes profiling data to identify bottlenecks, suggest optimizations, and predict impact of changes.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Profiling tools installed (Chrome DevTools, node --prof, py-spy, etc.)
- Application with performance concerns
- Baseline metrics established
- Understanding of performance targets

## Instructions

1. **Establish Baseline**
2. **Collect Profile Data**
3. **Analyze with Cascade**
4. **Implement Optimizations**
5. **Document and Monitor**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Profiling data and analysis
- Bottleneck identification reports
- Optimization recommendations
- Before/after comparison metrics

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Performance Guide](https://docs.windsurf.ai/features/performance)
- [Profiling Best Practices](https://docs.windsurf.ai/guides/profiling)
- [Optimization Patterns](https://docs.windsurf.ai/guides/optimization)
