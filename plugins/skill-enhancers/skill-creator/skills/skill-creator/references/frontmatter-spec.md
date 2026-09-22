# Frontmatter Field Specification

Complete reference for SKILL.md and agent frontmatter fields.

**Source**: https://code.claude.com/docs/en/skills (Anthropic, 2026)

---

## Skill Frontmatter — Anthropic Standard (12 fields)

### name

- **Type**: string
- **Default**: directory name (if omitted)
- **Format**: kebab-case (lowercase letters, numbers, hyphens)
- **Length**: 1-64 characters
- **Rules**:
  - Must start with a letter
  - Must end with letter or number
  - No consecutive hyphens (`my--skill`)
  - No start/end hyphens (`-my-skill`, `my-skill-`)
  - Must match containing directory name
  - No reserved words in isolation (`anthropic`, `claude`)
  - No XML tags (`<`, `>`) — breaks frontmatter parsing
  - Gerund naming preferred (`processing-pdfs`, `analyzing-data`)

```yaml
name: email-composer      # Good
name: processing-pdfs     # Good - gerund style
name: code-review-v2      # Good
name: EmailComposer       # Bad - not kebab-case
name: -my-skill           # Bad - starts with hyphen
name: my--skill           # Bad - consecutive hyphens
```

### description

- **Type**: string (multi-line with `|` supported)
- **Default**: first paragraph of skill body (if omitted)
- **Length**: 1-1024 characters
- **Purpose**: Tells Claude what the skill does AND when to activate it
- **Rules**:
  - MUST be third person ("Generates...", "Analyzes...")
  - MUST include what it does AND when to use it
  - MUST include specific keywords for discovery
  - MUST NOT use first person (I can, I will, I'm, I help)
  - MUST NOT use second person (You can, You should, You will)
  - MUST NOT contain XML tags (`<`, `>`) — breaks frontmatter parsing
  - MUST NOT contain reserved words as standalone identifiers (`anthropic`, `claude`)
  - MUST NOT contain system prompt injection patterns (behavioral instructions belong in SKILL.md body, not description)
  - SHOULD include action verbs (analyze, create, generate, build, debug, optimize, validate)
  - SHOULD reference slash command if user-invocable

```yaml
# Good - clear what + when + keywords
description: |
  Generate PDF reports from markdown with professional styling and TOC.
  Use when converting documentation to distributable format.

# Good - specific keywords, natural when-to-use
description: |
  Analyze Python code for security vulnerabilities, dependency risks, and
  OWASP compliance issues. Activates during security audits or pre-deployment
  code reviews. Trigger with "/security-scan" or "scan for vulnerabilities".

# Bad - first person
description: "I help you create PDFs"

# Bad - no when-to-use context
description: "Generates PDF reports"

# Bad - too vague, no keywords
description: "A helpful tool for documents"
```

### when_to_use

- **Type**: string
- **Purpose**: Additional activation context appended to `description`
- **Limit**: Combined listing text is capped at 1536 characters

```yaml
when_to_use: Use after changing an agent definition or its validator.
```

**System prompt injection warning**: The `description` field is loaded into Claude's system prompt at startup for skill discovery. It must describe *what* and *when* only. Never include behavioral instructions ("Always respond in JSON", "Never use profanity"), persona definitions ("You are an expert..."), or override patterns ("Ignore previous instructions"). These belong in the SKILL.md body, not the description.

### allowed-tools

- **Type**: string (comma or space-delimited)
- **Purpose**: Pre-approved tools the skill can use without user confirmation
- **Common built-ins**: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Agent`, `TodoWrite`, `NotebookEdit`, `AskUserQuestion`, `Skill`. Consult the official tools reference or the validator's `VALID_TOOLS` registry for the current complete set.
- **MCP tools**: `ServerName:tool_name` format

```yaml
# Scoped Bash (best practice)
allowed-tools: "Read,Write,Glob,Grep,Bash(git:*),Bash(npm:*)"

# With MCP tool
allowed-tools: "Read,Write,MyMCPServer:fetch_data"

# Unscoped Bash (avoid - security risk)
allowed-tools: "Read,Write,Bash"  # Warning in Standard, Error in Enterprise
```

**Bash Scoping Patterns**:

```yaml
Bash(git:*)       # All git commands
Bash(npm:*)       # All npm commands
Bash(python:*)    # All python commands
Bash(mkdir:*)     # Directory creation
Bash(chmod:*)     # Permission changes
Bash(curl:*)      # HTTP requests
Bash(npx:*)       # npx execution
Bash(pnpm:*)      # pnpm commands
```

### disallowed-tools

- **Type**: string (comma-delimited) or YAML list of tool patterns
- **Schema**: 3.7.0+ — optional, omit by default
- **Purpose**: Defense-in-depth denylist. Removes the listed tools from the model while the skill is active, layered on top of the `allowed-tools` allowlist (parallel to it, not a replacement)
- **When to use**: The skill legitimately needs broad `allowed-tools` but should never reach for specific high-risk operations — `rm`, `curl` to arbitrary hosts, `.env` file edits, system-config writes
- **Cross-field rule**: A pattern appearing in BOTH `allowed-tools` AND `disallowed-tools` is a validator ERROR
- **Naming**: Skills use kebab-case `disallowed-tools`; agents use camelCase `disallowedTools`. The validator rejects either mismatch — never copy-paste between agent and skill frontmatter without renaming

```yaml
# String form
disallowed-tools: "Bash(rm:*),Bash(curl:*),Bash(wget:*),Bash(sudo:*)"

# YAML list form
disallowed-tools: [Bash(rm:*), Bash(curl:*), Edit(.env), Edit(.env.*), Write(.env), Write(.env.*)]
```

### model

- **Type**: string
- **Default**: inherit (uses parent/caller model)
- **Values**: `sonnet`, `haiku`, `opus`, `fable`, `inherit`, or a supported full model ID
- **Purpose**: Override the LLM model used when this skill runs

```yaml
model: inherit                    # Use caller's model (recommended)
model: opus                       # Force Opus for complex tasks
model: haiku                      # Use Haiku for fast, simple tasks
model: sonnet                     # Use Sonnet for balanced tasks
```

**Avoid hardcoded model IDs** like `claude-opus-4-5-20251101` — they break on deprecation.

### effort

- **Type**: string
- **Default**: (inherits from caller)
- **Values**: `low`, `medium`, `high`, `xhigh`, `max`
- **Purpose**: Override model reasoning effort level
- **Note**: Available levels depend on the selected model

```yaml
effort: high                         # More reasoning for complex tasks
effort: low                          # Fast responses for simple tasks
```

### argument-hint

- **Type**: string
- **Purpose**: Autocomplete hint shown after `/skill-name` in the command palette
- **When to use**: When skill accepts arguments via `$ARGUMENTS`

```yaml
argument-hint: "[issue-number]"
argument-hint: "[file-path]"
argument-hint: "[search-query]"
argument-hint: "<component-name>"
```

### arguments

- **Type**: string or array
- **Purpose**: Names positional arguments for `$name` substitution

```yaml
arguments: [file, mode]
```

### context

- **Type**: string
- **Values**: `fork` (only valid value)
- **Purpose**: Execute skill in isolated subagent context
- **When to use**: Long-running tasks, tasks that need isolation from main conversation

```yaml
context: fork  # Run in subagent
```

### agent

- **Type**: string
- **Requires**: `context: fork` must also be set
- **Purpose**: Specify subagent type when running in fork context
- **Values**: `Explore`, `Plan`, `general-purpose`, or custom agent name

```yaml
context: fork
agent: Explore          # Fast codebase exploration
```

### background

- **Type**: boolean
- **Default**: true when `context: fork`
- **Purpose**: Set `false` to wait for a forked skill's result in the invoking turn

```yaml
context: fork
background: false
```

### user-invocable

- **Type**: boolean
- **Default**: true
- **Purpose**: Control visibility in `/` command menu
- **When to use**: Set `false` for background knowledge skills that inform behavior

```yaml
user-invocable: false  # Hidden from / menu, loaded as background knowledge
user-invocable: true   # Visible in / menu (default)
```

### disable-model-invocation

- **Type**: boolean
- **Default**: false
- **Purpose**: Prevent Claude from auto-activating; require explicit `/name` invocation

```yaml
disable-model-invocation: true   # Only via /skill-name
disable-model-invocation: false  # Can activate via natural language (default)
```

### hooks

- **Type**: object
- **Purpose**: Skill-scoped lifecycle hooks
- **Events**: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`

```yaml
hooks:
  PreToolUse:
    - command: "echo 'Tool about to be used'"
      event: PreToolUse
  PostToolUse:
    - command: "${CLAUDE_PLUGIN_ROOT}/scripts/post-check.sh"
      event: PostToolUse
```

### paths

- **Type**: string or array
- **Purpose**: Restrict automatic activation to matching repository paths

```yaml
paths: ["packages/cli/**", "scripts/**"]
```

### shell

- **Type**: string
- **Values**: `bash`, `powershell`
- **Purpose**: Select the shell for dynamic `!` commands

```yaml
shell: bash
```

---

## Marketplace and Agent Skills fields

The marketplace requires the tracking fields below and also requires the
Agent Skills `license` and `compatibility` fields for publication.

### version

- **Type**: string
- **Format**: Semver (`X.Y.Z`)
- **Purpose**: Skill version for tracking updates and marketplace display

```yaml
version: 1.0.0
version: 2.3.1
```

### author

- **Type**: string
- **Format**: `Name <email>` (email required for Enterprise tier)
- **Purpose**: Skill author identification

```yaml
author: Jeremy Longshore <jeremy@intentsolutions.io>
```

### license

- **Type**: string
- **Format**: SPDX identifier or bundled file reference
- **Purpose**: License for the skill

```yaml
license: MIT
license: Apache-2.0
license: Complete terms in LICENSE.txt
```

### compatibility

- **Type**: string, maximum 500 characters
- **Purpose**: State environment or product requirements in prose

```yaml
compatibility: Requires Claude Code 2.1.248+ and Python 3.11+.
```

### tags

- **Type**: array of strings
- **Purpose**: Discovery tags for categorization and search

```yaml
tags: [devops, ci, automation]
tags: [security, python, code-review]
```

### metadata

- **Type**: object
- **Purpose**: Free-form Agent Skills metadata for external tooling

```yaml
metadata:
  category: development
```

`compatible-with` is a deprecated IS extension. Replace it with
`compatibility` prose.

---

## Agent Frontmatter — Anthropic Standard (17 fields)

Agent files live in `agents/*.md`. Field-naming warning: agents use camelCase `disallowedTools` (canonical sub-agents spec); skills use `allowed-tools` (allowlist) plus optional kebab-case `disallowed-tools` (schema 3.7.0+). The validator rejects either mismatch — never copy-paste between agent and skill frontmatter without renaming.

### name

- **Type**: string
- **Required**: Yes
- **Purpose**: Unique identifier for the agent

```yaml
name: code-reviewer
```

### description

- **Type**: string
- **Required**: Yes
- **Length**: 20-1536 characters under the IS contract; keep it concise enough for agent selection
- **Purpose**: Agent's specialty — shown in agent selection UI

```yaml
description: "Reviews code for bugs, performance issues, and style violations"
```

### model

- **Type**: string
- **Values**: `sonnet`, `haiku`, `opus`, `fable`, `inherit`, or a full Claude model ID
- **Purpose**: Override LLM model for this agent

```yaml
model: opus
```

### effort

- **Type**: string
- **Values**: `low`, `medium`, `high`, `xhigh`, `max` (model-dependent)
- **Purpose**: Override reasoning effort for agent turns

```yaml
effort: high
```

### maxTurns

- **Type**: integer
- **Purpose**: Max agentic loop iterations before stopping

```yaml
maxTurns: 10
maxTurns: 25
```

### tools

- **Type**: string or array
- **Purpose**: Tool allowlist (same format as skill `allowed-tools`)

```yaml
tools: "Read,Glob,Grep,Bash(git:*)"
```

### disallowedTools

- **Type**: array under the IS contract
- **Purpose**: Tool denylist — block specific tools (opposite of allowlist)

```yaml
disallowedTools: [mcp__dangerous_server, Write]
```

### skills

- **Type**: array
- **Purpose**: Skill names to preload when agent activates

```yaml
skills: [code-review, test-generator]
```

### mcpServers

- **Type**: array upstream; the compatibility validator also accepts an object
- **Purpose**: Configured server-name strings or one-key inline definitions
- **Plugin restriction**: NOT supported in plugin agents (ignored silently by runtime)

```yaml
mcpServers:
  - slack
  - myserver:
      command: "node"
      args: ["server.js"]
```

### hooks

- **Type**: object
- **Purpose**: Agent-scoped lifecycle hooks
- **Plugin restriction**: NOT supported in plugin agents (ignored silently by runtime)

```yaml
hooks:
  PreToolUse:
    - command: "echo 'pre-hook'"
```

### memory

- **Type**: string
- **Values**: `user`, `project`, `local`
- **Purpose**: Memory persistence scope for the agent

```yaml
memory: project
```

### background

- **Type**: boolean
- **Purpose**: Run agent as a background task

```yaml
background: true
```

### isolation

- **Type**: string
- **Values**: `worktree` (only valid value)
- **Purpose**: Run agent in an isolated git worktree

```yaml
isolation: worktree
```

### permissionMode

- **Type**: string
- **Values**: `default`, `manual`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`
- **Purpose**: Permission behavior for the agent
- **Plugin restriction**: NOT supported in plugin agents (ignored silently by runtime)

```yaml
permissionMode: acceptEdits
```

### color

- **Type**: string
- **Values**: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`
- **Purpose**: Display color in the task list and transcript

### initialPrompt

- **Type**: string
- **Purpose**: First user turn when the agent runs as the main session agent

### experimental

- **Type**: object
- **Current setting**: `cacheTtl` accepts `5m` or `1h` in Claude Code v2.1.248+

```yaml
experimental:
  cacheTtl: 5m
```

---

## plugin.json Field Summary (8 allowed fields)

The `.claude-plugin/plugin.json` manifest defines plugin identity. CI rejects any fields not in this list.

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | string | Yes | Plugin name (kebab-case) |
| `version` | string | Yes | Semver version |
| `description` | string | Yes | Plugin description |
| `author` | string | Yes | Author name or `Name <email>` |
| `repository` | string | No | GitHub repository URL |
| `homepage` | string | No | Plugin homepage URL |
| `license` | string | No | SPDX license identifier |
| `keywords` | array | No | Discovery keywords |

```json
{
  "name": "my-plugin",
  "version": "2.0.0",
  "description": "What this plugin does",
  "author": "Name <email>",
  "repository": "https://github.com/user/repo",
  "license": "MIT",
  "keywords": ["devops", "automation"]
}
```

---

## Deprecated / Invalid Fields

| Field | Status | Notes |
|-------|--------|-------|
| `mode` | Deprecated | Use `disable-model-invocation` instead |
| `compatible-with` | Deprecated | Replace with Agent Skills `compatibility` prose |
| `capabilities` | Invalid | Invented field, never part of any spec |
| `expertise_level` | Invalid | Invented field, never part of any spec |
| `activation_priority` | Invalid | Invented field, never part of any spec |

The marketplace validator will flag these fields as errors in Enterprise tier validation.

---

## Recommended Field Order

### Skill (SKILL.md)

```yaml
---
# Anthropic standard
name: skill-name
description: |
  What it does. Use when [scenario].
  Trigger with "/skill-name" or "[natural phrase]".
allowed-tools: "Read,Write,Glob,Grep,Bash(git:*)"
model: inherit
# effort: high
argument-hint: "[arg]"
# context: fork
# agent: general-purpose
user-invocable: true
disable-model-invocation: false
# hooks: {}

# Enterprise additions (marketplace-required)
version: 1.0.0
author: Name <email>
license: MIT
compatibility: Requires Claude Code 2.1.248+.
tags: [devops, automation]
---
```

### Agent (agents/*.md)

```yaml
---
# Required
name: agent-name
description: "Concise 20-1536 char description of the agent's specialty"

# Model control
model: opus
effort: high
maxTurns: 15

# Tool access
tools: [Read, Write, Glob, Grep]
# disallowedTools: [mcp__dangerous_server]

# Preloaded skills
# skills: [code-review, test-generator]

# Execution
# background: false
# isolation: worktree
# memory: project
# color: blue
# initialPrompt: "Start with the intake."
# experimental:
#   cacheTtl: 5m

# NOT supported in plugin agents (ignored by runtime):
# hooks: {}
# mcpServers: []
# permissionMode: default
---
```
