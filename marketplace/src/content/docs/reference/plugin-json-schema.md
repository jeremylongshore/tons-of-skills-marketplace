---
title: "plugin.json Schema Reference"
description: "Complete schema reference for the plugin.json manifest file required in every Claude Code plugin, including field definitions, validation rules, and CI enforcement details."
section: "reference"
order: 2
keywords: ["plugin.json", "schema", "manifest", "plugin structure", "validation", "CI", "metadata"]
officialLinks:
  - title: "Claude Code Plugins Documentation"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Claude Code Plugin Structure"
    url: "https://code.claude.com/docs/en/plugins#plugin-structure"
relatedDocs:
  - "concepts/plugins"
  - "guides/build-a-plugin"
  - "reference/plugin-categories"
---

## Overview

Every Claude Code plugin must include a `plugin.json` manifest file at `.claude-plugin/plugin.json` relative to the plugin root. This file declares the plugin's identity, authorship, and discoverability metadata. Claude Code reads `plugin.json` during installation to register the plugin, and the marketplace uses it to populate listings on the [Explore](/explore) page.

The schema is intentionally minimal. Only eight fields are permitted, and CI validation rejects any `plugin.json` containing additional properties. This strict approach prevents schema drift and ensures all plugins remain compatible with the `ccpi` CLI and the Tons of Skills marketplace infrastructure.

## File Location

The `plugin.json` file must be placed in the `.claude-plugin/` directory at the plugin root:

```
plugins/devops/ci-optimizer/
  .claude-plugin/
    plugin.json           # Required manifest
  README.md               # Required documentation
  skills/
    optimize-pipeline/
      SKILL.md
  commands/
    analyze.md
```

The `.claude-plugin/` directory is a convention established by the Claude Code plugin system. It serves as the metadata directory for the plugin and may also contain `marketplace.json` and `marketplace.extended.json` at the repository level.

## Schema Reference

### Field Summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Plugin identifier |
| `version` | `string` | Yes | Semantic version |
| `description` | `string` | Yes | Human-readable summary |
| `author` | `object` | Yes | Author information |
| `repository` | `string` | No | Source code URL |
| `homepage` | `string` | No | Plugin homepage URL |
| `license` | `string` | No | SPDX license identifier |
| `keywords` | `string[]` | No | Discovery keywords |

These eight fields are the **only** fields permitted. The CI pipeline (`validate-plugins.yml`) runs a strict schema check that rejects any `plugin.json` containing fields not listed above.

### name

- **Type:** `string`
- **Required:** Yes

The plugin's unique identifier. Use kebab-case and keep names descriptive but concise. The name appears in `ccpi install` commands, marketplace URLs, and search results.

```json
"name": "ci-optimizer"
```

**Naming conventions:**

- Use kebab-case: `my-plugin-name`
- Be specific: `terraform-drift-detector` not `tf-tool`
- Avoid generic prefixes: `claude-` is unnecessary since all plugins are for Claude Code
- Match the directory name when possible

### version

- **Type:** `string`
- **Required:** Yes

Semantic version following [SemVer 2.0.0](https://semver.org/). Used by `ccpi update` to determine whether a newer version is available.

```json
"version": "1.2.0"
```

**Versioning guidelines:**

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking changes to skill behavior or removed skills | Major | `1.0.0` to `2.0.0` |
| New skills, commands, or agents added | Minor | `1.0.0` to `1.1.0` |
| Bug fixes, documentation updates, minor tweaks | Patch | `1.0.0` to `1.0.1` |

### description

- **Type:** `string`
- **Required:** Yes

A concise, human-readable description of what the plugin does. This text appears in marketplace listings, `ccpi search` results, and the plugin detail page. Write for developers scanning a list of results.

```json
"description": "Detect and fix Terraform configuration drift across AWS, GCP, and Azure environments"
```

**Guidelines:**

- Keep it under 200 characters for clean display in search results
- Start with a verb: "Detect...", "Generate...", "Audit...", "Scaffold..."
- Mention the primary technology or domain
- Avoid marketing language; be factual

### author

- **Type:** `object`
- **Required:** Yes

An object identifying the plugin author. The `name` property is required; `email` and `url` are optional.

```json
"author": {
  "name": "Jane Smith",
  "email": "jane@example.com",
  "url": "https://janesmith.dev"
}
```

**Author object properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | `string` | Yes | Display name of the author or organization |
| `email` | `string` | No | Contact email. Must be a valid email format if provided. |
| `url` | `string` | No | Author's website or profile page. Must be a valid URL if provided. |

For organizational authorship, use the organization name:

```json
"author": {
  "name": "Intent Solutions",
  "url": "https://intentsolutions.io"
}
```

### repository

- **Type:** `string`
- **Required:** No

URL of the plugin's source code repository. Used to generate "View Source" links on marketplace plugin pages. Should be a valid URL pointing to a public repository.

```json
"repository": "https://github.com/username/plugin-name"
```

If the plugin lives inside a monorepo, point to the specific directory:

```json
"repository": "https://github.com/username/plugins/tree/main/plugins/devops/ci-optimizer"
```

### homepage

- **Type:** `string`
- **Required:** No

URL of the plugin's homepage or documentation site. Distinct from `repository` in that it points to user-facing documentation rather than source code.

```json
"homepage": "https://ci-optimizer.dev"
```

If your plugin does not have a dedicated site, omit this field rather than duplicating the `repository` URL.

### license

- **Type:** `string`
- **Required:** No

An [SPDX license identifier](https://spdx.org/licenses/) specifying the terms under which the plugin is distributed. Displayed on marketplace listings and validated during enterprise compliance checks.

```json
"license": "MIT"
```

**Common license identifiers:**

| SPDX ID | License Name | Use Case |
|---------|-------------|----------|
| `MIT` | MIT License | Permissive, most common for open-source plugins |
| `Apache-2.0` | Apache License 2.0 | Permissive with patent grant |
| `ISC` | ISC License | Simplified MIT-style |
| `GPL-3.0-only` | GNU GPL v3 | Copyleft |
| `BSD-2-Clause` | BSD 2-Clause | Permissive, minimal requirements |
| `Proprietary` | Proprietary | Closed-source plugins |

If omitted, the plugin is assumed to have no explicit license, which may affect its compliance grade in the enterprise validator.

### keywords

- **Type:** `string[]`
- **Required:** No

An array of lowercase keywords used for marketplace search and discovery. These keywords supplement the `description` field and improve findability through `ccpi search` and the [Explore](/explore) page.

```json
"keywords": ["terraform", "infrastructure", "drift-detection", "aws", "gcp", "azure"]
```

**Keyword guidelines:**

- Use lowercase
- Include the primary technology (e.g., `terraform`, `react`, `kubernetes`)
- Include the problem domain (e.g., `security`, `testing`, `deployment`)
- Include platform names if relevant (e.g., `aws`, `gcp`, `vercel`)
- Aim for 3-8 keywords; more than 10 provides diminishing returns
- Avoid duplicating words already in the `name` or `description`

## Complete Example

A fully specified `plugin.json` with all eight fields:

```json
{
  "name": "terraform-drift-detector",
  "version": "2.1.0",
  "description": "Detect and remediate Terraform configuration drift across multi-cloud environments",
  "author": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "url": "https://janesmith.dev"
  },
  "repository": "https://github.com/janesmith/terraform-drift-detector",
  "homepage": "https://terraform-drift-detector.dev",
  "license": "Apache-2.0",
  "keywords": [
    "terraform",
    "infrastructure-as-code",
    "drift-detection",
    "aws",
    "gcp",
    "azure",
    "devops"
  ]
}
```

A minimal `plugin.json` with only required fields:

```json
{
  "name": "quick-formatter",
  "version": "1.0.0",
  "description": "Format code files using project-specific style rules",
  "author": {
    "name": "Developer Name"
  }
}
```

## CI Validation Rules

The Tons of Skills CI pipeline enforces strict validation on every `plugin.json` in pull requests. Understanding these rules prevents common PR failures.

### Strict Property Allowlist

The validation job checks that every `plugin.json` contains **only** the eight permitted fields. Any additional property causes a CI failure:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "A plugin",
  "author": { "name": "Dev" },
  "category": "devops"
}
```

The above would **fail** CI because `category` is not a permitted field in `plugin.json`. Categories are declared in `marketplace.extended.json`, not in the plugin manifest.

### JSON Validity

The file must be valid JSON. Trailing commas, single quotes, and unquoted keys all cause failures:

```json
// INVALID: trailing comma
{
  "name": "my-plugin",
  "version": "1.0.0",
}
```

### Required Field Presence

All four required fields (`name`, `version`, `description`, `author`) must be present. A missing required field fails validation:

```json
// INVALID: missing "author"
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "A plugin"
}
```

### Author Object Structure

When the `author` field is provided, it must be an object with at least a `name` string property. The string shorthand format (`"author": "Jane <jane@example.com>"`) is **not** supported; use the object form.

### URL Validation

If `repository` or `homepage` are provided, they must be valid URLs. If `author.url` is provided, it must also be a valid URL. If `author.email` is provided, it must be a valid email address.

## Relationship to marketplace.extended.json

The `plugin.json` manifest handles plugin-level metadata. Marketplace-specific metadata (categories, pricing, featured status, MCP tool declarations) lives in `.claude-plugin/marketplace.extended.json` at the repository root.

| Concern | Defined In |
|---------|-----------|
| Plugin identity (name, version, description) | `plugin.json` |
| Author and license | `plugin.json` |
| Discovery keywords | `plugin.json` |
| Marketplace category | `marketplace.extended.json` |
| Featured status | `marketplace.extended.json` |
| MCP tool declarations | `marketplace.extended.json` |
| Pricing tier | `marketplace.extended.json` |

The `marketplace.extended.json` file is the source of truth for the marketplace and is synced to `marketplace.json` (CLI-compatible) via `pnpm run sync-marketplace`. See the [Plugin Categories and Tags](/docs/reference/plugin-categories) reference for category details.

## Validation Commands

Validate your `plugin.json` locally before submitting a pull request:

```bash
# Validate plugin structure (includes plugin.json checks)
ccpi validate --strict

# Enterprise-tier validation (100-point rubric)
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/your-plugin/
```

The `ccpi validate --strict` command checks JSON validity, required fields, property allowlist compliance, and author object structure. The enterprise validator additionally scores documentation quality and completeness.

## MCP Server Plugins

MCP (Model Context Protocol) server plugins use the same `plugin.json` schema but have additional structural requirements. The `plugin.json` itself does not change, but MCP plugins also include:

- `package.json` for Node.js dependencies
- `src/*.ts` TypeScript source files
- `dist/index.js` that must be executable (shebang line + `chmod +x`)
- `.mcp.json` for MCP server configuration

The `plugin.json` for an MCP plugin follows the identical eight-field schema:

```json
{
  "name": "database-explorer",
  "version": "1.0.0",
  "description": "Browse and query databases through natural language via MCP",
  "author": {
    "name": "Intent Solutions",
    "url": "https://intentsolutions.io"
  },
  "repository": "https://github.com/intentsolutions/database-explorer",
  "license": "MIT",
  "keywords": ["database", "sql", "mcp", "query"]
}
```

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Adding `category` to plugin.json | CI rejection | Move category to `marketplace.extended.json` |
| Using string format for author | CI rejection | Use object: `{ "name": "..." }` |
| Trailing commas in JSON | CI rejection | Remove trailing commas |
| Missing required fields | CI rejection | Add all four: name, version, description, author |
| Invalid URL in repository | CI rejection | Use full URL: `https://github.com/...` |
| Version not following SemVer | Validator warning | Use `MAJOR.MINOR.PATCH` format |
| Duplicate name across plugins | Install conflicts | Choose a unique, descriptive name |
