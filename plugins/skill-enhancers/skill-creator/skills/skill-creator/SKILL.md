---
name: skill-creator
description: 'Create production-grade agent skills aligned with the 2026 AgentSkills.io
  spec and Anthropic

  best practices (2026). Also validates existing skills against the Intent Solutions
  100-point rubric.

  Use when building, testing, validating, or optimizing Claude Code skills.

  Trigger with "/skill-creator", "create a skill", "validate my skill", or "check
  skill quality".

  Make sure to use this skill whenever creating a new skill, slash command, or agent
  capability.

  '
argument-hint: "<create|validate|optimize> [skill-path]"
allowed-tools: Read,Write,Edit,Glob,Grep,Bash(mkdir:*),Bash(chmod:*),Bash(python:*),Bash(claude:*),Agent,AskUserQuestion
version: 5.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- skill-creation
- validation
- meta-tooling
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# Skill Creator

Creates complete, spec-compliant skill packages following AgentSkills.io and Anthropic standards.
Supports both creation and validation workflows with 100-point marketplace grading.

## Overview

Skill Creator solves the gap between writing ad-hoc agent skills and producing marketplace-ready
packages that score well on the Intent Solutions 100-point rubric. It enforces the 2026 spec
(top-level identity fields, `${CLAUDE_SKILL_DIR}` paths, scored sections) and catches
contradictions that would cost marketplace points. Supports two modes: create new skills from
scratch with full validation, or grade/audit existing skills with actionable fix suggestions.

## Prerequisites

- Claude Code CLI with skill support (v2.1.78+ for advanced features like `effort`, `maxTurns`)
- Python 3.10+ for validation scripts (`validate-skill.py`, `aggregate_benchmark.py`)
- Target skill directory writable (`~/.claude/skills/` or `.claude/skills/`)

## Instructions

### Mode Detection

Determine user intent from their prompt:

- **Create mode**: "create a skill", "build a skill", "new skill" -> proceed to Step 1
- **Validate mode**: "validate", "check", "grade", "score", "audit" -> jump to Validation Workflow

### Communicating with the User

Pay attention to context cues to understand the user's technical level. Skill creator is used by people across a wide range of familiarity — from first-time coders to senior engineers. In the default case:

- "evaluation" and "benchmark" are borderline but OK
- For "JSON" and "assertion", check for cues the user knows these terms before using them without explanation
- Briefly explain terms if in doubt

### Step 1: Understand Requirements

If the current conversation already contains a workflow the user wants to capture (e.g., "turn this into a skill"), extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. Confirm with the user before proceeding.

Ask the user with AskUserQuestion:

**Skill Identity:**

- Name (kebab-case, gerund preferred: `processing-pdfs`, `analyzing-data`)
- Purpose (1-2 sentences: what it does + when to use it)

**Execution Model:**

- User-invocable via `/name`? Or background knowledge only?
- Accepts arguments? (`$ARGUMENTS` substitution)
- Needs isolated context? (`context: fork` for subagent execution)
- Explicit-only invocation? (`disable-model-invocation: true` — prevents auto-activation, requires `/name`)

**Required Tools:**

- Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Agent, AskUserQuestion, Skill
- Bash must be scoped: `Bash(git:*)`, `Bash(npm:*)`, etc.
- MCP tools: `ServerName:tool_name`

**Optional: declare `disallowed-tools` (schema 3.7.0+):**

- Defense-in-depth — an explicit denylist layered on top of the `allowed-tools` allowlist
- Useful when the skill needs broad Bash but should never reach for high-risk operations
  like `rm`, `curl` to arbitrary hosts, `.env` file edits, or system-config writes
- Example: `disallowed-tools: [Bash(rm:*), Bash(curl:*), Bash(wget:*), Bash(sudo:*), Edit(.env), Write(.env)]`
- A pattern must never appear in BOTH `allowed-tools` and `disallowed-tools` — the
  marketplace validator reports the overlap as an ERROR
- Default: omit the field (don't clutter frontmatter with a denylist the allowlist already covers)
- Naming parallel: skills use kebab-case `disallowed-tools`; agents use camelCase
  `disallowedTools` — never copy-paste between the two without renaming

**Complexity:**

- Simple (SKILL.md only)
- With scripts (automation code in `scripts/`)
- With references (documentation in `references/`)
- With templates (boilerplate in `templates/`)
- Full package (all directories)

**Location:**

- Global: `~/.claude/skills/<skill-name>/`
- Project: `.claude/skills/<skill-name>/`

### Step 2: Plan the Skill

Before writing, determine:

**Degrees of Freedom:**

| Level | When to Use |
|-------|-------------|
| High | Creative/open-ended tasks (analysis, writing) |
| Medium | Defined workflow, flexible content (most skills) |
| Low | Strict output format (compliance, API calls, configs) |

Think of it as **narrow bridge vs open field**: a deployment skill is a narrow bridge (one safe path, guard rails everywhere), while a writing skill is an open field (Claude roams freely within broad boundaries). Match constraint level to the task.

**Workflow Pattern** (see `${CLAUDE_SKILL_DIR}/references/workflows.md`):

- Sequential: fixed steps in order
- Conditional: branch based on input
- Wizard: interactive multi-step gathering
- Plan-Validate-Execute: verifiable intermediates
- Feedback Loop: iterate until quality met
- Checklist Workflow: copy-pasteable progress tracking for complex multi-step processes
- Search-Analyze-Report: explore and summarize

**Output Pattern** (see `${CLAUDE_SKILL_DIR}/references/output-patterns.md`):

- Strict template (exact format)
- Flexible template (structure with creative content)
- Examples-driven (input/output pairs)
- Visual (HTML generation)
- Structured data (JSON/YAML)

### Step 3: Initialize Structure

Create the skill directory and files:

```bash
mkdir -p {location}/{skill-name}
mkdir -p {location}/{skill-name}/scripts      # if needed
mkdir -p {location}/{skill-name}/references   # if needed
mkdir -p {location}/{skill-name}/templates    # if needed
mkdir -p {location}/{skill-name}/assets       # if needed
mkdir -p {location}/{skill-name}/evals        # for eval-driven development
```

### Steps 4-10: Write, Validate, Test, Iterate, Optimize, Report

For detailed guidance on writing SKILL.md (frontmatter rules, description scoring, body guidelines, string substitutions, DCI syntax), creating supporting files, validation, testing, iteration, description optimization, and final reporting, see [Creation Guide](references/creation-guide.md).

Key rules:

- `version`, `author`, `license`, `compatibility`, and `tags` are top-level fields (not nested under `metadata:`)
- Scope Bash: `Bash(git:*)` not bare `Bash`
- Optional `disallowed-tools` denylist (schema 3.7.0+) must never overlap `allowed-tools` (validator ERROR)
- Keep under 500 lines; offload to `references/` if longer
- Include "Use when" and "Trigger with" in description for enterprise scoring
- No XML tags in name or description (Anthropic spec prohibition)
- No time-sensitive information; use 'old patterns' section for deprecated approaches
- Include feedback loops for quality-critical workflows
- Run `python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade {skill-dir}/SKILL.md` to validate
- Create `evals/evals.json` with 3+ scenarios, iterate until all assertions pass

## Validation Workflow

When the user wants to validate, grade, or audit an existing skill. For detailed steps (V1-V5), see [Creation Guide](references/creation-guide.md).

1. Locate the SKILL.md (global `~/.claude/skills/` or project `.claude/skills/`)
2. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade {path}/SKILL.md`
3. Review grade against the 100-point rubric (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: <60)
4. Report results with prioritized fix recommendations
5. Auto-fix if requested: add missing sections, fix description patterns, move nested metadata to top-level

## Output

The skill produces one of two outputs depending on mode:

- **Create mode**: A complete skill package directory containing SKILL.md, optional `scripts/`, `references/`, `templates/`, `assets/`, and `evals/` subdirectories, plus a creation summary report with validation grade and eval results.
- **Validate mode**: A grade report showing the 100-point rubric score across 5 pillars (Progressive Disclosure, Ease of Use, Utility, Spec Compliance, Writing Style), with prioritized fix recommendations sorted by point value.

## Examples

### Simple Skill (Create Mode)

```
User: Create a skill called "code-review" that reviews code quality

Creates:
~/.claude/skills/code-review/
├── SKILL.md
└── evals/
    └── evals.json

Frontmatter:
---
name: code-review
description: |
  Make sure to use this skill whenever reviewing code for quality, security
  vulnerabilities, and best practices. Use when doing code reviews, PR analysis,
  or checking code quality. Trigger with "/code-review" or "review this code".
allowed-tools: "Read,Glob,Grep"
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
model: inherit
---
```

### Full Package with Arguments (Create Mode)

```
User: Create a skill that generates release notes from git history

Creates:
~/.claude/skills/generating-release-notes/
├── SKILL.md              (argument-hint: "[version-tag]")
├── scripts/
│   └── parse-commits.py
├── references/
│   └── commit-conventions.md
├── templates/
│   └── release-template.md
└── evals/
    └── evals.json

Uses $ARGUMENTS[0] for version tag.
Uses context: fork for isolated execution.
```

### Validate Mode

```
User: Grade my skill at ~/.claude/skills/code-review/SKILL.md

Runs: python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade ~/.claude/skills/code-review/SKILL.md

Output:
  Grade: B (84/100)
  Improvements:
    - Add "Trigger with" to description (+3 pts)
    - Add ## Output section (+2 pts)
    - Add ## Prerequisites section (+2 pts)
```

## Edge Cases

- **Name conflicts**: Check if skill directory already exists before creating
- **Empty arguments**: If skill uses `$ARGUMENTS`, handle the empty case
- **Long content**: If SKILL.md exceeds 300 lines during writing, stop and split to references
- **Bash scoping**: If user requests raw `Bash`, always scope it
- **Model selection**: Default to `inherit`, only override with good reason
- **Undertriggering**: If skill isn't activating, make description more aggressive/pushy
- **Legacy metadata nesting**: If found, move author/version/license to top-level

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Name exists | Directory already present | Choose different name or confirm overwrite |
| Invalid name | Not kebab-case or >64 chars | Fix to lowercase-with-hyphens |
| Validation fails | Missing fields or anti-patterns | Run validator, fix reported issues |
| Resource missing | `${CLAUDE_SKILL_DIR}/` ref points to nonexistent file | Create the file or fix the reference |
| Undertriggering | Description too passive | Add "Make sure to use whenever..." phrasing |
| Eval failures | Skill not producing expected output | Iterate on instructions and re-test |
| Low grade | Missing scored sections or fields | Add Overview, Prerequisites, Output sections |

## Resources

**References:** `${CLAUDE_SKILL_DIR}/references/`

- `creation-guide.md` — Detailed Steps 4-10 and Validation Workflow (V1-V5)
- `source-of-truth.md` — Canonical spec ([AgentSkills.io](https://agentskills.io/specification), [Anthropic docs](https://code.claude.com/docs/en/skills), [Lee Han Chung deep dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)) | `frontmatter-spec.md` — Field reference | `validation-rules.md` — 100-point rubric
- `workflows.md` — Workflow patterns | `output-patterns.md` — Output formats | `schemas.md` — JSON schemas (evals, grading, benchmarks)
- `anthropic-comparison.md` — Gap analysis | `advanced-eval-workflow.md` — Eval, iteration, optimization, platform notes

**Agents** (read when spawning subagents): `${CLAUDE_SKILL_DIR}/agents/`

- `grader.md` — Assertion evaluation | `comparator.md` — Blind A/B comparison | `analyzer.md` — Benchmark analysis

**Scripts:** `${CLAUDE_SKILL_DIR}/scripts/`

- `validate-skill.py` — 100-point rubric grading | `quick_validate.py` — Lightweight validation
- `aggregate_benchmark.py` — Benchmark stats | `run_eval.py` — Trigger accuracy testing
- `run_loop.py` — Description optimization loop | `improve_description.py` — LLM-powered rewriting
- `generate_report.py` — HTML reports | `package_skill.py` — .skill packaging | `utils.py` — Shared utilities

**Eval Viewer:** `${CLAUDE_SKILL_DIR}/eval-viewer/` — `generate_review.py` + `viewer.html` (interactive output comparison)
**Assets:** `${CLAUDE_SKILL_DIR}/assets/eval_review.html` (trigger eval set editor)
**Templates:** `${CLAUDE_SKILL_DIR}/templates/skill-template.md` (SKILL.md skeleton)

---

For advanced workflows (empirical eval, description optimization, blind comparison, packaging, platform notes), see [Creation Guide](references/creation-guide.md) and `${CLAUDE_SKILL_DIR}/references/advanced-eval-workflow.md`.
