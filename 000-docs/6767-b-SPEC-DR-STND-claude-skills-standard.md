<!-- doc-class: canonical -->

# Global Master Standard – Claude Skills Specification

> ⚠️ **CURRENT SCHEMA: 4.2.0** (`scripts/validate-skills-schema.py` `SCHEMA_VERSION`). This document is the
> **v3.6.0 baseline** of the standard — the 8-field required set, tier model, and 100-point rubric below are
> still authoritative and unchanged, but subsequent schema releases add enforced rules that postdate it
> (3.7.0 `disallowed-tools` + overlap ERROR, 3.10.0/3.11.0 kernel-strict agent gates, 3.12.0/3.13.0
> `plugin.json` field rules, 3.15.x body-section fairness, and 4.0.0 malformed-allowlist errors, among others). **Read
> [`SCHEMA_CHANGELOG.md`](SCHEMA_CHANGELOG.md) for every change since this doc's 3.6.0 baseline** — the
> changelog, not this file, is where post-3.6.0 rules are specified.

**Document ID**: 6767-b-SPEC-DR-STND-claude-skills-standard.md
**Version**: 3.6.0
**Status**: AUTHORITATIVE - Single Source of Truth (8-field enterprise standard; self-improving-skills series complete 2026-05-14: progressive disclosure + conditional visibility + self-declared config)
**Created**: 2025-12-06
**Updated**: 2026-08-16
**Schema log**: `000-docs/SCHEMA_CHANGELOG.md`
**Changelog**: 2026-08-16 updates the current-schema banner to 4.0.0 for malformed-allowlist fail-closed enforcement; see `SCHEMA_CHANGELOG.md` 4.0.0. The v3.6.0 baseline adds the self-declared config surface — `required_environment_variables` (top-level list of objects with name+prompt+help+required*for) and `metadata.intent-solutions.config` (nested list of objects with key+description+default+prompt). Installer / runtime helpers prompt the user on first run instead of letting skills throw on unset secrets. Cross-field consistency with `requires_env` (3.5.0) emits a warning when a visibility-gated var has no installer-prompt description. Full reference: `000-docs/264-DR-GUID-skill-config-pattern.md`. Prior: 3.5.0 (conditional visibility — 4 `requires*_`/`fallback*for*_` fields), 3.4.0 (progressive-disclosure catalog protocol), 3.3.2 (agent-field bug fixes), 3.3.0 (restored 8-field enterprise required set).

**Sources** (every required-field claim in this document cites one of these — verified 2026-04-28):

1. [Anthropic Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — required: `name`, `description`
2. [Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — required: `name`, `description`
3. [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) — none required (`description` recommended)
4. [Anthropic Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — no SKILL.md fields beyond skills doc
5. [Anthropic Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — required: `name`, `description`
6. [AgentSkills.io Open Standard](https://agentskills.io/specification) — required: `name`, `description`; documents `license`, `compatibility`, `metadata`, `allowed-tools` as optional
7. [anthropics/skills Reference Implementation](https://github.com/anthropics/skills) — required: `name`, `description`

**Community references** (not authoritative — included for context only):

- [Lee Han Chung Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

---

## Executive Summary

### What Is a Claude Skill?

A Claude Skill is a **filesystem-based capability package** containing instructions, executable code, and resources that Claude can discover and use automatically. Skills are prompt-based context modifiers—NOT executable plugins or slash commands.

**Mental Model**: "Building a skill for an agent is like putting together an onboarding guide for a new hire."

### Why Use Skills Instead of Ad-Hoc Prompts?

| Aspect             | Ad-Hoc Prompts           | Skills                               |
| ------------------ | ------------------------ | ------------------------------------ |
| Reusability        | One conversation         | Persistent across all conversations  |
| Discovery          | Manual context provision | Automatic activation based on intent |
| Organization       | Scattered knowledge      | Structured packages                  |
| Context Management | Full context loaded      | Progressive disclosure (on-demand)   |
| Code Integration   | Generated each time      | Pre-written, deterministic scripts   |

### Where Skills Live

| Location                   | Scope                   | Priority    |
| -------------------------- | ----------------------- | ----------- |
| `~/.claude/skills/`        | Personal (all projects) | 1 (lowest)  |
| `.claude/skills/`          | Project-specific        | 2           |
| Plugin `skills/` directory | Plugin-bundled          | 3           |
| Built-in skills            | Platform-provided       | 4 (highest) |

Later sources override earlier ones when names conflict.

---

## 1. Core Concepts

### Skill = What + When + How + Allowed Tools + Optional Model Override

Every skill answers:

- **What**: What capability does this provide?
- **When**: When should Claude activate it?
- **How**: Step-by-step instructions for Claude
- **Allowed Tools**: Which tools are pre-approved during execution?
- **Model Override**: Should a different model handle this? (optional)

### The Skill Tool Architecture

**Critical insight**: Skills are NOT in the system prompt.

Skills live in a meta-tool called `Skill` within the `tools` array:

```javascript
tools: [
  { name: "Read", ... },
  { name: "Write", ... },
  {
    name: "Skill",                    // Meta-tool (capital S)
    inputSchema: { command: string },
    description: "<available_skills>..." // Dynamic list of all skill descriptions
  }
]
```

### How Skills Are Discovered and Invoked

**Model-Invoked (Automatic)**:

1. At startup, Claude's system prompt includes metadata (name + description) for all skills
2. Claude reads user request and matches intent to skill descriptions
3. Claude invokes `Skill` tool with matching `command` parameter
4. No algorithmic routing, embeddings, or keyword matching—**pure LLM reasoning**

**User-Invoked (Manual)**:

- Type `/skill-name` to explicitly invoke a skill
- Required when `disable-model-invocation: true`

---

## 2. Folder & Discovery Layout

### Standard Directory Structure

```
skill-name/
├── SKILL.md              # REQUIRED - Instructions + YAML frontmatter
├── scripts/              # OPTIONAL - Executable Python/Bash scripts
│   ├── analyze.py
│   └── validate.py
├── references/           # OPTIONAL - Docs loaded into context
│   ├── API_REFERENCE.md
│   └── EXAMPLES.md
├── assets/               # OPTIONAL - Templates referenced by path
│   └── report_template.md
└── LICENSE.txt           # OPTIONAL - License terms
```

### Naming Conventions

**Best Practice**: Folder names SHOULD match the `name` field for clarity and maintainability.

> **Note**: Anthropic's official spec does NOT enforce folder/name matching at runtime. Claude Code will load skills regardless of folder name. However, matching names is strongly recommended for discoverability and team collaboration.

**Recommended**: Use **gerund form** (verb + -ing) for clarity:

- `processing-pdfs`
- `analyzing-spreadsheets`
- `generating-commit-messages`

**Acceptable alternatives**:

- Noun phrases: `pdf-processing`, `data-analysis`
- Action-oriented: `process-pdfs`, `analyze-data`

**Avoid**:

- Vague names: `helper`, `utils`, `tools`
- Generic names: `documents`, `data`, `files`
- Reserved words: `anthropic-*`, `claude-*`

### Directory Purposes

| Directory     | Purpose                                    | Loaded Into Context?     | Token Cost |
| ------------- | ------------------------------------------ | ------------------------ | ---------- |
| `scripts/`    | Executable code (deterministic operations) | No (executed via Bash)   | None       |
| `references/` | Documentation (API docs, examples)         | Yes (via Read tool)      | High       |
| `assets/`     | Templates, configs, static files           | No (path reference only) | None       |

**Key Insight**: Scripts execute without loading code into context. Only script OUTPUT consumes tokens.

---

## 3. SKILL.md Specification

### Complete Structure

```yaml
---
name: skill-name
description: What this skill does. Use when [conditions]. Trigger with "[phrases]".
---

# Skill Name

Brief purpose statement (1-2 sentences).

## Overview

What this skill does, when to use it, key capabilities.

## Prerequisites

Required tools, APIs, environment variables, packages.

## Instructions

### Step 1: [Action Verb]
[Imperative instructions]

### Step 2: [Action Verb]
[More instructions]

## Output

What artifacts this skill produces.

## Error Handling

Common failures and solutions.

## Examples

Concrete usage examples with input/output.

## Resources

Links to bundled files using {baseDir} variable.
```

---

## 4. YAML Frontmatter Fields

The frontmatter schema is split into three layers:

1. **Required at Anthropic spec floor** — `name`, `description`. Citations: sources 1, 2, 5, 6, 7 above. These are the only two fields Anthropic itself requires; every other layer below is an Intent Solutions enterprise addition that sits on top of (not under) Anthropic's spec.
2. **Required at IS enterprise / marketplace tier** — the 8-field set: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, `tags`. Missing any of these = ERROR at marketplace tier. The IS marketplace is intentionally stricter than Anthropic's permissive spec floor — every shipped skill carries full tracking + governance metadata. Restored in schema 3.3.0 after the 3.0.0–3.2.0 experiments tried to demote them to "polish".
3. **Optional Anthropic + AgentSkills.io fields** — `model`, `effort`, `argument-hint`, `arguments`, `paths`, `shell`, `context`, `agent`, `user-invocable`, `disable-model-invocation`, `hooks`, `metadata`, `when_to_use`. Validated only when present; never required.

> **NON-NEGOTIABLE**: the IS enterprise required-field set is `{name, description, allowed-tools, version, author, license, compatibility, tags}` — full stop. Reframing tracking metadata (`version`, `author`, `license`) as "optional polish" is the bad direction that 3.3.0 explicitly reverted. See `000-docs/SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES.

### 4.1 Anthropic Spec Floor — `name` and `description`

#### `name`

**Type**: string
**Required**: YES
**Max Length**: 64 characters
**Constraints**:

- Lowercase letters, numbers, and hyphens only
- No XML tags
- Cannot contain reserved words: `"anthropic"`, `"claude"`

**Purpose**: Serves as the command identifier when Claude invokes the Skill tool.

**Examples**:

```yaml
name: processing-pdfs          # Good - gerund form
name: pdf-processing           # Good - noun phrase
name: PDF_Processing           # Bad - uppercase
name: claude-helper            # Bad - reserved word
```

#### `description`

**Type**: string
**Required**: YES
**Max Length**: 1024 characters
**Constraints**:

- Must be non-empty
- No XML tags
- Must use **third person** voice (injected into system prompt)

**Purpose**: Primary signal for Claude's skill selection. Claude uses this to decide when to activate the skill.

**Formula**:

```
[Primary capabilities]. [Secondary features]. Use when [scenarios]. Trigger with "[phrases]".
```

**Good Examples**:

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.

description: Analyze Polymarket prediction market contracts using TimeGPT forecasting. Fetches contract odds, transforms to time series, generates price predictions with confidence intervals. Use when analyzing prediction markets, forecasting contract prices, or comparing platform odds. Trigger with 'forecast Polymarket', 'analyze prediction market'.
```

**Bad Examples**:

```yaml
description: Helps with documents          # Too vague
description: I can process your PDFs       # Wrong voice (first person)
description: You can use this for data     # Wrong voice (second person)
```

### Optional Fields

#### `allowed-tools`

**Type**: comma-separated string, space-separated string, or YAML list (all three forms accepted; v3.3.1)
**Required**: YES at IS enterprise / marketplace tier; optional at Anthropic spec floor
**Default**: No pre-approved tools (user prompted for each)

**Purpose**: Pre-approves tools **scoped to skill execution only**. Tools revert to normal permissions after skill completes.

**Syntax Examples** — Anthropic accepts all three forms ([code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills): _"Accepts a space-separated string or a YAML list."_):

```yaml
# Comma-separated string (legacy IS form)
allowed-tools: "Read,Write,Glob,Grep,Edit"

# Space-separated string (Anthropic canonical form — paren-depth aware)
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)

# YAML list (Anthropic-documented form, v3.3.1 fix)
allowed-tools:
  - Read
  - Write
  - Bash(npm:*)
  - Edit

# Scoped bash commands (restrict to specific commands)
allowed-tools: "Bash(git status:*),Bash(git diff:*),Read,Grep"

# NPM-scoped operations
allowed-tools: "Bash(npm:*),Bash(npx:*),Read,Write"

# Read-only audit
allowed-tools: "Read,Glob,Grep"
```

**v3.3.1 parser note**: prior to schema 3.3.1 the IS validator rejected the YAML-list form with _"must be a comma-separated string (CSV), not a YAML array"_ — that was a divergence from Anthropic's documented behavior. 3.3.1 accepts all three forms; existing CSV skills still pass unchanged.

**Security Principle**: Grant ONLY tools the skill actually requires. Over-specifying creates unnecessary attack surface.

**NOTE**: Only supported in Claude Code, not claude.ai web version.

#### `model`

**Type**: string
**Required**: No
**Default**: `"inherit"` (use session model)

**Purpose**: Override the session model for skill execution.

**Examples**:

```yaml
model: inherit                           # Use current session model (default)
model: opus                              # Force Opus shorthand
model: sonnet                            # Force Sonnet shorthand
model: haiku                             # Force Haiku shorthand
```

**Guidance**: Reserve model overrides for genuinely complex tasks. Higher-capability models increase cost and latency.

**Use shorthand model values** (`opus` / `sonnet` / `haiku` / `inherit`) — full model IDs (e.g., `claude-opus-4-5-20251101`) bind a skill to a specific dated release and break silently when that release is retired. Shorthand values resolve to whichever model is currently the default for that family.

> **`version` and `license` moved**: prior to schema 3.3.0 these fields were duplicated here under "Optional Fields" with `Required: No`. Schema 3.3.0 restored them to the IS enterprise required-field set; their canonical specification now lives in **section 4.6 IS Enterprise Required Fields** below alongside `author`, `tags`, and `compatibility`. Anthropic's spec floor still treats these as optional — they are required only at the IS enterprise / marketplace tier.

#### `mode`

**Type**: boolean
**Required**: No
**Default**: `false`

**Purpose**: When `true`, categorizes the skill as a "mode command" appearing in a prominent UI section separate from utility skills.

**Use Case**: Skills that fundamentally transform Claude's behavior for an extended session.

```yaml
mode: true     # Appears in "Mode Commands" section
mode: false    # Appears in regular skills list (default)
```

#### `disable-model-invocation`

**Type**: boolean
**Required**: No
**Default**: `false`

**Purpose**: When `true`, removes the skill from the `<available_skills>` list. Users can still invoke manually via `/skill-name`.

**Use Cases**:

- Dangerous operations requiring explicit user action
- Infrastructure/deployment skills
- Skills that should never auto-activate

```yaml
disable-model-invocation: true    # Manual invocation only
disable-model-invocation: false   # Auto-discovery enabled (default)
```

#### `when_to_use`

**Type**: string
**Required**: No
**Source**: [`code.claude.com/docs/en/skills#frontmatter-reference`](https://code.claude.com/docs/en/skills#frontmatter-reference) — _"Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap."_

```yaml
description: Generate PDF reports from markdown.
when_to_use: |
  Use when the user asks to produce a PDF, export a report, or convert
  a Markdown file. Trigger phrases: "build a PDF", "export this", "make a report".
```

> **Correction note**: Earlier IS spec versions classified `when_to_use` as undocumented or deprecated. That was a misread of the Claude Code skills doc. Schema 3.1.0 (2026-04-28) restored it as a documented optional field.

#### `arguments`

**Type**: string or array (space-separated string OR YAML list)
**Required**: No
**Source**: [`code.claude.com/docs/en/skills#frontmatter-reference`](https://code.claude.com/docs/en/skills#frontmatter-reference)

Named positional arguments for `$name` substitution in the skill body. Names map to argument positions in order.

```yaml
arguments: issue branch          # String form
# or:
arguments: [issue, branch]       # YAML list

# Body uses $issue and $branch substitutions
```

#### `paths`

**Type**: string or array
**Required**: No

Glob patterns that limit when the skill auto-activates. When set, Claude loads the skill automatically only when working with files matching the patterns.

```yaml
paths: src/**/*.py, tests/**/*.py
# or:
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
```

#### `shell`

**Type**: string
**Valid values**: `bash` (default), `powershell`
**Required**: No

Shell to use for `` !`command` `` and ` ```! ` blocks in this skill. PowerShell on Windows requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`.

```yaml
shell: bash
shell: powershell
```

---

## 4.5 Optional Spec Fields (AgentSkills.io)

These fields are documented as optional in `agentskills.io/specification`. Any of them may appear at the top level. The validator accepts them at every tier and validates only their type/format.

#### `compatibility`

**Type**: string (free-text)
**Required**: NO
**Max length**: 500 characters
**Source**: [`agentskills.io/specification`](https://agentskills.io/specification)

**Purpose**: Indicates environment requirements (intended product, system packages, network access, etc.).

**Examples** (taken from / aligned with the AgentSkills.io spec):

```yaml
# Single platform
compatibility: "Designed for Claude Code"

# Multi-platform (free-text — no allow-list)
compatibility: "Designed for Claude Code, also compatible with Codex and OpenClaw"

# Runtime requirements
compatibility: "Requires Python 3.10+ with uv installed"
compatibility: "Requires git, docker, and jq on PATH"
compatibility: "Node.js >= 18, npm >= 9"

# Network / capability requirements
compatibility: "Requires network access to api.example.com (port 443)"
```

> **Migration note**: This field replaces the deprecated Intent Solutions `compatible-with` CSV-platform-list field, which had a closed allow-list and was not part of any published spec. Use `python3 scripts/batch-remediate.py --migrate-compatible-with` to translate existing files.

#### `metadata`

**Type**: object (mapping of arbitrary key-value pairs)
**Required**: NO
**Source**: [`agentskills.io/specification`](https://agentskills.io/specification)

**Purpose**: Free-form key-value mapping for any author-supplied metadata.

**Examples**:

```yaml
metadata:
  category: devops
  difficulty: intermediate
  language: python

# Or used as a container for fields the AgentSkills.io spec lists under metadata.*:
metadata:
  version: "1.2.0"
  author: "Jane Smith <jane@example.com>"
```

The validator accepts both top-level (e.g. `version: "1.2.0"`) and `metadata.*`-nested forms. The validator does not reject unknown keys inside `metadata`.

---

## 4.6 IS Enterprise Required Fields (Intent Solutions Extension)

These fields are **not** part of Anthropic's published spec — they are an Intent Solutions extension that **sits on top of** Anthropic's permissive spec floor. They are **required at the IS enterprise / marketplace tier** for richer discovery, governance, attribution, and lifecycle tracking. The validator emits **errors** (not warnings) when they are missing at marketplace tier (`--marketplace`). At standard tier (which mirrors Anthropic's spec floor of `name` + `description` only), these fields are validated when present but not required.

> **Anti-pattern (reverted in 3.3.0)**: schema versions 3.0.0–3.2.0 demoted these fields to "marketplace polish" with warning-only enforcement. That direction broke the marketplace gate — the IS rubric is intentionally stricter than Anthropic's spec floor, not aligned to it. See `000-docs/SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES for the full post-mortem.

#### `version`

**Type**: string (semver: `MAJOR.MINOR.PATCH`)
**Required**: YES at IS enterprise / marketplace tier

```yaml
version: '1.0.0'
```

#### `author`

**Type**: string
**Required**: YES at IS enterprise / marketplace tier
**Format**: `Name <email>` or `Name`

```yaml
author: 'Jeremy Longshore <jeremy@intentsolutions.io>'
```

#### `license`

**Type**: string
**Required**: YES at IS enterprise / marketplace tier
**Purpose**: License terms reference (SPDX identifier or human-readable description).

```yaml
license: "MIT"
license: "Proprietary - See LICENSE.txt"
license: "Apache-2.0"
```

#### `tags`

**Type**: array of strings
**Required**: YES at IS enterprise / marketplace tier (improves marketplace discovery + categorization)

```yaml
tags: ['security', 'audit', 'compliance']
```

#### IS Enterprise / Marketplace Required-Fields Summary

| Field             | Anthropic spec | AgentSkills.io spec       | IS marketplace tier                                                  |
| ----------------- | -------------- | ------------------------- | -------------------------------------------------------------------- |
| `name`            | Required       | Required                  | Required (error)                                                     |
| `description`     | Required       | Required                  | Required (error)                                                     |
| `allowed-tools`   | Optional       | Optional                  | **Required (error)**                                                 |
| `version`         | Not in spec    | Optional under `metadata` | **Required (error)**                                                 |
| `author`          | Not in spec    | Optional under `metadata` | **Required (error)**                                                 |
| `license`         | Not in spec    | Optional                  | **Required (error)**                                                 |
| `compatibility`   | Not in spec    | Optional (max 500 chars)  | **Required (error)**                                                 |
| `tags`            | Not in spec    | Not in spec               | **Required (error)**                                                 |
| `compatible-with` | Not in spec    | Not in spec               | **Deprecated** — migrate to `compatibility` (parsed as alias, warns) |

> Every "Required" cell in the Anthropic / AgentSkills.io columns is anchored to a specific source in the Sources block at the top of this document. The IS marketplace tier sits intentionally **on top of** the Anthropic spec floor — Anthropic's spec is permissive (only `name` + `description` required); the IS marketplace is strict (full 8-field tracking + governance metadata required). Demoting any of these eight fields back to "warn" or "polish" breaks the marketplace gate; see `000-docs/SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES for the post-mortem of the 3.0.0–3.2.0 experiments that did exactly that and were reverted in 3.3.0.

---

## 5. Instruction-Body Best Practices

### Recommended Markdown Layout

```markdown
# [Skill Name]

[1-2 sentence purpose statement]

## Overview

[What this skill does, when to use it, key capabilities - 3-5 sentences]

## Prerequisites

**Required**:

- [Tool/API/package 1]
- [Tool/API/package 2]

**Environment Variables**:

- `API_KEY_NAME`: [Description]

**Optional**:

- [Nice-to-have dependency]

## Instructions

### Step 1: [Action Verb]

[Clear, imperative instructions]

### Step 2: [Action Verb]

[More instructions]

## Output

This skill produces:

- [File/artifact 1]
- [File/artifact 2]

## Error Handling

**Common Failures**:

1. **Error**: [Error message or condition]
   **Solution**: [How to fix]

2. **Error**: [Another failure]
   **Solution**: [Resolution]

## Examples

### Example 1: [Scenario]

**Input**:
[Example input]

**Output**:
[Example output]

### Example 2: [Advanced Scenario]

[Another example]

## Resources

- Advanced patterns: `{baseDir}/references/ADVANCED.md`
- API reference: `{baseDir}/references/API_DOCS.md`
- Utility script: `{baseDir}/scripts/validate.py`
```

### Content Guidelines

| Guideline          | Requirement                                                         |
| ------------------ | ------------------------------------------------------------------- |
| **Size Limit**     | Keep SKILL.md body under **500 lines**                              |
| **Token Budget**   | Target ~2,500 tokens, max 5,000 tokens                              |
| **Language**       | Use **imperative voice** ("Analyze data", not "You should analyze") |
| **Paths**          | Always use `{baseDir}` variable, NEVER hardcode absolute paths      |
| **Examples**       | Include at least **2-3 concrete examples** with input/output        |
| **Error Handling** | Document **4+ common failures** with solutions                      |
| **Voice**          | Third person in descriptions, imperative in instructions            |

### Progressive Disclosure Patterns

**When SKILL.md exceeds 400 lines, split content:**

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

[Basic instructions]

## Advanced features

**Form filling**: See FORMS.md
**API reference**: See REFERENCE.md
```

**Pattern 2: Domain-specific organization**

```
bigquery-skill/
├── SKILL.md (overview)
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md
```

**Pattern 3: Conditional details**

```markdown
For basic edits, modify XML directly.
**For tracked changes**: See REDLINING.md
```

### Critical Rule: One-Level-Deep References

**AVOID deeply nested references**. Claude may only partially read nested files.

**Bad**:

```
SKILL.md → advanced.md → details.md → actual_info.md
```

**Good**:

```
SKILL.md → advanced.md
SKILL.md → reference.md
SKILL.md → examples.md
```

---

## 6. Security & Safety Guidance

### Choosing `allowed-tools` Conservatively

**Principle of Least Privilege**: Grant ONLY tools the skill actually needs.

**Good Examples**:

```yaml
# Read-only audit skill
allowed-tools: "Read,Glob,Grep"

# File transformation skill
allowed-tools: "Read,Write,Edit"

# Git operations only
allowed-tools: "Bash(git:*),Read,Grep"
```

**Bad Examples**:

```yaml
# Overly permissive - unnecessary attack surface
allowed-tools: "Bash,Read,Write,Edit,Glob,Grep,WebSearch,Task,Agent"

# Unscoped bash - allows any command
allowed-tools: "Bash"
```

### When to Use `disable-model-invocation: true`

Set this flag for skills that:

- Perform destructive operations (delete files, drop databases)
- Deploy to production environments
- Access sensitive credentials
- Run irreversible commands
- Should NEVER auto-activate

```yaml
---
name: deploy-production
description: Deploy application to production. Dangerous - requires explicit invocation.
disable-model-invocation: true
allowed-tools: 'Bash(deploy:*),Read,Glob'
---
```

### Security Considerations

**CRITICAL**: Only use Skills from trusted sources.

Before using an untrusted skill:

- [ ] Review all bundled files (SKILL.md, scripts, resources)
- [ ] Check for unusual network calls
- [ ] Inspect scripts for malicious code
- [ ] Verify tool invocations match stated purpose
- [ ] Validate external URLs (if any)

**Malicious skills could**:

- Exfiltrate data via network calls
- Access unauthorized files
- Misuse tools (Bash for system manipulation)
- Inject instructions overriding safety guidelines

---

## 7. Model Selection Guidance

### When to Inherit vs Override

| Scenario                   | Recommendation                 |
| -------------------------- | ------------------------------ |
| Most skills                | `model: inherit` or omit field |
| Complex reasoning required | Consider `claude-opus-4-*`     |
| Fast, simple tasks         | `claude-haiku-*`               |
| Balanced performance       | `claude-sonnet-4-*`            |

### Trade-offs

| Model  | Speed    | Cost   | Capability        |
| ------ | -------- | ------ | ----------------- |
| Haiku  | Fast     | Low    | Basic tasks       |
| Sonnet | Balanced | Medium | Most tasks        |
| Opus   | Slower   | High   | Complex reasoning |

### Testing Across Models

**Always test skills with all models you plan to use:**

- **Haiku**: Does the skill provide sufficient guidance?
- **Sonnet**: Is content clear and efficient?
- **Opus**: Are instructions avoiding over-explanation?

What works for Opus may need more detail for Haiku.

---

## 8. Production-Readiness Checklist

### Naming & Description

- [ ] `name` matches folder name (lowercase + hyphens)
- [ ] `name` is under 64 characters
- [ ] `description` under 1024 characters
- [ ] `description` uses third person voice
- [ ] `description` includes what + when + trigger phrases
- [ ] No reserved words (`anthropic`, `claude`)

### Structure & Tools

- [ ] SKILL.md at root of skill folder
- [ ] Body under 500 lines
- [ ] Uses `{baseDir}` for all paths
- [ ] No hardcoded absolute paths
- [ ] `allowed-tools` includes only necessary tools
- [ ] Forward slashes in all paths (not backslashes)

### Instructions Quality

- [ ] Has all required sections (Overview, Prerequisites, Instructions, Output, Error Handling, Examples, Resources)
- [ ] Uses imperative voice
- [ ] 2-3 concrete examples with input/output
- [ ] 4+ common errors documented with solutions
- [ ] One-level-deep file references only

### Testing

- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Trigger phrases activate skill correctly
- [ ] Scripts execute without errors
- [ ] Examples produce expected output
- [ ] No false positive activations

---

## 9. Versioning & Evolution

### Semantic Versioning

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes, clarifications
  │     └──────── New features, additive changes
  └────────────── Breaking changes to interface
```

**Examples**:

- `1.0.0` → Initial release
- `1.1.0` → Added new workflow step
- `1.0.1` → Fixed typo in instructions
- `2.0.0` → Changed output format (breaking)

### Changelog Notes

Include version history in SKILL.md:

```markdown
## Version History

- **v2.0.0** (2025-12-01): Breaking - Changed output format to JSON
- **v1.1.0** (2025-11-15): Added batch processing support
- **v1.0.0** (2025-11-01): Initial release
```

### Deprecation Strategy

When deprecating a skill:

1. Add deprecation notice to description:

   ```yaml
   description: '[DEPRECATED - Use new-skill instead] Original description...'
   ```

2. Set `disable-model-invocation: true` to prevent auto-activation

3. Keep skill available for manual invocation during transition

4. Remove entirely in next major version

---

## 10. Canonical SKILL.md Template

````yaml
---
name: your-skill-name
description: |
  [Primary capabilities as action verbs]. [Secondary features].
  Use when [3-4 trigger scenarios].
  Trigger with "[phrase 1]", "[phrase 2]", "[phrase 3]".
allowed-tools: "Read,Write,Glob,Grep,Edit"
version: "1.0.0"
---

# [Skill Name]

[1-2 sentence purpose statement explaining what this skill does.]

## Overview

[3-5 sentences covering:]
- What this skill does
- When to use it
- Key capabilities
- What it produces

## Prerequisites

**Required**:
- [Tool/API/package 1]: [Brief purpose]
- [Tool/API/package 2]: [Brief purpose]

**Environment Variables**:
- `ENV_VAR_NAME`: [Description and how to obtain]

**Optional**:
- [Nice-to-have dependency]: [When needed]

## Instructions

### Step 1: [Action Verb - e.g., "Analyze Input"]

[Clear, imperative instructions for this step]

```bash
# Example command if applicable
python {baseDir}/scripts/step1.py --input data.json
````

**Expected result**: [What should happen]

### Step 2: [Action Verb - e.g., "Transform Data"]

[Instructions for next step]

### Step 3: [Action Verb - e.g., "Generate Output"]

[Final step instructions]

## Output

This skill produces:

- **[Artifact 1]**: [Description and format]
- **[Artifact 2]**: [Description and format]
- **[Report/Summary]**: [Description]

## Error Handling

### Common Failures

1. **Error**: `[Error message or condition]`
   **Cause**: [Why this happens]
   **Solution**: [How to fix]

2. **Error**: `[Another error]`
   **Cause**: [Reason]
   **Solution**: [Resolution]

3. **Error**: `[Third error]`
   **Cause**: [Reason]
   **Solution**: [Fix]

4. **Error**: `[Fourth error]`
   **Cause**: [Reason]
   **Solution**: [Fix]

## Examples

### Example 1: [Basic Scenario]

**User Request**: "[What user says]"

**Input**:

```
[Example input data]
```

**Output**:

```
[Expected output]
```

### Example 2: [Advanced Scenario]

**User Request**: "[More complex request]"

**Input**:

```
[Input data]
```

**Output**:

```
[Expected result]
```

## Resources

**Reference Documentation**:

- API reference: `{baseDir}/references/API_REFERENCE.md`
- Advanced patterns: `{baseDir}/references/ADVANCED.md`

**Utility Scripts**:

- Data processor: `{baseDir}/scripts/process.py`
- Validator: `{baseDir}/scripts/validate.py`

**Templates**:

- Report template: `{baseDir}/assets/report_template.md`

## Version History

- **v1.0.0** (YYYY-MM-DD): Initial release

````

---

## 11. Minimal Example Skill

### Structured PR Review Helper

```yaml
---
name: reviewing-pull-requests
description: |
  Analyze pull request diffs and generate structured code reviews.
  Checks for bugs, security issues, performance problems, and style violations.
  Use when reviewing PRs, analyzing code changes, or checking diffs.
  Trigger with "review this PR", "check my code changes", "analyze diff".
allowed-tools: "Read,Grep,Glob,Bash(git:*)"
version: "1.0.0"
---

# Structured PR Review Helper

Generate comprehensive, structured code reviews from git diffs.

## Overview

This skill analyzes code changes and produces structured review feedback covering:
- Bug detection and edge cases
- Security vulnerabilities
- Performance considerations
- Code style and maintainability
- Test coverage gaps

## Prerequisites

**Required**:
- Git repository with staged or committed changes
- Read access to codebase

**Optional**:
- Project-specific style guide in `.github/STYLE_GUIDE.md`

## Instructions

### Step 1: Get the Diff

```bash
# For staged changes
git diff --staged

# For specific PR/branch
git diff main...feature-branch
````

### Step 2: Analyze Each Changed File

For each modified file:

1. Read the full file for context
2. Identify the nature of changes (new feature, bug fix, refactor)
3. Check for issues in each category

### Step 3: Generate Structured Review

Produce review in this format:

```markdown
## PR Review: [Brief Title]

### Summary

[1-2 sentence overview of changes]

### Findings

#### Critical Issues

- [ ] [Issue description with file:line reference]

#### Suggestions

- [ ] [Improvement suggestion]

#### Questions

- [ ] [Clarification needed]

### Recommendation

[APPROVE / REQUEST_CHANGES / COMMENT]
```

## Output

- Structured markdown review
- Categorized findings (Critical, Suggestions, Questions)
- Clear recommendation

## Error Handling

1. **Error**: No diff available
   **Solution**: Ensure changes are staged or specify correct branch comparison

2. **Error**: Binary files in diff
   **Solution**: Skip binary files, note in review that manual check needed

3. **Error**: Large diff (>1000 lines)
   **Solution**: Focus on most critical files, suggest splitting PR

4. **Error**: Missing context (file deleted)
   **Solution**: Note inability to review deleted code, focus on remaining changes

## Examples

### Example 1: Simple Bug Fix Review

**User Request**: "Review my bug fix PR"

**Output**:

```markdown
## PR Review: Fix null pointer in user validation

### Summary

Adds null check before accessing user.email property.

### Findings

#### Critical Issues

- None

#### Suggestions

- [ ] Consider adding unit test for null user case (src/validation.ts:45)

#### Questions

- [ ] Should we also check for empty string?

### Recommendation

APPROVE - Good defensive fix, minor test suggestion
```

### Example 2: Security-Sensitive Change

**User Request**: "Check this authentication change"

**Output**:

```markdown
## PR Review: Update JWT token validation

### Summary

Modifies token expiration handling and adds refresh token support.

### Findings

#### Critical Issues

- [ ] Token secret exposed in error message (src/auth.ts:78)
- [ ] Missing rate limiting on refresh endpoint (src/routes/auth.ts:112)

#### Suggestions

- [ ] Add token rotation on refresh
- [ ] Log authentication failures for monitoring

### Recommendation

REQUEST_CHANGES - Security issues must be addressed
```

```

---

## 12. Author Checklist

Run through this checklist every time you create or update a skill:

### Before Writing

- [ ] Identified clear, single-purpose capability
- [ ] Confirmed no existing skill handles this
- [ ] Gathered all necessary reference materials

### Frontmatter — Required (Anthropic spec)

- [ ] `name`: lowercase, hyphens, under 64 chars
- [ ] `description`: third person, under 1024 chars, includes what + when + triggers

### Frontmatter — Optional (Anthropic + AgentSkills.io spec)

- [ ] `allowed-tools`: minimal necessary tools only — scope `Bash(git:*)` etc.
- [ ] `compatibility`: free-text environment requirements (max 500 chars)
- [ ] `metadata`: arbitrary key-value mapping if useful

### Frontmatter — Marketplace Polish (Intent Solutions extension, recommended)

- [ ] `version`: semver format (e.g. `1.0.0`)
- [ ] `author`: `Name <email>` format
- [ ] `license`: SPDX identifier (MIT recommended)
- [ ] `tags`: array of category keywords for marketplace discovery

### Frontmatter — Deprecated (do NOT use in new skills)

- [ ] `compatible-with`: replaced by `compatibility` (free-text per AgentSkills.io). See Schema Changelog v3.0.0.

### Content

- [ ] Body under 500 lines
- [ ] All required sections present
- [ ] Imperative voice throughout instructions
- [ ] `{baseDir}` used for all paths
- [ ] 2-3 concrete examples with input/output
- [ ] 4+ errors documented with solutions
- [ ] One-level-deep references only

### Testing

- [ ] Triggers correctly on intended phrases
- [ ] Does NOT trigger on unrelated requests
- [ ] Scripts execute successfully
- [ ] Tested with multiple models (Haiku, Sonnet, Opus)
- [ ] Team review completed (if applicable)

### Security

- [ ] No secrets or credentials in skill
- [ ] Tools appropriately scoped
- [ ] Dangerous operations require explicit invocation
- [ ] External dependencies audited

---

## 13. Open Questions / Potentially Out-of-Date Areas

### Confirmed Speculative or Unclear

1. ~~**`when_to_use` field**: Exists in codebase but undocumented.~~ **Resolved (2026-04-28)**: `when_to_use` is documented at `code.claude.com/docs/en/skills#frontmatter-reference`. See section 4.5 above for usage. Combined `description` + `when_to_use` capped at 1,536 chars.

2. **Token budget limits**: The 15,000-character limit for skill descriptions is from Lee Han Chung's analysis, not official docs. May vary by platform.

3. **Model override behavior**: Exact list of supported model IDs not documented. Test with specific models before relying on overrides.

4. **Concurrency**: Skills are described as "not concurrency-safe" but exact failure modes unclear. Avoid simultaneous skill invocations.

5. **`allowed-tools` on claude.ai**: Official docs state this field is only supported in Claude Code, not the web version.

### How to Verify

1. **Test skill behavior directly** in Claude Code with various model settings
2. **Monitor Anthropic's official changelog** for updates to Skills API
3. **Check Claude Code release notes** for new frontmatter fields
4. **Review official GitHub repo** at https://github.com/anthropics/skills for reference implementations

### Areas Requiring Human Review

- Platform-specific behavior differences (API vs claude.ai vs Claude Code)
- New frontmatter fields added in future releases
- Changes to token budgets or context limits
- Model-specific guidance as new models release

---

## References

### Official Anthropic Documentation

- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Official Skills Repository](https://github.com/anthropics/skills)

### Community Resources

- [Lee Han Chung Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Simon Willison on Claude Skills](https://simonwillison.net/2025/Oct/16/claude-skills/)

---

**Last Updated**: 2026-04-28
**Maintained By**: Intent Solutions (Jeremy Longshore)
**Status**: AUTHORITATIVE - Single Source of Truth for Claude Skills Development
**Schema Version**: 3.0.0 (see `000-docs/SCHEMA_CHANGELOG.md`)
**Validator**: `scripts/validate-skills-schema.py` v7.0
**Migration tooling**: `scripts/batch-remediate.py --migrate-compatible-with`
```
