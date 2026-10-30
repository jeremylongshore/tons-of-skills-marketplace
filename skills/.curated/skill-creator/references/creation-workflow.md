# Create a skill

Read this workflow for a new skill or a requested revision. Keep the existing
user scope, target authority and behavioral-authorization boundaries.

## Workflow

### Step 1: Understand Requirements

If the current conversation already contains a workflow the user wants to capture (e.g., "turn this into a skill"), extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. Proceed within that scope; ask only for missing decisions.

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

- Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task, AskUserQuestion, Skill
- Bash must be scoped: `Bash(git:*)`, `Bash(npm:*)`, etc.
- MCP tools: use the actual fully qualified `mcp__server__tool` names

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

| Level  | When to Use                                           |
| ------ | ----------------------------------------------------- |
| High   | Creative/open-ended tasks (analysis, writing)         |
| Medium | Defined workflow, flexible content (most skills)      |
| Low    | Strict output format (compliance, API calls, configs) |

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

### Step 4: Write SKILL.md

Generate the SKILL.md using the template from `${CLAUDE_SKILL_DIR}/templates/skill-template.md`.

**Current target contract first:** read the marketplace `CLAUDE.md` validation
section, `000-docs/SCHEMA_CHANGELOG.md` and canonical validator. Kernel schemas
provide the machine contract; shadow comparisons do not waive the existing
Python gate before its approved cutover. A historical vendored snapshot is not
permission to override the target pin or its required-field semantics.
See `${CLAUDE_SKILL_DIR}/references/source-of-truth.md`.

**Frontmatter rules** (see `${CLAUDE_SKILL_DIR}/references/frontmatter-spec.md`):

**Required (Anthropic spec — `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`):**

```yaml
name: { skill-name } # Must match directory name
description: | # Third person, what + when + keywords
  {What it does}. Use when {scenario}.
  Trigger with "/{skill-name}" or "{natural phrase}".
```

**Constraints:**

- `name`: No XML tags (`<`, `>` characters prohibited). No reserved words (`anthropic`, `claude`) in isolation.
- `description`: No XML tags. Description is injected into Claude's system prompt — third person prevents discovery issues where Claude speaks as the skill author.

**Additional IS marketplace-required fields (optional upstream):**

```yaml
allowed-tools: "{scoped tools}" # Pre-approved tools
license: MIT # SPDX identifier
compatibility: "Designed for Claude Code" # Free-text, max 500 chars
```

**Optional structured metadata:**

```yaml
metadata:
  category: devops
```

**`compatibility` examples** (per AgentSkills.io spec — pick the one that matches your skill):

```yaml
compatibility: "Designed for Claude Code"
compatibility: "Designed for Claude Code, also compatible with Codex and OpenClaw"
compatibility: "Requires Python 3.10+ with uv installed"
compatibility: "Requires git, docker, and jq on PATH"
compatibility: "Node.js >= 18, npm >= 9"
compatibility: "Requires network access to api.example.com (port 443)"
```

**Required IS tracking fields (top-level, not nested metadata):**

```yaml
version: 1.0.0                # Semver
author: {name} <{email}>      # Attribution
tags: [devops, ci]            # Discovery tags
```

All eight top-level fields are required at marketplace tier. Missing any is an
error; a standard-tier pass does not establish marketplace acceptance.

**Other Claude Code optional fields:**

```yaml
model: inherit # Or: sonnet / haiku / opus
effort: medium # low / medium / high / xhigh / max
argument-hint: "[arg]" # If accepts $ARGUMENTS
context: fork # If needs isolated execution
agent: general-purpose # Subagent type (with context: fork)
disable-model-invocation: true # If explicit /name only (no auto-activation)
user-invocable: false # If background knowledge only
```

The optional `hooks` field takes documented lifecycle event groups. Read the
target hook schema before adding a handler; an empty example is not a tested hook.

**Deprecated — do NOT use in new skills:**

```yaml
# compatible-with: claude-code, codex   # ← REPLACED by `compatibility` (free-text)
# mode: true                            # ← REPLACED by disable-model-invocation
```

To migrate existing skills, run:

```bash
python3 ~/000-projects/claude-code-plugins/scripts/batch-remediate.py --migrate-compatible-with --root <skill-dir>
```

**Description writing — maximize discoverability scoring:**

Descriptions determine activation AND marketplace grade. "Use when"/"Trigger with" scoring is marketplace-tier only. Standard tier does not penalize for missing these patterns. However, they remain best practices for discoverability regardless of tier.

```yaml
# Good - scores +6 pts on marketplace tier grading
description: |
  Analyze Python code for security vulnerabilities. Use when reviewing code
  before deployment. Trigger with "/security-scan" or "scan for vulnerabilities".

# Acceptable at standard tier, but loses 6 pts at enterprise tier
description: |
  Analyzes code for security issues.
```

Pattern (enterprise): "Use when [scenario]" (+3 pts) + "Trigger with [phrases]" (+3 pts) + "Make sure to use whenever..." only when the capability and actual scope warrant those triggers.

**Token budget awareness:** All installed skill descriptions load at startup (~100 tokens each). Use the target runtime's disclosure-budget guidance rather than assuming one fixed estate-wide cap. Keep descriptions impactful but efficient.

**Body and resources:** use the complete skill template. The marketplace
validator enforces its required sections; upstream body flexibility does not
waive that gate. Keep SKILL.md under the current line limit and move substantial
mode-specific detail into linked references. Add supporting files only when the
actual workflow uses them. Prefer concrete output examples and clear recovery
instructions over generic advice.

Dynamic context preprocessing executes before the model receives the skill.
Treat it as executable code with the target runtime's permission checks; do not
add it merely to preload conditional or large references. Manual reference
loading is sufficient for the authoring modes here.

### Step 5: Create Supporting Files

**Scripts** (`scripts/`):

- Scripts should solve problems, not punt to Claude
- Explicit error handling
- No voodoo constants (document all magic values)
- List required packages
- Make executable: `chmod +x scripts/*.py`

**References** (`references/`):

- Heavy documentation that doesn't need to load at activation
- Use clear section headers for navigability
- For reference files >100 lines, include a TOC at the top so Claude can see full scope even with partial reads
- One-level-deep references only (no `references/sub/dir/`)

**Templates** (`templates/`):

- Boilerplate files used for generation
- Use clear placeholder syntax (`{{PLACEHOLDER}}`)

**Assets** (`assets/`):

- Static resources (images, configs, data files)

### Step 6: Validate

Run validation (see `${CLAUDE_SKILL_DIR}/references/validation-rules.md`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py {skill-dir}/SKILL.md
python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade {skill-dir}/SKILL.md
```

Standard tier is the default (Anthropic spec exactly: `name` + `description` required). Use `--marketplace` (formerly `--enterprise`) for full 100-point marketplace grading.

**Validation checks:**

- Frontmatter: required fields, types, constraints
- Description: third person, what + when, keywords, length
- Body: under 500 lines, no absolute paths, has instructions + examples
- Tools: valid names, scoped Bash
- Resources: all `${CLAUDE_SKILL_DIR}/` references exist
- Anti-patterns: Windows paths, nested refs, hardcoded model IDs
- Progressive disclosure: appropriate use of references/

**If validation fails:** fix issues and re-run. Common fixes:

- Scope Bash tools: `Bash(git:*)` not `Bash`
- Remove absolute paths, use `${CLAUDE_SKILL_DIR}/`
- Split long SKILL.md into references
- Add missing sections (Overview, Prerequisites, Output)
- Move author/version to top-level if nested in metadata

### Step 7: Verify Observable Behavior

Use focused fixtures for emitted artifacts or changed scripts. Include relevant
positive, edge and negative cases; confirm that a negative case actually fails.
For an agent template, exercise both plugin and standalone context through the
canonical validator rather than testing only a copied list of field names.

Model evaluation and description optimization are optional, separate workflows.
When requested and covered by existing model/provider authorization, read
[Advanced evaluation](advanced-eval-workflow.md). Preserve the target,
inputs, actual failures and evidence paths. When not run, report SKIPPED; missing
requested coverage is INCOMPLETE. Do not manufacture model comparisons from a
schema pass or package check.

### Step 8: Iterate

Fix demonstrated failures, repeat the relevant checks and keep unrelated user
content intact. Bundle a helper only when observed repeated work justifies it.
AskUserQuestion is useful for missing decisions, not for reconfirming scope the
user has already supplied.

### Step 10: Report

Show the user:

```
SKILL CREATED
====================================

Location: {full path}

Files:
  SKILL.md ({lines} lines)
  scripts/{files}
  references/{files}
  templates/{files}
  evals/evals.json

Validation: Enterprise tier
  Errors: {count}
  Warnings: {count}
  Disclosure Score: {score}/6
  Grade: {letter} ({points}/100)

Eval Results:
  Scenarios: {count}
  Passed: {count}/{count}
  Description Accuracy: {percentage}%

Usage:
  /{skill-name} {argument-hint}
  or: "{natural language trigger}"

====================================
```
