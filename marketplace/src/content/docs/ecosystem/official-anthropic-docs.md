---
title: "Official Anthropic Documentation Links"
description: "Organized directory of official Anthropic documentation for Claude Code. Find the right reference for skills, plugins, agents, hooks, MCP, CLI usage, and best practices."
section: "ecosystem"
order: 2
keywords: ["Anthropic documentation", "Claude Code docs", "official docs", "Claude Code reference", "skills documentation", "plugins documentation", "MCP documentation", "Claude Code CLI"]
officialLinks:
  - title: "Claude Code Overview"
    url: "https://code.claude.com/docs/en/overview"
  - title: "Claude Code Skills"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Plugins"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Claude Code Agents"
    url: "https://code.claude.com/docs/en/agents"
  - title: "Claude Code Hooks"
    url: "https://code.claude.com/docs/en/hooks"
  - title: "Claude Code MCP"
    url: "https://code.claude.com/docs/en/mcp"
  - title: "Claude Code CLI Reference"
    url: "https://code.claude.com/docs/en/cli-reference"
  - title: "Claude Code Best Practices"
    url: "https://code.claude.com/docs/en/best-practices"
relatedDocs:
  - "ecosystem/marketplace-overview"
  - "ecosystem/community-resources"
  - "ecosystem/faq"
---

## Why This Page Exists

Claude Code is Anthropic's product. The plugin and skill system is defined by Anthropic's specification. The Tons of Skills marketplace builds on top of that official foundation -- it does not replace it.

This page serves as an organized directory of the official Anthropic documentation for Claude Code, with context about what each section covers and guidance on when to consult the official docs versus the Tons of Skills docs. Bookmark it as your starting point whenever you need to look something up.

## Official Documentation Directory

The official Claude Code documentation lives at [code.claude.com/docs/en/](https://code.claude.com/docs/en/). Below is a topic-by-topic breakdown of what is covered and why it matters.

### Claude Code Overview

**URL:** [code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview)

This is the starting point for anyone new to Claude Code. It explains what Claude Code is -- an agentic coding assistant that runs in your terminal -- and covers the core capabilities: reading and editing files, running shell commands, reasoning about codebases, and interacting with developer tools.

**What you will find here:**

- What Claude Code does and how it differs from other AI assistants
- System requirements and supported platforms
- Authentication methods (API key, Claude Pro/Team/Enterprise subscriptions)
- Core interaction model: natural language instructions in the terminal
- How Claude Code reads your project context (CLAUDE.md, directory structure, git history)

**When to read this:** If you have never used Claude Code before, start here. If you are evaluating whether Claude Code fits your workflow, this page gives you the high-level picture.

### Skills

**URL:** [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

Skills are the fundamental building block of the Claude Code extension system. A skill is a SKILL.md file with YAML frontmatter that tells Claude Code when to activate and what instructions to follow. Skills auto-activate based on context -- they do not require a slash command.

**What you will find here:**

- SKILL.md file format and frontmatter schema
- How auto-activation works
- The `allowed-tools` field and tool permissions
- Supporting file references and relative markdown links
- Dynamic context injection (DCI) with the `` !`command` `` syntax
- Path variables: `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`
- String substitutions: `$ARGUMENTS`, `$0` through `$9`, `${CLAUDE_SESSION_ID}`
- The `context: fork` field for running skills in subagents
- Model overrides with the `model` field

**When to read this:** When you are writing a new skill, debugging why a skill is not activating, or trying to understand an advanced feature like DCI or subagent forking. This is the authoritative specification -- everything in the Tons of Skills marketplace conforms to it.

### Plugins

**URL:** [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

Plugins are the packaging format that bundles skills, commands, and agents into a distributable unit. The plugin specification defines the directory structure, the `plugin.json` manifest, and the installation and update mechanisms.

**What you will find here:**

- Plugin directory structure (`.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/`)
- The `plugin.json` schema and required fields
- Plugin installation: `/plugin install` command syntax
- Installation scopes: project-level vs. global
- Plugin marketplaces and the `/plugin marketplace add` command
- Plugin updates and version management
- How Claude Code discovers and loads plugins

**When to read this:** When you are creating a new plugin, troubleshooting plugin loading issues, or trying to understand the difference between project-scoped and global plugins. If you are publishing to the Tons of Skills marketplace, you need to know this specification thoroughly.

### Agents

**URL:** [code.claude.com/docs/en/agents](https://code.claude.com/docs/en/agents)

Agents are autonomous personas that Claude Code can adopt for specialized tasks. Unlike skills (which provide instructions) and commands (which are user-invoked), agents define a complete behavioral profile with capabilities, tool restrictions, and iteration limits.

**What you will find here:**

- Agent file format (`agents/*.md`) and frontmatter schema
- The `disallowedTools` field (denylist, as opposed to skills' `allowed-tools` allowlist)
- Agent-only fields: `effort`, `maxTurns`, `permissionMode`
- How agents differ from skills and commands
- The `capabilities` array and how it influences agent behavior
- Model and effort overrides for controlling agent reasoning depth

**When to read this:** When you are building a plugin that includes autonomous agents, or when you want to understand the behavioral differences between agents and skills. The key distinction -- agents use a denylist while skills use an allowlist -- is important for security modeling.

### Hooks

**URL:** [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

Hooks are lifecycle callbacks that run at specific points during Claude Code's operation. They let plugins execute custom logic before or after tool calls, at session start, or at other well-defined moments.

**What you will find here:**

- Available hook types: `pre-tool-call`, `post-tool-call`, `session-start`, and others
- Hook configuration in `plugin.json` and skill frontmatter
- The `${CLAUDE_PLUGIN_ROOT}` variable for portable hook scripts
- Hook execution model and error handling
- Practical examples: auto-formatting after file writes, pre-commit validation, audit logging

**When to read this:** When you want your plugin to react to Claude Code events automatically. Hooks are the mechanism for side effects -- things that should happen without explicit user invocation. Common use cases include running linters after file edits, logging tool usage, and enforcing project-specific constraints.

### MCP (Model Context Protocol)

**URL:** [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

MCP is a protocol for connecting Claude Code to external tools and data sources via local servers. An MCP server exposes tools that Claude Code can call, allowing integration with databases, APIs, file systems, and other services that go beyond what built-in tools provide.

**What you will find here:**

- What MCP is and how it extends Claude Code's tool repertoire
- MCP server architecture: stdio transport, tool definitions, request/response format
- Configuring MCP servers in `.mcp.json`
- Building MCP servers in TypeScript using the `@anthropic-ai/sdk`
- Tool naming and namespacing conventions
- Security considerations for MCP tool permissions

**When to read this:** When you want to build a plugin that connects Claude Code to an external service -- a database, an API, a custom internal tool. MCP plugins are more complex than instruction-only plugins (they require a running server process), but they unlock capabilities that markdown-based skills cannot provide.

### CLI Reference

**URL:** [code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)

The complete reference for the `claude` command-line interface, including all flags, environment variables, and configuration options.

**What you will find here:**

- All `claude` CLI flags and options
- Environment variables (`ANTHROPIC_API_KEY`, `CLAUDE_CODE_CONFIG_DIR`, etc.)
- Configuration files and their locations
- Non-interactive mode for CI/CD integration
- Piping input and output
- Session management and history

**When to read this:** When you need the exact flag name or syntax for a CLI operation, or when you are integrating Claude Code into scripts or CI pipelines.

### Best Practices

**URL:** [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices)

Anthropic's recommendations for getting the best results from Claude Code, covering prompt engineering, project setup, and workflow patterns.

**What you will find here:**

- Writing effective CLAUDE.md files for project context
- Structuring prompts for complex multi-step tasks
- When to use skills vs. commands vs. agents
- Managing context window and token usage
- Security best practices for tool permissions
- Team workflows and shared configuration

**When to read this:** Regularly. This page is updated as Claude Code evolves and as Anthropic learns from user feedback. The advice here directly impacts the quality of Claude Code's output in your projects.

## How Tons of Skills Extends Official Capabilities

The official Anthropic documentation defines the specification -- the format, rules, and mechanics. The Tons of Skills ecosystem builds on that foundation in several ways:

### Scale and curation

The official docs explain how to write a skill. Tons of Skills provides 2,834 pre-built skills ready to install. Rather than writing everything from scratch, you can browse the [marketplace](/explore), find a skill that does what you need, and install it in seconds.

### Quality assurance

The official docs define the SKILL.md format. Tons of Skills applies a 100-point compliance rubric on top of that format, scoring every plugin and skill for completeness, documentation quality, and structural correctness. When you install a plugin with an A-grade badge, you know it exceeds the minimum specification.

### Tooling

The official docs describe the `/plugin install` command. Tons of Skills provides the `ccpi` CLI, which adds marketplace management, bulk installation, plugin diagnostics, validation, and upgrade workflows on top of the built-in commands.

### Discovery

The official docs do not include a plugin registry. Tons of Skills provides the marketplace at [tonsofskills.com](https://tonsofskills.com) with full-text search, category filtering, skill-level browsing, side-by-side comparisons, and curated collections.

### Downloads and distribution

The official plugin system requires running install commands one at a time. Tons of Skills provides [Cowork](/cowork) -- downloadable zip bundles for individual plugins, categories, and the entire catalog.

## When to Refer to Official Docs vs. Tons of Skills Docs

Use this decision framework:

| Question | Go to |
|---|---|
| What is the SKILL.md frontmatter schema? | [Official Skills docs](https://code.claude.com/docs/en/skills) |
| How do I install a specific plugin from the marketplace? | [Tons of Skills installation guide](/docs/getting-started/installation) |
| What tool names can I use in `allowed-tools`? | [Official Skills docs](https://code.claude.com/docs/en/skills) |
| How do I search for plugins that do X? | [Explore page](/explore) or [Skills page](/skills) |
| How do I write an MCP server? | [Official MCP docs](https://code.claude.com/docs/en/mcp) |
| How do I publish my plugin to the marketplace? | Tons of Skills publishing guide |
| What does the `context: fork` field do? | [Official Skills docs](https://code.claude.com/docs/en/skills) |
| What is the compliance scoring rubric? | [Marketplace overview](/docs/ecosystem/marketplace-overview) |
| How do hooks work? | [Official Hooks docs](https://code.claude.com/docs/en/hooks) |
| How do I use the ccpi CLI? | [Tons of Skills CLI reference](/docs/getting-started/installation) |

**General rule:** If your question is about how Claude Code works at the platform level -- format specifications, runtime behavior, built-in commands -- start with the official Anthropic docs. If your question is about the marketplace, plugin discovery, quality scoring, the `ccpi` CLI, or Cowork downloads -- start with the Tons of Skills docs.

## Staying Current

Anthropic updates the Claude Code documentation as new features ship. The Tons of Skills documentation tracks these changes and updates accordingly, but there can be a lag. When in doubt, check the official docs for the latest specification and the Tons of Skills docs for ecosystem-specific guidance.

Key pages to watch for changes:

- **Skills spec** -- new frontmatter fields are added periodically as Claude Code gains capabilities.
- **Plugins spec** -- the `plugin.json` schema and installation mechanics evolve with major releases.
- **Best practices** -- Anthropic updates recommendations based on real-world usage patterns.

You can also follow the [Tons of Skills blog](/blog) for announcements about specification changes and how they affect the marketplace ecosystem.

## Next Steps

- [Marketplace Guide](/docs/ecosystem/marketplace-overview) -- browse and install plugins from the Tons of Skills catalog.
- [Community Resources](/docs/ecosystem/community-resources) -- contribute plugins, report issues, and connect with developers.
- [FAQ](/docs/ecosystem/faq) -- answers to the most common questions about Claude Code plugins.
- [Install Claude Code Plugins](/docs/getting-started/installation) -- get set up with the ccpi CLI and marketplace.
