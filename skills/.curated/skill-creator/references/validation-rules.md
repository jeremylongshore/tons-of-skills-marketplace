# Skill & Plugin Validation Rules

Sources: [Anthropic docs](https://code.claude.com/docs/en/skills) · Intent Solutions enterprise policy

Universal validation aligned with the Anthropic 2026 spec. Two tiers: Standard (Anthropic minimum) and Enterprise (our marketplace default — all fields required, zero tolerance for non-standard fields).

---

## Validation Tiers

### Standard Tier (Anthropic Minimum)

The baseline for any SKILL.md to be syntactically valid in Claude Code.

- Valid YAML frontmatter (parses without error, `---` delimiters present)
- `name` present, kebab-case (`^[a-z][a-z0-9-]*[a-z0-9]$`), no consecutive hyphens, matches directory name
- `description` present, third person, includes what + when context
- No first/second person in description
- Body under 500 lines
- No absolute paths (`/home/`, `/Users/`, `C:\`) outside code blocks

### Enterprise Tier (Marketplace Default)

Everything in Standard, plus ALL 8 core fields REQUIRED as hard ERRORS:

| # | Field | Validation |
|---|-------|-----------|
| 1 | `name` | 1-64 chars, kebab-case, matches directory name, no XML tags |
| 2 | `description` | 1-1024 chars, third person, what + when + keywords, "Use when" pattern, "Trigger with" pattern, no XML tags |
| 3 | `allowed-tools` | Non-empty, all tools from valid set, Bash scoped (unscoped = ERROR) |
| 4 | `version` | Semver format (`X.Y.Z`) — top-level, NOT under metadata |
| 5 | `author` | Non-empty string, email recommended (`Name <email>`) — top-level, NOT under metadata |
| 6 | `license` | Non-empty string, SPDX identifier — top-level |
| 7 | `compatibility` | Non-empty environment requirements, maximum 500 chars |
| 8 | `tags` | Non-empty array of discovery tags |

Conditional fields (required when relevant):

| Field | Condition | Level |
|-------|-----------|-------|
| `context` | Required if `agent` is set | ERROR |
| `agent` | Required if `context: fork` | ERROR |
| `argument-hint` | Recommended if `user-invocable` or body uses `$ARGUMENTS` | WARNING |
| `model` | Recommended for all skills | INFO |
| `effort` | Recommended for all skills | INFO |
| `hooks` | Only validated if present | — |

Body must contain all 7 sections (hard ERROR if any missing):

```
## Overview       — what the skill does and why it exists
## Prerequisites  — what must be true before running
## Instructions   — step-by-step workflow (numbered steps required)
## Output         — what the user gets back
## Error Handling — failure modes and recovery
## Examples       — concrete input/output pairs
## Resources      — references to supporting files
```

Supporting files required (gold standard):

- `PRD.md` must exist in skill root — Product Requirements Document
- `ARD.md` must exist in skill root — Architecture Requirements Document
- `references/` directory must exist (plural directory, NOT `reference.md` singular)
- `references/errors.md` must exist — troubleshooting table
- `references/examples.md` must exist — real usage examples with code
- `references/implementation.md` must exist — how the skill works internally

---

## Invalid Fields (ERROR — reject on sight)

Any field not in the Anthropic spec is an ERROR, not a warning. No "tolerated" or "transition" fields.

| Field | Reason |
|-------|--------|
| `capabilities` | Invented — not in Anthropic spec |
| `expertise_level` | Invented — not in Anthropic spec |
| `activation_priority` | Invented — not in Anthropic spec |
| `color` | Invented — not in Anthropic spec |
| `activation_triggers` | Invented — not in Anthropic spec |
| `type` | Invented — not in Anthropic spec |
| `category` | Invented — not in Anthropic spec |
| `mode` | Deprecated — use `disable-model-invocation` |
| `compatible-with` | Deprecated IS extension — replace with `compatibility` prose |

---

## Valid Frontmatter Fields (Complete List)

### SKILL.md Fields (Anthropic 2026)

```yaml
# Required (Enterprise)
name: kebab-case-name
description: |
  Third person. What + when + trigger phrases.
allowed-tools: "Read,Write,Edit,Bash(git:*)"
version: 1.0.0
author: Name <email>
license: MIT
compatibility: Requires Claude Code 2.1.248+.
tags: [devops, ci]

# Optional (Anthropic spec)
when_to_use: Use after changing a validation contract.
disallowed-tools: "Bash(rm:*)"   # Schema 3.7.0+ denylist (kebab-case on skills) — overlap with allowed-tools = ERROR
model: sonnet                     # sonnet | haiku | opus | fable | inherit | full model ID
effort: low                      # low | medium | high | xhigh | max; model-dependent
context: fork                    # Must be "fork" if present
agent: general-purpose           # Non-empty string; requires context: fork
background: false                # With context: fork, wait for result
argument-hint: "<file-path>"     # Autocomplete hint for $ARGUMENTS
arguments: [file-path]
user-invocable: false            # Boolean — hide from / menu
disable-model-invocation: true   # Boolean — prevent auto-activation
paths: ["packages/**"]
shell: bash
hooks:                           # Valid object with known event keys
  pre-tool-call: ...
metadata:
  category: development
```

### Agent Fields (Anthropic 2026 — 17 upstream fields)

```yaml
# Upstream required
name: agent-name
description: "Concise 20-1536 char description"

# IS marketplace-required overlay
tools: [Read, Glob, Grep]
model: sonnet
color: blue
version: 1.0.0
author: "Name <email@example.com>"
tags: [validation]
disallowedTools: []
skills: []
background: false

# Optional tuning
# effort: high                    # low | medium | high | xhigh | max
# maxTurns: 10
# memory: project
# isolation: worktree
# initialPrompt: "Start validation."
# experimental:
#   cacheTtl: 5m

# Standalone IS fields; omit in plugin agents
# hooks: {}
# mcpServers: []
# permissionMode: default
```

**Claude Code ignores these on plugin agents** (WARN if present):

- `hooks` — plugin-level only, not agent-level
- `mcpServers` — plugin-level only
- `permissionMode` — standalone agent only, not plugin-scoped

**Invalid for agents** (ERROR):

- `capabilities`, `expertise_level`, `activation_priority`, `activation_triggers`,
  `type`, and `category` — invented, not Anthropic. `color` is valid.

---

## Description Validation

### Must Include (Both Tiers)

- What the skill does (action-oriented, third person)
- When to use it (context/triggers)
- Specific keywords for discovery

### Must Not Include (Both Tiers)

| Pattern | Regex | Example |
|---------|-------|---------|
| First person | `\b(I can\|I will\|I'm\|I help)\b` | "I can generate..." |
| Second person | `\b(You can\|You should\|You will)\b` | "You can use..." |

### Enterprise Additions

- Must include "Use when" pattern (+3 pts)
- Must include "Trigger with" pattern (+3 pts)
- Action verbs (analyze, create, generate, build, debug, optimize, validate)
- Third person throughout

---

## Body Validation

### Standard Tier

| Check | Level | Detail |
|-------|-------|--------|
| Line count <=500 | Error | Must be under 500 lines |
| Line count 301-500 | Warning | Consider splitting to references |
| Absolute paths | Error | No `/home/`, `/Users/`, `C:\` outside code blocks |
| Has H1 title | Warning | Should have `# Title` |
| No time-sensitive info | Warning | Avoid dates, version numbers, or temporal references that rot |
| No XML tags in frontmatter | Error | XML tags in YAML frontmatter cause parse failures |
| Consistent terminology | Warning | Same concept should use same term throughout |
| Feedback loops present | Warning | Should include validation steps or self-check instructions |
| Required packages listed | Warning | External dependencies should be declared in Prerequisites |

### Enterprise Tier (adds)

| Check | Level | Detail |
|-------|-------|--------|
| 7 required sections present | Error | Overview, Prerequisites, Instructions, Output, Error Handling, Examples, Resources |
| Instructions have numbered steps | Warning | Should have numbered steps or `### Step N` headings |
| All `${CLAUDE_SKILL_DIR}/` refs exist | Error | Referenced scripts, references, templates must exist |
| No path escapes | Error | No `${CLAUDE_SKILL_DIR}/../` |
| `references/` directory exists | Error | Must use `references/` (plural directory), not `reference.md` singular |
| Word count | Warning | Over 5000 words suggests splitting to references |

### SKILL.md Line Limits

| Range | Level |
|-------|-------|
| 1-300 lines | OK |
| 301-500 lines | WARNING |
| >500 lines | ERROR |

---

## Stub Detection Rules

A component is flagged as a "stub" (ERROR at enterprise tier, WARNING at standard) if ANY of these are true:

| Condition | Detection |
|-----------|-----------|
| Body too short | SKILL.md body (after frontmatter) < 30 lines |
| No substantive content | Zero code blocks AND zero markdown links to supporting files |
| Empty supporting files | Files in `references/`, `scripts/`, `templates/` exist but are 0 bytes |
| Generic description | Matches patterns: "A helpful tool", "Generates...", or lacks "use when" |
| No instructions | Missing `## Instructions` section entirely |

---

## Tool Validation

### Valid Tool Names

```
Common built-ins: Read, Write, Edit, Bash, Glob, Grep,
WebFetch, WebSearch, Agent, NotebookEdit,
AskUserQuestion, Skill. Use the validator's VALID_TOOLS registry for the
current complete set.
```

Plus MCP tools in `ServerName:tool_name` format.

### Bash Scoping

| Tier | Unscoped `Bash` |
|------|-----------------|
| Standard | Warning |
| Enterprise | Error |

Valid scoped patterns:

```
Bash(git:*)
Bash(npm:*)
Bash(python:*)
Bash(mkdir:*)
Bash(chmod:*)
Bash(curl:*)
Bash(docker:*)
```

---

## Plugin-Level Validation

When the validator is pointed at a plugin directory (not just a single SKILL.md):

### 1. Validate `plugin.json`

Check against the 8-field schema. Only `name` is strictly required by Anthropic; enterprise requires all populated fields to be from the valid set:

Valid fields: `name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords`

ERROR on any field not in this list.

### 2. Walk `skills/*/SKILL.md`

Validate each SKILL.md against the active tier (standard or enterprise). Each skill scores independently.

### 3. Walk `agents/*.md`

Validate each agent against the 17-field Anthropic agent schema. Flag plugin agents using runtime-ignored fields (`hooks`, `mcpServers`, or `permissionMode`).

### 4. Walk `commands/*.md`

Validate each command file (YAML frontmatter + body). Legacy format — emit INFO suggesting migration to skills where appropriate.

### 5. Check `hooks/hooks.json` (if present)

Validate hook event keys are from the known set. Validate referenced scripts exist and are executable.

### 6. Check `.mcp.json` (if present)

Validate MCP server configuration structure.

### 7. Roll Up Plugin Score

Plugin score = weighted average of component scores:

- Skills: 50% weight
- Agents: 20% weight
- Commands: 15% weight
- Plugin.json completeness: 10% weight
- Hooks/MCP correctness: 5% weight

---

## Agent Validation Rules

Anthropic defines 17 valid fields for agents. `name` and `description` are the
upstream-required pair; the IS marketplace overlay requires its documented
enterprise field set as well.

### Valid Agent Fields

| Field | Required | Validation |
|-------|----------|-----------|
| `name` | Yes | 1-64 chars, kebab-case |
| `description` | Yes | 20-1536 chars under the IS contract; keep it specific and concise |
| `model` | No | `sonnet`, `haiku`, `opus`, `fable`, `inherit`, or full Claude model ID |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, `max` |
| `maxTurns` | No | Positive integer, controls autonomous iteration |
| `disallowedTools` | No | Array of tool names (denylist — camelCase on agents; skills use kebab-case `disallowed-tools`) |
| `permissionMode` | No | Includes `manual` as a `default` alias; ignored on plugin agents |
| `experimental` | No | Object; `cacheTtl` accepts `5m` or `1h` |

### Context-Aware Rules

**Plugin agents** (`plugins/*/agents/*.md`):

- WARN if `hooks` present (hooks belong at plugin level, not agent level)
- WARN if `mcpServers` present (plugin-level concern)
- WARN if `permissionMode` present (standalone-only field)

**Standalone agents** (`~/.claude/agents/*.md`):

- All fields valid without restriction

### Invalid Agent Fields (ERROR)

These are invented fields that appear in no Anthropic documentation:

`capabilities`, `expertise_level`, `activation_priority`, `activation_triggers`,
`type`, and `category`. `color` is a valid upstream field.

---

## Anti-Pattern Detection

| Anti-Pattern | Check | Level |
|-------------|-------|-------|
| Windows paths | `C:\` or backslash paths | Error |
| Nested references | `${CLAUDE_SKILL_DIR}/references/sub/dir/file` (more than 1 level deep) | Warning |
| Hardcoded model IDs | `claude-*-20\d{6}` pattern (use `sonnet`/`haiku`/`opus` instead) | Warning |
| Voodoo constants | Unexplained magic numbers | Info |
| Over-verbose | >5000 words in SKILL.md body | Warning |
| Missing progressive disclosure | >300 lines + no `references/` directory | Warning |
| Singular reference file | `reference.md` instead of `references/` directory | Error |
| Time-sensitive info | Dates, version numbers, or temporal references that rot | Warning |
| XML tags in frontmatter | `<tag>` syntax in YAML frontmatter fields | Error |
| Missing feedback loops | No validation steps or self-check instructions in workflow | Warning |

---

## Progressive Disclosure Scoring

| Metric | Score |
|--------|-------|
| SKILL.md under 200 lines | +2 |
| SKILL.md 200-400 lines | +1 |
| SKILL.md 400-500 lines | 0 |
| SKILL.md over 500 lines | -2 |
| Has `references/` directory | +1 |
| Has `scripts/` directory | +1 |
| Description under 200 chars | +1 |
| Description over 500 chars | -1 |
| Has unnecessary TOC | -1 (modifier) |
| Uses dynamic context injection | +1 (modifier) |
| Reference files >100 lines have TOC | +1 |

Score 4+: Excellent disclosure. Score 2-3: Good. Score 0-1: Needs improvement.

**Navigation signals** are scored by section header density (7+ `##` headers = 5/5), not by TOC presence. TOC in SKILL.md body wastes tokens and is not part of the Anthropic spec. However, reference files over 100 lines SHOULD have a TOC for navigability — this is a different context than the main SKILL.md body.

---

## Dynamic Context Injection

Skills can use `` !`command` `` syntax (Anthropic spec preprocessing) to inject dynamic content at activation time.

### Scoring

| Pattern | Effect |
|---------|--------|
| `` !`command` `` directives present | +1 modifier bonus |
| Combined with `references/` directory | INFO note on layered structure |

### DCI Validation Rules

| Check | Level |
|-------|-------|
| Command has error fallback (`2>/dev/null \|\| echo '...'`) | Warning if missing |
| Output expected to be small (<5KB) | Info if potentially large |
| No secrets in DCI commands (API keys, tokens) | Error |

### When to Use

| Scenario | Method |
|----------|--------|
| Always-needed, small references (<5KB) | `` !`cat ${CLAUDE_SKILL_DIR}/references/small.md` `` |
| Dynamic state (git log, env vars) | `` !`git log --oneline -5` `` |
| Conditional or large references (>5KB) | Manual `Load ...` instructions |

The command runs at skill activation time. Output is injected verbatim into the body before Claude processes it.

---

## Token Budget Validation

| Metric | Warning | Error |
|--------|---------|-------|
| Single description length | >500 chars | >1024 chars |
| SKILL.md body tokens (est.) | >4000 | >6000 |
| Estimated: `word_count * 1.3` | | |

---

## String Substitution Validation

If SKILL.md body contains `$ARGUMENTS` or `$0`, `$1`, etc.:

- `argument-hint` SHOULD be set in frontmatter (WARNING if missing)
- Instructions SHOULD handle empty `$ARGUMENTS` case
- `$ARGUMENTS[N]` indexing should be sequential from 0

Also recognized: `${CLAUDE_SESSION_ID}` — current session identifier (Anthropic substitution).

---

## Validation Process

### Pre-flight

1. File exists and is readable
2. YAML frontmatter parses without error
3. Frontmatter separator (`---`) present at start and end
4. No non-standard fields present (ERROR on any invented/deprecated field)

### Field Validation

1. All 8 required fields present (enterprise) or 2 required fields (standard)
2. Field types correct (string, array, boolean, semver)
3. Field constraints met (kebab-case, SPDX, valid tool names)
4. No deprecated fields (ERROR: `when_to_use`, `mode`, `compatibility`, `metadata`)
5. No invented fields (ERROR: `capabilities`, `expertise_level`, `activation_priority`, etc.)
6. Conditional field logic (`context` requires `agent` and vice versa)

### Body Validation

1. Length within limits (301-500 = WARNING, >500 = ERROR)
2. All 7 required sections present (enterprise) — hard ERROR if any missing
3. No absolute paths outside code blocks
4. Instructions have numbered steps (enterprise)
5. Stub detection (body <30 lines, no code blocks, no links, generic description)
6. `references/` directory exists (enterprise)

### Resource Validation

1. All `${CLAUDE_SKILL_DIR}/scripts/*` references exist
2. All `${CLAUDE_SKILL_DIR}/references/*` references exist
3. All `${CLAUDE_SKILL_DIR}/templates/*` references exist
4. All `${CLAUDE_SKILL_DIR}/assets/*` references exist
5. Relative markdown links (e.g., `ref`) point to existing files
6. No path escape attempts (`../`)
7. No empty (0-byte) supporting files (stub detection)

### Report

- Errors: Must fix (blocks pass)
- Warnings: Should fix (does not block pass)
- Info: Optional improvements (includes structural advisor suggestions)
- Score: Progressive disclosure score
- Stats: Word count, line count, token estimate
- Stub flags: Components identified as stubs

---

## Structural Advisors (Enterprise Tier)

INFO-level suggestions emitted after grading. Not scored — purely advisory.

### Split to Commands

- **Trigger**: 3+ kebab-case `## operation-name` sections without `commands/` directory
- **Suggestion**: Split into individual `commands/*.md` files
- **Why**: Each operation becomes a separate slash command; skill stays lean

### Offload to References

- **Trigger**: Body sections >20 lines (Output, Error Handling, Examples) without `references/`
- **Suggestion**: Move to `references/section-name.md` with relative markdown link
- **Why**: Reduces token footprint; Claude reads on demand

### DCI Opportunities

- **Trigger**: File existence checks, git operations, or tool version detection without DCI
- **Suggestion**: Add `` !`command` `` directives for auto-detection at activation
- **Why**: Eliminates discovery tool calls; Claude starts with context pre-loaded

### Migrate Commands to Skills

- **Trigger**: `commands/*.md` files present without corresponding `skills/` entries
- **Suggestion**: Consider migrating to SKILL.md format for auto-activation
- **Why**: Skills activate automatically on context; commands require explicit `/name` invocation

---

## Anthropic Official Checklist Alignment

22-item checklist mapped to validation checks, organized by category. Each item references the Anthropic best practices (2026) and maps to an existing validation rule or anti-pattern in this document.

### Content Quality (8 items)

| # | Checklist Item | Maps To | Level |
|---|---------------|---------|-------|
| 1 | Description is third person, action-oriented | Description Validation > Must Include | Error |
| 2 | No first/second person pronouns | Description Validation > Must Not Include | Error |
| 3 | Keywords present for discovery | Description Validation > Must Include | Warning |
| 4 | No XML tags in frontmatter values | Enterprise Tier table (`name`, `description`), Body Validation > Standard Tier | Error |
| 5 | No time-sensitive information (dates, versions that rot) | Body Validation > Standard Tier, Anti-Pattern Detection | Warning |
| 6 | Consistent terminology throughout | Body Validation > Standard Tier | Warning |
| 7 | No hardcoded model IDs (use `sonnet`/`haiku`/`opus`) | Anti-Pattern Detection > Hardcoded model IDs | Warning |
| 8 | No absolute paths outside code blocks | Body Validation > Standard Tier | Error |

### Structure & Disclosure (8 items)

| # | Checklist Item | Maps To | Level |
|---|---------------|---------|-------|
| 9 | SKILL.md body under 500 lines | Body Validation > Standard Tier, SKILL.md Line Limits | Error |
| 10 | Progressive disclosure used (references/ for heavy content) | Progressive Disclosure Scoring | Warning |
| 11 | No TOC in SKILL.md body (wastes tokens) | Progressive Disclosure Scoring > Has unnecessary TOC | -1 modifier |
| 12 | Reference files >100 lines have TOC | Progressive Disclosure Scoring > Reference files TOC | +1 modifier |
| 13 | All `${CLAUDE_SKILL_DIR}/` references resolve to existing files | Body Validation > Enterprise Tier, Resource Validation | Error |
| 14 | No path escapes (`../`) | Body Validation > Enterprise Tier, Resource Validation | Error |
| 15 | Required packages and dependencies listed | Body Validation > Standard Tier > Required packages listed | Warning |
| 16 | 7 required body sections present (Enterprise) | Body Validation > Enterprise Tier > 7 required sections | Error |

### Testing & Evaluation (6 items)

| # | Checklist Item | Maps To | Level |
|---|---------------|---------|-------|
| 17 | Feedback loops present (validation/self-check steps) | Body Validation > Standard Tier, Anti-Pattern Detection | Warning |
| 18 | Error handling section documents failure modes and recovery | Body Validation > Enterprise Tier > Error handling | Warning |
| 19 | Examples section has concrete input/output pairs | Body Validation > Enterprise Tier > Has examples | Warning |
| 20 | Instructions have numbered steps | Body Validation > Enterprise Tier > Instructions have steps | Warning |
| 21 | Stub detection passes (body >=30 lines, has code blocks or links) | Stub Detection Rules | Error (enterprise) |
| 22 | DCI commands have error fallbacks | Dynamic Context Injection > DCI Validation Rules | Warning |
