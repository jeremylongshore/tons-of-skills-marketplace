---
name: plugin-creator
description: 'Create automatically creates new AI assistant code plugins with proper
  structure, validation, and marketplace integration when user mentions creating a
  plugin, new plugin, or plugin from template. specific to AI assistant-code-plugins
  repository workflow. Use when generating or creating new content. Trigger with phrases
  like ''generate'', ''create'', or ''scaffold''.

  '
allowed-tools: Write, Read, Grep, Bash(cmd:*)
version: 2.20.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- workflow
- plugin-creator
compatibility: Designed for Claude Code
---
# Plugin Creator

## Overview

Scaffolds new Claude Code plugins with proper directory structure, required files, marketplace catalog integration, and full validation. Supports all plugin types: command plugins, agent plugins, skill plugins, MCP server plugins, and hybrid combinations.

## Prerequisites

- Write access to the `plugins/` directory and `.claude-plugin/marketplace.extended.json`
- `jq` installed for JSON generation and validation
- `pnpm run sync-marketplace` available at the repository root
- `./scripts/validate-all-plugins.sh` available for post-creation validation

## Instructions

1. Gather requirements from the user request: plugin name (kebab-case), category (`productivity`, `security`, `devops`, `testing`, etc.), plugin type (commands, agents, skills, MCP, or combination), description, and keywords. Default author to the repository owner if unspecified (see `${CLAUDE_SKILL_DIR}/references/plugin-creation-process.md`).
2. Create the plugin directory structure under `plugins/[category]/[plugin-name]/`:

   ```
   plugins/[category]/[plugin-name]/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── README.md
   ├── LICENSE
   └── [commands/ | agents/ | skills/ | hooks/ | mcp/]
   ```

3. Generate `.claude-plugin/plugin.json` using the template from `${CLAUDE_SKILL_DIR}/references/file-templates.md`. Populate all required fields: `name`, `version` (default `1.0.0`), `description`, `author` (name and email), `repository`, `license` (default MIT), and `keywords` (minimum 2).
4. Generate `README.md` with installation instructions, usage examples, a description section, and contributor information.
5. Create a `LICENSE` file with MIT license text (or the specified license).
6. Generate component files based on the plugin type:
   - **Commands**: create `commands/[command-name].md` with proper YAML frontmatter (`name`, `description`, `model`).
   - **Agents**: create `agents/[agent-name].md` with YAML frontmatter including `model` field.
   - **Skills**: create `skills/[skill-name]/SKILL.md` with frontmatter (`name`, `description`, `allowed-tools`).
   - **MCP**: create `package.json`, `tsconfig.json`, `src/index.ts`, and `.mcp.json`.
7. Add the new plugin entry to `.claude-plugin/marketplace.extended.json` with matching name, version, category, description, source path, and keywords.
8. Run `pnpm run sync-marketplace` to regenerate `marketplace.json`.
9. Validate the new plugin by running `./scripts/validate-all-plugins.sh plugins/[category]/[plugin-name]/`. Fix any reported issues before completion.

## Output

A complete, CI-ready plugin containing:

- All required files (`plugin.json`, `README.md`, `LICENSE`)
- Component files matching the requested plugin type with proper frontmatter
- Marketplace catalog entry in `marketplace.extended.json`
- Synchronized `marketplace.json`
- Validation confirmation from `validate-all-plugins.sh`

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Plugin name already exists | Duplicate name in `plugins/` directory or marketplace catalog | Choose a unique name; check existing plugins with `ls plugins/*/` |
| Invalid category | Category not recognized by marketplace schema | Use one of the valid categories: `productivity`, `security`, `devops`, `testing`, `community`, `examples`, `packages`, `mcp` |
| JSON syntax error in generated files | Malformed template output | Run `jq empty` on each generated JSON file and fix syntax |
| Marketplace sync failure | New entry has schema violations | Verify all required fields are present in the `marketplace.extended.json` entry |
| Validation script failure | Missing required files or incorrect structure | Review the validation output and create/fix the flagged files |

## Examples

**Create a command plugin:**
Trigger: "Create a new security plugin called 'owasp-scanner' with commands."
Process: Create `plugins/security/owasp-scanner/` directory, generate `plugin.json`, `README.md`, `LICENSE`, and `commands/scan.md` with proper frontmatter. Add to marketplace, sync, validate (see `${CLAUDE_SKILL_DIR}/references/examples.md`).

**Scaffold a skills plugin:**
Trigger: "Scaffold a skills plugin for code review."
Process: Create plugin directory with `skills/code-review/SKILL.md` containing trigger keywords for code review tasks. Generate `plugin.json` with appropriate keywords. Add to marketplace, sync, validate.

**Create an MCP server plugin:**
Trigger: "Create a new MCP plugin for database queries."
Process: Create `plugins/mcp/db-query/` with `package.json` (including `@modelcontextprotocol/sdk` dependency), `tsconfig.json`, `src/index.ts`, `.mcp.json`, and standard files. Add to marketplace, sync, validate.

## Resources

- `${CLAUDE_SKILL_DIR}/references/plugin-creation-process.md` -- detailed creation workflow
- `${CLAUDE_SKILL_DIR}/references/file-templates.md` -- templates for `plugin.json`, commands, agents, and skills
- `${CLAUDE_SKILL_DIR}/references/examples.md` -- creation scenario walkthroughs
- `${CLAUDE_SKILL_DIR}/references/errors.md` -- error handling patterns
