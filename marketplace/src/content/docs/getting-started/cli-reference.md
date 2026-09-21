---
title: "ccpi CLI Quick Reference"
description: "Complete command reference for the ccpi CLI -- install, list, search, upgrade, validate, and diagnose Claude Code plugins from your terminal."
section: "getting-started"
order: 4
keywords: ["ccpi CLI", "ccpi commands", "Claude Code CLI", "plugin management CLI", "ccpi install", "ccpi validate", "ccpi doctor"]
officialLinks:
  - title: "ccpi on npm"
    url: "https://www.npmjs.com/package/@intentsolutionsio/ccpi"
  - title: "Claude Code CLI Reference"
    url: "https://code.claude.com/docs/en/cli-reference"
relatedDocs:
  - "getting-started/installation"
  - "reference/cli-commands"
---

## Overview

The `ccpi` CLI (`@intentsolutionsio/ccpi`) is the command-line companion for managing Claude Code plugins. It runs in your regular terminal -- outside of Claude Code sessions -- and handles marketplace connections, plugin installation guidance, upgrade tracking, structural validation, and system diagnostics.

Install it globally via npm:

```bash
npm install -g @intentsolutionsio/ccpi
```

Or run on demand without installing:

```bash
npx @intentsolutionsio/ccpi <command>
```

## Quick command table

| Command | Description |
|---|---|
| `ccpi install <plugin>` | Guided install of a single plugin |
| `ccpi install --all` | Print install commands for all 418 plugins |
| `ccpi install --pack <name>` | Install a curated plugin pack |
| `ccpi install --category <name>` | Install all plugins in a category |
| `ccpi list` | List installed plugins |
| `ccpi list --all` | List all available plugins in the marketplace |
| `ccpi search <query>` | Search the marketplace by keyword |
| `ccpi upgrade` | Show available updates with upgrade guidance |
| `ccpi upgrade --check` | Check for updates without upgrading |
| `ccpi upgrade --all` | Guide upgrade of all outdated plugins |
| `ccpi upgrade --plugin <name>` | Guide upgrade of a specific plugin |
| `ccpi validate [path]` | Validate plugin structure and frontmatter |
| `ccpi validate --strict` | Validate with strict mode (fail on warnings) |
| `ccpi doctor` | Run system diagnostics |
| `ccpi doctor --fix` | Run diagnostics and auto-fix safe issues |
| `ccpi marketplace` | Show marketplace status |
| `ccpi marketplace --verify` | Verify marketplace installation |
| `ccpi marketplace-add` | Add the Tons of Skills marketplace |
| `ccpi marketplace-remove` | Remove the marketplace |
| `ccpi analytics` | View plugin usage analytics (coming soon) |
| `ccpi --version` | Print the ccpi version |
| `ccpi --help` | Show help for all commands |

## Command details

### ccpi install

The install command guides you through adding plugins to Claude Code. It does not install plugins directly -- it validates the plugin name against the marketplace catalog and outputs the `/plugin install` slash command you run inside Claude Code.

```bash
ccpi install code-reviewer
```

**Output:**

```
Found: code-reviewer v1.2.0
  Automated code review with quality scoring and actionable feedback

Installation Command:

Open Claude Code and run:

   /plugin install code-reviewer@claude-code-plugins-plus --project
```

**Flags:**

| Flag | Description |
|---|---|
| `-y, --yes` | Skip confirmation prompts |
| `--global` | Output install command with `--global` scope |
| `--all` | Print install commands for every plugin in the catalog |
| `--pack <name>` | Install a curated pack (see pack list below) |
| `--category <name>` | Install all plugins in a marketplace category |
| `--skills` | Install standalone skills (coming soon) |

**Available packs:**

| Pack | Plugin count | Included plugins |
|---|---|---|
| `devops` | 6 | terraform-specialist, kubernetes-architect, deployment-engineer, devops-troubleshooter, hybrid-cloud-architect, docker-pro |
| `security` | 4 | security-auditor, backend-security-coder, frontend-security-coder, mobile-security-coder |
| `api` | 3 | backend-architect, graphql-architect, fastapi-pro |
| `ai-ml` | 4 | ai-engineer, ml-engineer, mlops-engineer, prompt-engineer |
| `frontend` | 4 | frontend-developer, flutter-expert, mobile-developer, ui-ux-designer |
| `backend` | 10 | python-pro, golang-pro, rust-pro, java-pro, typescript-pro, csharp-pro, ruby-pro, php-pro, elixir-pro, scala-pro |
| `database` | 4 | database-optimizer, database-admin, sql-pro, data-engineer |
| `testing` | 4 | test-automator, debugger, error-detective, performance-engineer |

**Examples:**

```bash
# Install a single plugin (project scope, default)
ccpi install debugger

# Install with global scope
ccpi install debugger --global

# Install the DevOps pack
ccpi install --pack devops

# Install all security plugins
ccpi install --category security

# Install every plugin in the marketplace
ccpi install --all
```

### ccpi list

List plugins that are currently installed, or browse the full marketplace catalog.

```bash
# Installed plugins only
ccpi list

# All available plugins (grouped by category)
ccpi list --all
```

**Flags:**

| Flag | Description |
|---|---|
| `-a, --all` | Show all available plugins, not just installed ones |

The installed list includes plugin name, version, description, and install location (global or local). The `--all` view groups plugins by category and shows the full catalog count.

### ccpi search

Search the marketplace catalog by keyword. Matches against plugin names, descriptions, and keywords.

```bash
ccpi search kubernetes
```

This command searches the locally cached marketplace catalog. If no results appear, ensure the marketplace is added with `ccpi marketplace-add`.

### ccpi upgrade

Check for and apply plugin updates. The upgrade workflow uninstalls the current version and reinstalls the latest from the catalog.

```bash
# Show available updates with guidance
ccpi upgrade

# Check only (no upgrade guidance)
ccpi upgrade --check

# Guide upgrade of all outdated plugins
ccpi upgrade --all

# Guide upgrade of a specific plugin
ccpi upgrade --plugin terraform-specialist
```

**Flags:**

| Flag | Description |
|---|---|
| `--check` | List available updates without showing upgrade steps |
| `--all` | Show upgrade steps for every outdated plugin |
| `--plugin <name>` | Show upgrade steps for a specific plugin |

**How upgrades work:**

Claude Code does not have a native upgrade command yet. The ccpi upgrade flow generates a pair of commands for each update:

```bash
# Step 1: Uninstall current version
/plugin uninstall terraform-specialist@claude-code-plugins-plus

# Step 2: Install latest version
/plugin install terraform-specialist@claude-code-plugins-plus
```

Run these inside your Claude Code session. Plugin configuration is preserved across the uninstall/reinstall cycle.

### ccpi validate

Validate the structure and frontmatter of plugins, skills, commands, and agents. Useful for plugin authors and for diagnosing issues with installed plugins.

```bash
# Validate everything in the current directory
ccpi validate

# Validate a specific path
ccpi validate plugins/devops/terraform-specialist/

# Validate a single SKILL.md file
ccpi validate skills/pr-review/SKILL.md

# Strict mode (fail on warnings, used in CI)
ccpi validate --strict

# JSON output for programmatic consumption
ccpi validate --json
```

**Flags:**

| Flag | Description |
|---|---|
| `--skills` | Validate skills only |
| `--frontmatter` | Validate frontmatter only |
| `--strict` | Exit with non-zero code on warnings (for CI pipelines) |
| `--json` | Output results as JSON |

**What it checks:**

- **Plugin structure** -- `plugin.json` exists with required fields (`name`, `version`, `description`, `author`).
- **Skill frontmatter** -- SKILL.md files have valid YAML with required fields, allowed-tools syntax is correct, version follows semver.
- **Command frontmatter** -- command markdown files have properly structured YAML metadata.
- **Agent frontmatter** -- agent definitions include required fields (`name`, `description`).

For the authoritative, enterprise-grade validation with 100-point scoring, use the universal validator directly:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose
```

The universal validator is the source of truth for the Tons of Skills marketplace. The ccpi validator covers structural basics and is optimized for speed.

### ccpi doctor

Run comprehensive diagnostics on your Claude Code installation, plugin directory, and marketplace connection.

```bash
# Standard diagnostics
ccpi doctor

# Auto-fix safe issues
ccpi doctor --fix

# JSON output
ccpi doctor --json
```

**Flags:**

| Flag | Description |
|---|---|
| `--fix` | Automatically remediate safe issues (create missing directories, refresh stale catalogs) |
| `--json` | Output diagnostic results as JSON |

**Diagnostic categories:**

| Category | Checks |
|---|---|
| System | Node.js version, npm version, OS compatibility |
| Claude Code | Config directory exists, plugins directory exists, authentication status |
| Marketplace | Catalog file present, catalog parseable, plugin count valid |
| Plugins | Installed plugin structure, plugin.json validity |

The doctor command is the first thing to run when something is not working. Its output includes specific remediation steps for every warning and failure.

### ccpi marketplace

Manage the connection between ccpi and the Tons of Skills marketplace catalog.

```bash
# Show marketplace status
ccpi marketplace

# Verify marketplace installation
ccpi marketplace --verify

# Add the marketplace (first-time setup)
ccpi marketplace-add

# Remove the marketplace
ccpi marketplace-remove
```

The marketplace is identified by the slug `claude-code-plugins-plus` and the repository `jeremylongshore/claude-code-plugins`. Adding the marketplace downloads the catalog JSON from GitHub and stores it in Claude Code's config directory.

## Common workflows

### First-time setup

```bash
# 1. Install ccpi
npm install -g @intentsolutionsio/ccpi

# 2. Add the marketplace
ccpi marketplace-add

# 3. Verify everything works
ccpi doctor

# 4. Browse available plugins
ccpi list --all

# 5. Install your first plugin
ccpi install code-reviewer
```

### Daily plugin management

```bash
# Check for updates
ccpi upgrade --check

# Upgrade everything
ccpi upgrade --all

# Search for a new plugin
ccpi search "database migration"

# Install it
ccpi install database-migration-manager
```

### Plugin development

```bash
# Validate your plugin during development
ccpi validate .

# Strict validation before committing
ccpi validate --strict

# Check a single skill file
ccpi validate skills/my-skill/SKILL.md

# Run doctor to verify environment
ccpi doctor
```

### CI/CD integration

Add ccpi validation to your CI pipeline to catch plugin issues before they ship:

```yaml
# GitHub Actions example
- name: Validate plugins
  run: |
    npm install -g @intentsolutionsio/ccpi
    ccpi validate --strict --json > validation-results.json
```

The `--strict` flag causes ccpi to exit with a non-zero code if any warnings are found, which fails the CI step. The `--json` flag produces machine-readable output for further processing.

## Configuration and cache

### Cache location

The marketplace catalog is cached in Claude Code's config directory. The exact path depends on your operating system:

| OS | Config directory |
|---|---|
| macOS | `~/Library/Application Support/claude-code/` |
| Linux | `~/.config/claude-code/` or `$XDG_CONFIG_HOME/claude-code/` |
| Windows | `%APPDATA%/claude-code/` |

Within the config directory:

```
claude-code/
  marketplaces/
    claude-code-plugins-plus/
      .claude-plugin/
        marketplace.json      # Cached catalog
  plugins/
    installed_plugins.json    # Installed plugin registry
```

### Refreshing the cache

If the catalog seems stale (missing recently added plugins), refresh it:

```bash
ccpi marketplace-remove
ccpi marketplace-add
```

Or from inside Claude Code:

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
```

### Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude Code authentication |
| `XDG_CONFIG_HOME` | Override the default config directory on Linux |

## Relationship to Claude Code slash commands

The ccpi CLI and Claude Code's built-in `/plugin` slash commands serve complementary roles:

| Task | ccpi CLI (your terminal) | /plugin (Claude Code session) |
|---|---|---|
| Add marketplace | `ccpi marketplace-add` | `/plugin marketplace add ...` |
| Install plugin | `ccpi install <name>` (outputs command) | `/plugin install <name>@slug` (executes) |
| List plugins | `ccpi list` | `/plugin list` |
| Uninstall plugin | -- | `/plugin uninstall <name>@slug` |
| Validate | `ccpi validate` | -- |
| Diagnostics | `ccpi doctor` | -- |
| Search | `ccpi search <query>` | -- |
| Upgrade | `ccpi upgrade` | -- |

The ccpi CLI is a planning and management tool. It tells you what to do and validates that things are correct. The `/plugin` commands inside Claude Code are the execution layer that actually installs and removes plugins.

## Troubleshooting

### ccpi command not found after installation

Ensure the npm global bin directory is on your `PATH`:

```bash
# Find the directory
npm config get prefix

# Add to PATH (add to ~/.bashrc or ~/.zshrc for persistence)
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Catalog shows 0 plugins

The marketplace is not connected. Add it:

```bash
ccpi marketplace-add
```

### Validation reports false positives

The ccpi validator checks structural basics. For authoritative validation with the 100-point enterprise rubric, use the universal validator:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose
```

### Doctor reports failures in fix mode

Some issues cannot be auto-fixed (e.g., missing authentication, incompatible Node.js version). Follow the remediation steps in the doctor output to resolve these manually.

## Next steps

- [Install Claude Code Plugins](/docs/getting-started/installation) -- full setup walkthrough if you have not installed yet.
- [Install Your First Plugin](/docs/getting-started/first-plugin) -- hands-on plugin installation guide.
- [Your First Agent Skill](/docs/getting-started/first-skill) -- build a skill from scratch.
- [Browse the Marketplace](/explore) -- discover plugins on the web.
