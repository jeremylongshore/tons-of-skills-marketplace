---
title: "SKILL.md Frontmatter Reference"
description: "Complete field-by-field reference for SKILL.md frontmatter, path variables, string substitutions, and dynamic context injection (DCI) syntax used in Claude Code plugin skills."
section: "reference"
order: 1
keywords: ["SKILL.md", "frontmatter", "yaml", "schema", "skills", "allowed-tools", "DCI", "path variables", "string substitutions"]
officialLinks:
  - title: "Claude Code Skills Documentation"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Plugins Overview"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "concepts/skills"
  - "guides/write-a-skill"
  - "reference/allowed-tools"
---

## Overview

Every skill in a Claude Code plugin is defined by a single `SKILL.md` file located at `skills/<skill-name>/SKILL.md` within a plugin directory. The file consists of two parts: YAML frontmatter (delimited by `---`) and a markdown body containing the skill's instructions.

The frontmatter declares metadata that Claude Code uses to determine when and how to activate the skill, which tools it may access, and how it appears in the user interface. The markdown body below the frontmatter contains the actual instructions Claude follows when the skill is activated.

This reference documents every frontmatter field, path variable, string substitution, and dynamic context injection (DCI) pattern supported by the 2026 AgentSkills.io specification.

## Frontmatter Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Unique skill identifier in kebab-case. Must match the parent directory name (e.g., `skills/code-review/SKILL.md` uses `name: code-review`). |
| `description` | `string` | Explains when Claude should activate this skill. Include specific trigger phrases so Claude can match user intent accurately. Use the YAML `\|` literal block scalar for multi-line descriptions. |
| `allowed-tools` | `string` | Comma-separated list of tools this skill may use. Implements the principle of least privilege. See [Allowed Tools Reference](/docs/reference/allowed-tools) for the complete list. |

### Optional Metadata Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | `string` | none | Semantic version string (e.g., `"1.0.0"`, `"2.3.1"`). Follow [SemVer](https://semver.org/) conventions. |
| `author` | `string` | none | Author attribution in the format `"Name <email>"`. The email portion is optional but recommended for marketplace listings. |
| `license` | `string` | none | SPDX license identifier (e.g., `MIT`, `Apache-2.0`, `ISC`). Must be a valid [SPDX expression](https://spdx.org/licenses/). |
| `tags` | `array` | `[]` | Discovery tags as a YAML array (e.g., `[devops, ci, deployment]`). Used by marketplace search and the `ccpi search` command. |
| `compatibility` | `string` | none | Environment requirements in human-readable form (e.g., `"Node.js >= 18"`, `"Python 3.10+, Docker"`). Displayed on marketplace listings. |
| `compatible-with` | `string` | none | Comma-separated list of platforms this skill supports (e.g., `"claude-code, cursor"`). Helps users identify cross-platform skills. |

### Behavioral Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `string` | (user's default) | Override the LLM model for this skill. Valid values: `"sonnet"`, `"haiku"`, `"opus"`. Use `haiku` for fast, low-cost operations; `opus` for complex reasoning. |
| `context` | `string` | none | Set to `"fork"` to run the skill in a subagent (separate context window). Useful for long-running tasks that should not pollute the main conversation. |
| `agent` | `string` | none | Subagent type when `context: fork` is set. Example: `"Explore"`. Determines the subagent's base capabilities. |
| `user-invocable` | `boolean` | `true` | When `false`, hides the skill from the `/` slash command menu. The skill can still be activated programmatically or by other skills via the `Skill` tool. Use for helper skills that should not be called directly. |
| `argument-hint` | `string` | none | Autocomplete hint shown in the slash command menu (e.g., `"<file-path>"`, `"<component-name>"`). Helps users understand what input the skill expects. |
| `hooks` | `object` | none | Lifecycle hooks that execute at specific points. Currently supports `pre-tool-call`. See [Hooks](#hooks) below. |

## Field Details and Examples

### name

The `name` field must use kebab-case and match the directory structure:

```
plugins/devops/ci-optimizer/
  skills/
    lint-config/
      SKILL.md          # name: lint-config
    pipeline-audit/
      SKILL.md          # name: pipeline-audit
```

### description

The `description` field is critical for skill activation. Claude reads this field to determine whether a skill is relevant to the user's request. Write descriptions that include specific trigger phrases and clearly state when the skill should be used.

**Good description (specific triggers):**

```yaml
description: |
  Use this skill when the user asks to review a pull request,
  audit code changes, or check a diff for issues. Trigger phrases
  include "review this PR", "check my changes", "code review",
  and "audit this diff".
```

**Poor description (too vague):**

```yaml
description: "Helps with code."
```

The `|` block scalar is recommended for multi-line descriptions. It preserves newlines and is easier to read than quoted strings.

### allowed-tools

A comma-separated string listing every tool the skill is permitted to use. Claude Code enforces this list at runtime — the skill cannot call any tool not listed here.

```yaml
allowed-tools: Read, Glob, Grep
```

Tools can include scoped patterns for `Bash`:

```yaml
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(git:*)
```

See [Allowed Tools Reference](/docs/reference/allowed-tools) for all valid tool names and patterns.

### model

Override the model for specific use cases:

```yaml
# Fast operations (linting, formatting, simple transforms)
model: haiku

# Standard operations (code generation, reviews)
model: sonnet

# Complex reasoning (architecture decisions, security audits)
model: opus
```

### hooks

The `hooks` field accepts an object with lifecycle event handlers. Currently, the only supported hook is `pre-tool-call`:

```yaml
hooks:
  pre-tool-call:
    command: "${CLAUDE_PLUGIN_ROOT}/scripts/validate-input.sh"
```

Hooks run in the plugin's execution context. Use `${CLAUDE_PLUGIN_ROOT}` to reference scripts relative to the plugin root. Hooks that exit with a non-zero status code prevent the tool call from proceeding.

### tags

Tags power discovery in the [Explore](/explore) page and `ccpi search`. Use lowercase, specific terms:

```yaml
tags: [terraform, infrastructure-as-code, aws, gcp]
```

Avoid generic tags like `code` or `tool` that do not aid discovery.

## Path Variables

Path variables are resolved at runtime and allow skills to reference files relative to their own location or the plugin root. These are used within bash commands and DCI expressions, not in markdown links.

| Variable | Resolves To | Available Since | Use Case |
|----------|-------------|-----------------|----------|
| `${CLAUDE_SKILL_DIR}` | Absolute path to the directory containing the current `SKILL.md` | 2.0.0 | Reference supporting files (templates, configs, data) co-located with the skill. |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to the plugin's root directory (where `plugin.json` lives) | 2.0.0 | Reference shared scripts, hooks, and resources at the plugin level. |
| `${CLAUDE_PLUGIN_DATA}` | Persistent data directory for this plugin | 2.1.78 | Store state that survives plugin updates and reinstalls (caches, user preferences, logs). |

### Path Variable Examples

Reference a template file next to the skill:

```markdown
Read the template at `${CLAUDE_SKILL_DIR}/templates/component.tsx.tpl` and use it
to generate the new component.
```

Run a shared validation script from the plugin root:

```yaml
hooks:
  pre-tool-call:
    command: "${CLAUDE_PLUGIN_ROOT}/scripts/check-prerequisites.sh"
```

Store persistent state across sessions:

```markdown
Save the analysis cache to `${CLAUDE_PLUGIN_DATA}/analysis-cache.json` so it
persists across plugin updates.
```

### Markdown Links vs. Path Variables

For referencing supporting documentation within a skill's instructions, use relative markdown links rather than path variables. Claude follows these links with the Read tool on demand:

```markdown
See API Reference for endpoint details.
Review Examples for usage patterns.
```

Reserve `${CLAUDE_SKILL_DIR}` for bash commands and DCI expressions where Claude needs an absolute filesystem path.

## String Substitutions

String substitutions are replaced before Claude processes the skill body. They inject user-provided arguments and session context.

| Substitution | Description |
|-------------|-------------|
| `$ARGUMENTS` | The entire argument string the user provided after the slash command. |
| `$0` | The full argument string (alias for `$ARGUMENTS`). |
| `$1` through `$9` | Positional arguments, split by whitespace. `$1` is the first word, `$2` is the second, and so on. |
| `${CLAUDE_SESSION_ID}` | Unique identifier for the current Claude Code session. Useful for generating session-scoped file names or cache keys. |

### Using argument-hint with Substitutions

Pair `argument-hint` with substitutions so users know what to provide:

```yaml
---
name: scaffold-component
description: |
  Generate a React component with tests and stories.
  Use when the user says "scaffold component" or "create component".
allowed-tools: Read, Write, Edit, Glob
argument-hint: "<ComponentName>"
---

Create a React component named `$1` with the following structure:
- `src/components/$1/$1.tsx` - Component implementation
- `src/components/$1/$1.test.tsx` - Unit tests
- `src/components/$1/$1.stories.tsx` - Storybook stories
```

When a user types `/scaffold-component Button`, the `$1` substitution resolves to `Button` before Claude sees the instructions.

## Dynamic Context Injection (DCI)

Dynamic Context Injection allows a skill to run shell commands at activation time and inject their output directly into the skill body. This pre-loads discovery data so Claude does not need to spend tool call rounds gathering basic context.

### Syntax

Place a backtick-wrapped command prefixed with `!` on its own line:

```markdown
!`command`
```

The command runs in the user's shell, and the stdout output replaces the DCI line verbatim before Claude processes the skill.

### DCI Examples

Inject the current git status:

```markdown
## Current Repository State

!`git status --short 2>/dev/null || echo 'Not a git repository'`
```

Detect the runtime environment:

```markdown
## Environment

!`node --version 2>/dev/null || echo 'Node.js not installed'`
!`python3 --version 2>/dev/null || echo 'Python not installed'`
!`docker --version 2>/dev/null || echo 'Docker not installed'`
```

### DCI Best Practices

1. **Always include fallbacks.** Commands may not be available on every system. Use `|| echo 'fallback message'` to prevent activation failures.

2. **Keep output small.** DCI output is injected into the skill body and consumes context window tokens. Produce summaries, not full file contents.

3. **Use `2>/dev/null` for stderr.** Suppress error messages that would clutter the injected context.

4. **Avoid side effects.** DCI commands run at activation time, before Claude has any context about the user's request. Never modify files or state in DCI commands.

5. **Redirect long output.** If a command may produce many lines, pipe through `head` or `tail`:

```markdown
!`git log --oneline -10 2>/dev/null || echo 'No git history'`
```

## Complete Example

Below is a fully-specified `SKILL.md` demonstrating all frontmatter fields and body features:

```yaml
---
name: deploy-audit
description: |
  Audit a deployment configuration for security issues, missing environment
  variables, and infrastructure misconfigurations. Use when the user says
  "audit deployment", "check deploy config", or "review infrastructure".
allowed-tools: Read, Glob, Grep, Bash(docker:*), Bash(kubectl:*)
version: 2.1.0
author: Jane Smith <jane@example.com>
license: MIT
model: sonnet
context: fork
agent: Explore
user-invocable: true
argument-hint: "<environment>"
compatibility: "Docker 20+, kubectl 1.25+"
compatible-with: claude-code
tags: [devops, security, deployment, kubernetes, docker]
hooks:
  pre-tool-call:
    command: "${CLAUDE_PLUGIN_ROOT}/scripts/check-kube-context.sh"
---

## Environment Detection

!`kubectl config current-context 2>/dev/null || echo 'No active Kubernetes context'`
!`docker --version 2>/dev/null || echo 'Docker not available'`

## Instructions

You are auditing the **$1** deployment environment. Perform the following checks:

1. Read all Dockerfiles and check for security issues (running as root, no .dockerignore, secrets in build args)
2. Review Kubernetes manifests for missing resource limits, missing health checks, and privileged containers
3. Check environment variable configuration for missing or placeholder values
4. Verify that secrets are referenced from a secret store, not hardcoded

Reference the security checklist for the complete audit criteria.

Save the audit report to `${CLAUDE_PLUGIN_DATA}/audits/$1-audit-$(date +%Y%m%d).md`.
```

## Validation

Run the universal validator to check your SKILL.md against the standard and enterprise tiers:

```bash
# Standard tier (Anthropic minimum requirements)
python3 scripts/validate-skills-schema.py --verbose plugins/category/your-plugin/

# Enterprise tier (100-point marketplace grading rubric)
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/your-plugin/

# Single skill validation
python3 scripts/validate-skills-schema.py --skills-only plugins/category/your-plugin/skills/your-skill/
```

The standard tier checks structural validity (required fields present, valid tool names, proper YAML). The enterprise tier applies a 100-point rubric covering documentation quality, body structure, code examples, and completeness.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `name` does not match directory name | Rename the directory or the `name` field so they match. |
| `description` is a single sentence without trigger phrases | Add 2-4 specific phrases users might say to activate this skill. |
| `allowed-tools` includes tools the skill never uses | Remove unused tools. Only list tools the skill actually needs. |
| DCI command has no fallback | Add `\|\| echo 'fallback'` after every DCI command. |
| Using `${CLAUDE_SKILL_DIR}` in markdown links | Use relative markdown links instead: `file`. |
| Listing invalid tool names in `allowed-tools` | Check the [Allowed Tools Reference](/docs/reference/allowed-tools) for the canonical list. |
| Using `argument-hint` without `$ARGUMENTS` or `$1` in the body | If you declare an argument hint, use the substitution variables in the skill body. |
