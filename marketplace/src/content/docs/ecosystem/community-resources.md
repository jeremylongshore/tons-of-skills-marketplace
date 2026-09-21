---
title: "Claude Code Community and Resources"
description: "Connect with the Claude Code community. Contribute plugins to the Tons of Skills marketplace, file issues, join discussions, and explore learning resources across the ecosystem."
section: "ecosystem"
order: 3
keywords: ["Claude Code community", "contribute plugins", "open source", "GitHub", "Discord", "Claude Code learning", "plugin development", "Claude Code ecosystem tools"]
officialLinks:
  - title: "Claude Code Overview"
    url: "https://code.claude.com/docs/en/overview"
  - title: "Claude Code Plugins"
    url: "https://code.claude.com/docs/en/plugins"
relatedDocs:
  - "ecosystem/marketplace-overview"
  - "ecosystem/official-anthropic-docs"
  - "getting-started/installation"
---

## The Claude Code Plugin Ecosystem

Claude Code plugins are open source. The Tons of Skills marketplace at [tonsofskills.com](https://tonsofskills.com) is maintained by Intent Solutions and powered by contributions from developers around the world. Whether you want to use existing plugins, improve them, or build and publish your own, there are clear paths to get involved.

This page covers every channel, resource, and workflow available to community members -- from filing a bug report to publishing a full plugin with verification badges.

## GitHub Repository

The primary hub for all plugin development is the GitHub repository:

**[github.com/jeremylongshore/claude-code-plugins](https://github.com/jeremylongshore/claude-code-plugins)**

This monorepo contains:

- **All 418 plugins** organized under `plugins/` by category (`plugins/automation/`, `plugins/security/`, `plugins/devops/`, etc.)
- **MCP server plugins** under `plugins/mcp/`
- **SaaS skill packs** under `plugins/saas-packs/`
- **The marketplace website** under `marketplace/` (the Astro 5 site at tonsofskills.com)
- **The ccpi CLI** under `packages/cli/`
- **Build scripts, validators, and CI pipeline** at the root level
- **Templates** under `templates/` for bootstrapping new plugins

### Cloning the repository

```bash
git clone https://github.com/jeremylongshore/claude-code-plugins.git
cd claude-code-plugins
pnpm install
```

The repo uses pnpm workspaces. After cloning, `pnpm install` sets up all workspace dependencies. The marketplace directory uses npm (enforced by CI), so if you are working on the website, run `cd marketplace && npm install` separately.

### Repository structure at a glance

```
claude-code-plugins/
  plugins/
    automation/          # Automation plugins
    business-tools/      # Business tool plugins
    code-analysis/       # Code analysis plugins
    database/            # Database plugins
    debugging/           # Debugging plugins
    devops/              # DevOps plugins
    documentation/       # Documentation plugins
    frontend-development/ # Frontend plugins
    mcp/                 # MCP server plugins
    saas-packs/          # SaaS integration packs
    security/            # Security plugins
    testing/             # Testing plugins
    ...                  # Additional categories
  marketplace/           # Astro 5 website (tonsofskills.com)
  packages/cli/          # ccpi CLI package
  scripts/               # Build, validation, and sync scripts
  templates/             # Plugin templates (minimal, full, etc.)
  freshie/               # Ecosystem inventory database
```

## Filing Issues and Feature Requests

### Bug reports

If you encounter a problem with a plugin, the marketplace website, or the ccpi CLI, file an issue on GitHub:

1. Go to [github.com/jeremylongshore/claude-code-plugins/issues](https://github.com/jeremylongshore/claude-code-plugins/issues).
2. Click "New issue."
3. Choose the appropriate template if one matches your problem (bug report, feature request, plugin issue).
4. Include:
   - **What you expected** to happen.
   - **What actually happened**, including any error messages or unexpected behavior.
   - **Steps to reproduce** the issue.
   - **Environment details**: operating system, Node.js version, Claude Code version, ccpi version.
   - **Plugin name and version** if the issue is plugin-specific.

### Feature requests

Have an idea for a new plugin, a marketplace feature, or a CLI improvement? File a feature request issue with the "enhancement" label. Describe the use case, the expected behavior, and any alternatives you considered.

### Security issues

If you discover a security vulnerability in a plugin or in the marketplace infrastructure, do not file a public issue. Instead, use GitHub's private vulnerability reporting feature or contact the maintainers directly through the repository's security policy.

## Contributing Plugins to the Marketplace

Contributing a plugin to Tons of Skills is the most impactful way to participate in the ecosystem. Every plugin you contribute becomes available to the entire Claude Code community through the marketplace, the ccpi CLI, and Cowork downloads.

### Step 1: Choose a template

The repository includes several plugin templates under `templates/`:

- **Minimal** -- a bare-bones plugin with `plugin.json` and a single skill. Good for simple, focused utilities.
- **Command** -- a plugin built around slash commands. Good for tools that need explicit user invocation.
- **Agent** -- a plugin that defines an autonomous agent persona. Good for complex, multi-step workflows.
- **Skill** -- a plugin with one or more auto-activating skills. Good for context-sensitive capabilities.
- **Full** -- a plugin with skills, commands, agents, hooks, and documentation. Good for comprehensive tooling.

Copy the template that best matches your plugin's purpose:

```bash
cp -r templates/skill plugins/your-category/your-plugin-name
```

### Step 2: Build your plugin

At minimum, your plugin needs:

- **`.claude-plugin/plugin.json`** with required fields: `name`, `version`, `description`, `author`.
- **`README.md`** describing what the plugin does, how to install it, and how to use it.
- **At least one skill, command, or agent file** providing actual functionality.

Follow the [SKILL.md specification](https://code.claude.com/docs/en/skills) for skill files and the [plugin specification](https://code.claude.com/docs/en/plugins) for overall structure.

### Step 3: Validate locally

Run the universal validator to check your plugin against both the standard tier (Anthropic minimum) and the enterprise tier (100-point rubric):

```bash
# Standard validation
python3 scripts/validate-skills-schema.py --verbose plugins/your-category/your-plugin-name/

# Enterprise validation (full 100-point rubric)
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/your-category/your-plugin-name/
```

Fix any errors or warnings. Aim for a B grade or higher (80+ points) to earn a verification badge on the marketplace.

### Step 4: Add to the catalog

Add your plugin's entry to `.claude-plugin/marketplace.extended.json`. This is the source-of-truth catalog file. Then sync:

```bash
pnpm run sync-marketplace
```

This generates the CLI-compatible `marketplace.json` from your extended entry.

### Step 5: Run the test suite

Before opening a PR, run the quick validation suite:

```bash
pnpm run sync-marketplace
./scripts/quick-test.sh
```

This checks JSON validity, plugin structure, catalog sync, and marketplace build in about 30 seconds.

### Step 6: Open a pull request

Push your branch and open a PR against `main`. The CI pipeline runs parallel validation jobs including:

- Plugin structure and JSON validation
- Universal validator (standard and enterprise tiers)
- Marketplace build and route validation
- Performance budget checks
- End-to-end tests

A maintainer reviews your PR. Once approved and merged, your plugin appears on the live marketplace at the next deployment.

### Contribution guidelines

- **One plugin per PR** unless the plugins are closely related (e.g., a pack of SaaS integrations).
- **Include meaningful content** in skill and command files. Stubs with placeholder text will be flagged by the validator.
- **Follow naming conventions**: plugin directories use kebab-case, skill names use kebab-case, categories match the existing set.
- **Do not modify auto-generated files** (`marketplace.json`, `catalog.json`, `skills-catalog.json`, `unified-search-index.json`). These are rebuilt by the build pipeline.
- **Newest contributors go at the top** of the README contributors list.

## GitHub Discussions

The GitHub repository's Discussions tab is the place for open-ended conversations that do not fit neatly into an issue:

- **Q&A** -- ask questions about plugin development, Claude Code configuration, or marketplace usage.
- **Ideas** -- propose new directions for the ecosystem without the formality of a feature request.
- **Show and tell** -- share what you have built with Claude Code plugins and get feedback.
- **General** -- anything else related to the Claude Code plugin community.

Visit [github.com/jeremylongshore/claude-code-plugins/discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions) to participate.

## Claude Code Discord and Forums

The Claude Code community extends beyond this repository. Key channels:

- **Anthropic's Discord** -- the official Anthropic Discord server includes channels dedicated to Claude Code, where developers share tips, report issues, and discuss new features.
- **Claude Code subreddit** -- community discussions, tutorials, and plugin showcases on Reddit.
- **X / Twitter** -- follow `@AnthropicAI` and search for `#ClaudeCode` to find community posts and announcements.

These channels are community-run and not officially maintained by Tons of Skills, but they are valuable for connecting with other Claude Code users and staying current on ecosystem developments.

## Other Tools in the Claude Code Ecosystem

Claude Code plugins are one part of a larger ecosystem of tools built around Anthropic's Claude models. Understanding the landscape helps you choose the right tool for each situation.

### Claude Desktop

Claude Desktop is Anthropic's standalone application for macOS and Windows. It provides a chat-based interface to Claude with support for file uploads, image analysis, and extended conversations. Claude Desktop supports MCP servers, which means some MCP plugins from the Tons of Skills marketplace can be configured to work with it -- though the primary target for marketplace plugins is Claude Code in the terminal.

### Claude for VS Code

The Claude for VS Code extension integrates Claude into Visual Studio Code's editor environment. It provides inline code suggestions, chat-based assistance, and file-aware context. While it shares the underlying Claude model with Claude Code, its plugin system is separate. Claude Code plugins (SKILL.md, commands, agents) are specific to the Claude Code CLI and do not load in VS Code.

### Claude for JetBrains

Similar to the VS Code extension, Claude for JetBrains brings Claude's capabilities into IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs. It operates independently from the Claude Code plugin system.

### Cursor and Windsurf

Cursor and Windsurf are third-party AI-powered code editors that support Claude models. Some plugins in the Tons of Skills marketplace include `compatible-with` metadata indicating they work with these editors, but the primary target remains Claude Code. The `compatible-with` field in SKILL.md frontmatter can specify `claude-code`, `cursor`, `windsurf`, or combinations thereof.

### ccpi CLI

The `ccpi` CLI (`@intentsolutionsio/ccpi` on npm) is the companion tool for managing plugins outside of a Claude Code session. It handles marketplace connections, plugin search, installation workflows, validation, and diagnostics. See the [installation guide](/docs/getting-started/installation) for setup instructions.

## Learning Resources

The Tons of Skills website includes several sections dedicated to helping developers learn and grow their Claude Code skills.

### Learning Path (/learning)

The [Learning](/learning) section provides structured educational content organized by difficulty level:

- **Beginner** -- what Claude Code is, how plugins work, installing your first plugin.
- **Intermediate** -- writing skills, building commands, using the validator, publishing to the marketplace.
- **Advanced** -- MCP server development, hooks, agent design, dynamic context injection, enterprise compliance.

### Playbooks (/playbooks)

The [Playbooks](/playbooks) section contains opinionated, end-to-end workflow guides that combine multiple plugins to solve real-world problems. Each playbook walks through a complete scenario -- for example, setting up a security scanning pipeline or automating code review -- and shows which plugins to install, how to configure them, and what to expect.

### Research (/research)

The [Research](/research) section publishes technical analyses of the plugin ecosystem: benchmark results, compliance trends, adoption statistics, and architectural investigations. These are data-driven reports, not tutorials.

### Blog (/blog)

The [Blog](/blog) covers release announcements, contributor spotlights, technical deep dives, and ecosystem news. It is updated regularly and provides a running narrative of how the marketplace evolves.

## External Sync and Third-Party Contributions

The marketplace supports external plugin sources through an automated sync mechanism. Third-party repositories can register in `sources.yaml` and have their plugins pulled into the marketplace catalog automatically via a daily cron job (`scripts/sync-external.mjs`).

Each synced plugin receives a `.source.json` provenance file that tracks its origin repository, sync timestamp, and include/exclude globs. External sync creates PRs automatically (labeled `automated`, `sync`, `external-plugins`) for maintainer review.

If you maintain a separate repository of Claude Code plugins and want them listed on the Tons of Skills marketplace without moving them into the monorepo, external sync is the mechanism to use. File an issue or start a discussion to request onboarding.

## How to Stay Informed

- **Star the repository** on GitHub to receive notifications about releases and major changes.
- **Watch releases** to get notified when new versions of the marketplace or CLI ship.
- **Subscribe to the blog** at [tonsofskills.com/blog](/blog) for ecosystem updates.
- **Check the changelog** in the repository root for a detailed history of all changes.

## Next Steps

- [Marketplace Guide](/docs/ecosystem/marketplace-overview) -- browse and install plugins from the Tons of Skills catalog.
- [Official Anthropic Docs](/docs/ecosystem/official-anthropic-docs) -- organized directory of Anthropic's Claude Code documentation.
- [FAQ](/docs/ecosystem/faq) -- answers to the most common questions about Claude Code plugins.
- [Install Claude Code Plugins](/docs/getting-started/installation) -- get set up and install your first plugin.
