---
title: "Your First Agent Skill"
description: "Learn how SKILL.md files work in Claude Code plugins, then build a production-quality agent skill from scratch. Covers frontmatter schema, body structure, testing, and iteration."
section: "getting-started"
order: 3
keywords: ["Claude Code skills", "SKILL.md", "agent skills", "write a skill", "Claude Code skill tutorial", "skill frontmatter", "auto-activating skills"]
officialLinks:
  - title: "Claude Code Skills Documentation"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Plugin Structure"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "getting-started/first-plugin"
  - "concepts/skills"
  - "guides/write-a-skill"
---

## Overview

Skills are the core building blocks of Claude Code plugins. A skill is a single markdown file named `SKILL.md` that tells Claude *how* to perform a specific task -- code review, database migration, security scanning, or anything else you can express in structured instructions. When Claude detects that your request matches a skill's trigger conditions, it loads the skill automatically and follows its methodology.

This guide explains the anatomy of a SKILL.md file, walks you through building one from scratch, and shows how to test and refine it until it performs reliably.

## What is a SKILL.md file

A SKILL.md file lives inside a plugin at `skills/<skill-name>/SKILL.md`. It contains two parts:

1. **YAML frontmatter** -- metadata that tells Claude Code when and how to load the skill.
2. **Markdown body** -- the actual instructions Claude follows when the skill activates.

Here is a minimal example:

```markdown
---
name: quick-lint
description: |
  Run a fast lint check on the current file. Use when the user asks
  to lint, check style, or fix formatting issues.
allowed-tools: Read, Bash(npx:eslint)
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
---

## Overview

You are a code linting specialist. When activated, run ESLint on the
target file and report results in a structured format.

## Steps

1. Identify the file to lint from the user's request.
2. Run `npx eslint <file> --format stylish` using the Bash tool.
3. Parse the output and summarize findings.
4. If there are auto-fixable issues, offer to run `npx eslint <file> --fix`.
```

When a user says "lint this file" or "check the formatting," Claude matches those phrases against the skill's `description` field and loads the instructions.

## Frontmatter schema

Every SKILL.md starts with a YAML frontmatter block delimited by `---`. The following fields are supported.

### Required fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique identifier for the skill (kebab-case) |
| `description` | string | When to use this skill. Include trigger phrases that Claude matches against. |
| `allowed-tools` | string | Comma-separated list of tools the skill can use |
| `version` | string | Semantic version (e.g., `1.0.0`) |
| `author` | string | Author name and optional email |
| `license` | string | SPDX license identifier (e.g., `MIT`, `Apache-2.0`) |

### Optional fields

| Field | Type | Description |
|---|---|---|
| `model` | string | Override the LLM model (`sonnet`, `haiku`, `opus`) |
| `context` | string | Set to `fork` to run in a subagent context |
| `agent` | string | Subagent type (e.g., `Explore`) |
| `user-invocable` | boolean | Set to `false` to hide from the `/` menu |
| `argument-hint` | string | Autocomplete hint shown in the `/` menu |
| `hooks` | object | Lifecycle hooks (e.g., `pre-tool-call`) |
| `compatibility` | string | Environment requirements (e.g., `Node.js >= 18`) |
| `compatible-with` | string | Platform compatibility (`claude-code`, `cursor`) |
| `tags` | array | Discovery tags for search and categorization |

### The `description` field matters most

The `description` is the single most important field. Claude uses it to decide whether to activate the skill. Write it as a natural-language explanation of *when* the skill should fire, including specific trigger phrases:

```yaml
description: |
  Perform a security audit on JavaScript or TypeScript code. Use when the
  user asks to check for vulnerabilities, audit security, scan for XSS,
  or review authentication logic.
```

Poor descriptions that are too vague ("helps with code") or too narrow ("only for React useState hooks") cause skills to either fire too often or never fire at all.

### The `allowed-tools` field

This field is a whitelist of the tools Claude is permitted to use when the skill is active. Valid tools:

```
Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch,
Task, TodoWrite, NotebookEdit, AskUserQuestion, Skill
```

You can scope `Bash` to specific commands for tighter security:

```yaml
allowed-tools: Read, Edit, Bash(npm:*, npx:*, git:status)
```

This allows the skill to run any `npm` or `npx` command and `git status`, but nothing else.

## Markdown body structure

The body after the frontmatter closing `---` is the instruction set Claude follows. Use standard markdown with clear section headings.

### Recommended sections

A well-structured skill body includes these sections:

```markdown
## Overview
What this skill does and its core methodology.

## Steps
Numbered step-by-step procedure Claude follows.

## Output
The format and structure of the skill's output.

## Constraints
Boundaries, edge cases, and things to avoid.

## Examples
Concrete input/output examples that calibrate Claude's behavior.
```

You do not need every section in every skill. A simple linter skill might only need Overview and Steps. A complex security auditor benefits from all five.

### Writing effective instructions

Skills are prompt engineering. The same principles that make a good system prompt make a good skill body:

- **Be specific.** "Review the code" is weak. "Check for SQL injection, XSS, CSRF, insecure deserialization, and broken authentication" is strong.
- **Use numbered steps.** Claude follows numbered procedures more reliably than prose paragraphs.
- **Show the output format.** If you want structured output, include a template or example.
- **Set boundaries.** Tell Claude what *not* to do. "Do not modify files unless explicitly asked" prevents unwanted side effects.

### Referencing supporting files

Skills can reference other markdown files in the same skill directory using relative links:

```markdown
For the complete API reference, see API docs.
For usage examples, see examples.
```

Claude follows these links using the `Read` tool when it needs the referenced content. This keeps your main SKILL.md focused while allowing deep-dive documentation in supporting files.

For bash commands or dynamic context injection, use the `${CLAUDE_SKILL_DIR}` variable to reference the skill's directory:

```markdown
!`cat ${CLAUDE_SKILL_DIR}/templates/report.md`
```

## Build a skill from scratch

Let us build a practical skill: a code review assistant that evaluates pull request diffs against a quality checklist.

### Step 1: Create the directory structure

Inside your plugin directory, create the skill folder:

```bash
mkdir -p skills/pr-review
```

### Step 2: Write the SKILL.md

Create `skills/pr-review/SKILL.md`:

```markdown
---
name: pr-review
description: |
  Review code changes for a pull request. Use when the user asks to
  review a PR, check a diff, evaluate code changes, or assess code
  quality before merging.
allowed-tools: Read, Bash(git:*), Grep, Glob
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
tags: [code-review, pull-request, quality]
---

## Overview

You are an expert code reviewer. When activated, analyze the current
git diff or a specified PR and evaluate changes against a structured
quality checklist. Provide actionable, specific feedback -- not
generic advice.

## Steps

1. Determine the scope of the review:
   - If the user specifies a branch or PR number, use
     `git diff main...<branch>` to get the diff.
   - If no branch is specified, use `git diff --staged` for staged
     changes or `git diff` for unstaged changes.

2. Read the diff output and identify all changed files.

3. For each changed file, evaluate against this checklist:
   - **Correctness**: Does the logic do what it claims?
   - **Error handling**: Are failure cases covered?
   - **Security**: Any hardcoded secrets, SQL injection, or XSS risks?
   - **Performance**: Any O(n^2) loops, missing indexes, or redundant I/O?
   - **Readability**: Are names clear? Is complexity justified?
   - **Tests**: Are new code paths covered by tests?

4. Search for related test files using Glob and Grep to verify
   test coverage for changed functions.

5. Produce a structured review report.

## Output

Format the review as follows:

### Summary
One paragraph overview of the changes and overall quality assessment.

### Findings

For each issue found:

**[SEVERITY] File:Line -- Title**
Description of the issue and why it matters.
Suggested fix with a code snippet if applicable.

Severity levels:
- **CRITICAL** -- Must fix before merge (security, data loss, crashes)
- **WARNING** -- Should fix (bugs, performance, maintainability)
- **SUGGESTION** -- Nice to have (style, naming, minor improvements)
- **PRAISE** -- Highlight well-written code worth calling out

### Verdict
APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION with a one-line rationale.

## Constraints

- Do not modify any files. This is a read-only review.
- Do not review generated files (lockfiles, build output, vendor).
- If the diff is larger than 500 lines, summarize by file and focus
  detailed review on the highest-risk changes.
- Always include at least one PRAISE item to acknowledge good work.
```

### Step 3: Add the plugin manifest

If you do not already have a plugin, create the manifest at `.claude-plugin/plugin.json`:

```json
{
  "name": "my-code-tools",
  "version": "1.0.0",
  "description": "Personal code quality tools for Claude Code",
  "author": "Your Name <you@example.com>",
  "license": "MIT"
}
```

Also create a `README.md` at the plugin root:

```markdown
# My Code Tools

Personal code quality plugins for Claude Code.

## Skills

- **pr-review** -- Structured pull request code review with quality checklist.
```

Your directory structure should look like this:

```
my-code-tools/
  .claude-plugin/
    plugin.json
  README.md
  skills/
    pr-review/
      SKILL.md
```

## Test the skill

### Validate the structure

Run the validator to catch structural issues before testing in Claude Code:

```bash
# Using ccpi
ccpi validate skills/pr-review/SKILL.md

# Using the universal validator (if in the Tons of Skills repo)
python3 scripts/validate-skills-schema.py --enterprise skills/pr-review/
```

The validator checks frontmatter fields, required sections, allowed-tools syntax, and overall content quality.

### Test in Claude Code

Install your plugin locally and try the skill:

```bash
# Start Claude Code in a project with uncommitted changes
claude

# Ask for a review
Review the changes I have staged for commit.
```

If the skill activates, you will see Claude follow the methodology defined in your SKILL.md -- reading the diff, evaluating each file against the checklist, and producing a structured report.

If the skill does not activate, check:

- Is the plugin installed? Run `/plugin list` inside Claude Code.
- Does the `description` field match your request phrasing? Try using the exact trigger phrases from the description.
- Are there errors in the frontmatter? Run `ccpi validate` to check.

## Iterate and improve

Skills rarely work perfectly on the first try. Here is how to refine them.

### Tune the description

If the skill fires too often, narrow the trigger phrases. If it never fires, broaden them. The description should cover the most common ways a user would phrase the request.

### Add examples

Including input/output examples in the body dramatically improves consistency:

```markdown
## Examples

### Example: Small TypeScript PR

Input: `git diff main...feature/auth-refactor`

Expected output structure:
- Summary: "Refactors authentication middleware to use JWT validation..."
- 2-3 findings with severity, file, line, and suggested fix
- Verdict: APPROVE or REQUEST CHANGES
```

### Use dynamic context injection

For skills that need runtime information, use DCI to inject data at activation time:

```markdown
## Context

Current branch and recent commits:

!`git branch --show-current`

!`git log --oneline -5`
```

The `!` backtick syntax runs the command when the skill loads and injects the output into the prompt. This saves tool-call round trips and gives Claude immediate context.

### Reference supporting files

For complex skills, break instructions into multiple files:

```
skills/pr-review/
  SKILL.md            # Main instructions
  checklist.md        # Detailed quality checklist
  examples/
    typescript.md     # TypeScript-specific review examples
    python.md         # Python-specific review examples
```

Reference them from SKILL.md with relative links:

```markdown
For the full quality checklist, see checklist.
For language-specific guidance, see TypeScript examples.
```

## Common patterns

### Subagent delegation

For expensive or long-running skills, run them in a forked context so they do not consume the main conversation's token budget:

```yaml
context: fork
agent: Explore
```

### Model override

If a skill needs stronger reasoning (e.g., complex security analysis), override the model:

```yaml
model: opus
```

For simple, high-volume tasks (e.g., formatting checks), use a faster model:

```yaml
model: haiku
```

### Scoped Bash access

Limit Bash access to only the commands the skill needs:

```yaml
allowed-tools: Read, Bash(npm:test, npm:run, git:diff, git:log)
```

This follows the principle of least privilege and prevents the skill from accidentally running destructive commands.

## Next steps

- [ccpi CLI Quick Reference](/docs/getting-started/cli-reference) -- validate and manage skills from the command line.
- [Browse existing skills](/skills) -- study the 2,834 skills in the marketplace for patterns and inspiration.
- [Explore plugins](/explore) -- see how production plugins structure their skills.
