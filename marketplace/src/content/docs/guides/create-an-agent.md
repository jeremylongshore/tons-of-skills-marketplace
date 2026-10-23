---
title: 'How to Create a Claude Code Agent'
description: 'Guide to creating autonomous Claude Code agents. Learn the difference between agents and skills, write agent frontmatter with tools and disallowedTools, set maxTurns and effort, and test agent behavior.'
section: 'guides'
order: 3
keywords:
  - 'agent'
  - 'autonomous agent'
  - 'disallowedTools'
  - 'maxTurns'
  - 'capabilities'
  - 'sub-agent'
  - 'Claude Code agent'
  - 'agent development'
officialLinks:
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Anthropic Agents Reference'
    url: 'https://code.claude.com/docs/en/sub-agents'
relatedDocs:
  - 'concepts/agents'
  - 'reference/skill-frontmatter'
---

## Choose a delegated task

A subagent works in its own context and can perform a multi-step task before returning a result. Skills can also delegate through `context: fork`; skills are not limited to one response. A command or skill is often enough when a separate worker context adds no value.

Specify the task's input, scope, allowed actions, stopping condition, and output. A read-only report must not silently expand into editing, provider calls, or an unrelated audit.

## Tools are not denylist-only

Agents support a `tools` allowlist and `disallowedTools` removal list. Without an explicit allowlist, inherited capabilities can be broader than intended. Denying `Write` and `Edit` alone does not prevent a permitted shell, network tool, or MCP tool from changing state.

For a local configuration audit, prefer an explicit small tool set and no shell access. If the caller wants a changed-file review, the caller should supply that file scope; a read-only agent without Bash should not pretend it ran Git.

## Create a plugin agent

```bash
mkdir -p my-plugin/agents
```

Save this complete plugin-agent example as `agents/configuration-auditor.md`:

```markdown
---
name: configuration-auditor
description: Review selected configuration files and return a bounded report with source lines and cited authority; do not modify files or invoke services.
tools: Read, Glob, Grep
model: inherit
color: blue
version: 1.0.0
author: Example Maintainer
tags: [configuration, review]
disallowedTools: [Write, Edit, Bash]
skills: []
background: false
maxTurns: 10
---

# Configuration Auditor

Review only the files explicitly supplied by the caller. If no scope is supplied, report that missing input and stop.

## Process

1. Read the selected files and applicable project instructions.
2. Compare the settings with supplied or locally available primary authority.
3. Cite exact lines for contradictions. Separate unresolved questions from observed defects.
4. Return the bounded report; do not edit files, call a provider, or delegate new work.

## Output

For each finding, include the file, line, evidence, impact, and proposed correction. State which behavior was not tested. Do not claim security or deployment certification from static inspection.
```

The repository's agent gate requires the eight kernel-floor fields (`name`, `description`, `tools`, `model`, `color`, `version`, `author`, `tags`) plus `disallowedTools`, `skills`, and `background` for plugin agents. Standalone agents additionally require the repository's `hooks`, `mcpServers`, and `permissionMode` live set. Those component fields have different native applicability for plugin agents; do not blindly copy a standalone envelope into a plugin.

These are repository authoring requirements, not a claim that upstream Claude Code requires every field. [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md), the schema changelog, and the current validator name the exact contract.

## Field and tuning decisions

| Field             | Decision                                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `description`     | Describe the real task and delegation context; the old universal 20–200 character rule is not the current repository contract |
| `tools`           | List actual tools; include explicitly named MCP tools when the body uses them                                                 |
| `disallowedTools` | Remove tools using the agent's camelCase field; do not use the skill field name                                               |
| `model`           | Choose an installed-runtime-supported alias, `inherit`, or supported model identifier                                         |
| `maxTurns`        | Bound iteration and report incomplete work when the bound is reached                                                          |
| `effort`          | Optional runtime-supported reasoning setting, not a quality guarantee                                                         |
| `skills`          | Only the skills deliberately loaded for this worker                                                                           |
| `background`      | Deliberate foreground/background behavior, not an implicit activation priority                                                |

`capabilities`, `expertise_level`, and `activation_priority` are banned repository agent fields. Put actual expertise and process instructions in the body. They are not native controls that make an agent more capable or invoke it automatically.

Model names, effort values, memory/isolation features, permission modes, and hook support evolve. Consult [the current subagent reference](https://code.claude.com/docs/en/sub-agents) and installed runtime before adopting a tuning field; do not treat a short table here as a complete registry.

## Write useful instructions

A working agent contract should answer:

1. What exact files or task inputs may it inspect?
2. What authority supports its conclusions?
3. What actions are permitted, and which require a separate decision?
4. What ends the task, including missing inputs, errors, and iteration limits?
5. What evidence and uncertainties must be returned?

An output-format sketch is useful, but `[file]`, `[line]`, and role names in such a sketch are placeholders, not findings. Avoid canned APPROVE results when the worker lacks the evidence or authority to approve a change.

## Validate the authoring contract

From the repository root:

```bash
python3 scripts/validate-skills-schema.py --agents-only --verbose ./my-plugin/agents/configuration-auditor.md
```

Substitute the actual path. The agent gate is strict at every tier: merely adding `--standard` does not make banned fields or missing repository agent fields acceptable.

For development loading:

```bash
claude --plugin-dir ./my-plugin
```

Use a reviewed local plugin in an isolated session. Ask for a bounded audit and verify the actual result and side effects. The example does not require provider access or credentials.

## Meaningful checks

- Supply a small valid file and verify exact-line evidence.
- Omit the file scope and verify a missing-input report rather than an invented scope.
- Request a write or provider action and verify the task stays within the intended boundary.
- Check the actual runtime's exposed tools; prose promises alone do not enforce read-only behavior.
- Exercise the turn limit and verify incomplete work is reported honestly.
- If hooks are added later, test stdin JSON, event matching, exit behavior, timeouts, and cleanup independently.

Do not describe a full-access agent as safe merely because it has no explicit deny entries. Likewise, a successful static check does not prove runtime containment or a complete security review.

## Next steps

- [Build the enclosing plugin](/docs/guides/build-a-plugin)
- [Review skill frontmatter separately](/docs/reference/skill-frontmatter)
- [Submit with evidence](/docs/guides/publish-to-marketplace)
