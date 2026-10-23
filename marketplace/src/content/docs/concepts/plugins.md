---
title: 'What Are Claude Code Plugins?'
description: 'A comprehensive guide to Claude Code plugins — what they are, how they work, and how they extend Claude Code with new capabilities through AI instruction files, MCP servers, and SaaS skill packs.'
section: 'concepts'
order: 1
keywords:
  - 'Claude Code plugins'
  - 'plugin structure'
  - 'plugin.json'
  - 'AI instruction plugins'
  - 'MCP server plugins'
  - 'SaaS skill packs'
  - 'Claude Code extensions'
  - 'plugin lifecycle'
officialLinks:
  - title: 'Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Claude Code Plugins Overview'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Tons of Skills Marketplace'
    url: 'https://tonsofskills.com'
relatedDocs:
  - 'concepts/skills'
  - 'concepts/agents'
  - 'concepts/commands-and-hooks'
  - 'concepts/mcp-servers'
---

## Overview

A plugin packages Claude Code extensions: skills, agents, legacy commands, hooks, MCP configuration, and supporting resources. Some plugins are mostly instructions; others execute scripts or start servers. There is no supported fixed percentage that makes instruction plugins inherently non-executable or harmless.

Browse the current public catalog at [Explore](/explore). Catalog entries, public search results, and discovered skills are different cohorts; the site's displayed counts describe its generated public snapshot rather than a universal inventory.

## Layout and manifest

A typical repository submission looks like this:

```text
example-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── review-diff/
│       └── SKILL.md
├── README.md
└── LICENSE
```

Native Claude can discover components from the standard layout without a manifest. If a native manifest is present, `name` is required. That permissive platform floor is **not** this marketplace's submission contract.

The current local manifest overlay requires `name`, `version`, `description`, `author`, `homepage`, `license`, `keywords`, and `commands`. A plugin with no legacy command files can use an empty `commands` array. This complete metadata example uses an illustrative project identity:

```json
{
  "name": "example-plugin",
  "version": "1.0.0",
  "description": "Review supplied diffs with documented local instructions.",
  "author": { "name": "Example Team" },
  "homepage": "https://example.com/example-plugin",
  "license": "MIT",
  "keywords": ["review", "testing"],
  "commands": []
}
```

Replace the example homepage and author with truthful project metadata. `author` is an object, not a string. Additional supported manifest fields exist, including component paths and other native metadata; this example is not an exhaustive allowlist. Consult the [plugin reference](https://code.claude.com/docs/en/plugins-reference), the pinned authoring kernel, and the repository validator for the applicable contract.

## Install and load

The canonical marketplace repository is `jeremylongshore/tons-of-skills-marketplace`; the marketplace slug is `claude-code-plugins-plus`.

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
claude plugin install api-test-automation@claude-code-plugins-plus --scope project
```

Native scopes are `user`, `project`, and `local`. Project and local settings have different sharing boundaries. Inspect the install summary; reload plugins or start a new session when required. Copying a directory into a cache path is not equivalent to registering and enabling a plugin.

For a local development directory, load it explicitly:

```bash
claude --plugin-dir /absolute/path/to/example-plugin
```

Use only reviewed local code. Hooks, dynamic skill preprocessing, scripts, and MCP servers can execute commands under the applicable permission model.

## Skills, agents, commands, hooks, and MCP

| Component      | Typical location                      | Purpose                                                                                      |
| -------------- | ------------------------------------- | -------------------------------------------------------------------------------------------- |
| Skill          | `skills/<name>/SKILL.md`              | Reusable instructions and resources; manual and/or model invocation according to frontmatter |
| Agent          | `agents/<name>.md`                    | Delegated worker with a separate context and configured tools                                |
| Legacy command | `commands/<name>.md`                  | Filename-based slash invocation; still supported                                             |
| Hook           | `hooks/hooks.json`                    | Lifecycle-triggered behavior using the native event schema                                   |
| MCP server     | `.mcp.json` or manifest configuration | External tool/resource connection with runtime prerequisites                                 |

Plugin skill and command invocations are namespaced. A plugin named `example-plugin` with a skill named `review-diff` exposes `/example-plugin:review-diff` when user invocation is allowed.

## Validation and quality evidence

The Python validator defaults to standard outside CI and auto-selects marketplace in CI unless a tier is explicit. Select the intended tier explicitly:

```bash
python3 scripts/validate-skills-schema.py --standard /absolute/path/to/example-plugin
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/example-plugin
```

Marketplace skills require all eight fields: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing required fields are errors. The public schema, static production gate, and optional behavioral evidence answer different questions; a static grade or badge is not a runtime, security, or provider certification.

When contributing here, use the repository's current validation and generation instructions. Do not hand-edit generated catalogs. Commit legitimate generated changes produced by the canonical commands.

## Updates and removal

Claude Code provides native plugin update and uninstall operations; consult the current [plugin management reference](https://code.claude.com/docs/en/discover-plugins). Do not assume uninstall/reinstall is required for updates or that it preserves all plugin-specific data.

The tracked `ccpi` helper has `upgrade`, not `update`, and that command currently prints guidance rather than applying a complete plugin upgrade transaction. Its legacy installation guidance is not the authority for native scope flags. See the [CLI reference](/docs/getting-started/cli-reference/) for the delivered commands and limitations.
