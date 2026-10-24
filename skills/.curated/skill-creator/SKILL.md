---
name: skill-creator
description: 'Create, validate, optimize or refresh Claude Code skills. Use when scaffolding
  a skill,

  grading an existing skill, or using forge/reforge for an API plugin.

  Trigger with "/skill-creator", "create a skill", or "validate my skill".

  '
argument-hint: '[create|validate|optimize|--forge|--reforge] [target]'
allowed-tools: Read,Write,Edit,Glob,Grep,Bash(mkdir:*),Bash(chmod:*),Bash(python:*),Bash(claude:*),Agent,AskUserQuestion,Bash(python3:*),Bash(pnpm:*),Bash(node:*),Bash(git:*),Bash(scripts/run-jrig-eval.sh:*)
version: 5.25.0
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
contradictions that would cost marketplace points. Supports create, validate, forge and reforge modes, loading their details only
when selected.

## Prerequisites

- A known target location, workflow and authoring authority.
- The target's canonical validator and required local tools available for any
  claimed static result; report unavailable tools rather than claiming a pass.
- Known provenance and licensing for reused content.

## Instructions

For test-quality or infrastructure work, use `audit-tests` for diagnosis and
`implement-tests` for the authorized repair handoff. Skill grading, package
checks and behavioral evaluation are separate; ordinary authoring does not
implicitly authorize installing a test stack or making paid provider calls.

### Mode Detection

Determine user intent from their prompt:

- **Optimize mode**: improve an existing description through the requested
  [advanced workflow](references/advanced-eval-workflow.md), using its existing
  model/provider authorization.
- **Create mode** (default): "create a skill", "build a skill", "new skill" -> proceed to Step 1
- **Validate mode**: "validate", "check", "grade", "score", "audit" -> read [Validation Workflow](references/validation-workflow.md)
- **Forge mode** (`--forge`): "/skill-creator --forge <api>", "forge a skill from <api>", "generate plugin from API" -> read [Forge Mode Workflow](references/forge-workflow.md). The `--forge` flag invokes a stricter pipeline with NOI gate, ecosystem absorb, mandatory validation, and `.forge/` audit trail. Right when generating a plugin from an API surface; not needed for hand-authored skills.
- **Reforge mode** (`--reforge`): "/skill-creator --reforge <plugin-name>", "reforge plugin", "regenerate against current API" -> read [Reforge Mode Workflow](references/reforge-workflow.md). Targets an existing forge-generated plugin and regenerates against the current API surface to fight catalog rot. Reuses existing NOI from `.forge/research.md` (no re-prompting unless `--reset-noi` is passed).

### Communicating with the User

Pay attention to context cues to understand the user's technical level. Skill creator is used by people across a wide range of familiarity — from first-time coders to senior engineers. In the default case:

- "evaluation" and "benchmark" are borderline but OK
- For "JSON" and "assertion", check for cues the user knows these terms before using them without explanation
- Briefly explain terms if in doubt

### Step 1: Select Scope and Authority

Use Read, Glob and Grep to inspect the target. Use AskUserQuestion only for
missing decisions. Establish the target
location, provenance, runtime and current repository contract. Preserve unrelated
files and supported optional metadata. Do not promote a skill on the homepage
or change repository governance as part of ordinary authoring.

IS marketplace skill output needs all eight top-level fields: `name`,
`description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`,
`tags`. Agent output goes through `agent-creator` and its context-specific
11-field plugin or 14-field standalone template. Upstream-minimum examples do
not satisfy those overlays. Read [authoring authority](references/source-of-truth.md)
when sources disagree; preserve the target's existing gate and report the mismatch.

### Step 2: Run the Selected Workflow

- Create or revise: [Creation workflow](references/creation-workflow.md).
- Grade an existing skill: [Validation workflow](references/validation-workflow.md).
- Generate from an API: [Forge workflow](references/forge-workflow.md).
- Refresh a generated plugin: [Reforge workflow](references/reforge-workflow.md).

Use Write for new files and Edit for bounded revisions. Use WebSearch and
WebFetch for current API documentation only when the selected forge mode has
those capabilities available and already authorized in the parent session. The
ordinary authoring grant does not automatically grant network research. Report
missing capability instead of expanding permissions as part of grading. Use [field guidance](references/frontmatter-spec.md) and the actual templates.
Keep shared purpose and essential constraints in SKILL.md; put substantial
conditional procedures in linked references. Choose supporting resources for
the actual workflow rather than creating a fixed directory checklist.

### Step 3: Validate and Report

Run the target's canonical validator and the relevant deterministic package and
production checks described in [validation rules](references/validation-rules.md).
Use real generated artifacts and positive/negative fixtures for changed scripts
or templates; fixing a copied field list is not proof of output correctness.
Retain errors, warnings and missing tooling. Never change the validator,
required-field sets, pins or baselines to make generated output pass.

Behavioral evaluation and description optimization are separate opt-in work.
When requested and already authorized, follow
[advanced evaluation](references/advanced-eval-workflow.md) within its actual
model/provider scope. Otherwise report SKIPPED; missing requested coverage is
INCOMPLETE. A schema pass, package check or ignored flag is not execution proof.

## Output

Deliver the requested skill files, their provenance and a concise verification
report. Name the actual schema/rubric results and unresolved findings. Distinguish
static validation from model execution, and record unrun behavioral work as
SKIPPED. Forge and reforge additionally retain their build-time `.forge/` records;
runtime users should not need to load that diary.

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
  Review code changes for correctness and actionable findings. Use when doing
  a code review. Trigger with "/code-review" or "review this change".
allowed-tools: "Read,Glob,Grep"
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: "Designed for Claude Code"
tags: [review, quality]
model: inherit
---
```

### Full Package with Arguments (Create Mode)

```
User: Create a skill that generates release notes from git history
Creates: SKILL.md (argument-hint: "[version-tag]") + scripts/ + references/ + templates/ + evals/
Uses $ARGUMENTS[0] for version tag. Uses context: fork for isolated execution.
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

| Error            | Cause                                                 | Solution                                     |
| ---------------- | ----------------------------------------------------- | -------------------------------------------- |
| Name exists      | Directory already present                             | Choose different name or confirm overwrite   |
| Invalid name     | Not kebab-case or >64 chars                           | Fix to lowercase-with-hyphens                |
| Validation fails | Missing fields or anti-patterns                       | Run validator, fix reported issues           |
| Resource missing | `${CLAUDE_SKILL_DIR}/` ref points to nonexistent file | Create the file or fix the reference         |
| Undertriggering  | Description too passive                               | Add "Make sure to use whenever..." phrasing  |
| Eval failures    | Skill not producing expected output                   | Iterate on instructions and re-test          |
| Low grade        | Missing scored sections or fields                     | Add Overview, Prerequisites, Output sections |

## Resources

**References:** `${CLAUDE_SKILL_DIR}/references/`

- `source-of-truth.md` — Canonical spec ([AgentSkills.io](https://agentskills.io/specification), [Anthropic docs](https://code.claude.com/docs/en/skills), [Lee Han Chung deep dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)) | `frontmatter-spec.md` — Field reference | `validation-rules.md` — Canonical validation and evidence classes
- `workflows.md` — Workflow patterns | `output-patterns.md` — Output formats | `schemas.md` — JSON schemas (evals, grading, benchmarks)
- `anthropic-comparison.md` — Upstream and IS contract distinctions | `advanced-eval-workflow.md` — Eval, iteration, optimization, platform notes

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

## Authentication

Local authoring and static validation need no provider credentials. Forge API
research and requested model evaluations may need the relevant service's existing
credential setup; use its approved loader and retain only sanitized evidence.
Do not request, print or invent credentials merely to grade a local skill.
