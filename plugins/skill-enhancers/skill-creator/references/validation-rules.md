# Skill Validation Rules

Sources: [AgentSkills.io spec](https://agentskills.io/specification) · [Anthropic docs](https://code.claude.com/docs/en/skills) · Intent Solutions 100-point rubric

Two-tier validation aligned with AgentSkills.io spec + Enterprise extensions.

---

## Validation Tiers

### Standard Tier (AgentSkills.io Minimum)

The baseline. Any skill published to the ecosystem must pass this.

- `name` and `description` are the only required frontmatter fields
- Body format is flexible ("no format restrictions" - Anthropic)
- Under 500 lines
- No absolute paths
- No first/second person in description

### Enterprise Tier (Default for Our Skills)

Everything in Standard, plus:

- `author` and `version` present (top-level fields, NOT under metadata)
- `allowed-tools` with scoped Bash
- Recommended sections present (title, instructions, examples)
- Progressive disclosure used (references/ for heavy content)
- Error handling documented
- `${CLAUDE_SKILL_DIR}` used for all internal paths
- All referenced resources exist

---

## Frontmatter Validation

### Required Fields (Both Tiers)

| Field | Validation |
|-------|-----------|
| `name` | 1-64 chars, kebab-case `^[a-z][a-z0-9-]*[a-z0-9]$`, no consecutive hyphens, no reserved words, matches directory name, no XML tags (`<`, `>`) |
| `description` | 1-1024 chars, non-empty, third person only, no first/second person, specific keywords, no XML tags |

### Enterprise-Required Fields (Top-Level)

| Field | Validation |
|-------|-----------|
| `author` | Non-empty string, email recommended (`Name <email>`) — top-level, NOT in metadata |
| `version` | Semver format (`X.Y.Z`) — top-level, NOT in metadata |
| `license` | Non-empty string (SPDX identifier) — top-level |
| `allowed-tools` | Non-empty, all tools valid, Bash scoped |

### Optional Field Validation

| Field | Validation |
|-------|-----------|
| `license` | Non-empty string if present |
| `compatibility` | 1-500 chars if present |
| `metadata` | Valid YAML object if present |
| `model` | One of: `inherit`, `sonnet`, `haiku`, `opus`, or valid model ID |
| `effort` | One of: `low`, `medium`, `high`, `xhigh`, `max` (availability depends on model) |
| `argument-hint` | Non-empty string if present |
| `disable-model-invocation` | Boolean if present |
| `user-invocable` | Boolean if present |
| `context` | Must be `fork` if present |
| `agent` | Non-empty string if present; requires `context: fork` |
| `hooks` | Valid object with known event keys if present |

### Deprecated Field Warnings

| Field | Warning |
|-------|---------|
| `mode` | Deprecated - use `disable-model-invocation` |
| `compatible-with` | Deprecated - replace with Agent Skills `compatibility` prose |

**Note**: `version`, `author`, `license`, `compatibility`, and `tags` are valid
top-level fields. The marketplace validator scores them at top level.

---

## Description Validation

### Must Include (Both Tiers)

- What the skill does (action-oriented)
- When to use it (context/triggers)
- Specific keywords for discovery

### Must Not Include (Both Tiers)

| Pattern | Regex | Example |
|---------|-------|---------|
| First person | `\b(I can\|I will\|I'm\|I help)\b` | "I can generate..." |
| Second person | `\b(You can\|You should\|You will)\b` | "You can use..." |

### Recommended (Enterprise)

- Action verbs (analyze, create, generate, build, debug, optimize, validate)
- Slash command reference
- Third person throughout

---

## Body Validation

### Standard Tier

| Check | Level | Detail |
|-------|-------|--------|
| Line count | Error | Must be under 500 lines |
| Absolute paths | Error | No `/home/`, `/Users/`, `C:\` outside code blocks |
| Has H1 title | Warning | Should have `# Title` |
| No time-sensitive info | Warning | No dates/versions that will go stale |
| No XML tags in frontmatter | Error | name and description must not contain XML tags (`<`, `>`) |

### Enterprise Tier (adds)

| Check | Level | Detail |
|-------|-------|--------|
| Has instructions | Warning | Should have `## Instructions` or step-by-step content |
| Has examples | Warning | Should have `## Examples` or example content |
| Instructions have steps | Warning | Should have numbered steps or `### Step N` headings |
| Error handling | Warning | Should document error cases |
| Resources section | Warning | Should list `${CLAUDE_SKILL_DIR}/` references if resources exist |
| All `${CLAUDE_SKILL_DIR}/` refs exist | Error | Referenced scripts, references, templates must exist |
| No path escapes | Error | No `${CLAUDE_SKILL_DIR}/../` |
| Word count | Warning | Over 5000 words suggests splitting to references |
| Consistent terminology | Warning | No synonym rotation for key concepts |
| Concrete examples | Warning | Examples should show input AND output, not abstract |
| Feedback loops present | Warning | Quality-critical workflows should have validator loops |
| Required packages listed | Warning | Scripts should list dependencies in instructions or compatibility field |

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

## Anti-Pattern Detection

| Anti-Pattern | Check | Level |
|-------------|-------|-------|
| Windows paths | `C:\` or backslash paths | Error |
| Nested references | `${CLAUDE_SKILL_DIR}/references/sub/dir/file` | Warning |
| Hardcoded model IDs | `claude-*-20\d{6}` pattern | Warning |
| Voodoo constants | Unexplained magic numbers | Info |
| Over-verbose | >5000 words in SKILL.md | Warning |
| Missing progressive disclosure | >300 lines + no `references/` dir | Warning |
| Time-sensitive info | Dates, versions, URLs that will go stale | Warning |
| XML tags in frontmatter | `<tags>` in name or description fields | Error |
| Missing feedback loops | Quality-critical workflow without validate→fix→repeat | Warning |

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
| Reference files >100 lines have TOC | +1 |
| Uses dynamic context injection | +1 (modifier) |

Score 4+: Excellent disclosure. Score 2-3: Good. Score 0-1: Needs improvement.

**Navigation signals** are scored by section header density (7+ `##` headers = 5/5), not by TOC presence. No TOC in SKILL.md body (wastes tokens). But reference files >100 lines SHOULD have a TOC at top so Claude can see full scope even with partial reads.

---

## Dynamic Context Injection

Skills can use `` !`command` `` syntax (Anthropic spec preprocessing) to inject dynamic content at activation time.

### Scoring

| Pattern | Effect |
|---------|--------|
| `` !`command` `` directives present | +1 modifier bonus |
| Combined with `references/` directory | INFO note on layered structure |

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

- `argument-hint` SHOULD be set in frontmatter
- Instructions SHOULD handle empty `$ARGUMENTS` case
- `$ARGUMENTS[N]` indexing should be sequential from 0

Also recognized: `${CLAUDE_SESSION_ID}` — current session identifier (official Anthropic substitution).

---

## Validation Process

### Pre-flight

1. File exists and is readable
2. YAML frontmatter parses without error
3. Frontmatter separator (`---`) present at start and end

### Field Validation

1. Required fields present
2. Field types correct
3. Field constraints met
4. No deprecated fields (or warned)

### Body Validation

1. Length within limits
2. Required sections present (Enterprise)
3. No absolute paths
4. Instructions have steps (Enterprise)

### Resource Validation

1. All `${CLAUDE_SKILL_DIR}/scripts/*` references exist
2. All `${CLAUDE_SKILL_DIR}/references/*` references exist
3. All `${CLAUDE_SKILL_DIR}/templates/*` references exist
4. All `${CLAUDE_SKILL_DIR}/assets/*` references exist
5. Relative markdown links (e.g., `ref`, `api`) point to existing files
6. No path escape attempts

### Report

- Errors: Must fix (blocks pass)
- Warnings: Should fix (does not block pass)
- Info: Optional improvements (includes structural advisor suggestions)
- Score: Progressive disclosure score
- Stats: Word count, line count, token estimate

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

---

## Anthropic Official Checklist Alignment

Maps every item from the Anthropic "Skill authoring best practices" checklist to a specific validation check and scoring pillar.

### Content Quality (8 items)

| # | Anthropic Checklist Item | Validation Check | Pillar | Scored |
|---|--------------------------|-----------------|--------|--------|
| 1 | Name is kebab-case, 1-64 chars | `name` field validation | Spec Compliance | Yes |
| 2 | Description is specific with key terms | Description keyword check | Ease of Use | Yes |
| 3 | Description includes what + when (third person) | Description pattern check | Ease of Use | Yes |
| 4 | No XML tags in name or description | XML tag detection in frontmatter | Spec Compliance | Yes |
| 5 | SKILL.md body under 500 lines | Line count check | Progressive Disclosure | Yes |
| 6 | No time-sensitive information | Time-sensitive content detection | Writing Style | Yes |
| 7 | Consistent terminology throughout | Synonym rotation detection | Writing Style | Yes |
| 8 | Concrete examples (input AND output) | Example quality check | Utility | Yes |

### Structure & Disclosure (8 items)

| # | Anthropic Checklist Item | Validation Check | Pillar | Scored |
|---|--------------------------|-----------------|--------|--------|
| 9 | Heavy details in references/ (progressive disclosure) | References directory presence | Progressive Disclosure | Yes |
| 10 | Reference files >100 lines have TOC | TOC presence in long reference files | Progressive Disclosure | Yes |
| 11 | File references one level deep only | Nested reference detection | Progressive Disclosure | Yes |
| 12 | Clear workflow steps in instructions | Step/heading structure check | Ease of Use | Yes |
| 13 | Feedback loops for quality-critical workflows | Feedback loop pattern detection | Utility | Yes |
| 14 | Checklist workflow for complex processes | Checklist pattern detection | Utility | Info |
| 15 | "Old patterns" section for deprecated info | Old patterns section detection | Writing Style | Info |
| 16 | Required packages listed | Dependency listing check | Utility | Yes |

### Testing & Evaluation (6 items)

| # | Anthropic Checklist Item | Validation Check | Pillar | Scored |
|---|--------------------------|-----------------|--------|--------|
| 17 | At least 3 evaluation scenarios | Eval file presence/count | Utility | Yes |
| 18 | Tested with Haiku, Sonnet, and Opus | Model coverage in eval results | Utility | Info |
| 19 | Team feedback incorporated | Team testing notes | Ease of Use | Info |
| 20 | Observe Claude navigation patterns | Iteration notes | Ease of Use | Info |
| 21 | Scripts solve problems with error handling | Script quality checks | Utility | Yes |
| 22 | No voodoo constants | Magic number detection | Writing Style | Yes |
