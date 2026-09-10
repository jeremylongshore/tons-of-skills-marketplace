# Frontmatter Field Specification

Complete reference for SKILL.md frontmatter fields aligned with:

- AgentSkills.io open standard (required/optional fields)
- Claude Code platform extensions (runtime features)

---

## Required Fields (AgentSkills.io Minimum)

### name

- **Type**: string
- **Required**: Yes
- **Format**: kebab-case (lowercase letters, numbers, hyphens)
- **Length**: 1-64 characters
- **Rules**:
  - Must start with a letter
  - Must end with letter or number
  - No consecutive hyphens (`my--skill`)
  - No start/end hyphens (`-my-skill`, `my-skill-`)
  - Must match containing directory name
  - Cannot contain XML tags (`<`, `>` characters prohibited)
  - No reserved words in isolation (`anthropic`, `claude`)
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
- **Required**: Yes
- **Length**: 1-1024 characters
- **Rules**:
  - MUST be third person ("Generates...", "Analyzes...")
  - MUST include what it does AND when to use it
  - MUST include specific keywords for discovery
  - MUST NOT use first person (I can, I will, I'm, I help)
  - MUST NOT use second person (You can, You should, You will)
  - MUST NOT contain XML tags (no `<` or `>` characters)
  - Cannot contain reserved words: `anthropic`, `claude` (in isolation)
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

**Important**: The `description` field is injected directly into Claude's system prompt at startup. Third person voice prevents a discovery issue where Claude speaks as the skill author (e.g., "I can help you...") when deciding whether to activate the skill.

---

## Optional Fields (AgentSkills.io Spec)

### license

- **Type**: string
- **Purpose**: License for the skill
- **Format**: SPDX identifier or bundled file reference

```yaml
license: MIT
license: Apache-2.0
license: Complete terms in LICENSE.txt
```

### compatibility

- **Type**: string
- **Length**: 1-500 characters
- **Purpose**: Environment requirements (OS, runtime, tools, dependencies)
- **When to use**: When skill requires specific tools, OS, or runtime

```yaml
compatibility: "Requires Python 3.10+, pdflatex, and pandoc"
compatibility: "Linux/macOS only. Requires jq and curl"
compatibility: "Node.js 18+ with npm"
```

### version

- **Type**: string (top-level)
- **Format**: Semver (`X.Y.Z`)
- **Purpose**: Skill version for tracking updates

```yaml
version: 2.0.0
```

### author

- **Type**: string (top-level)
- **Format**: `Name <email>` (email recommended for Enterprise tier)
- **Purpose**: Skill author identification

```yaml
author: Jeremy Longshore <jeremy@intentsolutions.io>
```

### tags

- **Type**: array of strings
- **Purpose**: Discovery tags for categorization

```yaml
tags: [devops, ci, automation]
```

### metadata

- **Type**: object (arbitrary key-value map)
- **Purpose**: Custom data not covered by other top-level fields
- **Note**: Do NOT put `author`, `version`, `license`, or `tags` here — they belong at top-level

```yaml
metadata:
  category: development
  maintainer: team@example.com
```

### allowed-tools

- **Type**: string (comma or space-delimited)
- **Purpose**: Pre-approved tools the skill can use without user confirmation
- **Status**: Experimental in AgentSkills.io; widely used in Claude Code
- **Common built-ins**: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Agent, NotebookEdit, AskUserQuestion, Skill. Consult the official tools reference or the validator's `VALID_TOOLS` registry for the current complete set.
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
```

---

## Claude Code Extension Fields

These fields are platform-specific to Claude Code and not part of the AgentSkills.io open standard.

### argument-hint

- **Type**: string
- **Purpose**: Autocomplete hint shown after `/skill-name` in the command palette
- **When to use**: When skill accepts arguments via `$ARGUMENTS`

```yaml
argument-hint: "[issue-number]"
argument-hint: "[file-path]"
argument-hint: "[search-query]"
```

### disable-model-invocation

- **Type**: boolean
- **Default**: false
- **Purpose**: Prevent Claude from auto-activating; require explicit `/name` invocation

```yaml
disable-model-invocation: true   # Only via /skill-name
disable-model-invocation: false  # Can activate via natural language (default)
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

### model

- **Type**: string
- **Default**: inherit (uses parent/caller model)
- **Values**: `inherit`, `sonnet`, `haiku`, `opus`, `fable`, or a supported full model ID

```yaml
model: inherit                    # Use caller's model (recommended)
model: opus                       # Force Opus for complex tasks
model: haiku                      # Use Haiku for fast, simple tasks
model: sonnet                     # Use Sonnet for balanced tasks
```

**Avoid hardcoded model IDs** like `claude-opus-4-5-20251101` - they break on deprecation.

### effort

- **Type**: string
- **Default**: (inherits from caller)
- **Values**: `low`, `medium`, `high`, `xhigh`, `max`
- **Purpose**: Override model reasoning effort level
- **Note**: Available levels depend on the selected model
- **Added**: v2.1.80 (March 2026)

```yaml
effort: high                         # More reasoning for complex tasks
effort: low                          # Fast responses for simple tasks
```

*Source: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)*

### context

- **Type**: string
- **Values**: `fork`
- **Purpose**: Execute skill in isolated subagent context
- **When to use**: Long-running tasks, tasks that need isolation from main conversation

```yaml
context: fork  # Run in subagent
```

### agent

- **Type**: string
- **Purpose**: Specify subagent type when `context: fork` is set
- **Values**: `Explore`, `Plan`, `general-purpose`, or custom agent name

```yaml
context: fork
agent: Explore          # Fast codebase exploration
```

### hooks

- **Type**: object
- **Purpose**: Skill-scoped lifecycle hooks
- **Events**: PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd

```yaml
hooks:
  PreToolUse:
    - command: "echo 'Tool about to be used'"
      event: PreToolUse
```

---

## Deprecated / Removed Fields

| Field | Status | Migration |
|-------|--------|-----------|
| `mode` | Deprecated | Use `disable-model-invocation` instead |
| `compatible-with` | Deprecated | Replace with Agent Skills `compatibility` prose |

**Note**: `version`, `author`, `license`, `compatibility`, and `tags` are valid
top-level fields. The marketplace validator scores them at top level. Keep
`metadata` as a map for custom data rather than duplicating those fields.

---

## Recommended Field Order

```yaml
---
# Required (AgentSkills.io)
name: skill-name
description: |
  What it does. Use when [scenario].
  Trigger with "/skill-name" or "[natural phrase]".

# Tools (recommended)
allowed-tools: "Read,Write,Glob,Grep"

# Identity (top-level — marketplace validator scores these here)
version: 1.0.0
author: Name <email>
license: MIT

# Claude Code extensions (as needed)
model: inherit
# effort: high
argument-hint: "[arg]"
context: fork
agent: general-purpose
disable-model-invocation: false
user-invocable: true

# Marketplace discovery
tags: [devops, automation]

# Optional spec fields
compatibility: "Python 3.10+"

# Metadata (custom data only — NOT for author/version/license)
# metadata:
#   category: development
#   maintainer: team@example.com
---
```
