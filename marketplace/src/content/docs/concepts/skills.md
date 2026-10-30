---
title: 'Understanding Agent Skills (SKILL.md)'
description: 'How skill discovery, invocation, eight-field marketplace metadata, supporting resources, permissions, and static evidence fit together.'
section: 'concepts'
order: 2
keywords:
  - 'SKILL.md'
  - 'Claude Code skills'
  - 'agent skills'
  - 'auto-activating skills'
  - 'allowed-tools'
  - 'dynamic context injection'
  - 'skill frontmatter'
  - 'Claude Code plugin skills'
officialLinks:
  - title: 'Claude Code Skills Documentation'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'AgentSkills.io Specification'
    url: 'https://agentskills.io/specification'
  - title: 'Claude Code Plugins Overview'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'concepts/plugins'
  - 'concepts/agents'
  - 'concepts/commands-and-hooks'
  - 'reference/skill-frontmatter'
---

## Overview

A skill is a directory containing `SKILL.md` and optional supporting resources. Claude initially discovers its metadata; the full instructions load when the skill is invoked. A useful description explains when the skill applies, rather than promising that every installed body is always in context.

Skills support manual slash invocation as well as model invocation. Plugin skills use names such as `/example-plugin:review-diff`. `argument-hint` helps users understand arguments but is not required for manual invocation.

## Marketplace-required frontmatter

Native Claude's permissive format and the Agent Skills open standard are separate from this repository's marketplace overlay. The repository requires **all eight** fields below; missing fields are errors at marketplace tier.

| Field           | Purpose                                       |
| --------------- | --------------------------------------------- |
| `name`          | Stable skill identity                         |
| `description`   | When to use the skill and what it does        |
| `allowed-tools` | Tool permission preapproval for an invocation |
| `version`       | Skill version tracking                        |
| `author`        | Authorship tracking                           |
| `license`       | License identification                        |
| `compatibility` | Environment and runtime prerequisites         |
| `tags`          | Classification metadata                       |

This example includes a nested output fence, so the outer Markdown fence is longer:

````markdown
---
name: review-diff
description: Review a supplied Git diff for correctness and missing tests without modifying files.
allowed-tools: Read, Grep, Glob
version: 1.0.0
author: Example Team
license: MIT
compatibility: Claude Code with access to the local repository and a user-supplied diff.
tags: [review, testing]
---

# Review Diff

## Overview

Read the supplied diff and relevant source. Do not run project scripts.

## Prerequisites

The user supplies the diff and identifies the repository to inspect.

## Instructions

1. Identify changed behavior and its callers.
2. Check failure handling and test coverage in the available source.
3. Report concrete findings with file locations and remaining uncertainty.

## Output

```text
Finding: file path — risk and suggested test
Uncertainty: behavior requiring execution
```

## Error Handling

If the diff or source is unavailable, request that input. Do not invent results.

## Examples

Input: a supplied diff changing an error handler.
Output: a located failure-path concern and a proposed test, if supported.

## Resources

Use the user-supplied diff and the relevant local source and tests identified
for this review. The diff establishes the changed lines; source and tests
establish caller behavior and existing coverage. If those inputs are missing,
report the gap rather than fetching unrelated code or inventing evidence.
````

The identity and output are illustrative, not evidence that a deployed skill passed behavioral evaluation.

## Permissions and invocation

`allowed-tools` is **preapproval**, not an exclusive allowlist of every tool Claude can call. Unlisted tools remain subject to normal permission rules. Use the actual harness permission controls when you need restrictions.

For Bash preapproval, use separate supported rules, for example `Bash(git diff *)` and `Bash(git status *)`. Do not combine unrelated subrules inside one `Bash(...)` expression, and do not preapprove package installers just to lint source.

`user-invocable: false` blocks direct user invocation but does not itself block Claude's Skill access. `disable-model-invocation: true` controls model invocation. Setting both restrictive values can intentionally disable both routes; it is not a schema change made by this documentation.

`effort` is supported for skills as well as agents. Current values are `low`, `medium`, `high`, `xhigh`, and `max`, subject to model support; omitted effort inherits the applicable setting. Other optional fields, including `context`, `agent`, `arguments`, and `paths`, must follow the current native reference and unchanged local schema.

## Supporting references

Keep detailed material beside the skill and link to it explicitly:

```text
review-diff/
├── SKILL.md
└── references/
    └── api-reference.md
```

After creating the actual referenced file, use a same-skill relative link such as `[API reference](references/api-reference.md)`. A plain label without a Markdown href is not a navigable reference. Keep links within the skill's supported directory boundary.

Progressive disclosure lets the main file describe the workflow while linked files hold details. It is not a blanket instruction to make the main file long. A 500-word example or score component is not a new marketplace acceptance floor.

## Dynamic context and paths

Claude supports documented substitutions and dynamic command preprocessing. Treat preprocessing as executable behavior: permission rules apply, and commands can read files, install packages, or reach a network if permitted. Do not hide installers or credential probes in a body that users expect to be passive documentation.

Use `${CLAUDE_PLUGIN_ROOT}` for plugin execution paths where supported, rather than converting runtime paths into documentation-relative links. Follow the current [plugin reference](https://code.claude.com/docs/en/plugins-reference) for persistent plugin data; a data directory is not a backup, retention, or confidentiality guarantee.

If a skill declares hooks, use the real native hook schema and event names such as `PreToolUse` and `PostToolUse`. The labels `pre-tool-call` and `post-tool-call` are not substitutes for those event keys.

## Quality and validation

The static rubric has five pillars: progressive disclosure (30), ease of use (25), utility (20), specification compliance (15), and writing style (10), with modifiers. Letter thresholds are A ≥90, B ≥80, C ≥70, D ≥60, and F below 60. Stub classification is separate; do not claim every stub flag directly changes the score.

Static scoring does not prove production readiness. Keep the static production gate and optional same-source behavioral evidence distinct. See [grading](/grading) and the repository's canonical standards for their authority.

```bash
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/review-diff
```

For a deliberate native-floor comparison, use `--standard` explicitly. Do not weaken the marketplace overlay to make an example pass.
