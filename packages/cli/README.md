# @intentsolutionsio/ccpi

> Command-line tool for installing and managing Claude Code plugins from [tonsofskills.com](https://tonsofskills.com)

[![npm version](https://img.shields.io/npm/v/@intentsolutionsio/ccpi.svg)](https://www.npmjs.com/package/@intentsolutionsio/ccpi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **One-Command Installation**: Install plugins with a single command
- **Universal Compatibility**: Works with npm, bun, pnpm, and deno
- **Built-in Diagnostics**: `ccpi doctor` checks your Claude Code installation
- **Cross-Platform**: Supports Linux, macOS, and Windows
- **Zero Configuration**: Automatically detects Claude Code paths

## Installation

You don't need to install this package globally. Just use your preferred package manager:

### npm / npx

```bash
npx @intentsolutionsio/ccpi install <plugin-name>
```

### Bun

```bash
bunx @intentsolutionsio/ccpi install <plugin-name>
```

### pnpm

```bash
pnpx @intentsolutionsio/ccpi install <plugin-name>
```

### Deno

```bash
deno run -A npm:@intentsolutionsio/ccpi install <plugin-name>
```

## Quick Start

### Install a Plugin

```bash
npx @intentsolutionsio/ccpi install devops-pack
```

### List Installed Plugins

```bash
npx @intentsolutionsio/ccpi list
```

### Run Diagnostics

```bash
npx @intentsolutionsio/ccpi doctor
```

### Search for Plugins

```bash
npx @intentsolutionsio/ccpi search terraform
```

## Commands

### `tons skills install <skill-directory>`

Install a first-party skill from a clean Git checkout into a verified harness path:

```bash
tons skills install ./plugins/testing/example/skills/example-skill --harness claude-code --scope project
```

The source must be a committed `plugins/<category>/<plugin>/skills/<skill>` directory
with an HTTPS or SSH `origin`. Uncommitted, untracked, ignored, symlinked, and mirrored
sources are refused. Installation uses committed Git bytes and preserves executable
modes; it never copies the checkout recursively or overwrites an existing skill.

Allowed content is `SKILL.md`, `README.md`, `LICENSE`, `LICENSE.md`, `eval-spec.yaml`,
and files under `assets/`, `examples/`, `references/`, `scripts/`, or `templates/`.
Hidden files, credential/key files, caches, build output, and local databases are
refused even when tracked. Review committed skill content before installing it.

Each installation includes `.ccpi-portable-install.json`, binding its file hashes to
the source repository, commit, tree, harness, and CLI compatibility validation.
The associated validation report is retained without automatic expiry in the harness
skill root's `.ccpi-evidence/` directory. This local receipt records provenance and
compatibility; it does not certify marketplace quality or skill behavior. Installers
use an exclusive per-skill lock and publish the verified directory by atomic rename.

`--dry-run` performs the same source and validation checks without creating harness
paths. `--scope user` selects the harness's user directory. `--json` includes the
destination and receipt path. Unknown and unverified harnesses are refused.

### `tons skills doctor`

Inspect installed byte integrity without changing files:

```bash
tons skills doctor --harness claude-code --source-repo /path/to/trusted/checkout --json
tons skills doctor --harness claude-code --source-repo /path/to/trusted/checkout --skill example-skill
```

The selected source repository defaults to the current directory. Doctor checks its
origin identity and committed history against each receipt, rehashes installed files,
and verifies retained compatibility evidence. It reports `verified`, `outdated`,
`locally-modified`, `missing`, or `unverifiable` in the **integrity** field. Every
result includes source commit/path and expected/installed digest evidence, or an
explicit unavailable value. `--skill` can diagnose an absent installation; without
it, doctor inspects the visible entries in the harness skill directory.

`verified` here means byte identity only. Quality remains `not-assessed`; this command
does not certify marketplace grades, production readiness, or behavioral evaluations.
The selected checkout is your trust source; a receipt cannot authenticate itself.
Malformed receipts, missing evidence, and mismatched repository provenance fail closed.

Update availability is reported separately against the selected repository's local
`HEAD`, never an implied latest remote version. A newer unrelated commit is not a
skill update. A deleted source path can leave original bytes verified while current
source availability is unknown. Local modifications remain visible even when an
update exists. Doctor never fetches, checks out commits, refreshes the Git index,
uploads installed content, writes reports, or repairs a skill. Review its suggested
next action and preserve local work before explicitly changing anything.

### `ccpi install <plugin>`

Install a plugin from the marketplace.

**Options:**

- `-y, --yes` - Skip confirmation prompts
- `--global` - Install globally for all projects (default: project-local if in a project)

**Example:**

```bash
npx @intentsolutionsio/ccpi install python-pro
```

### `ccpi upgrade`

Check for and install plugin updates.

**Options:**

- `--check` - Check for available updates without upgrading
- `--all` - Upgrade all plugins with available updates
- `--plugin <name>` - Upgrade a specific plugin

**Examples:**

```bash
# Check for available updates
npx @intentsolutionsio/ccpi upgrade --check

# Upgrade all plugins
npx @intentsolutionsio/ccpi upgrade --all

# Upgrade a specific plugin
npx @intentsolutionsio/ccpi upgrade --plugin python-pro
```

**Sample Output (Updates Available):**

```
Plugin Upgrade Manager

2 update(s) available:

  python-pro
    Current: 1.0.0 -> Latest: 1.2.0
    Write idiomatic Python code with advanced features

  devops-pack
    Current: 2.1.0 -> Latest: 2.3.0
    Complete DevOps toolchain

To upgrade:

   npx @intentsolutionsio/ccpi upgrade --all
   (Updates all plugins)

   npx @intentsolutionsio/ccpi upgrade --plugin <name>
   (Updates specific plugin)
```

**Version Pinning:**

To pin a plugin to a specific version, simply keep the current version installed and don't upgrade. The CLI will continue to show available updates, but you can choose when to upgrade.

### `ccpi list`

List installed plugins.

**Options:**

- `-a, --all` - Show all available plugins (not just installed)

**Example:**

```bash
npx @intentsolutionsio/ccpi list --all
```

### `ccpi doctor`

Run diagnostics on your Claude Code installation and plugins.

**Options:**

- `--json` - Output results as JSON

**Example:**

```bash
npx @intentsolutionsio/ccpi doctor
```

**Sample Output:**

```
Claude Code Plugins - System Diagnostics

System Environment:
  Node.js Version: v22.20.0 (supported)
  Operating System: linux 6.8.0-86-generic
  Package Managers: npm, bun

Claude Code Installation:
  Claude Config Directory: /home/user/.claude
  Plugins Directory: /home/user/.claude/plugins
  Marketplaces Directory: /home/user/.claude/marketplaces

Plugins:
  Installed Plugins: 5 total (3 global, 2 local)

Marketplace:
  Marketplace Catalog: Installed
  Catalog Freshness: Up to date

Summary:
  9 passed

All checks passed! Your Claude Code setup is healthy.
```

### `ccpi search <query>`

Search for plugins in the marketplace.

**Example:**

```bash
npx @intentsolutionsio/ccpi search terraform
```

_Note: Search functionality coming soon. For now, visit [tonsofskills.com](https://tonsofskills.com) to browse plugins._

### `ccpi analytics`

View plugin usage analytics (Coming Soon).

**Options:**

- `--json` - Output as JSON

### `ccpi marketplace`

Manage marketplace connection and setup.

**Options:**

- `--verify` - Verify marketplace installation and show detailed status

**Example:**

```bash
# Check marketplace status
npx @intentsolutionsio/ccpi marketplace

# Verify installation with detailed diagnostics
npx @intentsolutionsio/ccpi marketplace --verify
```

**Sample Output (Not Installed):**

```
Claude Code Plugins Marketplace

Marketplace not added yet

Setup Instructions:

1. Open Claude Code (terminal or desktop app)
2. Run this command:

   /plugin marketplace add jeremylongshore/claude-code-plugins

3. Wait for confirmation (usually < 5 seconds)
4. Verify installation:

   npx @intentsolutionsio/ccpi marketplace --verify
```

**Sample Output (Installed):**

```
Claude Code Plugins Marketplace

Marketplace is already added!

Marketplace Status:

Installation:
  Marketplace added
  Location: /home/user/.claude/marketplaces/claude-code-plugins-plus

  Catalog found
  File: /home/user/.claude/marketplaces/claude-code-plugins-plus/.claude-plugin/marketplace.json
```

### `ccpi marketplace-add`

Guide you through adding the marketplace to Claude Code.

**Example:**

```bash
npx @intentsolutionsio/ccpi marketplace-add
```

### `ccpi marketplace-remove`

Guide you through removing the marketplace from Claude Code.

**Example:**

```bash
npx @intentsolutionsio/ccpi marketplace-remove
```

## Package Manager Performance

| Package Manager | Startup Time | Market Share |
| --------------- | ------------ | ------------ |
| Bun (bunx)      | ~0.05s       | ~5%          |
| Deno            | ~0.1s        | ~5%          |
| pnpm (pnpx)     | ~0.5s        | ~10%         |
| npm (npx)       | ~2-5s        | ~80%         |

**Recommendation**: For fastest performance, use `bunx` if you have Bun installed.

## Configuration

No configuration required! The CLI automatically:

- Detects your Claude Code installation directory
- Finds your global plugins directory (`~/.claude/plugins`)
- Detects project-local plugins (`.claude-plugin/` directory)
- Creates necessary directories if they don't exist

### Supported Paths

**Linux & macOS:**

- Config: `~/.claude`
- Plugins: `~/.claude/plugins`
- Marketplaces: `~/.claude/marketplaces`

**Windows:**

- Config: `%APPDATA%\Claude`
- Plugins: `%APPDATA%\Claude\plugins`
- Marketplaces: `%APPDATA%\Claude\marketplaces`

## Requirements

- Node.js 22 or higher (18 and 20 are end of life). ccpi 3.0.0 dropped them; on Node 18 or 20, stay on `@intentsolutionsio/ccpi@2`.
- Claude Code installed and run at least once

## Troubleshooting

### "Claude Code config directory not found"

Ensure Claude Code is installed and has been run at least once. The CLI looks for:

- Linux/macOS: `~/.claude`
- Windows: `%APPDATA%\Claude`

Run `ccpi doctor` to diagnose installation issues.

### Permission Errors

If you get permission errors during installation:

1. Try installing locally (project-level) instead of globally
2. Check that you have write permissions to the Claude directories
3. Run `ccpi doctor` to check your setup

### Plugin Not Found

If a plugin can't be found:

1. Check the plugin name spelling
2. Run `ccpi list --all` to see available plugins
3. Visit [tonsofskills.com](https://tonsofskills.com) to browse the full marketplace
4. Ensure your marketplace catalog is up to date

## Development

### Setup

```bash
npm install
npm run build
```

### Testing

```bash
npm test
```

### Build

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## Architecture

The CLI is built with:

- **Commander.js** - CLI framework
- **Chalk** - Terminal styling
- **Ora** - Loading spinners
- **fs-extra** - File system operations
- **axios** - HTTP requests

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../000-docs/007-DR-GUID-contributing.md) for guidelines.

## License

MIT (c) [Intent Solutions IO](https://intentsolutions.io)

## Links

- **Website**: [tonsofskills.com](https://tonsofskills.com)
- **GitHub**: [jeremylongshore/claude-code-plugins](https://github.com/jeremylongshore/claude-code-plugins)
- **Issues**: [GitHub Issues](https://github.com/jeremylongshore/claude-code-plugins/issues)
- **Marketplace**: [Browse Plugins](https://tonsofskills.com)

---

**Built with love for the Claude Code community**
