---
title: "How to Build a Claude Code Plugin"
description: "Complete guide to building a Claude Code plugin from scratch. Covers plugin.json configuration, commands, skills, agents, directory structure, validation, and testing with full code examples."
section: "guides"
order: 2
keywords:
  - "plugin"
  - "plugin.json"
  - "commands"
  - "agents"
  - "skills"
  - "Claude Code plugin"
  - "plugin development"
  - "build plugin"
officialLinks:
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Anthropic Plugins Reference"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "concepts/plugins"
  - "reference/plugin-json-schema"
  - "guides/publish-to-marketplace"
---

## What Is a Claude Code Plugin?

A Claude Code plugin is a directory containing AI instruction files that extend Claude Code's capabilities. Plugins can include slash commands, auto-activating skills, and autonomous agents -- all defined as Markdown files with YAML frontmatter. No compiled code is required. The entire plugin is plain text.

Plugins are installed with a single command:

```bash
claude /plugin add username/repo-name
```

Once installed, Claude Code reads the plugin's manifest, discovers its commands, skills, and agents, and makes them available in the session. This guide walks through building a complete plugin from an empty directory to a validated, installable package.

## Step 1: Plan Your Plugin

A plugin is a coherent collection of capabilities around a single domain. Good plugin boundaries:

- **One technology:** A plugin for Docker, Terraform, or Kubernetes
- **One workflow:** A plugin for code review, release engineering, or CI/CD
- **One integration:** A plugin for Stripe, GitHub, or Slack

Avoid "mega plugins" that try to cover everything. Instead, create focused plugins that compose well together.

### Decide What to Include

| Component | Use When |
|-----------|----------|
| **Commands** (`commands/*.md`) | User explicitly invokes with `/command-name` |
| **Skills** (`skills/name/SKILL.md`) | Auto-activates based on context |
| **Agents** (`agents/*.md`) | Runs as autonomous sub-agent with its own tool permissions |

A plugin can contain any combination of these. A minimal plugin might have one skill. A full plugin might have several commands, multiple skills, and a couple of agents.

## Step 2: Create the Directory Structure

Every plugin follows this layout:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # Required: plugin manifest
├── README.md              # Required: documentation
├── LICENSE                # Recommended: license file
├── CHANGELOG.md           # Recommended: version history
├── commands/              # Optional: slash commands
│   ├── deploy.md
│   └── rollback.md
├── skills/                # Optional: auto-activating skills
│   └── docker-compose/
│       ├── SKILL.md
│       └── reference.md
└── agents/                # Optional: autonomous agents
    └── security-scanner.md
```

Create the scaffolding:

```bash
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/commands
mkdir -p my-plugin/skills
mkdir -p my-plugin/agents
touch my-plugin/.claude-plugin/plugin.json
touch my-plugin/README.md
```

You can also start from one of the [templates](https://github.com/jeremylongshore/claude-code-plugins/tree/main/templates) included in the Tons of Skills repository:

| Template | Includes |
|----------|----------|
| `minimal-plugin` | plugin.json and README only |
| `command-plugin` | One slash command |
| `skill-plugin` | One auto-activating skill |
| `agent-plugin` | One autonomous agent |
| `full-plugin` | Commands, skills, and agents |

## Step 3: Configure plugin.json

The `plugin.json` file is the plugin's manifest. It tells Claude Code what the plugin is, who wrote it, and where to find it. Only these fields are allowed:

```json
{
  "name": "docker-workflow",
  "version": "1.0.0",
  "description": "Docker development workflow automation: compose management, image optimization, multi-stage builds, and container debugging",
  "author": "Your Name <you@example.com>",
  "repository": "https://github.com/username/docker-workflow",
  "homepage": "https://tonsofskills.com/plugins/devops/docker-workflow",
  "license": "MIT",
  "keywords": ["docker", "containers", "devops", "compose", "deployment"]
}
```

### Field Reference

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | Lowercase kebab-case. Must be unique across the marketplace. |
| `version` | Yes | Semantic versioning (e.g., `1.0.0`, `1.2.3`). |
| `description` | Yes | One to two sentences. Describe what the plugin does, not how. |
| `author` | Yes | Name and optional email in angle brackets. |
| `repository` | No | Full URL to the source repository. |
| `homepage` | No | Full URL to the plugin's page or documentation. |
| `license` | No | SPDX identifier (e.g., `MIT`, `Apache-2.0`). |
| `keywords` | No | Array of strings for search and categorization. |

**Important:** CI validation rejects any fields not in this list. Do not add `dependencies`, `scripts`, `main`, or any other fields. The `plugin.json` schema is intentionally minimal.

### Choosing a Name

- Use kebab-case: `docker-workflow`, not `DockerWorkflow` or `docker_workflow`
- Be specific: `react-test-writer` is better than `test-helper`
- Avoid generic prefixes: skip `claude-`, `ai-`, or `plugin-` in the name
- Check the [marketplace](/explore) for name conflicts

## Step 4: Write the README

The README is both documentation for users and content for the marketplace listing. Structure it clearly:

```markdown
# Docker Workflow

Docker development workflow automation for Claude Code. Manages compose
files, optimizes images, builds multi-stage Dockerfiles, and debugs
running containers.

## Features

- Generate and validate docker-compose.yml files
- Optimize Dockerfiles with multi-stage build patterns
- Debug containers with log analysis and exec commands
- Manage environment-specific compose overrides

## Installation

\```bash
claude /plugin add username/docker-workflow
\```

## Commands

| Command | Description |
|---------|-------------|
| `/docker-build` | Generate an optimized Dockerfile |
| `/docker-debug` | Debug a running container |

## Skills

- **docker-compose** - Auto-activates when working with compose files
- **dockerfile-optimizer** - Activates when editing Dockerfiles

## Requirements

- Docker installed and running
- docker-compose v2+

## License

MIT
```

## Step 5: Add Commands

Commands are user-invoked actions triggered with `/command-name` in Claude Code. Each command is a Markdown file in the `commands/` directory.

### Command File Structure

Create `commands/docker-build.md`:

```yaml
---
name: docker-build
description: "Generate an optimized multi-stage Dockerfile for the current project"
argument-hint: "<project-type>"
---

# Docker Build

Generate a production-ready, multi-stage Dockerfile optimized for the
current project.

## Instructions

1. Detect the project type by reading package.json, requirements.txt,
   go.mod, or Cargo.toml
2. Choose the appropriate base image (slim variants preferred)
3. Implement a multi-stage build:
   - Stage 1: Install dependencies
   - Stage 2: Build/compile
   - Stage 3: Production runtime (minimal image)
4. Add health checks, non-root user, and proper signal handling
5. Write the Dockerfile to the project root
6. Validate with `docker build --check .` if available

## Output

Write a `Dockerfile` with:
- Multi-stage build reducing final image size
- Layer caching optimized for dependency changes
- Non-root USER directive
- HEALTHCHECK instruction
- Descriptive comments on each stage
```

### Command Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | The slash command name (users type `/name`) |
| `description` | Yes | Short description shown in the command menu |
| `argument-hint` | No | Placeholder text for autocomplete |
| `user-invocable` | No | Set to `false` to hide from the menu (default `true`) |
| `model` | No | Override the LLM model (`sonnet`, `haiku`, `opus`) |
| `context` | No | Set to `fork` to run in a sub-agent |

## Step 6: Add Skills

Skills auto-activate based on context. See the full guide at [How to Write a Claude Code Skill](/docs/guides/write-a-skill). Here is a quick example.

Create `skills/docker-compose/SKILL.md`:

```yaml
---
name: docker-compose
description: |
  Manage Docker Compose configurations. Auto-activates when creating,
  editing, or debugging docker-compose.yml files. Handles service
  definitions, networking, volumes, and environment variables. Trigger
  phrases: "create a compose file", "add a service to compose",
  "fix my docker-compose", "debug compose networking".
allowed-tools: Read, Write, Edit, Bash(docker:*), Glob, Grep
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
compatible-with: claude-code
tags: [docker, compose, containers, devops]
---

# Docker Compose Manager

Create, modify, and debug Docker Compose configurations.

## Overview

Manages docker-compose.yml files with best practices: proper service
ordering, health checks, named volumes, custom networks, and
environment variable management.

## Instructions

1. Read the existing docker-compose.yml if present
2. Identify all services, networks, and volumes
3. Apply the requested changes
4. Validate the compose file with `docker compose config`
5. Report any warnings or errors

## Error Handling

- If docker compose is not installed, suggest installation steps
- If the compose file has syntax errors, show the specific line and fix
- If a referenced image does not exist, suggest alternatives
```

### Adding Supporting Files

Skills can reference additional documentation files. Create `skills/docker-compose/reference.md` with compose file patterns, and link to it from the SKILL.md body:

```markdown
For advanced networking patterns, see Reference.
```

Claude Code follows these relative links using the Read tool when the information is needed.

## Step 7: Add Agents

Agents are autonomous sub-agents with their own capabilities and constraints. They differ from skills in two important ways:

1. Agents use `disallowedTools` (a denylist) instead of `allowed-tools` (an allowlist)
2. Agents can iterate autonomously up to `maxTurns` iterations

Create `agents/security-scanner.md`:

```yaml
---
name: security-scanner
description: "Scans the codebase for security vulnerabilities, secrets, and misconfigurations"
capabilities:
  - "Dependency vulnerability scanning"
  - "Secret detection in source code"
  - "Docker security configuration review"
  - "Environment variable exposure analysis"
model: sonnet
maxTurns: 15
expertise_level: advanced
activation_priority: medium
---

# Security Scanner Agent

You are a security-focused agent that scans codebases for vulnerabilities,
exposed secrets, and security misconfigurations.

## Your Expertise

- OWASP Top 10 vulnerabilities
- Secret detection (API keys, tokens, passwords in source)
- Dependency vulnerability analysis (CVEs)
- Docker and container security
- Environment variable exposure

## Scanning Process

1. Scan for hardcoded secrets using pattern matching
2. Check dependency manifests for known vulnerabilities
3. Review Dockerfile security (root user, exposed ports, secrets in layers)
4. Analyze environment variable handling
5. Check for sensitive files committed to git (.env, credentials, keys)

## Output Format

Present findings as a security report:

**Critical:** Issues requiring immediate attention
**High:** Significant vulnerabilities
**Medium:** Best practice violations
**Low:** Informational findings

For each finding, include:
- File and line number
- Description of the issue
- Recommended fix with code example
```

### Agent Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Unique identifier |
| `description` | Yes | 20-200 characters describing the agent's specialty |
| `capabilities` | No | Array of capability descriptions |
| `model` | No | LLM model override |
| `effort` | No | Reasoning effort: `low`, `medium`, `high` |
| `maxTurns` | No | Maximum autonomous iterations |
| `disallowedTools` | No | Tools the agent cannot use (denylist) |
| `expertise_level` | No | `intermediate`, `advanced`, `expert` |
| `activation_priority` | No | `low`, `medium`, `high`, `critical` |
| `permissionMode` | No | Permission behavior override |

For a deeper dive, see [How to Create a Claude Code Agent](/docs/guides/create-an-agent).

## Step 8: Validate Your Plugin

Run the universal validator to check your plugin against both the Anthropic spec and the enterprise quality rubric.

### Structural Validation

```bash
# Validate plugin.json fields, file references, permissions
./scripts/validate-all-plugins.sh plugins/devops/docker-workflow/
```

This checks:

- `plugin.json` contains only allowed fields
- All referenced files exist
- Script files have execute permissions
- No secrets or dangerous patterns

### Content Validation

```bash
# Standard tier: Anthropic minimum requirements
python3 scripts/validate-skills-schema.py --verbose plugins/devops/docker-workflow/

# Enterprise tier: 100-point rubric for marketplace quality
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/devops/docker-workflow/
```

The enterprise validator grades each SKILL.md on a 100-point rubric:

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent: production-ready, well-documented |
| B | 70-89 | Good: functional with minor improvements needed |
| C | 50-69 | Adequate: works but needs more documentation |
| D | 30-49 | Poor: significant gaps in structure or content |
| F | 0-29 | Failing: stub or placeholder content |

Target a B grade (70+) minimum for marketplace submission. A grade (90+) plugins are featured on the [Explore](/explore) page.

### Quick Test Script

For rapid iteration during development, use the quick test:

```bash
pnpm run sync-marketplace && ./scripts/quick-test.sh
```

This runs the build, lint, and validation pipeline in about 30 seconds.

## Full Example: Building a Complete Plugin

Here is the complete file tree for a production-ready Docker workflow plugin:

```
docker-workflow/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── LICENSE
├── commands/
│   ├── docker-build.md
│   └── docker-debug.md
├── skills/
│   ├── docker-compose/
│   │   ├── SKILL.md
│   │   └── reference.md
│   └── dockerfile-optimizer/
│       ├── SKILL.md
│       └── patterns.md
└── agents/
    └── security-scanner.md
```

Each file follows the patterns shown in the steps above. The plugin provides:

- Two commands users can invoke explicitly (`/docker-build`, `/docker-debug`)
- Two skills that activate automatically when working with Docker files
- One agent that can run autonomous security scans

## Testing Your Plugin

### Local Installation

Install the plugin from a local path:

```bash
claude /plugin add /path/to/docker-workflow
```

### Verify Discovery

Check that Claude Code finds your commands, skills, and agents:

1. Type `/docker-` and verify autocomplete shows your commands
2. Say "create a docker-compose file" and verify the skill activates
3. Ask Claude to "run a security scan" and verify the agent responds

### Iterate

Edit your Markdown files, re-run validation, and test again. No build step is required for instruction plugins -- Claude Code reads the Markdown directly.

## Next Steps

Once your plugin passes validation:

1. Push to a GitHub repository
2. [Publish to the Tons of Skills marketplace](/docs/guides/publish-to-marketplace)
3. Share with the community at [tonsofskills.com](https://tonsofskills.com)

For platform-specific integrations, consider building a [SaaS Skill Pack](/docs/guides/saas-skill-packs). For tools that need runtime capabilities beyond Markdown instructions, see [Building an MCP Server Plugin](/docs/guides/mcp-server-plugin).
