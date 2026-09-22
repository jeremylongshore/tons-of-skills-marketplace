---
title: "Publish a Plugin to the Marketplace"
description: "Complete guide to publishing a Claude Code plugin to the Tons of Skills marketplace. Covers requirements, marketplace.extended.json, sync-marketplace, enterprise validation, submission process, and versioning."
section: "guides"
order: 6
keywords:
  - "publish"
  - "marketplace"
  - "submit plugin"
  - "marketplace.extended.json"
  - "sync-marketplace"
  - "enterprise validation"
  - "Tons of Skills"
  - "plugin submission"
  - "versioning"
officialLinks:
  - title: "Tons of Skills Marketplace"
    url: "https://tonsofskills.com"
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
relatedDocs:
  - "guides/build-a-plugin"
  - "reference/plugin-json-schema"
  - "ecosystem/marketplace-overview"
---

## Marketplace Overview

The [Tons of Skills marketplace](https://tonsofskills.com) is the central directory for Claude Code plugins. With over 418 plugins and 2,834 skills, it provides discovery, search, and installation for the Claude Code ecosystem. Publishing your plugin to the marketplace makes it installable with a single command and discoverable by thousands of Claude Code users.

This guide covers the full publication process: meeting requirements, adding your plugin to the catalog, passing validation, and submitting for review.

## Prerequisites

Before starting, ensure you have:

1. A working plugin that follows the standard structure (see [How to Build a Plugin](/docs/guides/build-a-plugin))
2. A GitHub repository containing your plugin
3. A passing validation at the standard tier minimum
4. A README.md with installation instructions and feature descriptions

## Step 1: Meet Marketplace Requirements

### Required Files

Every marketplace plugin must have:

| File | Purpose | Notes |
|------|---------|-------|
| `.claude-plugin/plugin.json` | Plugin manifest | Only allowed fields; see below |
| `README.md` | Documentation | Installation, features, usage |

### plugin.json Schema

The marketplace enforces a strict schema for `plugin.json`. Only these fields are accepted:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Clear, specific description of what this plugin does",
  "author": "Your Name <you@example.com>",
  "repository": "https://github.com/username/repo-name",
  "homepage": "https://tonsofskills.com/plugins/category/my-plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

**Field rules:**

- `name`: Required. Lowercase kebab-case. Must be unique across the marketplace.
- `version`: Required. Semantic versioning (MAJOR.MINOR.PATCH).
- `description`: Required. One to two sentences. No marketing language.
- `author`: Required. Name and optionally email in angle brackets.
- `repository`: Optional but recommended. Full HTTPS URL.
- `homepage`: Optional. Full HTTPS URL.
- `license`: Optional but recommended. SPDX identifier.
- `keywords`: Optional but recommended. Array of lowercase strings.

CI rejects any fields not in this list. Do not add `dependencies`, `main`, `scripts`, or custom fields.

### README Standards

Your README should include:

1. **Title and description** -- What the plugin does, in plain language
2. **Features** -- Bulleted list of capabilities
3. **Installation** -- The exact install command
4. **Commands** -- Table of slash commands with descriptions (if any)
5. **Skills** -- List of auto-activating skills (if any)
6. **Agents** -- List of autonomous agents (if any)
7. **Requirements** -- Runtime dependencies, minimum versions
8. **License** -- License type

### Quality Threshold

Plugins must meet minimum quality standards:

- No stub or placeholder content in SKILL.md files
- All frontmatter fields properly formatted
- Description fields longer than 50 characters
- Body content with real instructions (not "TODO" or "Coming soon")
- No hardcoded secrets, API keys, or credentials

## Step 2: Run Validation

### Standard Validation

Run the universal validator against your plugin:

```bash
python3 scripts/validate-skills-schema.py --verbose plugins/category/my-plugin/
```

This checks Anthropic minimum requirements:

- Valid YAML frontmatter syntax
- Required fields present (`name`, `description`, `version`, `author`, `license`)
- Valid `allowed-tools` entries (no misspelled tool names)
- File structure matches expected layout

### Enterprise Validation

The enterprise tier applies a 100-point rubric that evaluates marketplace readiness:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/my-plugin/
```

The rubric scores across several dimensions:

| Category | Points | What It Measures |
|----------|--------|------------------|
| Frontmatter | 25 | Field completeness, description quality, valid tools |
| Body structure | 25 | Sections (Overview, Instructions, Output, Error Handling) |
| Content depth | 20 | Word count, code examples, specificity |
| Documentation | 15 | Supporting files, references, examples |
| Metadata | 15 | Tags, compatibility, version, license |

### Grade Thresholds

| Grade | Score | Marketplace Status |
|-------|-------|--------------------|
| A | 90-100 | Featured on Explore page |
| B | 70-89 | Accepted for marketplace |
| C | 50-69 | Needs improvement before acceptance |
| D | 30-49 | Significant gaps; not marketplace-ready |
| F | 0-29 | Stub or placeholder; rejected |

**Minimum for marketplace acceptance: B grade (70+).**

### Fix Common Issues

The most frequent validation failures and their fixes:

**"Description too short"** -- Expand your description to at least 100 characters. Include trigger phrases and specific technologies.

```yaml
# Bad
description: "Helps with Docker"

# Good
description: |
  Manage Docker Compose configurations for development and production
  environments. Handles service definitions, networking, volumes, and
  environment-specific overrides. Trigger phrases: "create a compose
  file", "add a Docker service", "fix compose networking".
```

**"Missing sections"** -- Add the expected sections to your SKILL.md body: Overview, Instructions, Output, Error Handling, Examples.

**"No code examples"** -- Add at least one fenced code block with a language tag showing expected input or output.

**"Invalid allowed-tools"** -- Check for typos. The valid tools are: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Task`, `TodoWrite`, `NotebookEdit`, `AskUserQuestion`, `Skill`.

### Populate Freshie Inventory

Optionally, write your validation results to the ecosystem inventory database for tracking:

```bash
python3 scripts/validate-skills-schema.py --enterprise \
  --populate-db freshie/inventory.sqlite \
  plugins/category/my-plugin/
```

## Step 3: Add to marketplace.extended.json

The marketplace catalog is driven by `.claude-plugin/marketplace.extended.json`. This is the source of truth for all marketplace listings.

### Catalog Entry Format

Add your plugin to the `plugins` array in `marketplace.extended.json`:

```json
{
  "name": "my-plugin",
  "description": "Clear description of what this plugin does",
  "version": "1.0.0",
  "category": "devops",
  "keywords": ["docker", "containers", "deployment"],
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/username"
  },
  "repository": "https://github.com/username/repo-name",
  "license": "MIT",
  "installation": "claude /plugin add username/repo-name",
  "featured": false,
  "features": [
    "Feature description 1",
    "Feature description 2",
    "Feature description 3"
  ],
  "requirements": [
    "Docker installed",
    "docker-compose v2+"
  ]
}
```

### Category Options

Choose the most appropriate category:

| Category | Examples |
|----------|----------|
| `automation` | Workflow automation, task scheduling |
| `business-tools` | CRM, invoicing, project management |
| `devops` | CI/CD, Docker, Kubernetes, infrastructure |
| `code-analysis` | Linting, code review, static analysis |
| `debugging` | Error analysis, log parsing, debugging tools |
| `ai-ml-assistance` | ML pipelines, model training, AI safety |
| `frontend-development` | React, Vue, CSS, accessibility |
| `security` | Vulnerability scanning, secret detection |
| `testing` | Unit testing, E2E testing, test generation |
| `documentation` | Doc generation, API docs, README writing |
| `performance` | Profiling, optimization, monitoring |
| `database` | SQL, migrations, schema design |
| `cloud-infrastructure` | AWS, GCP, Azure, serverless |
| `accessibility` | WCAG compliance, screen reader testing |
| `mobile` | React Native, Flutter, iOS, Android |
| `skill-enhancers` | Meta-skills, skill development tools |
| `other` | Anything that does not fit above |

### Extended-Only Fields

`marketplace.extended.json` supports additional fields that are stripped when syncing to the CLI-compatible `marketplace.json`:

| Field | Purpose |
|-------|---------|
| `featured` | Boolean. Featured plugins appear prominently on the Explore page. |
| `mcpTools` | Array of MCP tool descriptions (for MCP server plugins). |
| `pluginCount` | Number of sub-plugins (for packs). |
| `pricing` | Pricing tier information. |
| `components` | Component breakdown (skills, commands, agents). |
| `zcf_metadata` | Zero-config framework metadata. |
| `external_sync` | External repository sync configuration. |

## Step 4: Sync the Marketplace

After editing `marketplace.extended.json`, regenerate the CLI-compatible catalog:

```bash
pnpm run sync-marketplace
```

This command:

1. Reads `marketplace.extended.json`
2. Strips extended-only fields (`featured`, `mcpTools`, `pluginCount`, etc.)
3. Writes the result to `marketplace.json`
4. Validates the output JSON

**CI fails if `marketplace.json` is out of sync with `marketplace.extended.json`.** Always run `sync-marketplace` after editing the extended file.

### Verify the Sync

```bash
# Check that marketplace.json was updated
git diff .claude-plugin/marketplace.json

# Run the quick test to verify everything passes
./scripts/quick-test.sh
```

## Step 5: Submit to the Marketplace

### For Tons of Skills Repository Contributors

If your plugin lives inside the `claude-code-plugins` repository:

1. Create a feature branch:

   ```bash
   git checkout -b feat/add-my-plugin
   ```

2. Add your plugin files and the marketplace entry:

   ```bash
   git add plugins/category/my-plugin/
   git add .claude-plugin/marketplace.extended.json
   git add .claude-plugin/marketplace.json
   ```

3. Run the full validation suite:

   ```bash
   pnpm run sync-marketplace
   ./scripts/quick-test.sh
   python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/my-plugin/
   ```

4. Commit and push:

   ```bash
   git commit -m "feat: add my-plugin to marketplace"
   git push -u origin feat/add-my-plugin
   ```

5. Open a pull request. CI runs the full validation pipeline including:
   - Plugin structure validation
   - Enterprise skill grading
   - Marketplace build and route validation
   - Performance budget checks
   - Secret scanning

### For External Repository Submissions

If your plugin lives in its own GitHub repository:

1. Ensure your repo follows the standard plugin structure
2. Open an issue on the [claude-code-plugins repository](https://github.com/jeremylongshore/claude-code-plugins) requesting inclusion
3. Include:
   - Repository URL
   - Plugin category
   - Brief description
   - Enterprise validation score

External plugins can also be synced automatically via `sources.yaml`. See the repository documentation for the external sync process.

## Step 6: Versioning and Updates

### Semantic Versioning

Follow semantic versioning for all updates:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Bug fix, typo correction | PATCH | `1.0.0` to `1.0.1` |
| New command or skill | MINOR | `1.0.1` to `1.1.0` |
| Breaking changes, restructure | MAJOR | `1.1.0` to `2.0.0` |

Update the version in both `plugin.json` and `marketplace.extended.json`, then run `pnpm run sync-marketplace`.

### Changelog

Maintain a `CHANGELOG.md` in your plugin directory:

```markdown
# Changelog

## 1.1.0 (2026-04-06)

### Added
- New `/docker-debug` command for container troubleshooting
- `dockerfile-optimizer` skill for multi-stage build patterns

### Fixed
- Fixed compose file validation for v2 syntax

## 1.0.0 (2026-03-15)

### Added
- Initial release
- `docker-compose` skill for compose file management
- `/docker-build` command for Dockerfile generation
- `security-scanner` agent
```

### Updating Published Plugins

To update a plugin already in the marketplace:

1. Make your changes
2. Bump the version in `plugin.json`
3. Update the version in `marketplace.extended.json`
4. Run `pnpm run sync-marketplace`
5. Run enterprise validation to confirm quality is maintained
6. Submit a PR with your changes

## Post-Publication

### Monitor Your Plugin

After publication, your plugin is visible on the [Explore](/explore) page and searchable on the [Skills](/skills) page. Monitor its listing to ensure:

- The description displays correctly
- Keywords match user search behavior
- The installation command works from the marketplace page

### Improve Your Grade

If your plugin scored a B, work toward an A (90+) for featured placement:

1. Add more code examples to SKILL.md files
2. Add supporting reference files
3. Expand error handling sections
4. Add DCI for runtime context
5. Re-run enterprise validation after each improvement

### Batch Remediation

Use the automated remediation tools to fix common quality issues across all your skills:

```bash
# Preview what would be fixed
python3 freshie/scripts/batch-remediate.py --dry-run

# Apply all auto-fixes
python3 freshie/scripts/batch-remediate.py --all --execute

# Re-validate
python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/category/my-plugin/
```

## Quick Reference Checklist

Use this checklist before submitting:

- [ ] `plugin.json` has only allowed fields (`name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords`)
- [ ] `README.md` exists with installation instructions
- [ ] All SKILL.md files have required frontmatter (`name`, `description`, `allowed-tools`, `version`, `author`, `license`)
- [ ] All SKILL.md files have structured body sections
- [ ] Standard validation passes with zero errors
- [ ] Enterprise validation scores B grade (70+) or higher
- [ ] Entry added to `marketplace.extended.json` with correct category
- [ ] `pnpm run sync-marketplace` executed
- [ ] `marketplace.json` committed (auto-generated, but must be committed)
- [ ] `./scripts/quick-test.sh` passes
- [ ] No secrets, API keys, or credentials in source files
- [ ] Plugin installs correctly from a clean environment
