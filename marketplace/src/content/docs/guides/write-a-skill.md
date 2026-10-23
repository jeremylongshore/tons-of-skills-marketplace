---
title: 'How to Write a Claude Code Skill'
description: 'Step-by-step guide to writing a SKILL.md file for Claude Code. Learn how to plan, structure, and test auto-activating skills with proper frontmatter, allowed-tools, dynamic context injection, and supporting files.'
section: 'guides'
order: 1
keywords:
  - 'skill'
  - 'SKILL.md'
  - 'auto-activating'
  - 'frontmatter'
  - 'allowed-tools'
  - 'dynamic context injection'
  - 'DCI'
  - 'Claude Code plugin development'
officialLinks:
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Anthropic Skills Reference'
    url: 'https://code.claude.com/docs/en/skills'
relatedDocs:
  - 'concepts/skills'
  - 'reference/skill-frontmatter'
  - 'reference/allowed-tools'
---

## Plan the operator outcome

A skill is an instruction file at `skills/<name>/SKILL.md`. Claude Code can load it when relevant or when a user invokes it; a skill can also fork into a delegated context. It is not inherently a single response, and a trigger phrase is not a guarantee that every runtime selects it.

Before authoring, decide:

1. What bounded task should it perform?
2. Which inputs are trusted, and which need validation?
3. What tools, credentials, files, or services are actually required?
4. What observable output distinguishes success, failure, and unavailable evidence?
5. Which behavior can be tested without personal state or live provider access?

Use the current [Skills catalog](/skills) rather than an undated total to discover comparable work.

## Create the structure

From an existing author-owned plugin root:

```bash
mkdir -p skills/configuration-review/references
```

Keep supporting documents inside the skill's directory unless a separately reviewed shared boundary is intended. Do not modify a pure external mirror locally; improvements belong upstream.

## Write the marketplace envelope and instructions

The marketplace requires eight fields: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. The open Agent Skills floor and native runtime extensions are separate; see [the frontmatter reference](/docs/reference/skill-frontmatter).

This complete example performs a bounded local review:

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

Descriptions should explain a real capability and relevant invocation context. Clear phrases help discoverability; padding a description or promising deterministic activation does not improve the task contract. Keep the body operational: prerequisites, instructions, outputs, failure handling, and examples must describe actual behavior.

## Choose tools deliberately

A pre-approval fragment might be:

```yaml
allowed-tools: Read, Glob, Grep, Bash(npm:*)
```

This pre-approves a command family; it does not block all other shell commands. Unlisted tools remain governed by user permissions. Use documented deny controls or tested guards when an actual restriction is required, and do not infer a sandbox from a short prefix. Agents use their own `tools` / `disallowedTools` fields.

Read the [tool reference](/docs/reference/allowed-tools) before granting file writes, network tools, shell interpreters, delegation, or another skill's permissions. Review scripts as executable code, including their dependency installation, process cleanup, and output paths.

## Add supporting material

Create real targets before linking them. This is a Markdown excerpt for a skill that supplies these documents:

```markdown
For API constraints, see [API reference](references/api.md).
For reviewed cases, see [examples](references/examples.md).
```

Use quoted runtime paths for a bundled script when a command is actually needed. Do not substitute a relative documentation link for an executable path or silently fetch mutable remote instructions at runtime.

## Keep executable examples honest

Label partial snippets and placeholders. A test template with `ComponentName` and assertions such as `getByRole('...')` is a sketch, not a passing suite. A complete example needs its imports, dependency contract, actual input, expected output, and meaningful error cases.

For generated React tests, for example, specify the real component's props, accessibility roles, asynchronous behavior, and observable state transitions. Do not claim coverage from render-only snapshots or silently skip a feature because its tests are inconvenient.

## Review preprocessing separately

Native dynamic context injection can execute shell commands before the model sees the rendered skill body. Avoid side effects, secret output, implicit downloads, and unbounded output. A fallback must report missing or failed evidence honestly rather than turn a required check into success. Do not add preprocessing simply for rubric points.

An explicit manual command is often clearer than an automatic environment probe. If injection is necessary, document and independently test the exact current runtime behavior and permissions.

## Validate and try the skill

From the repository root, substituting the real plugin directory:

```bash
python3 scripts/validate-skills-schema.py --standard --verbose plugins/category/my-plugin/skills/configuration-review/SKILL.md
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/skills/configuration-review/SKILL.md
```

For an isolated development session, load the plugin directory through the native CLI:

```bash
claude --plugin-dir ./plugins/category/my-plugin
```

The example path is not an existing marketplace identity. Review the plugin before loading it; a temporary session must not activate real provider credentials or unrelated hooks merely to test prose.

Test a successful selection, a missing file, an out-of-scope path, an unavailable authority, and a request outside the skill's purpose. Check the actual output and side effects, not only the numeric grade.

The current rubric bands are A 90–100, B 80–89, C 70–79, D 60–69, and F below 60. These describe the static rubric, not automatic publication, featured placement, legal compliance, or runtime certification. The required field set, severity rules, and publication authorities remain governed by [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md).

## Next steps

- [Build the surrounding plugin](/docs/guides/build-a-plugin)
- [Review frontmatter semantics](/docs/reference/skill-frontmatter)
- [Submit through the current contribution workflow](/docs/guides/publish-to-marketplace)
