---
name: windsurf-test-generation
description: 'Generate comprehensive test suites using Cascade. Activate when users
  mention

  "generate tests", "test coverage", "write unit tests", "create test suite",

  or "tdd assistance". Handles AI-powered test generation. Use when writing or running
  tests. Trigger with phrases like "windsurf test generation", "windsurf generation",
  "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*),Grep,Glob
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- testing
compatibility: Designed for Claude Code
---
# Windsurf Test Generation

## Overview

This skill enables AI-powered test generation for any codebase using Windsurf's Cascade. It analyzes function signatures, identifies edge cases, creates meaningful assertions, and generates mock data.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Testing framework installed (Jest, Vitest, pytest, etc.)
- Project with testable code (functions, classes, components)
- Code coverage tool configured (optional but recommended)
- Understanding of testing patterns and best practices

## Instructions

1. **Configure Testing Framework**
2. **Select Target Code**
3. **Generate Tests with Cascade**
4. **Add Custom Scenarios**
5. **Integrate into Workflow**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Test files with comprehensive coverage
- Mock data and fixture files
- Coverage report with metrics
- Test pattern documentation for team

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Test Generation Guide](https://docs.windsurf.ai/features/test-generation)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles)
