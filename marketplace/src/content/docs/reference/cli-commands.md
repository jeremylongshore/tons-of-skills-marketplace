---
title: "ccpi CLI Command Reference"
description: "Complete command reference for the ccpi CLI tool, including syntax, options, examples, and common workflows for installing, managing, and validating Claude Code plugins."
section: "reference"
order: 5
keywords: ["ccpi", "CLI", "command line", "install", "search", "validate", "update", "remove", "marketplace"]
officialLinks:
  - title: "ccpi on npm"
    url: "https://www.npmjs.com/package/@intentsolutionsio/ccpi"
  - title: "Claude Code Plugins Documentation"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "getting-started/installation"
  - "getting-started/cli-reference"
  - "reference/plugin-json-schema"
---

## Overview

`ccpi` (Claude Code Plugin Installer) is the official CLI for managing Claude Code plugins from the Tons of Skills marketplace. It handles plugin discovery, installation, updates, removal, and validation from the command line.

The package is published to npm as `@intentsolutionsio/ccpi` and can be installed globally or used via `npx`.

```bash
# Install globally
npm install -g @intentsolutionsio/ccpi

# Or use via npx (no install required)
npx @intentsolutionsio/ccpi <command>
```

Once installed, all commands are available under the `ccpi` binary.

## Command Reference

### ccpi install

Install a plugin from the marketplace or a Git repository.

**Syntax:**

```
ccpi install <plugin>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<plugin>` | Plugin name from the marketplace, or a GitHub `owner/repo` path for direct repository installs. |

**Examples:**

```bash
# Install by marketplace name
ccpi install ci-optimizer

# Install from a GitHub repository
ccpi install jeremylongshore/claude-code-plugins

# Install a specific plugin from a monorepo
ccpi install jeremylongshore/claude-code-plugins --path plugins/devops/ci-optimizer
```

**Behavior:**

1. Resolves the plugin name against the marketplace catalog
2. Clones the plugin repository to the local plugin directory
3. Validates the plugin structure (checks for `plugin.json`, required fields)
4. Registers the plugin with Claude Code

If the plugin is already installed, `ccpi install` reports the current version and prompts for update if a newer version is available.

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | Installation successful |
| `1` | Plugin not found or network error |
| `2` | Validation failure (invalid plugin structure) |

---

### ccpi list

List all installed plugins.

**Syntax:**

```
ccpi list
```

**Options:**

This command takes no options. It scans the local plugin directory and displays all installed plugins with their name, version, and category.

**Example output:**

```
Installed plugins:

  ci-optimizer          v2.1.0    devops
  react-scaffolder      v1.3.2    frontend-development
  terraform-drift       v1.0.0    cloud-infrastructure
  security-scanner      v3.0.1    security

4 plugins installed
```

**Behavior:**

1. Scans the Claude Code plugin directory for installed plugins
2. Reads each plugin's `plugin.json` to extract metadata
3. Displays a formatted table sorted alphabetically by name

---

### ccpi search

Search the marketplace catalog for plugins matching a query.

**Syntax:**

```
ccpi search <query>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<query>` | Search string matched against plugin names, descriptions, keywords, and categories. |

**Examples:**

```bash
# Search by keyword
ccpi search terraform

# Search by category
ccpi search devops

# Search by problem domain
ccpi search "code review"

# Search by technology
ccpi search kubernetes
```

**Example output:**

```
Search results for "terraform":

  terraform-drift-detector    v2.1.0    devops
    Detect and remediate Terraform configuration drift

  terraform-module-gen        v1.4.0    cloud-infrastructure
    Generate Terraform modules from architecture diagrams

  iac-validator               v1.2.0    devops
    Validate infrastructure-as-code across Terraform, Pulumi, CDK

3 results found
```

**Behavior:**

1. Fetches the marketplace catalog (cached locally, refreshed periodically)
2. Runs a fuzzy search across plugin names, descriptions, keywords, and categories
3. Ranks results by relevance
4. Displays matching plugins with name, version, category, and description

**Search ranking factors:**

| Factor | Weight | Description |
|--------|--------|-------------|
| Name match | Highest | Exact or partial match in the plugin name |
| Description match | High | Keywords found in the description |
| Keywords match | Medium | Match against the `keywords` array in plugin.json |
| Category match | Medium | Match against the category name |

---

### ccpi update

Update one or all installed plugins to their latest versions.

**Syntax:**

```
ccpi update [plugin]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `[plugin]` | No | Plugin name to update. If omitted, updates all installed plugins. |

**Examples:**

```bash
# Update a specific plugin
ccpi update ci-optimizer

# Update all installed plugins
ccpi update
```

**Example output:**

```
Checking for updates...

  ci-optimizer      v2.1.0 → v2.2.0    updated
  react-scaffolder  v1.3.2              up to date
  security-scanner  v3.0.1 → v3.1.0    updated

2 plugins updated, 1 already up to date
```

**Behavior:**

1. Reads the installed version from each plugin's `plugin.json`
2. Fetches the latest version from the marketplace catalog
3. If a newer version is available, pulls the updated plugin
4. Validates the updated plugin structure
5. Reports the update results

**Version comparison:** Uses semantic versioning (SemVer) comparison. A version `2.2.0` is newer than `2.1.0`. Pre-release versions (e.g., `2.2.0-beta.1`) are not automatically installed unless already on a pre-release track.

---

### ccpi remove

Remove an installed plugin.

**Syntax:**

```
ccpi remove <plugin>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<plugin>` | Name of the installed plugin to remove. |

**Examples:**

```bash
# Remove a plugin
ccpi remove ci-optimizer
```

**Example output:**

```
Removed ci-optimizer v2.1.0
```

**Behavior:**

1. Locates the plugin in the local plugin directory
2. Removes the plugin directory and all its contents
3. Deregisters the plugin from Claude Code

If the plugin is not found, the command exits with an error and lists installed plugins.

**Data persistence:** Plugin data stored in `${CLAUDE_PLUGIN_DATA}` is **not** removed by `ccpi remove`. This directory persists across installs and removals, preserving user-generated state. To fully clean up, manually delete the data directory after removal.

---

### ccpi validate

Validate plugin structure and schema compliance.

**Syntax:**

```
ccpi validate [--strict]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--strict` | Enable strict validation mode. Fails on warnings that would normally be non-blocking. |

**Examples:**

```bash
# Standard validation
ccpi validate

# Strict validation (CI mode)
ccpi validate --strict
```

**Example output (passing):**

```
Validating plugin structure...

  plugin.json          valid
  README.md            present
  skills/              2 skills found
    code-review        valid (7 tools)
    lint-fix           valid (5 tools)
  commands/            1 command found
    analyze            valid

Validation passed (0 errors, 0 warnings)
```

**Example output (failing):**

```
Validating plugin structure...

  plugin.json          valid
  README.md            MISSING
  skills/              2 skills found
    code-review        valid (7 tools)
    lint-fix           ERROR: unknown tool "Readfile"

Validation failed (1 error, 1 warning)
  ERROR: skills/lint-fix/SKILL.md - unknown tool "Readfile" in allowed-tools
  WARNING: README.md is missing
```

**Checks performed:**

| Check | Standard | Strict |
|-------|----------|--------|
| `plugin.json` exists and is valid JSON | Error | Error |
| Required fields present (name, version, description, author) | Error | Error |
| No extra fields in plugin.json | Error | Error |
| Author is an object with `name` property | Error | Error |
| URLs are valid (repository, homepage, author.url) | Warning | Error |
| `README.md` exists | Warning | Error |
| SKILL.md frontmatter has required fields | Error | Error |
| Tool names in `allowed-tools` are valid | Error | Error |
| Version follows SemVer | Warning | Error |
| License is a valid SPDX identifier | Warning | Error |

**Behavior:**

1. Scans the current directory (or specified path) for plugin structure
2. Validates `plugin.json` against the schema
3. Validates each SKILL.md frontmatter against the skill schema
4. Validates each command and agent markdown frontmatter
5. Reports all errors and warnings
6. Exits with code 0 (pass) or 1 (fail)

For more comprehensive validation, use the universal validator with the `--enterprise` flag. See the [Validation](#validation-pipeline) section below.

---

### ccpi marketplace add

Add a marketplace source for plugin discovery. This enables `ccpi search` and `ccpi install` to find plugins from the specified repository.

**Syntax:**

```
ccpi marketplace add <repo>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<repo>` | GitHub repository in `owner/repo` format that hosts a plugin marketplace catalog. |

**Examples:**

```bash
# Add the Tons of Skills marketplace
ccpi marketplace add jeremylongshore/claude-code-plugins
```

**Behavior:**

1. Fetches the `marketplace.json` catalog from the specified repository
2. Caches the catalog locally for offline search
3. Registers the source for future `ccpi search` and `ccpi install` commands

The default marketplace source is the Tons of Skills catalog hosted at `tonsofskills.com/catalog.json`. Adding additional sources allows organizations to host private plugin catalogs alongside the public marketplace.

---

### ccpi info

Display detailed information about a plugin.

**Syntax:**

```
ccpi info <plugin>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<plugin>` | Plugin name from the marketplace or an installed plugin. |

**Examples:**

```bash
# Show plugin details
ccpi info ci-optimizer
```

**Example output:**

```
ci-optimizer v2.1.0

  Description:  Optimize CI/CD pipeline configurations for faster builds
  Author:       Jane Smith <jane@example.com>
  License:      MIT
  Category:     devops
  Repository:   https://github.com/janesmith/ci-optimizer
  Homepage:     https://ci-optimizer.dev

  Keywords:     ci, cd, pipeline, optimization, github-actions, gitlab-ci

  Skills:       2
    pipeline-audit        Audit CI pipeline for performance issues
    config-optimizer      Generate optimized CI configurations

  Commands:     1
    analyze               Run CI analysis on current project

  Installed:    Yes (v2.1.0, up to date)
```

**Behavior:**

1. Looks up the plugin in the marketplace catalog
2. If installed locally, reads the local `plugin.json` for installed version
3. Displays all metadata fields and lists skills, commands, and agents
4. Indicates whether the plugin is installed and up to date

---

## Common Workflows

### First-Time Setup

Install the CLI and add the Tons of Skills marketplace:

```bash
npm install -g @intentsolutionsio/ccpi
ccpi marketplace add jeremylongshore/claude-code-plugins
```

### Discover and Install Plugins

Search for plugins by keyword, review details, then install:

```bash
ccpi search "code review"
ccpi info code-reviewer
ccpi install code-reviewer
```

### Keep Plugins Updated

Periodically check for and apply updates:

```bash
ccpi update
```

### Validate Before Publishing

Run validation locally before submitting a plugin to the marketplace:

```bash
cd plugins/category/my-plugin/
ccpi validate --strict
```

For enterprise-grade validation, use the universal validator:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/my-plugin/
```

### Clean Up Unused Plugins

List installed plugins, review what is no longer needed, and remove:

```bash
ccpi list
ccpi remove old-plugin
```

## Catalog Caching

The `ccpi` CLI caches the marketplace catalog locally to enable fast searches and reduce network requests. Understanding the cache behavior helps troubleshoot stale search results.

### Cache Location

The catalog cache is stored in the user's local data directory. The exact path depends on the operating system:

| OS | Cache Path |
|----|-----------|
| Linux | `~/.local/share/ccpi/catalog-cache.json` |
| macOS | `~/Library/Application Support/ccpi/catalog-cache.json` |
| Windows | `%APPDATA%\ccpi\catalog-cache.json` |

### Cache Refresh

The cache refreshes automatically when:

- `ccpi search` is run and the cache is older than 24 hours
- `ccpi update` is run (always fetches fresh catalog)
- `ccpi marketplace add` is run (fetches and caches the new source)

To force a cache refresh, delete the cache file or run `ccpi update`.

## Validation Pipeline

The `ccpi validate` command provides quick structural validation suitable for development. For comprehensive validation, the ecosystem provides a multi-tier pipeline:

| Tier | Tool | Coverage |
|------|------|----------|
| **Quick** | `ccpi validate` | JSON validity, required fields, tool names |
| **Strict** | `ccpi validate --strict` | All quick checks + warnings become errors |
| **Enterprise** | `python3 scripts/validate-skills-schema.py --enterprise` | 100-point rubric: documentation quality, body structure, code examples, completeness |
| **CI** | `validate-plugins.yml` | All tiers + build verification + secret scanning + performance budgets |

For marketplace submissions, plugins must pass at minimum the strict tier. The enterprise tier provides a compliance score and letter grade (A through F) used for marketplace quality rankings.

```bash
# Quick check during development
ccpi validate

# Pre-submission check
ccpi validate --strict

# Enterprise compliance score
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/your-plugin/

# Full CI simulation (runs all checks)
./scripts/quick-test.sh
```

## Exit Codes

All `ccpi` commands follow standard Unix exit code conventions:

| Code | Meaning |
|------|---------|
| `0` | Command completed successfully |
| `1` | General error (plugin not found, network failure, validation failure) |
| `2` | Usage error (invalid arguments, missing required parameters) |

Scripts and CI pipelines can check exit codes to determine command success:

```bash
ccpi validate --strict || echo "Validation failed"
```

## Global Options

These options are available on all `ccpi` commands:

| Option | Description |
|--------|-------------|
| `--help` | Display help for the command |
| `--version` | Display the ccpi version |

```bash
# Show help
ccpi --help
ccpi install --help

# Show version
ccpi --version
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CCPI_CATALOG_URL` | Override the default marketplace catalog URL | `https://tonsofskills.com/catalog.json` |
| `CCPI_PLUGIN_DIR` | Override the default plugin install directory | `~/.claude/plugins` |
| `CCPI_CACHE_TTL` | Cache time-to-live in seconds | `86400` (24 hours) |

Set environment variables in your shell profile for persistent configuration:

```bash
# ~/.bashrc or ~/.zshrc
export CCPI_CATALOG_URL="https://internal.company.com/plugins/catalog.json"
```

## Troubleshooting

### "Plugin not found" on install

The marketplace catalog may be stale. Force a refresh:

```bash
ccpi update  # Refreshes the catalog cache
ccpi search <plugin-name>  # Verify the plugin exists
ccpi install <plugin-name>
```

### Search returns no results

Check that a marketplace source is configured:

```bash
ccpi marketplace add jeremylongshore/claude-code-plugins
ccpi search <query>
```

### Validation passes locally but fails in CI

CI runs `ccpi validate --strict`, which treats warnings as errors. Run strict mode locally to reproduce:

```bash
ccpi validate --strict
```

Common strict-mode failures: missing `README.md`, non-SemVer version strings, invalid SPDX license identifiers.

### Plugin installed but not appearing in Claude Code

Restart Claude Code after installing a plugin. Claude Code scans the plugin directory at startup and may not detect newly installed plugins mid-session.
