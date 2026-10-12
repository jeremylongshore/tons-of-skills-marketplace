# Schema Reminder — Frontmatter Fields

The standard tier requires these fields:

```yaml
name: my-skill                  # Required (Anthropic)
description: |                  # Required (Anthropic)
  What it does. Use when ...
```

Marketplace submissions require **all eight** of `name`, `description`,
`allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`.
The following six fields are optional in standard mode but required with
`--marketplace`:

```yaml
allowed-tools: "Read,Write,Bash(git:*)"
license: MIT
compatibility: "Designed for Claude Code"   # Free-text, max 500 chars per agentskills.io/specification
version: 1.0.0
author: Name <email>
tags: [devops, ci]
```

Other accepted optional fields (validated when present):

```yaml
metadata: { category: devops }              # Arbitrary key-value mapping

# Per code.claude.com/docs/en/skills
model: inherit
effort: medium
argument-hint: "[file-path]"
context: fork
agent: Explore
user-invocable: true
disable-model-invocation: false
hooks: { ... }
```

## `compatibility` Field Examples (per `agentskills.io/specification`)

The `compatibility` field is a free-text string, max 500 characters. It indicates environment requirements (intended product, system packages, network access, etc.). Pick the form that matches your skill:

```yaml
# Single platform
compatibility: "Designed for Claude Code"

# Multi-platform — free-text, no allow-list
compatibility: "Designed for Claude Code, also compatible with Codex and OpenClaw"

# Runtime requirements
compatibility: "Requires Python 3.10+ with uv installed"
compatibility: "Requires git, docker, and jq on PATH"
compatibility: "Node.js >= 18, npm >= 9"

# Platform + tooling
compatibility: "Designed for Claude Code; requires Bash 5+ and rg (ripgrep)"

# Network / capability requirements
compatibility: "Requires network access to api.example.com (port 443)"
```

**Migration**: Replace the deprecated `compatible-with` CSV-platform-list field
with free-text `compatibility`. From the marketplace root, preview the migration
within the target skill's directory (`skill_file` is the absolute SKILL.md path):

```bash
python3 scripts/batch-remediate.py --migrate-compatible-with \
  --root "$(dirname "$skill_file")" --dry-run
```

Remove `--dry-run` only when the repair is authorized. The directory scan is recursive.
