---
title: "What Are Claude Code Plugins?"
description: "A comprehensive guide to Claude Code plugins — what they are, how they work, and how they extend Claude Code with new capabilities through AI instruction files, MCP servers, and SaaS skill packs."
section: "concepts"
order: 1
keywords:
  - "Claude Code plugins"
  - "plugin structure"
  - "plugin.json"
  - "AI instruction plugins"
  - "MCP server plugins"
  - "SaaS skill packs"
  - "Claude Code extensions"
  - "plugin lifecycle"
officialLinks:
  - title: "Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Claude Code Plugins Overview"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Tons of Skills Marketplace"
    url: "https://tonsofskills.com"
relatedDocs:
  - "concepts/skills"
  - "concepts/agents"
  - "concepts/commands-and-hooks"
  - "concepts/mcp-servers"
---

Plugins are the primary mechanism for extending Claude Code beyond its built-in capabilities. A Claude Code plugin is a structured directory of files that teaches Claude new behaviors, gives it access to new tools, or adds domain-specific knowledge that would not otherwise be available in a general-purpose coding assistant.

The [Tons of Skills marketplace](/) hosts over 418 plugins containing more than 2,834 individual skills. Whether you need Claude to manage Kubernetes clusters, enforce your team's coding standards, generate database migrations, or run security audits, there is likely a plugin for it -- and if there is not, building one is straightforward.

## Why Plugins Exist

Claude Code is a powerful AI coding assistant out of the box. It can read files, write code, run commands, and reason about complex systems. But every team and every project has unique requirements that a general-purpose tool cannot anticipate.

Plugins solve this gap by providing a standardized way to:

- **Add domain expertise.** A plugin can contain detailed instructions for working with a specific framework, API, or business domain that Claude would not otherwise know about.
- **Enforce standards.** Teams can codify their coding conventions, review checklists, deployment procedures, and architectural patterns into plugins that Claude follows automatically.
- **Expose new tools.** MCP server plugins give Claude access to external APIs, databases, and services through a standardized protocol.
- **Package reusable workflows.** Common multi-step processes -- like setting up a new microservice, running a security audit, or generating documentation -- can be packaged as plugins and shared across teams.

## Plugin Anatomy

Every Claude Code plugin lives in a directory with a specific structure. At minimum, a plugin requires two files: a manifest (`plugin.json`) and a readme (`README.md`). Most plugins also include one or more of: slash commands, agent definitions, and auto-activating skills.

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: plugin manifest
├── README.md                # Required: documentation
├── commands/                # Optional: slash commands
│   ├── review.md
│   └── deploy.md
├── agents/                  # Optional: agent definitions
│   └── security-analyst.md
└── skills/                  # Optional: auto-activating skills
    └── code-style/
        └── SKILL.md
```

### The Plugin Manifest (plugin.json)

The `plugin.json` file is the identity card of your plugin. It lives inside the `.claude-plugin/` directory and contains metadata that the marketplace and CLI use to discover, display, and manage plugins.

```json
{
  "name": "code-review-pro",
  "version": "1.2.0",
  "description": "Automated code review with security scanning and style enforcement",
  "author": "Jane Developer <jane@example.com>",
  "repository": "https://github.com/jane/code-review-pro",
  "homepage": "https://tonsofskills.com/plugins/code-review-pro",
  "license": "MIT",
  "keywords": ["code-review", "security", "linting", "best-practices"]
}
```

The schema is intentionally strict. Only these fields are permitted:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique plugin identifier (kebab-case) |
| `version` | Yes | Semantic version (e.g., `1.2.0`) |
| `description` | Yes | One-line summary of the plugin's purpose |
| `author` | Yes | Author name, optionally with email |
| `repository` | No | URL to the source code repository |
| `homepage` | No | URL to the plugin's documentation or landing page |
| `license` | No | SPDX license identifier (e.g., `MIT`, `Apache-2.0`) |
| `keywords` | No | Array of discovery tags |

CI validation rejects any `plugin.json` that includes fields not on this list. This keeps the manifest lean and prevents metadata sprawl.

### README.md

Every plugin must include a `README.md` at the root level. This serves dual purposes: it is the documentation that human developers read, and it is extracted by the marketplace build pipeline to populate plugin detail pages on [tonsofskills.com](/explore).

A good plugin README includes:

- A clear description of what the plugin does and when to use it
- Installation instructions
- A list of included commands, agents, and skills
- Configuration options (if any)
- Examples of common usage

### Commands Directory

The `commands/` directory contains slash command definitions -- markdown files that define actions users can invoke explicitly by typing `/command-name` in Claude Code. Each file is a self-contained instruction set with YAML frontmatter. See [Slash Commands and Hooks](/docs/concepts/commands-and-hooks) for details.

### Agents Directory

The `agents/` directory contains agent definitions -- markdown files that describe specialized AI personas with specific capabilities, tool restrictions, and behavioral parameters. Agents are designed for autonomous, multi-step workflows. See [Claude Code Agents and Subagents](/docs/concepts/agents) for details.

### Skills Directory

The `skills/` directory contains auto-activating skill definitions in `SKILL.md` files. Unlike commands (which require explicit invocation), skills activate automatically when Claude determines they are relevant to the current task. See [Understanding Agent Skills (SKILL.md)](/docs/concepts/skills) for details.

## Types of Plugins

The Tons of Skills ecosystem supports three distinct plugin types, each suited to different use cases.

### AI Instruction Plugins

The vast majority of plugins (approximately 98%) are AI instruction plugins. These contain no executable code -- they are collections of markdown files with carefully crafted instructions, examples, and constraints that shape how Claude behaves.

AI instruction plugins are powerful because they leverage Claude's ability to follow complex, nuanced instructions. A well-written instruction plugin can teach Claude to:

- Follow a specific API's conventions and best practices
- Apply a team's architectural patterns consistently
- Execute multi-step workflows with proper error handling
- Enforce security policies during code generation

**Example directory structure:**

```
terraform-pro/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── commands/
│   ├── plan.md              # /plan — run terraform plan with analysis
│   ├── apply.md             # /apply — safe terraform apply workflow
│   └── drift-check.md       # /drift-check — detect configuration drift
├── agents/
│   └── infra-reviewer.md    # Infrastructure review specialist
└── skills/
    ├── module-patterns/
    │   └── SKILL.md          # Auto-activates when writing Terraform modules
    └── state-management/
        └── SKILL.md          # Auto-activates for state operations
```

### MCP Server Plugins

MCP (Model Context Protocol) server plugins are TypeScript applications that expose external tools and data sources to Claude through a standardized protocol. Unlike instruction plugins, these contain executable code that runs as a local server process.

MCP plugins are the right choice when you need Claude to interact with external systems -- databases, APIs, file systems with special requirements, or any service that requires programmatic access beyond what Claude's built-in tools provide.

See [MCP Servers in Claude Code Plugins](/docs/concepts/mcp-servers) for a deep dive into building and consuming MCP server plugins.

**Example directory structure:**

```
database-explorer/
├── .claude-plugin/
│   └── plugin.json
├── src/
│   └── index.ts             # TypeScript source
├── dist/
│   └── index.js             # Compiled, executable (shebang + chmod +x)
├── package.json
├── tsconfig.json
└── .mcp.json                # MCP server configuration
```

### SaaS Skill Packs

SaaS skill packs are curated collections of skills organized around a specific SaaS platform or service. Each pack provides comprehensive coverage of a platform's API, best practices, and common workflows.

For example, a Stripe skill pack might include skills for payment processing, subscription management, webhook handling, and dispute resolution -- each as a separate `SKILL.md` with focused instructions.

SaaS packs are managed as pnpm workspace members and follow a consistent structure:

```
stripe-pack/
├── .claude-plugin/
│   └── plugin.json
├── package.json
├── README.md
└── skills/
    ├── payments/
    │   └── SKILL.md
    ├── subscriptions/
    │   └── SKILL.md
    ├── webhooks/
    │   └── SKILL.md
    └── disputes/
        └── SKILL.md
```

You can browse all available SaaS packs on the [Explore](/explore) page.

## How Plugins Extend Claude Code

When a plugin is installed, Claude Code loads its contents into context at the appropriate time:

1. **Skills** are loaded when Claude determines they are relevant to the current task. The `description` field in a SKILL.md's frontmatter acts as a trigger -- Claude matches the user's intent against skill descriptions to decide which skills to activate.

2. **Commands** are loaded when a user explicitly invokes them via the `/command-name` syntax in the Claude Code interface.

3. **Agents** are loaded when Claude decides to delegate a subtask to a specialized agent, or when a skill or command explicitly references an agent via the `agent` frontmatter field.

4. **MCP servers** run as background processes and expose their tools through the MCP protocol. Claude can call these tools alongside its built-in tools (Read, Write, Edit, Bash, etc.).

This lazy-loading approach is important for performance. With thousands of skills available across hundreds of plugins, loading everything into context at startup would be impractical. Instead, Claude activates only what is needed for the current task.

## The Plugin Lifecycle

### Discovery

Users discover plugins through several channels:

- **The Marketplace.** Browse the [Tons of Skills marketplace](/) to search, filter, and compare plugins. The [Explore](/explore) page provides category-based browsing, and the [Skills](/skills) page lets you search individual skills across all plugins.
- **The CLI.** The `ccpi` CLI tool provides command-line access to the marketplace catalog. Run `ccpi search <query>` to find plugins or `ccpi list` to browse categories.
- **Recommendations.** Plugins can reference other plugins in their documentation, and the marketplace suggests related plugins on each plugin's detail page.

### Installation

Plugins are installed using the `ccpi` CLI or directly through Claude Code:

```bash
# Install via ccpi CLI
ccpi install code-review-pro

# Install from the marketplace
/plugin marketplace add jeremylongshore/claude-code-plugins
```

Installation copies the plugin directory into your local Claude Code configuration, making its commands, agents, and skills available in your sessions.

### Activation

Once installed, the plugin's components activate in different ways:

- **Skills** activate automatically based on context matching
- **Commands** are available via the `/` menu
- **Agents** are available for delegation by Claude or explicit invocation
- **MCP servers** start as background processes when Claude Code launches

### Updates

Plugin updates follow semantic versioning. When a new version is published, users can update through the CLI:

```bash
ccpi update code-review-pro
ccpi update --all
```

## Plugin Quality and Compliance

The Tons of Skills marketplace enforces quality standards through a multi-tier validation system:

- **Standard tier** validates structural requirements -- proper `plugin.json` schema, required files present, valid YAML frontmatter in all markdown files.
- **Enterprise tier** applies a 100-point compliance rubric that evaluates documentation quality, instruction depth, security practices, and metadata completeness. Plugins are graded A through F.

You can validate your own plugins locally before publishing:

```bash
# Standard validation
python3 scripts/validate-skills-schema.py --verbose plugins/my-category/my-plugin/

# Enterprise validation with full grading
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/my-category/my-plugin/
```

The [Tons of Skills marketplace](/) displays compliance grades on plugin detail pages, helping users make informed decisions about which plugins to trust in their workflows.

## What Makes a Good Plugin

The best plugins in the ecosystem share several characteristics:

**Focused scope.** A plugin should do one thing well rather than trying to cover everything. A plugin for "React Testing" is more useful than a plugin for "Frontend Development" because it can provide deeper, more actionable instructions.

**Rich instructions.** The body of each SKILL.md, command, or agent definition should contain detailed, specific instructions -- not vague guidelines. Include code examples, edge cases, error handling patterns, and decision trees.

**Proper metadata.** Complete and accurate frontmatter makes your plugin discoverable. Write clear descriptions that include trigger phrases so Claude knows when to activate your skills.

**Minimal tool permissions.** Skills should request only the tools they actually need via the `allowed-tools` field. A skill that only reads and analyzes code should not request `Write` or `Bash` permissions.

**Version discipline.** Follow semantic versioning. Bump the patch version for fixes, minor for new features, and major for breaking changes to skill behavior or command interfaces.

## Next Steps

- Learn about the core building block of plugins: [Understanding Agent Skills (SKILL.md)](/docs/concepts/skills)
- Understand how agents provide autonomous capabilities: [Claude Code Agents and Subagents](/docs/concepts/agents)
- Explore slash commands and lifecycle hooks: [Slash Commands and Hooks](/docs/concepts/commands-and-hooks)
- Discover how MCP servers bridge external systems: [MCP Servers in Claude Code Plugins](/docs/concepts/mcp-servers)
- Browse the full plugin catalog: [Explore Plugins](/explore)
