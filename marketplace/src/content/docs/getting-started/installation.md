---
title: 'Install Claude Code Plugins'
description: 'Complete installation guide for Claude Code plugins. Set up the ccpi CLI, connect to the Tons of Skills marketplace, and start extending Claude Code with 2,800+ agent skills.'
section: 'getting-started'
order: 1
keywords:
  - "install Claude Code plugins"
  - "ccpi CLI"
  - "Claude Code setup"
  - "Tons of Skills marketplace"
  - "plugin installation"
  - "Claude Code extensions"
officialLinks:
  - title: 'Claude Code Overview'
    url: 'https://code.claude.com/docs/en/overview'
  - title: 'Claude Code CLI Installation'
    url: 'https://code.claude.com/docs/en/getting-started'
  - title: 'ccpi on npm'
    url: 'https://www.npmjs.com/package/@intentsolutionsio/ccpi'
relatedDocs:
  - 'getting-started/first-plugin'
  - 'getting-started/cli-reference'
---

## Choose an installation route

Claude Code installs marketplace plugins. The `ccpi` companion CLI provides plugin discovery guidance, installation commands, diagnostics, and local authoring checks; several commands are guidance rather than an installer. Portable skills use a separate `ccpi skills install` workflow.

Browse the current [marketplace](/explore) rather than relying on a fixed plugin or skill count. Adding a marketplace makes its catalog available; it does not install every plugin or approve its code.

## Prerequisites

- Install and authenticate [Claude Code](https://code.claude.com/docs/en/setup) using a supported account or provider configuration. An API key is one option, not a requirement for subscription login. Do not paste credentials into source files or shared logs.
- The independently installed `ccpi` CLI also requires Node.js 22 or later. Repository development and website builds require Node 22.12+ and the repository's pinned package-manager versions; see the [runtime contract](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/000-docs/814-DR-STND-node-runtime-contract.md).
- Review the plugin's ownership, dependencies, permissions, and supported runtime before installing it. A listing or structural validation result is not a behavioral security certification.

Check the tools you intend to use:

```bash
node --version
npm --version
claude --version
```

If you already use `nvm`, select the repository's Node 22 line and verify that the installed patch version is at least 22.12:

```bash
nvm install 22
nvm use 22
node --version
```

The official setup guide covers native, package-manager, and npm installation routes. If you choose npm for Claude Code:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

Do not use `sudo` to work around npm permission problems; follow the setup guide for an appropriate user installation.

## Add the marketplace

Run this in a terminal:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
```

The equivalent interactive command, inside Claude Code, is:

```text
/plugin marketplace add jeremylongshore/tons-of-skills-marketplace
```

Use the [native plugin manager](https://code.claude.com/docs/en/discover-plugins) to inspect configured marketplaces and installed plugins. Do not treat a printed setup command as evidence it ran.

## Install a plugin

For example, `git-commit-smart` is a plugin in this marketplace. Review its listing and dependencies first, then choose an explicit scope:

```bash
claude plugin install git-commit-smart@claude-code-plugins-plus --scope project
```

| Native scope | Who gets the enablement setting            | Settings location             |
| ------------ | ------------------------------------------ | ----------------------------- |
| `user`       | You, across projects on this machine       | `~/.claude/settings.json`     |
| `project`    | Collaborators using the repository setting | `.claude/settings.json`       |
| `local`      | You, in this repository only               | `.claude/settings.local.json` |

The native CLI defaults to user scope. A committed project setting does not download a plugin to every collaborator's machine: each collaborator still installs it. A plugin may also start disabled. Check the native install result and enablement state.

Shell installs load in a new Claude Code session or after `/reload-plugins` in an existing session. Check the installed plugin list and the plugin's namespaced skills rather than assuming every runtime component is immediately active.

## Optional: install ccpi

```bash
npm install -g @intentsolutionsio/ccpi
ccpi --version
ccpi --help
```

Or inspect help without a global installation:

```bash
npx @intentsolutionsio/ccpi --help
```

`npx` can download and execute a package. Review the publisher and selected version; it is not an offline or no-install guarantee. The repository package currently uses the 3.x version line; consult the installed version's help for its actual surface.

### Implemented companion commands

| Command                                    | Current behavior                                                                              |
| ------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `ccpi list` / `ccpi list --all`            | Show installed plugins or the available catalog                                               |
| `ccpi install <name>`                      | Look up a catalog plugin and print guided native installation instructions                    |
| `ccpi install --pack <name>`               | Print instructions for the named built-in collection                                          |
| `ccpi install --category <name>` / `--all` | Print instructions for selected catalog plugins                                               |
| `ccpi marketplace-add`                     | Print the native marketplace setup instructions                                               |
| `ccpi marketplace --verify`                | Inspect the expected marketplace directory and catalog-file presence                          |
| `ccpi upgrade --check`                     | Compare installed and catalog versions                                                        |
| `ccpi upgrade --all`                       | Print guided upgrade steps; it does not apply all upgrades itself                             |
| `ccpi doctor`                              | Inspect the supported environment, directories, installation registry, and catalog integrity  |
| `ccpi validate <path>`                     | Run companion authoring checks; use the repository Python validator for authoritative grading |

`ccpi search` and `ccpi analytics` currently report that their features are coming soon. Use the website for search. There are no `ccpi update`, `ccpi remove`, or `ccpi info` commands in this version.

The companion's legacy guided output can contain `--project` or `--global`; those are not the native `--scope` syntax above. Use the native help rather than copying unsupported flags. This documentation does not change the companion implementation.

## Verify the result

```bash
claude plugin list
ccpi doctor
```

Check each result separately. `ccpi marketplace --verify` does not prove that every catalog entry parses or that authentication succeeds. `ccpi doctor` does not verify an authenticated Claude account or certify every plugin's behavior.

`ccpi doctor --fix` can create missing directories and refresh catalog data. Review its current repair plan and intended paths before allowing writes; it is not an authentication repair command.

## Troubleshooting

| Symptom                                 | Next check                                                                                                                    |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `ccpi` is not found                     | Inspect the npm installation prefix and your platform's PATH configuration; do not overwrite your shell profile blindly       |
| Marketplace is missing                  | Run the native marketplace-add command, then inspect its result                                                               |
| Plugin name is not found                | Check the current catalog identity on [Explore](/explore); a sample or retired name may not exist                             |
| Installed plugin is absent in a session | Check scope, enablement, marketplace trust, and `/reload-plugins` or a new session                                            |
| Authentication fails                    | Follow the selected Claude Code provider's authentication instructions; do not infer success from directory existence         |
| An MCP tool fails to launch             | Review the plugin's entry path, dependencies, environment requirements, and stderr; installation is not runtime certification |

Use the native plugin manager for update and uninstall operations. Review data-retention behavior before uninstalling or deleting plugin state; this guide does not promise that arbitrary plugin configuration survives every update.

## Next steps

- [Install your first plugin](/docs/getting-started/first-plugin)
- [Companion CLI quick reference](/docs/getting-started/cli-reference)
- [Detailed command reference](/docs/reference/cli-commands)
- [Browse plugins](/explore)
