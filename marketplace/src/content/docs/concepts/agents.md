---
title: 'Claude Code Agents and Subagents'
description: 'How Claude Code plugin agents use delegated context and tool controls, and how native behavior differs from this marketplace’s agent contract.'
section: 'concepts'
order: 3
keywords:
  - 'Claude Code agents'
  - 'subagents'
  - 'agent definition'
  - 'disallowedTools'
  - 'agent vs skill'
  - 'multi-agent'
  - 'autonomous agent'
  - 'agent frontmatter'
officialLinks:
  - title: 'Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Claude Code Plugins Overview'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'concepts/plugins'
  - 'concepts/skills'
  - 'concepts/commands-and-hooks'
---

## Overview

An agent is a delegated worker with its own context and instructions. A plugin can ship agent definitions in `agents/*.md`; Claude can delegate work to them using the current **Agent** tool. Older material may call the delegation tool `Task`.

Use an agent when a task benefits from an independent context or a specialist tool set. Use a [skill](/docs/concepts/skills/) when you want reusable instructions in the current conversation, or a skill that explicitly forks into a subagent. Neither artifact makes an unsafe command safe.

## Native behavior and this marketplace's contract

The [native subagent reference](https://code.claude.com/docs/en/sub-agents) requires `name` and `description`. This repository deliberately applies a stricter agent contract. Its eight required fields are `name`, `description`, `tools`, `model`, `color`, `version`, `author`, and `tags`.

Plugin agents also carry `disallowedTools`, `skills`, and `background` in the repository's live shape. Standalone agent definitions have additional requirements. Plugin agents must not declare the standalone-only `hooks`, `mcpServers`, or `permissionMode` fields. Check the current validator rather than copying a standalone definition into a plugin.

The following is a plugin-agent frontmatter example, followed by its instructions:

```markdown
---
name: diff-reviewer
description: Review a supplied Git diff for correctness and missing tests without modifying files.
tools: Read, Grep, Glob
disallowedTools: []
skills: []
background: false
model: inherit
color: blue
version: 1.0.0
author: Example Team
tags: [review, testing]
---

# Diff Reviewer

## Instructions

Read the supplied diff and the relevant local source files. Report concrete
correctness risks with file locations and suggested tests. Do not claim to have
executed tests or verified a provider when you have only read source.

## Output

Return findings ordered by impact, followed by remaining uncertainties.
```

The example uses an illustrative author identity. It is not a claim that a named reviewer is installed or that its output has been behaviorally evaluated.

## Tool controls

An agent's `tools` field is an allowlist. `disallowedTools` is a denylist; both are supported. Select only the tools the task needs. The example omits Bash and MCP tools, but that is not a general network-isolation guarantee: other enabled tools, harness permissions, and integrations determine actual capabilities.

A skill's `allowed-tools` has different semantics: it preapproves listed tools for that skill invocation. It does **not** remove all unlisted tools from Claude's available pool. Permission rules still apply. Do not use that field as a security sandbox.

## Model and optional tuning

Use a model supported by the current harness and repository contract. `inherit` follows the surrounding session. `effort` is not agent-only: skills support it too. The current documented values are `low`, `medium`, `high`, `xhigh`, and `max`, with availability dependent on the model. When omitted, effort inherits the applicable setting; do not assume a universal `medium` default.

Optional tuning such as `maxTurns`, `memory`, and `isolation` must follow the current native reference and local validator. The repository's agent authoring guidance separates live fields from optional upgrade levers. Do not add `capabilities`, `expertise_level`, or `activation_priority`: those are not supported runtime controls and the local validator rejects them.

## Delegation and verification

Write a description that tells Claude when delegation is useful and what the agent will return. A universal 20–200-character native description constraint is not established by the subagent reference; consult the local validator for repository-specific checks.

Ask for a bounded task, such as reviewing an already supplied diff. Inspect the returned findings and any tool evidence. A confident answer is not proof that tests ran, files changed, or a remote service accepted a request.

For development, load the containing plugin explicitly:

```bash
claude --plugin-dir /absolute/path/to/review-plugin
```

Then ask Claude to delegate the supplied diff review. This is an instruction example, not a recorded execution receipt. Review current permissions before allowing additional tools.

## Validate before submission

From a repository checkout with its documented prerequisites installed:

```bash
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/review-plugin
```

Existing templates are starting material, not proof of compliance with the current agent contract. Inspect their fields and run the validator. See [plugins](/docs/concepts/plugins/) for the manifest and [the official subagent reference](https://code.claude.com/docs/en/sub-agents) for platform behavior.
