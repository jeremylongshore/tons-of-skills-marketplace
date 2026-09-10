# Anthropic Agent Spec — Official Reference

Source: https://code.claude.com/docs/en/sub-agents (fetched 2026-09-09)

## Supported Frontmatter Fields

Only `name` and `description` are required.

| Field | Required | Description |
|:------|:---------|:------------|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tools the subagent can use (allowlist). Inherits all tools if omitted |
| `disallowedTools` | No | Tools to deny, removed from inherited or specified list |
| `model` | No | `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, or `manual` (`default` alias) |
| `maxTurns` | No | Maximum number of agentic turns before the subagent stops |
| `skills` | No | Skills to preload at startup; unlisted skills remain invocable through the Skill tool |
| `mcpServers` | No | List of MCP servers; each entry is a configured-name string or one-key inline definition |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | Set to `true` to always run as background task. Default: `false` |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, or `max`; availability depends on the model |
| `isolation` | No | `worktree` — run in temporary git worktree |
| `color` | No | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | No | Auto-submitted as first user turn when running as main agent via `--agent` |
| `experimental` | No | Experimental options; `cacheTtl` accepts `5m` or `1h` in Claude Code v2.1.248+ |

Total: 17 official fields.

## Key Facts

- The **body** (markdown after frontmatter) becomes the **system prompt** that guides the subagent
- Subagents receive ONLY the system prompt + basic environment details, NOT the full Claude Code system prompt
- `tools` is an **allowlist** (like skills' `allowed-tools`)
- `disallowedTools` is a **denylist** — if both set, disallowed applied first, then tools resolved
- Naming parallel (marketplace note): agents use camelCase `disallowedTools`; skills use kebab-case `disallowed-tools` (schema 3.7.0+). The validator rejects either mismatch — never copy-paste between agent and skill frontmatter without renaming
- Subagents can spawn nested subagents when `Agent` is available, up to three
  layers below the main conversation by default. `CLAUDE_CODE_MAX_AGENT_SPAWN_DEPTH`
  can set the depth from 1 through 3; omit or deny `Agent` to prevent delegation.
- The `skills` field preloads full skill content, but subagents can still invoke
  unlisted project, user, and plugin skills through the Skill tool

## Plugin Agent Restrictions

Claude Code ignores these fields on plugin agents (`plugins/*/agents/*.md`):

- `hooks` — ignored when loading from plugin
- `mcpServers` — ignored when loading from plugin
- `permissionMode` — ignored when loading from plugin

These are standalone-only features. If needed, copy the agent to `.claude/agents/` or `~/.claude/agents/`.

## Tool Scoping

Main-thread agents launched with `--agent` can use `Agent(type)` syntax to restrict
which subagents they spawn. Inside a subagent, including `Agent` enables nested
delegation while the depth limit allows it, but a parenthesized type list is ignored.

## Skills Preloading

```yaml
skills:
  - api-conventions
  - error-handling-patterns
```

Full content of each skill is injected at startup. This is the inverse of `context: fork` in skills.

## Model Resolution Order

1. `CLAUDE_CODE_SUBAGENT_MODEL` env var
2. Per-invocation `model` parameter
3. Subagent definition's `model` frontmatter
4. Main conversation's model

## Example Agent File

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

## Scope Priority (highest to lowest)

1. Managed settings (organization-wide)
2. `--agents` CLI flag (current session only)
3. `.claude/agents/` (project)
4. `~/.claude/agents/` (personal)
5. Plugin `agents/` directory (where plugin enabled)
