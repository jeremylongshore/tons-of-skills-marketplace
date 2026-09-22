# Skill Creation Guide — Detailed Steps

This reference covers the detailed implementation steps for creating production-grade skills.
Referred from the main SKILL.md Steps 4-10.

## Step 4: Write SKILL.md

Generate the SKILL.md using the template from `${CLAUDE_SKILL_DIR}/templates/skill-template.md`.

**Frontmatter rules** (see `${CLAUDE_SKILL_DIR}/references/frontmatter-spec.md`):

Required fields:

```yaml
name: {skill-name}          # Must match directory name
description: |               # Third person, what + when + keywords
  {What it does}. Use when {scenario}.
  Trigger with "/{skill-name}" or "{natural phrase}".
```

**Frontmatter constraints (Anthropic spec):**

- `name`: No XML tags (`<`, `>` characters prohibited). No reserved words (`anthropic`, `claude`) in isolation.
- `description`: No XML tags. Description is injected into Claude's system prompt — third person prevents discovery issues where Claude speaks as the skill author.

Identity fields (top-level — marketplace validator scores these here):

```yaml
version: 1.0.0
author: {name} <{email}>
license: MIT
```

**IMPORTANT**: `version`, `author`, `license`, `compatibility`, and `tags` are top-level fields.
Do NOT nest them under `metadata:`. The marketplace 100-point validator checks them at top-level.

Recommended fields:

```yaml
allowed-tools: "{scoped tools}"
model: inherit
```

**Optional: `disallowed-tools` (schema 3.7.0+):**

Defense-in-depth denylist layered on top of the `allowed-tools` allowlist. Declare it when the
skill legitimately needs broad Bash but should never reach for high-risk operations (`rm`,
`curl` to arbitrary hosts, `.env` file edits, system-config writes):

```yaml
disallowed-tools: [Bash(rm:*), Bash(curl:*), Bash(wget:*), Bash(sudo:*), Edit(.env), Edit(.env.*), Write(.env), Write(.env.*)]
```

Rules:

- A pattern must never appear in BOTH `allowed-tools` and `disallowed-tools` — the marketplace
  validator reports the overlap as an ERROR.
- Default is to omit the field — only declare it when the allowlist is broad enough to warrant
  a denylist.
- Naming parallel: skills use kebab-case `disallowed-tools`; agents use camelCase
  `disallowedTools`. The validator rejects either mismatch — never copy-paste between agent
  and skill frontmatter without renaming.

Optional Claude Code extensions:

```yaml
argument-hint: "[arg]"              # If accepts $ARGUMENTS
context: fork                       # If needs isolated execution
agent: general-purpose              # Subagent type (with context: fork)
disable-model-invocation: true      # If explicit /name only (no auto-activation)
user-invocable: false               # If background knowledge only
compatibility: "Python 3.10+"      # If environment-specific
tags: [devops, ci]                  # Discovery tags
```

**Description writing — maximize discoverability scoring:**

Descriptions determine activation AND marketplace grade. "Use when"/"Trigger with" scoring is enterprise-tier only (marketplace grading). Standard tier does not penalize for missing these patterns. However, they remain best practices for discoverability regardless of tier.

```yaml
# Good - scores +6 pts on enterprise marketplace grading
description: |
  Analyze Python code for security vulnerabilities. Use when reviewing code
  before deployment. Trigger with "/security-scan" or "scan for vulnerabilities".

# Acceptable at standard tier, but loses 6 pts at enterprise tier
description: |
  Analyzes code for security issues.
```

Pattern (enterprise): "Use when [scenario]" (+3 pts) + "Trigger with [phrases]" (+3 pts) + "Make sure to use whenever..." for aggressive claiming.

**Token budget awareness:** All installed skill descriptions load at startup (~100 tokens each). The total skill list is capped at ~15,000 characters (`SLASH_COMMAND_TOOL_CHAR_BUDGET`). Keep descriptions impactful but efficient.

**Body content guidelines — section recommendations:**

Anthropic's spec places no format restrictions on body content. The sections below are enterprise-tier quality recommendations scored by the Intent Solutions marketplace rubric. At standard tier, these are not required but are still good practice:

```
## Overview       (>50 chars content: +4 pts enterprise)
## Prerequisites  (+2 pts enterprise)
## Instructions   (numbered steps: +3 pts enterprise)
## Output         (+2 pts enterprise)
## Error Handling (+2 pts enterprise)
## Examples       (+2 pts enterprise)
## Resources      (+1 pt enterprise)
5+ sections total: +2 pts bonus (enterprise)
```

Additional guidelines:

- Keep under 500 lines (offload to `references/` if longer)
- Concise — Claude is smart, don't over-explain
- Concrete examples over abstract descriptions
- Reference supporting files with relative markdown links: `details` or `API` — Claude reads these on demand
- Use `${CLAUDE_SKILL_DIR}/` in DCI/bash contexts only: exclamation + backtick-wrapped command, e.g. `cat ${CLAUDE_SKILL_DIR}/references/config.md`
- Sections >20 lines (Output, Error Handling, Examples) → offload to `references/` with relative links
- If skill has 3+ distinct user operations → split into individual `commands/*.md` files
- Add DCI for common discovery: file existence checks, git status, tool version detection
- Include edge cases that actually matter
- No time-sensitive information — use an 'old patterns' section for deprecated approaches that users may encounter
- Consistent terminology throughout — pick one term per concept and use it everywhere
- Include feedback loops for quality-critical workflows (run validator -> fix -> repeat until passing)
- No TOC in SKILL.md body (wastes tokens). For reference files >100 lines, include a TOC at the top
- Checklist workflow pattern: for complex multi-step processes, include a copy-pasteable checklist
- **No surprise behavior**: Skills must not contain malware, exploit code, or content that could compromise security. A skill's behavior should not surprise the user if described honestly

**String substitutions available:**

- `$ARGUMENTS` / `$0`, `$1` - user-provided arguments (pair with `argument-hint` frontmatter)
- `${CLAUDE_SESSION_ID}` - current session ID
- `` !`command` `` syntax — dynamic context injection (Anthropic spec feature):
  - Runs shell command at skill activation time, injects stdout into body
  - **Use for**: always-needed, small references (<5KB) — e.g., `!`cat ${CLAUDE_SKILL_DIR}/references/config.md``
  - **Don't use for**: large references (>5KB), conditional content, or anything that varies by mode
  - Conditional or large references → keep manual `Load ${CLAUDE_SKILL_DIR}/references/...` instructions

## Step 5: Create Supporting Files

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

## Step 6: Validate

Run validation (see `${CLAUDE_SKILL_DIR}/references/validation-rules.md`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py {skill-dir}/SKILL.md
python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade {skill-dir}/SKILL.md
```

Standard tier is the default (no required fields, broad compatibility). Use `--enterprise` for full 100-point marketplace grading.

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

## Step 7: Test & Evaluate

Create `evals/evals.json` with minimum 3 scenarios: happy path, edge case, negative test.

```json
[
  {"name": "basic_usage", "prompt": "Trigger prompt", "assertions": ["Expected behavior"]},
  {"name": "edge_case", "prompt": "Edge case prompt", "assertions": ["Expected handling"]},
  {"name": "negative_test", "prompt": "Should NOT trigger", "assertions": ["Skill inactive"]}
]
```

Run parallel evaluation: Claude A with skill installed vs Claude B without. Compare outputs against assertions — the skill should produce meaningfully better results for its target use cases.

**Additional testing practices:**

- **Team feedback**: If applicable, share the skill with teammates and observe usage patterns
- **Observe Claude navigation**: Watch how Claude reads and navigates the skill — look for unexpected exploration paths, missed references, or overreliance on certain sections

## Step 8: Iterate

1. Review which assertions passed/failed
2. Modify SKILL.md instructions, examples, or constraints
3. Re-validate with `validate-skill.py --grade`
4. Re-test evals until all assertions pass

Common fixes: undertriggering -> pushier description, wrong format -> explicit output examples, over-constraining -> increase degrees of freedom.

**Look for repeated work across test cases**: Read transcripts from test runs. If all test cases independently wrote similar helper scripts or took the same multi-step approach, that's a signal the skill should bundle that script in `scripts/`. Write it once and tell the skill to use it.

## Step 9: Optimize Description

Create 20 trigger evaluation queries (10 should-trigger, 10 should-not-trigger). Split into train (14) and test (6) sets. Iterate description until >90% accuracy on both sets.

**How skill triggering works:** Skills appear in Claude's available_skills list with their name + description. Claude decides whether to consult a skill based on that description. Important: Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries may not trigger a skill even if the description matches perfectly. Complex, multi-step, or specialized queries reliably trigger skills when the description matches. Design eval queries accordingly — make them substantive enough that Claude would benefit from consulting a skill.

Tips: front-load distinctive keywords, include specific file types/tools/domains, add "Use when...", "Trigger with...", "Make sure to use whenever..." patterns. Avoid generic terms that overlap with other skills. Ensure no XML tags (`<`, `>`) appear in the description.

## Step 10: Report

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

## Validation Workflow

When the user wants to validate, grade, or audit an existing skill:

### Step V1: Locate the Skill

Ask for the SKILL.md path or detect from context. Common locations:

- `~/.claude/skills/{name}/SKILL.md` (global)
- `.claude/skills/{name}/SKILL.md` (project)

### Step V2: Run Validator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py --grade {path}/SKILL.md
```

### Step V3: Review Grade

100-point rubric across 5 pillars:

| Pillar | Max | What It Measures |
|--------|-----|------------------|
| Progressive Disclosure | 30 | Token economy, layered structure, navigation |
| Ease of Use | 25 | Metadata, discoverability, workflow clarity |
| Utility | 20 | Problem solving, examples, feedback loops |
| Spec Compliance | 15 | Frontmatter, naming, description quality |
| Writing Style | 10 | Voice, objectivity, conciseness |
| Modifiers | +/-5 | Bonuses/penalties for patterns |

Grade scale: A (90+), B (80-89), C (70-79), D (60-69), F (<60)

See `${CLAUDE_SKILL_DIR}/references/validation-rules.md` for detailed sub-criteria.

### Step V4: Report Results

Present the grade report with specific fix recommendations. Prioritize fixes by point value (highest first).

### Step V5: Auto-Fix (if requested)

If the user says "fix it" or "auto-fix", apply the suggested improvements:

1. Add missing sections (Overview, Prerequisites, Output)
2. Add "Use when" / "Trigger with" to description
3. Move author/version from metadata to top-level
4. Fix path variables to `${CLAUDE_SKILL_DIR}/`
5. Re-run grading to confirm improvement

## Running and Evaluating Test Cases

For detailed empirical eval workflow (Steps E1-E5), read `${CLAUDE_SKILL_DIR}/references/advanced-eval-workflow.md`.

**Quick summary:** Spawn with-skill and baseline subagents in parallel -> draft assertions while running -> capture timing data from task notifications -> grade with `${CLAUDE_SKILL_DIR}/agents/grader.md` -> aggregate with `scripts/aggregate_benchmark.py` -> launch `eval-viewer/generate_review.py` for interactive human review -> read `feedback.json`.

## Improving the Skill

For iteration loop details, read `${CLAUDE_SKILL_DIR}/references/advanced-eval-workflow.md` (section "Improving the Skill").

**Key principles:** Generalize from feedback (don't overfit), keep prompts lean, explain the *why* behind rules (not just prescriptions), and bundle repeated helper scripts.

## Description Optimization (Automated)

For the full pipeline (Steps D1-D4), read `${CLAUDE_SKILL_DIR}/references/advanced-eval-workflow.md` (section "Description Optimization"). Quick summary: generate 20 realistic trigger eval queries -> review with user via `${CLAUDE_SKILL_DIR}/assets/eval_review.html` -> run `python -m scripts.run_loop` (60/40 train/test, 3 runs/query, up to 5 iterations) -> apply `best_description`.

## Advanced: Blind Comparison

For A/B testing between skill versions, read `${CLAUDE_SKILL_DIR}/agents/comparator.md` and `${CLAUDE_SKILL_DIR}/agents/analyzer.md`. Optional; most users won't need it.

## Packaging

`python -m scripts.package_skill <path/to/skill-folder> [output-directory]` — Creates distributable `.skill` zip after validation.

## Platform-Specific Notes

See `${CLAUDE_SKILL_DIR}/references/advanced-eval-workflow.md` (section "Platform-Specific Notes").

- **Claude.ai**: No subagents — run tests yourself, skip benchmarking/description optimization.
- **Cowork**: Full subagent workflow. Use `--static` for eval viewer. Generate viewer BEFORE self-evaluation.
