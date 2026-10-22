---
name: windsurf-linting-config
description: 'Configure and enforce code quality with AI-assisted linting. Activate
  when users mention

  "configure linting", "eslint setup", "code quality rules", "linting configuration",

  or "code standards". Handles linting tool configuration. Use when configuring systems
  or services. Trigger with phrases like "windsurf linting config", "windsurf config",
  "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- windsurf-linting
compatibility: Designed for Claude Code
---
# Windsurf Linting Config

## Overview

This skill enables comprehensive linting configuration within Windsurf. Cascade assists with ESLint, Prettier, Stylelint, and other linting tool setup, helping resolve configuration conflicts, suggesting rules based on project patterns, and automating code quality enforcement.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Node.js for JavaScript/TypeScript projects
- Package manager (npm, yarn, pnpm)
- Understanding of code style preferences
- Team agreement on quality standards

## Instructions

1. **Choose Base Configuration**
2. **Configure Rules**
3. **Set Up Prettier Integration**
4. **Add Pre-Commit Hooks**
5. **Integrate with CI**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Configured .eslintrc.js
- Prettier configuration
- Pre-commit hooks
- CI integration

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Linting Guide](https://docs.windsurf.ai/features/linting)
- [ESLint Documentation](https://eslint.org/docs/latest/)
- [Prettier Integration](https://prettier.io/docs/en/integrating-with-linters.html)
