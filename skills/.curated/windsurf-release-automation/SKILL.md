---
name: windsurf-release-automation
description: 'Execute automate release processes with semantic versioning. Activate
  when users mention

  "release automation", "version bump", "changelog generation", "semantic release",

  or "publish release". Handles release engineering automation. Use when working with
  windsurf release automation functionality. Trigger with phrases like "windsurf release
  automation", "windsurf automation", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- windsurf-release
compatibility: Designed for Claude Code
---
# Windsurf Release Automation

## Overview

This skill enables automated release workflows within Windsurf using Cascade AI. It analyzes commits to determine semantic version bumps, generates comprehensive changelogs, manages Git tags, and publishes releases.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Git repository with commit history
- Conventional commits or consistent commit format
- npm/yarn/pnpm for JavaScript projects (or equivalent)
- CI/CD pipeline for automated publishing (optional)

## Instructions

1. **Configure Version Strategy**
2. **Set Up Automation**
3. **Prepare Release**
4. **Execute Release**
5. **Post-Release Tasks**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Updated version in package.json
- Generated CHANGELOG.md entry
- Git tag for release version
- Published package to registry
- Release notes for distribution

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Release Automation](https://docs.windsurf.ai/features/release)
- [Semantic Release Documentation](https://semantic-release.gitbook.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
