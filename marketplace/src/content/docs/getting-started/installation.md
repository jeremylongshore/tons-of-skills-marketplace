---
title: "Install Claude Code Plugins"
description: "Complete installation guide for Claude Code plugins. Set up the ccpi CLI, connect to the Tons of Skills marketplace, and start extending Claude Code with 2,800+ agent skills."
section: "getting-started"
order: 1
keywords: ["install Claude Code plugins", "ccpi CLI", "Claude Code setup", "Tons of Skills marketplace", "plugin installation", "Claude Code extensions"]
officialLinks:
  - title: "Claude Code Overview"
    url: "https://code.claude.com/docs/en/overview"
  - title: "Claude Code CLI Installation"
    url: "https://code.claude.com/docs/en/getting-started"
  - title: "ccpi on npm"
    url: "https://www.npmjs.com/package/@intentsolutionsio/ccpi"
relatedDocs:
  - "getting-started/first-plugin"
  - "getting-started/cli-reference"
---

## Overview

Claude Code is Anthropic's agentic coding assistant that runs in your terminal. Out of the box, it reads your codebase, edits files, runs commands, and reasons about complex engineering problems. Plugins extend Claude Code with specialized skills, slash commands, and autonomous agents that cover domains from DevOps to security auditing to SaaS integrations.

This guide walks you through every step required to go from a bare terminal to a fully equipped Claude Code environment with access to the Tons of Skills marketplace -- 418 plugins and 2,834 agent skills you can install in seconds.

## Prerequisites

Before you begin, confirm that the following are in place.

### Node.js 18 or later

Claude Code and its plugin tooling require Node.js 18+. Check your version:

```bash
node --version
# Expected output: v18.x.x or higher (v20+ recommended)
```

If you need to install or upgrade Node.js, use [nvm](https://github.com/nvm-sh/nvm) (macOS / Linux) or download the LTS installer from [nodejs.org](https://nodejs.org).

```bash
# Using nvm (recommended)
nvm install 20
nvm use 20
```

### npm 9 or later

npm ships with Node.js, but confirm you have a recent version:

```bash
npm --version
# Expected output: 9.x.x or higher
```

### Claude Code CLI

Install the Claude Code CLI globally:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify the installation:

```bash
claude --version
```

If the command is not found, make sure your npm global bin directory is on your `PATH`. On most systems this is `~/.npm-global/bin` or the path shown by `npm config get prefix`.

### Anthropic API key or subscription

Claude Code requires authentication. You can use either:

- **Anthropic API key** -- set `ANTHROPIC_API_KEY` in your environment or pass it during first launch.
- **Claude Pro, Team, or Enterprise subscription** -- authenticate through the interactive login flow when you first run `claude`.

Refer to the [Claude Code getting-started guide](https://code.claude.com/docs/en/getting-started) for detailed authentication instructions.

## Step 1: Install the ccpi CLI

The `ccpi` CLI (`@intentsolutionsio/ccpi`) is the companion command-line tool for managing Claude Code plugins outside of a Claude session. It handles marketplace connections, plugin discovery, validation, upgrades, and diagnostics.

```bash
npm install -g @intentsolutionsio/ccpi
```

Confirm the installation:

```bash
ccpi --version
```

You should see a version string such as `1.x.x`. If you prefer not to install globally, you can run it on demand with `npx`:

```bash
npx @intentsolutionsio/ccpi --version
```

### What ccpi provides

| Capability | Command | Description |
|---|---|---|
| Install plugins | `ccpi install <name>` | Guided install of a marketplace plugin |
| List plugins | `ccpi list` | Show installed plugins |
| Search | `ccpi search <query>` | Find plugins by keyword |
| Upgrade | `ccpi upgrade --check` | Check for available updates |
| Validate | `ccpi validate` | Lint plugin structure and frontmatter |
| Diagnostics | `ccpi doctor` | Full system health check |

See the [ccpi CLI Quick Reference](/docs/getting-started/cli-reference) for the complete command catalogue.

## Step 2: Add the Tons of Skills marketplace

The marketplace is the central catalog that maps plugin names to their source repository. Adding it gives Claude Code access to every plugin published on [tonsofskills.com](https://tonsofskills.com).

### Option A: From inside Claude Code (recommended)

Launch Claude Code in any project directory and run the built-in slash command:

```bash
# Start Claude Code
claude

# Inside the Claude Code session:
/plugin marketplace add jeremylongshore/claude-code-plugins
```

Claude Code downloads the marketplace catalog and indexes all available plugins. This is a one-time operation -- the catalog persists across sessions and projects.

### Option B: Using the ccpi CLI

If you prefer to set things up from your regular terminal first:

```bash
ccpi marketplace-add
```

This writes the same catalog files that the `/plugin marketplace add` command creates, so the result is identical.

### Verify the marketplace connection

```bash
ccpi marketplace --verify
```

A successful response confirms the marketplace slug (`claude-code-plugins-plus`), the catalog location on disk, and the number of available plugins.

## Step 3: Verify your installation

Run the built-in diagnostics to make sure everything is wired up:

```bash
ccpi doctor
```

The doctor command checks:

- **System environment** -- Node.js version, npm version, OS compatibility.
- **Claude Code installation** -- config directory, plugins directory, authentication status.
- **Marketplace catalog** -- catalog file exists and is parseable, plugin count matches expectations.
- **Installed plugins** -- structural validity of every installed plugin.

If any check reports a warning or failure, the output includes remediation steps. You can also run with the `--fix` flag to automatically resolve safe issues such as missing directories or stale catalog caches:

```bash
ccpi doctor --fix
```

### Quick smoke test

List all available plugins to confirm the catalog loaded:

```bash
ccpi list --all
```

You should see 418 plugins grouped by category. If the list is empty, re-run `ccpi marketplace-add` and try again.

## Step 4: Install your first plugin

With the marketplace connected, install any plugin by name. For example, to install the `code-reviewer` plugin:

```bash
ccpi install code-reviewer
```

The CLI confirms the plugin exists in the catalog, checks whether it is already installed, and prints the exact `/plugin install` command to run inside Claude Code:

```bash
/plugin install code-reviewer@claude-code-plugins-plus --project
```

Paste that command into your Claude Code session. The plugin's skills, commands, and agents are available immediately -- no restart required.

For a detailed walkthrough of browsing, installing, and using your first plugin, see [Install Your First Plugin](/docs/getting-started/first-plugin).

## Installation scope: global vs. project

Every plugin install has a scope:

| Scope | Flag | Effect |
|---|---|---|
| Project | `--project` | Plugin is available only in the current project directory |
| Global | `--global` | Plugin is available in every project you open with Claude Code |

Project scope is the default and is recommended for most use cases. It keeps your plugin surface area small and avoids loading irrelevant skills in unrelated projects. Use global scope for plugins you want everywhere, such as a general-purpose code reviewer or debugger.

## Bulk installation options

### Install a curated pack

Packs are curated collections of related plugins. Install an entire pack in one step:

```bash
ccpi install --pack devops
```

Available packs include `devops`, `security`, `api`, `ai-ml`, `frontend`, `backend`, `database`, and `testing`. Each pack installs between 3 and 10 plugins.

### Install by category

Install every plugin in a marketplace category:

```bash
ccpi install --category security
```

### Install everything

Install all 418 plugins at once:

```bash
ccpi install --all
```

This outputs a full list of `/plugin install` commands grouped by category. It is primarily useful for evaluation environments or teams that want to expose the entire catalog to developers.

## Troubleshooting

### `ccpi` command not found

Your npm global bin directory is not on your `PATH`. Find it with:

```bash
npm config get prefix
```

Add the `bin` subdirectory of that path to your shell profile (`~/.bashrc`, `~/.zshrc`, or equivalent):

```bash
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Marketplace catalog is empty

Re-add the marketplace:

```bash
ccpi marketplace-add
```

Or from inside Claude Code:

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
```

### Doctor reports authentication failure

Claude Code is not authenticated. Launch `claude` in your terminal and follow the interactive login flow, or set `ANTHROPIC_API_KEY` in your environment:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Plugin install command does nothing

Make sure you are running the `/plugin install` command inside an active Claude Code session, not in your regular terminal. The `/plugin` prefix is a Claude Code slash command, not a shell command.

## Keeping plugins up to date

After initial setup, check for updates periodically:

```bash
ccpi upgrade --check
```

If updates are available, apply them all at once:

```bash
ccpi upgrade --all
```

The upgrade flow uninstalls the old version and reinstalls the latest from the catalog. Plugin configuration is preserved across upgrades.

## Next steps

- [Install Your First Plugin](/docs/getting-started/first-plugin) -- a hands-on walkthrough of browsing, installing, and using a plugin.
- [ccpi CLI Quick Reference](/docs/getting-started/cli-reference) -- every command, flag, and workflow in one page.
- [Browse the Marketplace](/explore) -- search and filter all 418 plugins and 2,834 skills.
