---
title: 'Install Your First Plugin'
description: 'Step-by-step guide to browsing the Tons of Skills marketplace, installing a Claude Code plugin, using its skills and commands, and removing plugins you no longer need.'
section: 'getting-started'
order: 2
keywords:
  - "install Claude Code plugin"
  - "Claude Code marketplace"
  - "browse plugins"
  - "ccpi install"
  - "plugin commands"
  - "uninstall plugin"
officialLinks:
  - title: 'Claude Code Plugins Documentation'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Claude Code Slash Commands'
    url: 'https://code.claude.com/docs/en/slash-commands'
relatedDocs:
  - 'getting-started/installation'
  - 'getting-started/first-skill'
  - 'concepts/plugins'
---

## Overview

This walkthrough uses the real catalog entry **`api-test-automation`**, whose source is `plugins/testing/api-test-automation`. It contains the `automating-api-testing` skill. Catalog versions and public counts change, so this page does not fabricate an installed-version transcript or promise a fixed inventory.

Before installing, you need Claude Code, a project you are authorized to work in, and permission to enable the plugin's capabilities. Read the plugin's current README and source. Installation is not a security or behavioral certification.

## Step 1: Find and inspect the plugin

Use [Explore](/explore) or the website search. Inspect the description, author, skill list, prerequisites, and source. `ccpi search` is currently a coming-soon stub, so do not expect it to return working catalog matches.

The helper recognizes the catalog name:

```bash
ccpi install api-test-automation
```

This currently displays guidance rather than performing a complete native installation transaction. Its printed legacy scope flags are not the authority for current native Claude syntax. Continue with the native commands below instead of copying those flags.

## Step 2: Register the marketplace

Run this in a terminal with the intended Claude Code installation:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
```

The canonical repository is `jeremylongshore/tons-of-skills-marketplace`; the marketplace slug used by plugin installation is `claude-code-plugins-plus`. The native `/plugin` interface also provides marketplace management.

## Step 3: Install with an explicit scope

From the intended project directory:

```bash
claude plugin install api-test-automation@claude-code-plugins-plus --scope project
```

Choose scope intentionally:

| Scope     | Intended boundary                                              |
| --------- | -------------------------------------------------------------- |
| `user`    | Your user-level installation across projects                   |
| `project` | Shared project configuration                                   |
| `local`   | Local project configuration that is not shared in the same way |

Review what the installer reports. Project scope can affect collaborators through shared settings; local and user scope have different sharing boundaries. See the [native management reference](https://code.claude.com/docs/en/discover-plugins) before changing an existing project's configuration.

## Step 4: Confirm availability

Use the Installed view in `/plugin` or native `claude plugin list` to inspect registration and enabled state. Follow any installation summary instruction to reload plugins or start a new session; do not assume every install is immediately available in an already-running session.

Check that the expected plugin and skill appear. If they do not, inspect scope, enablement, runtime prerequisites, and native diagnostics rather than copying files into a cache directory.

## Step 5: Invoke the actual skill

In a Claude Code session where the plugin is enabled:

```text
/api-test-automation:automating-api-testing
```

Start with a bounded request and explicitly state the desired execution boundary:

> Review the example API specification I supply and draft tests without sending requests or installing dependencies. Identify any information you need before execution.

This is an instruction example, not evidence that the skill will always satisfy the request or that a provider has been tested. Inspect its current `allowed-tools`, body, scripts, and applicable permission rules. Skill tool preapproval is not an exclusive sandbox. Do not supply real credentials or sensitive production payloads merely to try a tutorial.

There is no universal `/review src/auth.ts` command supplied by all plugins. Use the actual namespaced skill or command discovered from the installed artifact.

## Step 6: Update or remove deliberately

Use the current native plugin manager for update and uninstall operations. Claude Code supports native updates; removing and reinstalling is not a required universal workaround. Review plugin-specific persistent data and configuration before removal rather than assuming they are always preserved.

The helper's `ccpi upgrade` currently prints guidance; `ccpi update`, `remove`, and `info` are not delivered commands. See the [CLI reference](/docs/getting-started/cli-reference/) for the exact helper boundary.

## If something fails

- Confirm the catalog name and marketplace slug instead of substituting historical examples.
- Confirm the intended scope and enabled state.
- Follow native reload or restart instructions.
- Inspect source and prerequisites before authorizing execution.
- Report exact command/version and redacted diagnostics; do not post tokens or raw private tool output.

For authoring a local instruction skill, continue with [your first skill](/docs/getting-started/first-skill/). For a local plugin directory, use `claude --plugin-dir /absolute/path/to/plugin`; a plain `claude` invocation does not automatically register an arbitrary directory as a plugin.
