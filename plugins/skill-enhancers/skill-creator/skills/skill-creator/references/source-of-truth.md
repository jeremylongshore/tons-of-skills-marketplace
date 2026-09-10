# Claude Agent Skills: Source of Truth Specification

Canonical reference from [Anthropic docs](https://code.claude.com/docs/en/skills). Last synced: 2026-09-09.

Additional references:

- **Claude Code Extensions** — platform-specific fields ([changelog](https://code.claude.com/docs/en/changelog))
- **Anthropic Engineering Blog** — progressive disclosure, degrees of freedom
- **anthropics/skills** — [github.com/anthropics/skills](https://github.com/anthropics/skills) (official skill-creator reference implementation)

---

## 1. Frontmatter Fields

### Claude Code and Agent Skills fields

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | string | Yes | 1-64 chars, kebab-case, must match directory name, no XML tags (`<`, `>`) |
| `description` | string | Yes | 1-1024 chars, what + when to use, third person, no XML tags |
| `when_to_use` | string | No | Additional activation context; combined with description must remain within 1536 chars |
| `allowed-tools` | string\|array | No | Tool allowlist |
| `disallowed-tools` | string\|array | No | Tool denylist while the skill is active |
| `model` | string | No | `sonnet`, `haiku`, `opus`, `fable`, `inherit`, or a supported full model ID |
| `effort` | string | No | `low`, `medium`, `high`, `xhigh`, `max` |
| `argument-hint` | string | No | Autocomplete hint for `/skill-name` |
| `arguments` | string\|array | No | Accepted arguments |
| `context` | string | No | `fork` only |
| `agent` | string | No | Subagent type (requires `context: fork`) |
| `background` | boolean | No | With `context: fork`, `false` waits for the result; default `true` |
| `user-invocable` | boolean | No | Default: `true` |
| `disable-model-invocation` | boolean | No | Default: `false` |
| `hooks` | object | No | Skill-scoped lifecycle hooks |
| `paths` | string\|array | No | Path activation filters |
| `shell` | string | No | `bash` or `powershell` |
| `license` | string | No | Agent Skills license name or bundled-file reference |
| `compatibility` | string | No | Environment requirements, maximum 500 chars |
| `metadata` | object | No | Arbitrary Agent Skills metadata |

### Marketplace tracking fields

These top-level fields are required by the Tons of Skills marketplace overlay.

| Field | Type | Constraints |
|-------|------|-------------|
| `version` | string | Semver (`X.Y.Z`) |
| `author` | string | `Name <email>` |
| `tags` | array | Discovery tags as list of strings |

### Field Relationships

- `context: fork` + `agent` work together (agent requires fork context)
- `disable-model-invocation: true` + `user-invocable: false` are contradictory (use one)
- `allowed-tools` scoped Bash like `Bash(git:*)` is best practice but not enforced by runtime
- `author`, `version`, and `tags` are top-level marketplace tracking fields;
  `license`, `compatibility`, and `metadata` are Agent Skills fields
- `effort` overrides model reasoning effort (works independently of other fields)
- available effort levels depend on the selected model

### Invalid or deprecated fields

| Field | Origin | Migration |
|-------|--------|-----------|
| `capabilities` | Invented | Remove — describe capabilities in `description` |
| `expertise_level` | Invented | Remove — no replacement |
| `activation_priority` | Invented | Remove — no replacement |
| `mode` | Deprecated | Use `disable-model-invocation` instead |
| `compatible-with` | Deprecated IS extension | Replace with Agent Skills `compatibility` prose |

### Recommended Field Order

```yaml
---
# Required (Anthropic)
name: skill-name
description: |
  What it does. Use when [scenario].
  Trigger with "/skill-name" or "[natural phrase]".

# Tools
allowed-tools: "Read,Write,Glob,Grep"

# Marketplace tracking (top-level)
version: 1.0.0
author: Name <email>
license: MIT
tags: [devops, automation]
compatibility: Requires Python 3.11+ and Git.

# Anthropic extensions (as needed)
model: inherit
# effort: high
argument-hint: "[arg]"
context: fork
agent: general-purpose
disable-model-invocation: false
user-invocable: true

# Optional Agent Skills metadata
metadata:
  category: development
---
```

### Valid Tools for `allowed-tools`

Common built-ins include `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`,
`WebFetch`, `WebSearch`, `Agent`, `TodoWrite`, `NotebookEdit`,
`AskUserQuestion`, and `Skill`. The validator's `VALID_TOOLS` registry is the
current complete set.

MCP tools use `ServerName:tool_name` format.

Bash scoping patterns:

```yaml
Bash(git:*)       # All git commands
Bash(npm:*)       # All npm commands
Bash(python:*)    # All python commands
Bash(mkdir:*)     # Directory creation
```

---

## 2. Agent Frontmatter (17 Anthropic fields)

Agents live in `agents/*.md` and use a different frontmatter schema than skills.

### Agent Fields

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | string | Yes | Agent identifier |
| `description` | string | Yes | 20-1536 chars under the IS contract; keep the specialty concise |
| `model` | string | No | `sonnet`, `haiku`, `opus`, `fable`, `inherit`, or full Claude model ID |
| `effort` | string | No | `low`, `medium`, `high`, `xhigh`, `max` |
| `maxTurns` | integer | No | Max agentic loop iterations |
| `tools` | string\|array | No | Allowed tools; the IS template prefers an array |
| `disallowedTools` | array | No | Denied tools; the IS overlay requires an array |
| `skills` | array | No | Skill names to preload into subagent context |
| `mcpServers` | object\|array | No | MCP server references or inline definitions; array is the current upstream form |
| `hooks` | object | No | Lifecycle hooks |
| `memory` | string | No | `user`, `project`, or `local` |
| `background` | boolean | No | Run in background |
| `isolation` | string | No | `worktree` only |
| `permissionMode` | string | No | `default`, `manual`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `color` | string | No | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | string | No | First turn when launched as the main agent |
| `experimental` | object | No | Current key: `cacheTtl` (`5m` or `1h`) |

### Key Differences from Skills

- Agents use camelCase `disallowedTools` (denylist); skills use `allowed-tools` (allowlist) plus optional kebab-case `disallowed-tools` (schema 3.7.0+) — the validator rejects either casing mismatch
- `effort` and `maxTurns` control autonomous iteration behavior (agent-only semantics)
- Agents support `mcpServers`, `memory`, `background`, `isolation`, `permissionMode`,
  `initialPrompt`, and `experimental`

### Plugin Agent Restrictions

When agents are distributed inside plugins, these fields are NOT supported:

- `hooks`
- `mcpServers`
- `permissionMode`

---

## 3. Plugin.json Schema (15 fields)

Every plugin requires `.claude-plugin/plugin.json`. Only `name` is required.

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | string | Yes | Plugin identifier |
| `version` | string | No | Semver version |
| `description` | string | No | Plugin description |
| `author` | object | No | `{name, email, url}` |
| `homepage` | string | No | Plugin homepage URL |
| `repository` | string | No | Source repository URL |
| `license` | string | No | SPDX identifier |
| `keywords` | array | No | Discovery keywords |
| `commands` | object | No | Command definitions |
| `agents` | object | No | Agent definitions |
| `skills` | object | No | Skill definitions |
| `hooks` | object | No | Plugin-level lifecycle hooks |
| `mcpServers` | object | No | MCP server configuration |
| `outputStyles` | object | No | Output formatting rules |
| `lspServers` | object | No | Language server configuration |

**CI enforcement**: Only these 15 fields are allowed. CI rejects any others.

### Plugin Directory Structure (Anthropic Official)

```
plugin-root/
├── .claude-plugin/plugin.json    # Required — plugin manifest
├── commands/                     # Slash commands (*.md with YAML frontmatter)
├── agents/                       # Custom agents (*.md with YAML frontmatter)
├── skills/
│   └── skill-name/
│       └── SKILL.md              # Auto-activating skill
├── hooks/hooks.json              # Lifecycle hooks configuration
├── .mcp.json                     # MCP server declarations
├── .lsp.json                     # LSP server declarations
├── settings.json                 # Plugin settings
├── scripts/                      # Executable automation code
├── LICENSE                       # License file
└── CHANGELOG.md                  # Version history
```

### Skill Subdirectory Structure (Gold Standard)

The crypto pack defines the gold standard. Every marketplace skill should target this structure.

```
skill-name/
├── SKILL.md                      # Required — frontmatter + instructions (≤150 lines)
├── PRD.md                        # Required — Product Requirements Document
├── ARD.md                        # Required — Architecture Requirements Document
├── references/                   # Required — progressive disclosure docs
│   ├── errors.md                 # Required — troubleshooting table (error | cause | fix)
│   ├── examples.md               # Required — real usage examples with code
│   └── implementation.md         # Required — how the skill works internally
├── scripts/                      # If skill uses ${CLAUDE_SKILL_DIR}/scripts/
├── config/                       # If skill needs configuration templates
├── templates/                    # Optional — boilerplate files for generation
└── assets/                       # Optional — static resources (images, configs)
```

**PRD.md** — Product Requirements Document. Answers: what problem, who uses it, success criteria, functional requirements, dependencies, out of scope. Written from the perspective of the skill's purpose, not generic template filler.

**ARD.md** — Architecture Requirements Document. Answers: system context, data flow, key design decisions, tool usage pattern, error handling strategy, extension points. Written from the perspective of how the skill actually works.

**Gold Standard Compliance**: tracked in `freshie/inventory.sqlite` as `gold_standard_pct` (0-100%). Target: 87%+ for all marketplace skills.

---

## 4. Progressive Disclosure (Three Levels)

Skills use progressive disclosure to minimize context window usage.

### Level 1: Metadata (~100 tokens)

- Frontmatter `name` and `description` only
- Always loaded at startup for all installed skills
- Aggregated into skill list in Claude's system prompt
- **Budget**: ~2% of context window (configurable via `SLASH_COMMAND_TOOL_CHAR_BUDGET`)

### Level 2: SKILL.md Body (<5000 tokens / <500 lines)

- Full instruction body loaded when skill activates
- Contains workflow steps, examples, edge cases
- Keep concise — Claude is already capable

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

## 5. Description Writing Rules

The description is the most important field. It determines when and whether the skill activates.

### Requirements

1. **Third person always** — "Generates reports..." not "I generate..." or "You can generate..."
2. **What + When** — Include both what it does AND when to use it
3. **Specific keywords** — Use discovery-relevant terms the model will match on
4. **Action verbs** — Start with or include: analyze, create, generate, build, debug, optimize, validate, deploy, configure, process
5. **No first person** — Never "I can", "I will", "I help", "I'm"
6. **No second person** — Never "You can", "You should", "You will"

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

## 6. Core Principles (Anthropic Official)

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
| **Medium** | Defined structure with flexible content | Most skills — defined workflow, flexible execution |
| **Low** | Strict templates, exact output format | Compliance, API calls, deterministic output |

Choose the right level. Over-constraining wastes tokens and fights Claude's capabilities.

**Analogy**: Think of it as a narrow bridge vs. an open field. Low degrees of freedom = narrow bridge (Claude must cross exactly this way). High degrees of freedom = open field (Claude picks the best path). Most skills should be medium — a wide road with guardrails, not a tightrope.

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

For complex skills, structure the body as a checklist that Claude works through sequentially. Each item should be:

- A concrete action (not a vague instruction)
- Independently verifiable (Claude can confirm it's done)
- Ordered by dependency (prerequisites first)

This pattern reduces skipped steps and improves consistency across models (Haiku benefits most).

### Observation of Claude Navigation

Claude navigates SKILL.md and references differently than humans:

- **Reads top-down on first activation** — front-load the most important instructions
- **Searches by heading** when returning to a section — use descriptive H2/H3 headers
- **Follows markdown links eagerly** — a `reference` link will trigger a Read tool call
- **Skips content after long code blocks** — keep code examples short, move long ones to references
- **Loses context in long files** — the 500-line limit exists because Claude's attention degrades past it

### Team Feedback

When multiple authors maintain skills in a shared plugin:

- Establish a shared glossary of terms used in descriptions (prevents synonym drift)
- Use PR review checklists that include trigger-eval accuracy checks
- Rotate skill ownership periodically to catch assumptions baked into instructions
- Track description optimization scores over time (should-trigger / should-not-trigger accuracy)

### Description Optimization ("Pushy" Pattern)

Skills frequently undertrigger because descriptions are too passive. Use aggressive claiming language:

- "Make sure to use this skill whenever..." + specific scenarios
- Front-load distinctive keywords
- Include trigger phrases: "Use when...", "Activates for..."
- Token budget: all descriptions load at startup (~15,000 char total via `SLASH_COMMAND_TOOL_CHAR_BUDGET`)

### No Time-Sensitive Information

- Don't include dates, versions, or URLs that change
- Reference tools by name, not version

### Consistent Terminology

- Pick terms and stick with them throughout
- Don't alternate between synonyms
- Match terminology to the domain

---

## 7. Body Content Guidelines

### Format

- **No mandatory format** — Anthropic explicitly states "no format restrictions"
- Recommended but not required: Instructions, Examples, Edge Cases
- Single H1 heading for the skill title
- Keep under 500 lines total
- Markdown formatting (headers, lists, code blocks, tables)

### Required Sections (Enterprise)

Enterprise-grade skills should include these 7 sections:

| Section | Purpose | Notes |
|---------|---------|-------|
| **Title** (`# Name`) | Identify the skill | Required — single H1 |
| **Overview** | What this does | 1-2 sentences |
| **Prerequisites** | Tools, runtimes, env needed | List dependencies |
| **Instructions** | Step-by-step workflow | Numbered steps or sub-headers |
| **Output** | Expected deliverables | What the skill produces |
| **Error Handling** | Failure modes and recovery | Common errors + fixes |
| **Examples** | Concrete input/output | At least 1, ideally 2-3 |
| **Resources** | Links to bundled files | `${CLAUDE_SKILL_DIR}/` paths |

### Content Quality

- Concrete examples over abstract explanations
- Show input AND expected output
- Include edge cases that actually occur
- One-level-deep file references only
- Clear section headers for navigability (TOC not required)
- Code blocks with language identifiers
- No time-sensitive information (dates, versions, URLs that change)
- Consistent terminology throughout — pick terms and stick with them
- Feedback loops: include verification steps so Claude can confirm each phase completed correctly
- Required packages/tools documented in Prerequisites or description (don't assume availability)

---

## 8. String Substitutions

Available in SKILL.md body for dynamic content:

| Substitution | Resolves To |
|-------------|-------------|
| `$ARGUMENTS` | All arguments passed after `/skill-name` |
| `$ARGUMENTS[0]`, `$ARGUMENTS[1]`, ... | Specific positional argument |
| `$0`, `$1`, `$2`, ... | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session identifier |
| `` !`command` `` | Dynamic context injection — runs command, injects output |

### Path Variables

| Variable | Context | Purpose |
|----------|---------|---------|
| `${CLAUDE_SKILL_DIR}` | Bash/DCI in skills | Resolves to skill's root directory |
| `${CLAUDE_PLUGIN_ROOT}` | Hooks, plugin-level | Resolves to plugin root directory |
| `${CLAUDE_PLUGIN_DATA}` | Persistent state | Survives updates/reinstalls (v2.1.78+) |

Relative markdown links (`API Reference`) work without path variables — Claude follows these with the Read tool on demand.

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

### Notes

- `$ARGUMENTS` is empty string if no arguments provided
- `` !`command` `` runs at skill **activation** time (preprocessing), not on demand
- Output is injected verbatim into the SKILL.md body before Claude sees it
- Guard against empty arguments in instructions

---

## 9. Skill Patterns

### Script Automation

Deterministic scripts that solve specific problems.

```
skill activates -> runs script -> returns result
```

Best for: file conversion, data transformation, API calls.

### Read-Process-Write

Format conversion and transformation pipeline.

```
read input -> process/transform -> write output
```

Best for: document conversion, code generation, data formatting.

### Search-Analyze-Report

Codebase analysis and reporting.

```
search codebase -> analyze findings -> generate report
```

Best for: code review, security audit, dependency analysis.

### Template-Based Generation

Generate output from templates with variable substitution.

```
load template -> fill variables -> validate -> output
```

Best for: boilerplate generation, project scaffolding, config files.

### Wizard-Style Workflow

Interactive multi-step gathering with AskUserQuestion.

```
ask question -> gather input -> ask more -> generate result
```

Best for: complex configuration, multi-option setup.

### Conditional Workflow

Branch based on input or context.

```
analyze input -> choose path -> execute branch -> output
```

Best for: skills that handle multiple related tasks.

### Plan-Validate-Execute

Verifiable intermediates with feedback loops.

```
plan steps -> validate plan -> execute -> verify each step -> report
```

Best for: deployment, migration, refactoring tasks.

### Visual Output Generation

Generate HTML or visual artifacts.

```
gather data -> generate HTML -> render preview
```

Best for: dashboards, reports, documentation sites.

---

## 10. Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Windows-style paths | Not portable | Use `${CLAUDE_SKILL_DIR}/` or Unix paths |
| Too many options without defaults | Analysis paralysis | Provide sensible defaults |
| Deeply nested references (>1 level) | Loading failures | Flatten to one level |
| Assuming tools are installed | Runtime failures | Note requirements in description or body |
| Over-verbose explanations | Wastes tokens, Claude is smart | Be concise |
| Vague descriptions | Poor discovery, wrong activation | Specific keywords + what/when |
| Time-sensitive information | Goes stale | Use generic references |
| Monolithic SKILL.md | Slow loading, poor disclosure | Split into references/ |
| Hardcoded model IDs | Break on deprecation | Use `inherit` or short names |
| First/second person in description | Spec violation | Third person always |
| Mandatory format enforcement | Fights Anthropic guidance | Recommend, don't require |
| Unscoped Bash in allowed-tools | Security risk | Use `Bash(git:*)` patterns |
| Voodoo constants | Unmaintainable | Document why each value exists |
| XML tags in name/description | Breaks frontmatter parsing | Use plain text, no `<` or `>` characters |
| System prompt injection in description | Security risk, spec violation | Description is for discovery only, not behavioral instructions |
| Reserved words in name (`anthropic`, `claude`) | Trademark conflict, confusing | Choose distinctive skill names |
| Long code blocks in SKILL.md body | Claude loses context after them | Move to `references/examples.md` |
| Using `compatibility` field | Not in Anthropic spec | Note requirements in body or description |
| Using `metadata` field | Not in Anthropic spec | Use top-level fields instead |
| Using `capabilities` / `expertise_level` | Invented fields, not in any spec | Remove entirely |

---

## 11. Validation Checklist

### Core Quality (Anthropic Standard)

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
- [ ] No invalid fields (`compatibility`, `metadata`, `capabilities`, `expertise_level`, `activation_priority`, `when_to_use`, `mode`)

### Code/Scripts Quality

- [ ] Scripts solve problems (don't punt to Claude)
- [ ] Explicit error handling in scripts
- [ ] No voodoo constants (all values justified)
- [ ] Required packages/tools documented
- [ ] Scripts documented with usage comments
- [ ] No Windows paths in scripts
- [ ] Validation/verification steps included
- [ ] Feedback loops for quality assurance

### Testing

- [ ] At least 3 evaluation scenarios created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Edge cases tested (empty args, missing files, etc.)

### Anthropic Best Practices (2026)

- [ ] No XML tags in `name` or `description` fields
- [ ] No system prompt injection patterns in description
- [ ] No reserved words (`anthropic`, `claude`) in skill name
- [ ] Description uses "pushy" pattern with "Make sure to use this skill whenever..." language
- [ ] Degrees of freedom explicitly chosen (high/medium/low) and documented
- [ ] Checklist workflow pattern used for complex multi-step skills
- [ ] Reference files >100 lines include TOC at top
- [ ] No long code blocks in SKILL.md body (moved to references)
- [ ] Trigger eval queries defined (10 should-trigger, 10 should-not-trigger)
- [ ] DCI (`!`backtick`) used for always-needed small context (<5KB)
- [ ] Feedback loops included (verification steps after each phase)

### Enterprise Extensions

- [ ] `author` and `version` present (top-level fields)
- [ ] `allowed-tools` scoped (Bash specifically)
- [ ] Error handling section or guidance included
- [ ] Resources section references all bundled files
- [ ] `${CLAUDE_SKILL_DIR}` used for all internal paths
- [ ] All 7 required body sections present (Title, Overview, Prerequisites, Instructions, Output, Error Handling, Examples)

---

## 12. MCP Tool References

Skills can reference MCP (Model Context Protocol) tools:

```yaml
allowed-tools: "Read,Write,ServerName:tool_name"
```

Format: `ServerName:tool_name` where ServerName matches the MCP server configuration.

---

## 13. Token Budget

The skill list (all descriptions) loads into Claude's system prompt at startup.

| Metric | Guideline |
|--------|-----------|
| Single description | Keep under 200 chars for efficiency |
| Total all skills | ~2% of context window |
| SKILL.md body | Under 500 lines / ~5000 tokens |
| Configurable via | `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var |

Longer descriptions reduce space for other skills and conversation context.
