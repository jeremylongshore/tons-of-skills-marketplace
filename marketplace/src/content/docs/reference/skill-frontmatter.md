---
title: 'SKILL.md Frontmatter Reference'
description: 'Complete field-by-field reference for SKILL.md frontmatter, path variables, string substitutions, and dynamic context injection (DCI) syntax used in Claude Code plugin skills.'
section: 'reference'
order: 1
keywords:
  - "SKILL.md"
  - "frontmatter"
  - "yaml"
  - "schema"
  - "skills"
  - "allowed-tools"
  - "DCI"
  - "path variables"
  - "string substitutions"
officialLinks:
  - title: 'Claude Code Skills Documentation'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Plugins Overview'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'concepts/skills'
  - 'guides/write-a-skill'
  - 'reference/allowed-tools'
---

## Separate the native format from marketplace publication

The open [Agent Skills specification](https://agentskills.io/specification) requires `name` and `description` and defines a small optional field surface. Claude Code adds runtime-specific fields. This repository adds an eight-field marketplace contract. These are different distribution contracts; a file accepted here is not automatically accepted by every skill uploader.

The authoritative repository set is `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing required marketplace fields are errors. Optional native or repository fields do not replace them. `compatible-with` is a deprecated repository alias, not a substitute for `compatibility`.

[STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md), the schema changelog, and the pinned kernel name the owners. Kernel shadow evidence does not silently replace the authoritative Python validator.

## Complete marketplace skill example

This is a complete instruction file for `skills/configuration-review/SKILL.md`. The tool declarations narrow pre-approval but do not enforce the prose's read-only boundary by themselves; inherited permissions must also be reviewed.

```markdown
---
name: configuration-review
description: |
  Review a selected configuration file and produce an evidence-linked report.
  Use when the user asks to review configuration, inspect deployment settings,
  or check a configuration change. Trigger with "review this configuration".
allowed-tools: Read, Glob, Grep
version: 1.0.0
author: Example Maintainer
license: MIT
compatibility: Requires a local project and Claude Code file-reading tools
tags: [configuration, review]
argument-hint: '<existing-file>'
---

# Configuration Review

## Overview

Inspect one selected local configuration without changing it or claiming live service verification.

## Prerequisites

- An existing file explicitly selected by the user
- The relevant project conventions or current primary documentation

## Instructions

1. Treat `$ARGUMENTS` as an untrusted file selection, not shell code. Resolve it within the selected project; stop if it escapes that scope or is ambiguous.
2. Read the file and the applicable project instructions. Do not read unrelated credentials.
3. Compare each relevant setting with the cited owner documentation.
4. Report observed contradictions separately from questions that need runtime evidence.
5. Do not modify files, invoke a provider, or claim that a static review proves deployment safety.

## Output

Return a table with the setting, source line, evidence, and proposed correction. Mark unverified behavior explicitly.

## Error Handling

If the file or authority is unavailable, report the missing input and stop. Do not fabricate configuration or convert a failed check into success.

## Examples

Input: "Review config/example.json."

Output: A bounded report for that file, with exact lines and evidence; no edits or live operations.

## Resources

Use the selected project’s applicable instructions and the domain authority supplied for the review. The [native skill reference](https://code.claude.com/docs/en/skills) describes this instruction format; it does not certify the configuration being inspected. If the relevant domain source is missing or outdated, report that limitation instead of inventing a rule.
```

## Field guide

| Field                          | Role                                                                                                                 |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `name`                         | Kebab-case skill identity; align it with its directory                                                               |
| `description`                  | Actual capability and invocation context; do not promise deterministic activation from trigger text                  |
| `allowed-tools`                | Pre-approval during the invoking turn, not an exclusive capability list                                              |
| `version`, `author`, `license` | Marketplace tracking and distribution metadata                                                                       |
| `compatibility`                | Actual runtime requirements in prose                                                                                 |
| `tags`                         | Marketplace discovery metadata                                                                                       |
| `argument-hint`                | Optional invocation hint; not input validation                                                                       |
| `disable-model-invocation`     | Optional control over automatic model invocation                                                                     |
| `user-invocable`               | When false, blocks direct manual invocation; model invocation is controlled separately by `disable-model-invocation` |
| `context: fork`, `agent`       | Optional delegated execution context                                                                                 |
| `model`, `effort`              | Optional runtime tuning, subject to the installed runtime's supported values                                         |
| `disallowed-tools`             | Skill tool removal while active, distinct from pre-approval                                                          |
| `hooks`                        | Native lifecycle-hook configuration, not an invented `pre-tool-call` event                                           |

This table is a guide, not a complete second schema registry. Consult the current [native field table](https://code.claude.com/docs/en/skills) and repository validator before adopting an additional field. Model support and managed permission controls can vary by runtime and deployment.

## Tool semantics

`allowed-tools` accepts a string or array of tool names/rules. It grants pre-approval for the invoking turn; unlisted tools still follow the user's normal permission settings. `disallowed-tools` removes listed tools for that turn. Review the [tool reference](/docs/reference/allowed-tools) and managed settings before relying on either.

Agents use `tools` and `disallowedTools`; do not transfer those agent field names into skill frontmatter.

## Hook configuration

The following is a hook-field fragment, not a complete skill or a working guard script:

```yaml
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: '"${CLAUDE_SKILL_DIR}/scripts/check-input.sh"'
```

Supply and independently test the referenced script before using this fragment. Native hooks receive event JSON on stdin. For a blocking `PreToolUse` command hook, exit 2 blocks the tool; other failures have event- and configuration-specific behavior. A generic nonzero exit is not a universal refusal guarantee. Use the [hook reference](https://code.claude.com/docs/en/hooks) for the actual event, matcher, handler, timeout, and decision contracts.

## Paths and supporting files

Use relative Markdown links for supporting documents. For example, in a skill that actually ships both files:

```markdown
See [API reference](references/api.md) and [examples](references/examples.md).
```

These are illustrative paths, not links from this documentation page. Ensure the targets exist and remain within the skill's intended boundary.

Claude Code can substitute `${CLAUDE_SKILL_DIR}` in skill content and `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` for plugin content in documented contexts. Persistent plugin data is separate from the replaceable installation. Do not infer that every variable exists in the environment of every Bash tool call. Quote resolved paths when constructing shell commands, and consult [the plugin variable table](https://code.claude.com/docs/en/plugins-reference) instead of relying on unverified historical “available since” dates.

## Arguments

| Substitution            | Meaning                                               |
| ----------------------- | ----------------------------------------------------- |
| `$ARGUMENTS`            | Entire invocation argument string                     |
| `$ARGUMENTS[0]` or `$0` | First argument                                        |
| `$ARGUMENTS[1]` or `$1` | Second argument                                       |
| `${CLAUDE_SESSION_ID}`  | Session identifier in supported content substitutions |

Indexed arguments use shell-style quoting: an invocation with `"hello world" second` gives `hello world` to `$0` and `second` to `$1`. Do not mistake `$0` for the whole argument string. Validate values before using them as filenames, shell fragments, identifiers, or provider parameters.

## Dynamic context injection

The native syntax `!` followed by a backtick-wrapped shell command injects command output while the skill is rendered. It is preprocessing, not an ordinary model tool call after the body has been read. Review execution permissions, outbound access, output size, secret exposure, and failure behavior before adding it.

This fenced excerpt illustrates the syntax; it does not run as part of this page:

```markdown
!`git status --short`
```

Do not add injections to improve a static score. Prefer an explicit manual diagnostic when it avoids unexpected execution. A missing tool or failed command remains unavailable or failed evidence; suppressing stderr or echoing a fallback does not make it a successful check. Never modify state in an incidental environment probe.

## Validation

Run from the repository root with the actual file path:

```bash
python3 scripts/validate-skills-schema.py --standard --verbose plugins/category/my-plugin/skills/configuration-review/SKILL.md
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/skills/configuration-review/SKILL.md
```

`--standard` requests the upstream format floor; `--marketplace` requests the repository contract and rubric. Do not omit the flag when teaching the distinction: outside CI the Python CLI defaults to standard, while its CI environment can select marketplace behavior. A format/grade result is not a retained behavioral-evaluation receipt or a portable-host compatibility certification.
