---
name: test-skill
description: |
  Test skill for E2E validation. Use when testing skill activation and tool
  permissions. Trigger with "run test skill" or "execute test".
allowed-tools: Read, Write, Bash(pnpm:*)
version: 1.0.0
license: MIT
author: Test Author <test@example.com>
compatibility: Works with model-agnostic agents that support Agent Skills frontmatter.
tags:
  - testing
  - e2e
---

# Test Skill

This is a minimal skill used for E2E testing of the Claude Code plugin system.

## Purpose

This skill validates:
- Skill loading from plugin directory
- Frontmatter parsing (YAML)
- Trigger phrase detection
- Tool permission validation
- Current marketplace schema compliance

## Prerequisites

- Run only inside the isolated E2E test directory.
- Use fixture data rather than production credentials or user files.

## Activation

This skill activates when you use phrases like:
- "run test skill"
- "execute test"
- "test skill activation"

## Allowed Tools

- **Read** - Read files for validation
- **Write** - Write test results
- **Bash** - Execute test commands

## Instructions

Use this skill only to perform the isolated fixture operations below.

### Test Operations

1. Read test files
2. Write test results
3. Execute validation commands

## Output

When activated, this skill should:
- Load successfully from the plugin
- Parse frontmatter correctly
- Match trigger phrases
- Respect tool permissions

## Examples

- `run test skill` activates the fixture.
- `execute test` exercises the alternate trigger phrase.

## Safety Justification

Write access creates disposable fixture output only. Scoped Bash access permits pnpm test commands only; it does not authorize arbitrary shell commands.

## Error Handling

If this skill fails to activate:
- Check plugin installation
- Verify SKILL.md frontmatter
- Validate allowed-tools format
- Ensure trigger phrases are correct

## Resources

- E2E Test Suite Documentation: `/tests/e2e/README.md`
- Plugin Structure: `/.claude-plugin/plugin.json`
