---
name: windsurf-dependency-management
description: 'Analyze and update dependencies with vulnerability scanning. Activate
  when users mention

  "update dependencies", "security audit", "npm audit", "vulnerability scan",

  or "dependency updates". Handles dependency analysis and updates. Use when working
  with windsurf dependency management functionality. Trigger with phrases like "windsurf
  dependency management", "windsurf management", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*),Grep
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- security
- audit
compatibility: Designed for Claude Code
---
# Windsurf Dependency Management

## Overview

This skill enables comprehensive dependency management within Windsurf projects. Cascade analyzes your dependency tree, identifies security vulnerabilities, suggests safe updates, and helps plan migration paths for major version upgrades.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Package manager installed (npm, yarn, pnpm, pip)
- Project with package.json, requirements.txt, or equivalent
- Understanding of semantic versioning
- CI/CD pipeline for testing updates (recommended)

## Instructions

1. **Run Initial Audit**
2. **Analyze Update Paths**
3. **Plan Updates**
4. **Apply and Verify**
5. **Establish Monitoring**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Security audit report with findings
- Update plan with prioritized changes
- Compatibility matrix for version combinations
- Migration guides for breaking changes

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Dependency Management](https://docs.windsurf.ai/features/dependencies)
- [npm Audit Documentation](https://docs.npmjs.com/cli/audit)
- [Semantic Versioning Spec](https://semver.org/)
