---
title: "Claude Code Plugins FAQ"
description: "Frequently asked questions about Claude Code plugins, the Tons of Skills marketplace, skills, agents, MCP servers, installation, troubleshooting, and publishing. Clear answers with links to detailed docs."
section: "ecosystem"
order: 4
keywords: ["Claude Code FAQ", "plugin FAQ", "skills FAQ", "Claude Code troubleshooting", "plugin installation help", "SKILL.md help", "ccpi FAQ", "Claude Code marketplace FAQ"]
officialLinks:
  - title: "Claude Code Overview"
    url: "https://code.claude.com/docs/en/overview"
  - title: "Claude Code Skills"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Plugins"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Claude Code Best Practices"
    url: "https://code.claude.com/docs/en/best-practices"
relatedDocs:
  - "getting-started/installation"
  - "ecosystem/marketplace-overview"
  - "ecosystem/official-anthropic-docs"
  - "ecosystem/community-resources"
---

## General Questions

### What are Claude Code plugins?

Plugins are packaged extensions for Claude Code -- Anthropic's agentic coding assistant that runs in your terminal. A plugin bundles one or more skills, slash commands, and/or autonomous agents into a directory with a `plugin.json` manifest. When installed, the plugin's capabilities are loaded into your Claude Code session, giving Claude specialized knowledge and behaviors for specific domains.

For example, a security plugin might include a skill that automatically applies secure coding patterns, a `/security-audit` command that scans your codebase for vulnerabilities, and an agent that autonomously reviews pull requests for security issues.

Plugins follow the directory structure and manifest format defined in the [official Anthropic plugin specification](https://code.claude.com/docs/en/plugins).

### Are Claude Code plugins free?

Yes. Every plugin on the Tons of Skills marketplace is free and open source. The [GitHub repository](https://github.com/jeremylongshore/claude-code-plugins) is publicly accessible, and plugins are licensed individually (most use the MIT license). You can install, modify, and redistribute any plugin according to its license terms.

The `ccpi` CLI tool is also free and open source, published on npm as `@intentsolutionsio/ccpi`.

Note that while the plugins themselves are free, using Claude Code requires an Anthropic API key or a Claude Pro/Team/Enterprise subscription. Plugin instructions are processed by Claude, so normal API usage and token costs apply.

### Is the marketplace open source?

Yes. The entire Tons of Skills marketplace -- the Astro 5 website, the build pipeline, the validation scripts, and the ccpi CLI -- is open source in the [GitHub repository](https://github.com/jeremylongshore/claude-code-plugins). The website source lives in the `marketplace/` directory. Contributions to both the website and the plugin catalog are welcome. See [Community Resources](/docs/ecosystem/community-resources) for contribution guidelines.

### How many plugins and skills are available?

As of the latest catalog, the marketplace contains 418 plugins and 2,834 individual skills. These span categories including automation, DevOps, security, testing, code analysis, frontend development, database, documentation, AI/ML assistance, and more. The catalog grows regularly as contributors submit new plugins.

Browse the full catalog on the [Explore](/explore) page or search individual skills on the [Skills](/skills) page.

## Installation Questions

### How do I install Claude Code plugins?

There are two approaches:

**From inside Claude Code** (recommended):

```bash
# Start Claude Code
claude

# Add the Tons of Skills marketplace (one-time setup)
/plugin marketplace add jeremylongshore/claude-code-plugins

# Install a specific plugin
/plugin install plugin-name@claude-code-plugins-plus --project
```

**Using the ccpi CLI:**

```bash
# Install the CLI
npm install -g @intentsolutionsio/ccpi

# Connect to the marketplace
ccpi marketplace-add

# Search and install
ccpi search security
ccpi install code-reviewer
```

For the complete setup walkthrough, see [Install Claude Code Plugins](/docs/getting-started/installation).

### Where are plugins stored on my machine?

Plugins are stored in your Claude Code configuration directory, which varies by installation scope:

- **Project-scoped plugins**: `.claude/plugins/` inside your project directory. These are only loaded when Claude Code runs in that project.
- **Global plugins**: `~/.claude/plugins/` in your home directory. These are loaded in every Claude Code session regardless of project.

You can verify installed plugins with:

```bash
ccpi list
```

### How do I update installed plugins?

Check for available updates:

```bash
ccpi upgrade --check
```

Apply all updates:

```bash
ccpi upgrade --all
```

The upgrade process uninstalls the old version and reinstalls the latest from the catalog. Your plugin configuration is preserved across upgrades.

### Can I install plugins without the CLI?

Yes. Plugins are just directories of markdown and JSON files. You can manually download a plugin (from GitHub or from the [Cowork](/cowork) download page) and place it in your Claude Code plugins directory. Claude Code discovers plugins by scanning for `.claude-plugin/plugin.json` files in the expected locations.

The CLI and the `/plugin install` command are convenience wrappers -- they automate download, placement, and catalog management, but they are not strictly required.

### Can I install all plugins at once?

Yes. Use the ccpi CLI:

```bash
ccpi install --all
```

Or download the mega-zip from the [Cowork](/cowork) page, which contains every plugin in the marketplace as a single archive. This is useful for evaluation environments or air-gapped systems.

You can also install by category:

```bash
ccpi install --category security
```

## Skills Questions

### What is a SKILL.md file?

A SKILL.md file is a markdown document with YAML frontmatter that provides Claude Code with domain-specific instructions. It is the fundamental building block of the plugin system. The frontmatter declares metadata (name, description, version, author, allowed tools), and the markdown body contains the actual instructions that Claude follows.

Example frontmatter:

```yaml
---
name: database-migration
description: |
  Generates and validates database migration files.
  Activates when user mentions migrations, schema changes, or database versioning.
allowed-tools: Read, Write, Edit, Bash(npx:*), Glob
version: 1.0.0
author: Developer Name <dev@example.com>
license: MIT
---
```

The body below the frontmatter contains the detailed instructions -- what Claude should do, in what order, with what constraints, and how to handle edge cases.

See the [official Skills documentation](https://code.claude.com/docs/en/skills) for the complete specification.

### How do skills auto-activate?

Claude Code reads all installed SKILL.md files at session start. When the `description` field matches the current context -- based on what the user is asking, what files are open, and what the project contains -- Claude automatically applies the skill's instructions without requiring a slash command.

The `description` field is the primary activation trigger. Write it to include specific phrases, file types, or scenarios that should cause activation. For example:

```yaml
description: |
  Activates when writing React components, JSX files, or discussing
  component architecture. Use for component generation, refactoring,
  and best-practice enforcement.
```

Skills can also be explicitly invoked if they have an `argument-hint` field, but auto-activation is the default and most common behavior.

### Can I write my own skills?

Absolutely. Creating a skill requires:

1. A directory under `skills/skill-name/` inside your plugin.
2. A `SKILL.md` file with valid YAML frontmatter and instructional content in the body.

You can create skills for personal use (drop them in your local plugins directory) or contribute them to the marketplace. The [official Skills specification](https://code.claude.com/docs/en/skills) defines all available frontmatter fields and features.

To validate a skill you have written:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/your-category/your-plugin/
```

### What is the difference between skills, commands, and agents?

These are the three extension types in the Claude Code plugin system:

| Type | Location | Activation | Scope |
|---|---|---|---|
| **Skills** | `skills/name/SKILL.md` | Auto-activate based on context | Provide instructions and constraints |
| **Commands** | `commands/name.md` | User types `/name` | Execute a specific, discrete action |
| **Agents** | `agents/name.md` | User invokes or context triggers | Autonomous persona with iteration control |

**Skills** use `allowed-tools` (allowlist) to restrict what tools Claude can use. They auto-activate and are best for ongoing, context-sensitive capabilities.

**Commands** are slash commands (`/command-name`) that the user explicitly invokes. They are best for discrete, on-demand operations like generating a report or running a scan.

**Agents** use `disallowedTools` (denylist) and have agent-specific fields like `effort`, `maxTurns`, and `permissionMode`. They are best for autonomous, multi-step workflows where Claude needs to iterate and make decisions independently.

## Agent Questions

### What is the difference between agents and skills?

The core differences are:

1. **Tool permissions**: Skills use an allowlist (`allowed-tools` -- only these tools may be used). Agents use a denylist (`disallowedTools` -- all tools except these may be used). This is a critical security distinction.

2. **Autonomy**: Agents have `maxTurns` and `effort` fields that control how many iterations they can perform and how deeply they reason. Skills do not have these controls.

3. **Identity**: Agents define a persona with `capabilities`, `expertise_level`, and behavioral framing. Skills provide instructions but do not redefine Claude's persona.

4. **Invocation**: Skills auto-activate based on context. Agents are typically invoked explicitly or by other agents.

Use skills for focused, single-purpose instructions. Use agents when you need Claude to adopt a specialized persona and work autonomously through a complex, multi-step task.

See the [official Agents documentation](https://code.claude.com/docs/en/agents) for the complete specification.

## MCP Questions

### What is MCP?

MCP stands for Model Context Protocol. It is a protocol for connecting Claude Code to external tools and data sources via locally running servers. An MCP server exposes tools that Claude Code can call, enabling integration with databases, APIs, custom internal systems, and anything else that a TypeScript (or other language) server can interact with.

MCP plugins are distinct from instruction-only plugins. While most plugins in the Tons of Skills marketplace are pure markdown (skills, commands, agents), a small number are MCP servers written in TypeScript that run as background processes.

See the [official MCP documentation](https://code.claude.com/docs/en/mcp) for architecture details and development guides.

### Do I need MCP to use Claude Code plugins?

No. The vast majority of plugins in the marketplace (approximately 98%) are instruction-only -- they consist of markdown files with no server component. These plugins work out of the box with Claude Code and require no additional infrastructure.

MCP plugins provide deeper integrations (e.g., direct database queries, API calls to external services) but are only needed if you specifically want those capabilities. You can use the entire marketplace without ever touching MCP.

### How do I set up an MCP plugin?

MCP plugins include a `.mcp.json` configuration file and a built executable (typically `dist/index.js`). To set up an MCP plugin:

1. Install the plugin's dependencies: `cd plugins/mcp/plugin-name && pnpm install`
2. Build the server: `pnpm build && chmod +x dist/index.js`
3. Configure the MCP server in your Claude Code settings, referencing the built executable.

Each MCP plugin's README includes specific setup instructions. The build step compiles TypeScript source into a runnable JavaScript file with a shebang line for direct execution.

## Marketplace Questions

### How do I publish a plugin to the marketplace?

The full contribution workflow:

1. **Create your plugin** following the directory structure convention (`.claude-plugin/plugin.json`, `README.md`, skill/command/agent files).
2. **Validate** using the universal validator: `python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/your-category/your-plugin/`
3. **Add a catalog entry** in `.claude-plugin/marketplace.extended.json`.
4. **Sync the catalog**: `pnpm run sync-marketplace`
5. **Open a pull request** on the [GitHub repository](https://github.com/jeremylongshore/claude-code-plugins).

CI runs the full validation suite. A maintainer reviews your PR and merges it. Your plugin appears on the live site at the next deployment.

For detailed instructions, see [Community Resources](/docs/ecosystem/community-resources).

### How are plugins verified?

The Tons of Skills marketplace applies a 100-point enterprise compliance rubric to every plugin. The universal validator (`validate-skills-schema.py`) scores plugins across dimensions including:

- Frontmatter completeness and correctness
- Body content quality and substance (not stubs or placeholders)
- Documentation presence (README, changelog)
- Metadata hygiene (keywords, descriptions, author fields)
- Structural conformance to the plugin specification

Scores map to letter grades: A (90-100), B (80-89), C (70-79), D (60-69), F (below 60). Plugins with A or B grades earn a verification badge displayed on their marketplace card.

The validator runs in CI on every pull request, so compliance is enforced before plugins are published.

### Can I list plugins from my own repository?

Yes. The marketplace supports external plugin sources through the `sources.yaml` configuration and the `sync-external.mjs` script. Your repository's plugins are synced daily via a cron job, and each sync creates an automated PR for maintainer review. File an issue on GitHub to request onboarding as an external source.

## Troubleshooting

### My plugin is not loading in Claude Code

Check these common causes:

1. **Plugin directory structure**: Ensure you have a `.claude-plugin/plugin.json` file with the required fields (`name`, `version`, `description`, `author`). Missing or malformed JSON is the most common cause.

2. **Installation location**: Verify the plugin is in the correct directory. Run `ccpi list` to see what Claude Code detects. For project-scoped plugins, the directory should be `.claude/plugins/your-plugin/` inside your project root.

3. **JSON syntax errors**: Run `ccpi validate` to check for structural issues. Even a single trailing comma or missing quote in `plugin.json` will prevent loading.

4. **Restart required**: After manually placing files, you may need to start a new Claude Code session for the plugin to be detected.

Run `ccpi doctor` for a comprehensive diagnostic that checks all of these conditions and provides remediation steps.

### A skill is not triggering when expected

Skill auto-activation depends on the `description` field matching the current context. If a skill is not activating:

1. **Check the description**: Open the SKILL.md file and read the `description` field. Does it include the phrases, file types, or scenarios you are expecting to trigger it? If not, update it.

2. **Check `allowed-tools`**: If the skill restricts its tool set too narrowly, Claude may not be able to perform the actions needed. Make sure the tools listed are sufficient for the skill's purpose.

3. **Check for conflicts**: If multiple skills have overlapping descriptions, Claude may activate a different skill than the one you expect. Make descriptions specific and distinct.

4. **Validate the frontmatter**: Malformed YAML in the frontmatter will prevent the skill from loading. Run the validator to check:

   ```bash
   python3 scripts/validate-skills-schema.py --verbose path/to/plugin/
   ```

### The ccpi command is not found

Your npm global bin directory is not on your `PATH`. Find it:

```bash
npm config get prefix
```

Add the `bin` subdirectory to your shell profile:

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export PATH="$(npm config get prefix)/bin:$PATH"
```

Then reload your shell or open a new terminal window.

### ccpi reports "marketplace catalog is empty"

The marketplace catalog file is missing or corrupted. Re-add it:

```bash
ccpi marketplace-add
```

Or from inside Claude Code:

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
```

### Validation errors when building a plugin

The universal validator checks plugins against two tiers:

- **Standard tier**: Anthropic's minimum requirements. This is the blocking check in CI.
- **Enterprise tier**: The 100-point rubric used for marketplace grading. This is reported but not blocking.

If you see validation errors:

1. Read the error message carefully -- it tells you exactly which field is missing or malformed.
2. Check your `plugin.json` against the [plugin specification](https://code.claude.com/docs/en/plugins).
3. Check your SKILL.md frontmatter against the [skills specification](https://code.claude.com/docs/en/skills).
4. Run with `--verbose` for detailed output:

   ```bash
   python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/your-category/your-plugin/
   ```

Common issues include missing `version` fields, invalid tool names in `allowed-tools`, descriptions that are too short, and body content that is detected as a stub.

### The marketplace website build fails locally

The marketplace uses npm (not pnpm). Make sure you are in the right directory and using the right package manager:

```bash
cd marketplace
npm install
npm run build
```

If the build fails on the skill discovery step, it usually means a plugin has malformed YAML frontmatter. The error output identifies the offending file. Fix the YAML and rebuild.

If the build passes but route validation fails, check that your plugin's slug does not conflict with an existing route. The route validator checks for duplicates and orphans.

## Next Steps

- [Install Claude Code Plugins](/docs/getting-started/installation) -- complete setup guide for the ccpi CLI and marketplace.
- [Marketplace Guide](/docs/ecosystem/marketplace-overview) -- browse plugins, skills, Cowork downloads, and collections.
- [Official Anthropic Docs](/docs/ecosystem/official-anthropic-docs) -- organized directory of the official specification.
- [Community Resources](/docs/ecosystem/community-resources) -- contribute plugins, file issues, and connect with developers.
