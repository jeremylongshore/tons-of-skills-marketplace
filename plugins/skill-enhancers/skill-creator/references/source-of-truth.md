# Claude Agent Skills: Source of Truth Specification

Canonical reference synthesizing all authoritative sources:

- **AgentSkills.io** — [agentskills.io/specification](https://agentskills.io/specification) (open standard, Dec 2025)
- **Anthropic Best Practices** — [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- **Claude Code Extensions** — platform-specific fields ([changelog](https://code.claude.com/docs/en/changelog))
- **Anthropic Engineering Blog** — progressive disclosure, degrees of freedom
- **anthropics/skills** — [github.com/anthropics/skills](https://github.com/anthropics/skills) (official skill-creator reference implementation)
- **Lee Han Chung Deep Dive** — [leehanchung.github.io](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) (authoritative technical reference)

---

## 1. Frontmatter Fields

### Required (AgentSkills.io Spec)

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | 1-64 chars, lowercase alphanumeric + hyphens, no start/end/consecutive hyphens, must match directory name, no XML tags (`<`, `>`) |
| `description` | string | 1-1024 chars, non-empty, what it does + when to use it, third person, specific keywords for discovery, no XML tags |

### Optional (AgentSkills.io Spec)

| Field | Type | Constraints |
|-------|------|-------------|
| `license` | string | License name (SPDX) or bundled file reference |
| `compatibility` | string | 1-500 chars, environment requirements (OS, runtime, tools needed) |
| `metadata` | object | Arbitrary key-value map for custom data (category, maintainer, etc.) |
| `allowed-tools` | string\|array | Space/comma-delimited or YAML-list pre-approved tools |

### Tons of Skills marketplace overlay

| Field | Type | Constraints |
|-------|------|-------------|
| `version` | string | Semver (X.Y.Z), top-level field |
| `author` | string | Author name + email (`Name <email>`), top-level field |
| `tags` | array | Discovery tags as list of strings |

### Claude Code Extensions (platform-specific, not in open standard)

| Field | Type | Purpose |
|-------|------|---------|
| `argument-hint` | string | Autocomplete hint shown after `/name`, e.g. `[issue-number]` |
| `arguments` | string\|array | Named positional arguments for `$name` substitution |
| `when_to_use` | string | Additional activation context appended to description |
| `disable-model-invocation` | boolean | Prevent auto-loading; require explicit `/name` invocation |
| `user-invocable` | boolean | `false` = hide from `/` menu (background knowledge only) |
| `disallowed-tools` | string\|array | Remove tools while the skill is active |
| `model` | string | Model override: `inherit`, `sonnet`, `haiku`, `opus`, `fable`, or a supported full model ID |
| `effort` | string | Model reasoning effort override: `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | string | `fork` = execute in subagent (isolated context) |
| `agent` | string | Subagent type when `context: fork`: `Explore`, `Plan`, `general-purpose`, or custom agent name |
| `background` | boolean | With `context: fork`, `false` waits for the result; default `true` |
| `hooks` | object | Skill-scoped lifecycle hooks (PreToolUse, PostToolUse, etc.) |
| `paths` | string\|array | Restrict automatic activation to matching paths |
| `shell` | string | `bash` or `powershell` for dynamic shell commands |

### Field Relationships

- `context: fork` + `agent` work together (agent requires fork context)
- `disable-model-invocation: true` + `user-invocable: false` are contradictory (use one)
- `allowed-tools` is experimental; scoped Bash like `Bash(git:*)` is best practice but not enforced by runtime
- `author`, `version`, and `tags` are top-level marketplace tracking fields;
  `license`, `compatibility`, and `metadata` are portable Agent Skills fields
- `metadata` is for custom data not covered by the spec (category, maintainer, etc.)
- `effort` overrides model reasoning effort; available levels depend on the model

---

## 2. Directory Structure

```
skill-name/
├── SKILL.md           # Required - frontmatter + instructions
├── scripts/           # Optional - executable automation code
├── references/        # Optional - documentation loaded on demand
├── templates/         # Optional - boilerplate files for generation
└── assets/            # Optional - static resources (images, configs)
```

### Path Conventions

- **`${CLAUDE_SKILL_DIR}`** - resolves to the skill's root directory at runtime (2026 standard)
- **`{baseDir}`** - legacy alias, still works in Claude Code
- All internal references SHOULD use `${CLAUDE_SKILL_DIR}/` prefix
- One-level-deep file references only (no `{baseDir}/references/subdir/file.md`)
- No absolute paths (`/home/...`, `/Users/...`, `C:\...`)
- No path escapes (`{baseDir}/../other-skill/`)
- No Windows-style paths (`C:\Users\...`)

### File Loading

| Location | When Loaded | Token Impact |
|----------|-------------|--------------|
| Frontmatter (`name`, `description`) | Always (startup) | ~100 tokens per skill |
| SKILL.md body | When skill activates | Full body loaded |
| `references/` files | When explicitly referenced | On-demand via Read tool |
| `scripts/` files | When executed | Via Bash tool |
| `templates/` files | When skill generates from them | Via Read tool |
| `assets/` files | When referenced | On-demand |

---

## 3. Progressive Disclosure (Three Levels)

Skills use progressive disclosure to minimize context window usage.

### Level 1: Metadata (~100 tokens)

- Frontmatter `name` and `description` only
- Always loaded at startup for all installed skills
- Aggregated into skill list in Claude's system prompt
- **Budget**: ~2% of context window (configurable via `SLASH_COMMAND_TOOL_CHAR_BUDGET`)

### Level 2: SKILL.md Body (<5000 tokens / <500 lines)

- Full instruction body loaded when skill activates
- Contains workflow steps, examples, edge cases
- Keep concise - Claude is already capable

### Level 3: Bundled Resources (unlimited)

- `references/`, `scripts/`, `templates/`, `assets/`
- Loaded only when explicitly needed during execution
- Use clear section headers for navigability
- No TOC in SKILL.md body (wastes tokens). For reference files >100 lines, include a TOC at top so Claude can see full scope even with partial reads
- Heavy content belongs here, not in SKILL.md body

### Design Implications

- Descriptions must be self-contained for discovery (Level 1)
- SKILL.md body should be actionable instructions, not encyclopedic (Level 2)
- Offload detailed specs, examples, and data to references (Level 3)

---

## 4. Description Writing Rules

The description is the most important field. It determines when and whether the skill activates.

### Requirements

1. **Third person always** - "Generates reports..." not "I generate..." or "You can generate..."
2. **What + When** - Include both what it does AND when to use it
3. **Specific keywords** - Use discovery-relevant terms the model will match on
4. **Action verbs** - Start with or include: analyze, create, generate, build, debug, optimize, validate, deploy, configure, process
5. **No first person** - Never "I can", "I will", "I help", "I'm"
6. **No second person** - Never "You can", "You should", "You will"

### Recommended Pattern

```yaml
description: |
  {What it does in 1-2 sentences with specific keywords}. {When to use it}.
  {Optional: slash command reference}.
```

### Good Examples

```yaml
# Clear what + when + keywords
description: |
  Generate PDF reports from markdown with professional styling and TOC.
  Use when converting documentation to distributable format.

# Specific keywords for discovery
description: |
  Analyze Python code for security vulnerabilities, dependency risks, and
  OWASP compliance issues. Use when reviewing code before deployment or
  during security audits.
```

### Bad Examples

```yaml
# First person
description: "I help you create PDFs"

# Missing when-to-use
description: "Generates PDF reports"

# Too vague - no keywords for discovery
description: "A helpful tool for documents"
```

### Naming Convention

- **Gerund naming preferred**: `processing-pdfs`, `analyzing-data`, `generating-reports`
- Kebab-case always: `my-skill-name`
- No reserved words: `anthropic`, `claude`

---

## 5. Core Principles (Anthropic Official)

### Concise is Key

Claude is already smart. Don't over-explain. Provide:

- Clear workflow steps
- Concrete examples
- Edge cases that matter
- Nothing else

### Degrees of Freedom

Skills have three levels of constraint:

| Level | Description | When to Use |
|-------|-------------|-------------|
| **High** | Loose guidance, Claude decides specifics | Creative tasks, analysis, open-ended work |
| **Medium** | Defined structure with flexible content | Most skills - defined workflow, flexible execution |
| **Low** | Strict templates, exact output format | Compliance, API calls, deterministic output |

Choose the right level. Over-constraining wastes tokens and fights Claude's capabilities.

Think of it as **narrow bridge vs open field**: a deployment skill is a narrow bridge (one safe path, guard rails everywhere), while a writing skill is an open field (Claude roams freely within broad boundaries).

### Evaluation-Driven Development

1. Write skill
2. Create `evals/evals.json` with at least 3 scenarios (happy path, edge case, negative test)
3. Test with Haiku, Sonnet, AND Opus (behavior differs)
4. Use parallel subagent methodology:
   - Agent A: executes the prompt WITH the skill installed
   - Agent B: executes the same prompt WITHOUT the skill
   - Compare outputs against assertions
5. Iterate based on evaluation results
6. Optimize description with trigger eval queries (10 should-trigger, 10 should-not-trigger)
7. Use train/test split (14/6) for description optimization — target >90% accuracy

### Checklist Workflow Pattern

For complex multi-step processes, include a copy-pasteable checklist so users can track progress. Claude will check items off as it completes them.

```markdown
## Progress
- [ ] Step 1: Initialize
- [ ] Step 2: Validate inputs
- [ ] Step 3: Execute
- [ ] Step 4: Verify results
```

### Observation of Claude Navigation

Iterative refinement technique: watch how Claude reads and navigates the skill during test runs. Look for:

- Unexpected exploration paths (reading files in wrong order)
- Missed references (Claude not finding bundled resources)
- Overreliance on certain sections (skipping others)
- Repeated discovery commands that DCI could eliminate

Adjust skill structure, section ordering, and reference links based on these observations.

### Team Feedback

If applicable, share the skill with teammates and observe their usage:

- Do they trigger the skill as expected?
- Do they understand the output format?
- Do they hit edge cases you didn't anticipate?
- Does the skill behave differently across their projects?

Incorporate findings into skill instructions and eval scenarios.

### Description Optimization ("Pushy" Pattern)

Skills frequently undertrigger because descriptions are too passive. Use aggressive claiming language:

- "Make sure to use this skill whenever..." + specific scenarios
- Front-load distinctive keywords
- Include trigger phrases: "Use when...", "Activates for..."
- Token budget: all descriptions load at startup (~15,000 char total via `SLASH_COMMAND_TOOL_CHAR_BUDGET`)

### No Time-Sensitive Information

- Don't include dates, versions, or URLs that change
- Reference tools by name, not version
- Use `compatibility` field for environment requirements

### Consistent Terminology

- Pick terms and stick with them throughout
- Don't alternate between synonyms
- Match terminology to the domain

---

## 6. Body Content Guidelines

### Format

- **No mandatory format** - Anthropic explicitly states "no format restrictions"
- Recommended but not required: Instructions, Examples, Edge Cases
- Single H1 heading for the skill title
- Keep under 500 lines total
- Markdown formatting (headers, lists, code blocks, tables)

### Recommended Sections

| Section | Purpose | Notes |
|---------|---------|-------|
| Title (`# Name`) | Identify the skill | Required - single H1 |
| Brief description | What this does | 1-2 sentences |
| Instructions | Step-by-step workflow | Numbered steps or sub-headers |
| Examples | Concrete input/output | At least 1, ideally 2-3 |
| Edge cases | What to watch for | Common pitfalls |
| Resources | Links to bundled files | `{baseDir}/` paths |

### Content Quality

- Concrete examples over abstract explanations
- Show input AND expected output
- Include edge cases that actually occur
- One-level-deep file references only
- Clear section headers for navigability (no TOC in SKILL.md body; reference files >100 lines should have TOC)
- Code blocks with language identifiers
- No time-sensitive information — dates, versions, and URLs that change should be avoided; use an "old patterns" section for deprecated approaches users may encounter
- Consistent terminology — pick one term per concept and use it throughout; don't alternate between synonyms
- Feedback loops — for quality-critical workflows, include explicit validate→fix→repeat cycles
- Required packages — list all dependencies in instructions or the `compatibility` field

---

## 7. String Substitutions (Claude Code)

Available in SKILL.md body for dynamic content:

| Substitution | Resolves To |
|-------------|-------------|
| `$ARGUMENTS` | All arguments passed after `/skill-name` |
| `$ARGUMENTS[0]`, `$ARGUMENTS[1]`, ... | Specific positional argument |
| `$0`, `$1`, `$2`, ... | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session identifier |
| `` !`command` `` | Dynamic context injection - runs command, injects output |

### Usage Examples

```markdown
## Instructions

Analyze the issue: $ARGUMENTS[0]

Run the following to get context:
!`git log --oneline -10`

Session tracking: ${CLAUDE_SESSION_ID}
```

### When to Use Backtick Injection vs Manual Loading

| Scenario | Method | Why |
|----------|--------|-----|
| Always-needed, small (<5KB) | `` !`cat ${CLAUDE_SKILL_DIR}/references/small.md` `` | Saves a Read tool call, always available |
| Conditional (mode-dependent) | Manual `Load ${CLAUDE_SKILL_DIR}/references/...` | Only loads when the branch executes |
| Large (>5KB) | Manual load | Avoids bloating context on every activation |
| Dynamic state (git log, env) | `` !`git log --oneline -5` `` | Fresh data at activation time |

### Best Practices

- Add a `## Current State` section with DCI directives right after the skill title heading
- Always use fallbacks to avoid error output: `` !`terraform version 2>/dev/null || echo 'not installed'` ``
- Keep injections small — summaries and version info, not full file contents
- For skills that typically run 3+ discovery commands first, DCI saves those entire tool call rounds

Example `## Current State` section:

```markdown
## Current State
!`git status --short`
!`git log --oneline -5`
!`node -v 2>/dev/null || echo 'N/A'`
```

### Notes

- `$ARGUMENTS` is empty string if no arguments provided
- `` !`command` `` runs at skill **activation** time (preprocessing), not on demand
- Output is injected verbatim into the SKILL.md body before Claude sees it
- Guard against empty arguments in instructions

---

## 8. Skill Patterns

### Script Automation

Deterministic scripts that solve specific problems.

```
skill activates → runs script → returns result
```

Best for: file conversion, data transformation, API calls.

### Read-Process-Write

Format conversion and transformation pipeline.

```
read input → process/transform → write output
```

Best for: document conversion, code generation, data formatting.

### Search-Analyze-Report

Codebase analysis and reporting.

```
search codebase → analyze findings → generate report
```

Best for: code review, security audit, dependency analysis.

### Template-Based Generation

Generate output from templates with variable substitution.

```
load template → fill variables → validate → output
```

Best for: boilerplate generation, project scaffolding, config files.

### Wizard-Style Workflow

Interactive multi-step gathering with AskUserQuestion.

```
ask question → gather input → ask more → generate result
```

Best for: complex configuration, multi-option setup.

### Conditional Workflow

Branch based on input or context.

```
analyze input → choose path → execute branch → output
```

Best for: skills that handle multiple related tasks.

### Plan-Validate-Execute

Verifiable intermediates with feedback loops.

```
plan steps → validate plan → execute → verify each step → report
```

Best for: deployment, migration, refactoring tasks.

### Visual Output Generation

Generate HTML or visual artifacts.

```
gather data → generate HTML → render preview
```

Best for: dashboards, reports, documentation sites.

---

## 9. Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Windows-style paths | Not portable | Use `{baseDir}/` or Unix paths |
| Too many options without defaults | Analysis paralysis | Provide sensible defaults |
| Deeply nested references (>1 level) | Loading failures | Flatten to one level |
| Assuming tools are installed | Runtime failures | Check or use `compatibility` field |
| Over-verbose explanations | Wastes tokens, Claude is smart | Be concise |
| Vague descriptions | Poor discovery, wrong activation | Specific keywords + what/when |
| Time-sensitive information | Goes stale | Use generic references |
| Monolithic SKILL.md | Slow loading, poor disclosure | Split into references/ |
| Hardcoded model IDs | Break on deprecation | Use `inherit` or short names |
| First/second person in description | Spec violation | Third person always |
| Mandatory format enforcement | Fights Anthropic guidance | Recommend, don't require |
| Unscoped Bash in allowed-tools | Security risk | Use `Bash(git:*)` patterns |
| Voodoo constants | Unmaintainable | Document why each value exists |
| Time-sensitive info | Goes stale, confuses Claude | Use "old patterns" section for deprecated approaches |
| XML tags in frontmatter | Spec violation, breaks parsing | Remove all XML markup from name and description |
| Missing feedback loops | Quality degrades silently | Add validate→fix→repeat for quality-critical workflows |
| Inconsistent terminology | Confuses Claude and users | Pick one term per concept, use it everywhere |

---

## 10. Validation Checklist (Anthropic Official + Enterprise)

### Core Quality

- [ ] `name` is kebab-case, 1-64 chars, matches directory name
- [ ] `description` is specific with key terms for discovery
- [ ] `description` includes what + when (third person)
- [ ] `description` has no first/second person language
- [ ] SKILL.md body under 500 lines
- [ ] Heavy details in `references/` files (progressive disclosure)
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Concrete examples (not abstract descriptions)
- [ ] File references one level deep only
- [ ] Clear workflow steps in instructions

### Code/Scripts Quality

- [ ] Scripts solve problems (don't punt to Claude)
- [ ] Explicit error handling in scripts
- [ ] No voodoo constants (all values justified)
- [ ] Required packages/tools listed or in `compatibility`
- [ ] Scripts documented with usage comments
- [ ] No Windows paths in scripts
- [ ] Validation/verification steps included
- [ ] Feedback loops for quality assurance

### Testing

- [ ] At least 3 evaluation scenarios created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Edge cases tested (empty args, missing files, etc.)

### Enterprise Extensions

- [ ] `author` and `version` present (top-level fields)
- [ ] `allowed-tools` scoped (Bash specifically)
- [ ] Error handling section or guidance included
- [ ] Resources section references all bundled files
- [ ] `${CLAUDE_SKILL_DIR}` (or `{baseDir}`) used for all internal paths

### Anthropic Best Practices (2026)

- [ ] No XML tags in `name` or `description` fields
- [ ] No time-sensitive information (dates, versions, URLs that change)
- [ ] Consistent terminology (no synonym rotation)
- [ ] Concrete examples show input AND output
- [ ] Feedback loops present for quality-critical workflows
- [ ] Reference files >100 lines include TOC at top
- [ ] Required packages/dependencies listed
- [ ] "Old patterns" section used for deprecated approaches (if applicable)
- [ ] Checklist workflow pattern for complex multi-step processes (if applicable)
- [ ] Team feedback incorporated (if applicable)
- [ ] Claude navigation patterns observed and skill structure adjusted

---

## 11. MCP Tool References

Skills can reference MCP (Model Context Protocol) tools:

```yaml
allowed-tools: "Read,Write,ServerName:tool_name"
```

Format: `ServerName:tool_name` where ServerName matches the MCP server configuration.

---

## 12. Token Budget

The skill list (all descriptions) loads into Claude's system prompt at startup.

| Metric | Guideline |
|--------|-----------|
| Single description | Keep under 200 chars for efficiency |
| Total all skills | ~2% of context window |
| SKILL.md body | Under 500 lines / ~5000 tokens |
| Configurable via | `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var |

Longer descriptions reduce space for other skills and conversation context.
