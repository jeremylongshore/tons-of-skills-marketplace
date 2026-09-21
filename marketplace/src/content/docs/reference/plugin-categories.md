---
title: "Plugin Categories and Tags"
description: "Complete reference of all allowed plugin categories in the Tons of Skills marketplace, with descriptions, selection guidance, and tagging best practices for maximum discoverability."
section: "reference"
order: 3
keywords: ["categories", "tags", "marketplace", "discovery", "filtering", "plugin categories", "keywords"]
officialLinks:
  - title: "Claude Code Plugins Documentation"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Tons of Skills Marketplace"
    url: "https://tonsofskills.com/explore"
relatedDocs:
  - "guides/build-a-plugin"
  - "guides/publish-to-marketplace"
  - "reference/plugin-json-schema"
---

## Overview

Every plugin in the Tons of Skills marketplace is assigned exactly one category. Categories drive the primary navigation on the [Explore](/explore) page, power filtered search results, and help developers find plugins relevant to their workflow. Choosing the right category directly affects your plugin's discoverability.

Categories are defined in `marketplace.extended.json` (the marketplace source of truth), not in `plugin.json`. The plugin manifest handles identity and keywords; the marketplace catalog handles categorization and display metadata. This separation means you can update a plugin's category without modifying the plugin itself.

## Allowed Categories

The marketplace schema enforces a fixed set of 17 categories. CI validation rejects any plugin listing with a category not in this list.

### Category Reference Table

| Category | Slug | Description | Example Plugins |
|----------|------|-------------|-----------------|
| Automation | `automation` | Workflow automation, task scheduling, process orchestration, and repetitive task elimination. | CI pipeline generators, cron job managers, file watchers |
| Business Tools | `business-tools` | Business process tools, project management integrations, invoicing, CRM workflows, and operational utilities. | Invoice generators, project trackers, reporting tools |
| DevOps | `devops` | Infrastructure management, CI/CD pipelines, container orchestration, deployment automation, and monitoring. | Terraform helpers, Docker compose generators, Kubernetes auditors |
| Code Analysis | `code-analysis` | Static analysis, code quality metrics, complexity scoring, dependency auditing, and architectural review. | Linters, complexity analyzers, dead code detectors |
| Debugging | `debugging` | Bug diagnosis, error analysis, log parsing, stack trace interpretation, and runtime debugging assistance. | Error tracers, log parsers, memory leak detectors |
| AI/ML Assistance | `ai-ml-assistance` | Machine learning workflows, model training, prompt engineering, data science pipelines, and AI integration. | Model evaluators, prompt optimizers, dataset validators |
| Frontend Development | `frontend-development` | UI component generation, CSS tooling, responsive design, accessibility testing, and frontend framework utilities. | React scaffolders, CSS generators, design system builders |
| Security | `security` | Vulnerability scanning, secret detection, compliance checking, penetration testing assistance, and security auditing. | Secret scanners, dependency auditors, OWASP checkers |
| Testing | `testing` | Test generation, test coverage analysis, mutation testing, E2E test scaffolding, and test quality auditing. | Unit test generators, coverage reporters, test data factories |
| Documentation | `documentation` | API documentation generation, README scaffolding, changelog management, and technical writing assistance. | API doc generators, changelog builders, JSDoc helpers |
| Performance | `performance` | Performance profiling, bundle analysis, load testing, optimization recommendations, and runtime benchmarking. | Bundle analyzers, lighthouse auditors, query optimizers |
| Database | `database` | Database schema management, query optimization, migration generation, and data modeling. | Schema designers, migration generators, query explainers |
| Cloud Infrastructure | `cloud-infrastructure` | Cloud provider integrations, serverless deployment, infrastructure-as-code, and multi-cloud management. | AWS CDK helpers, GCP deployers, serverless scaffolders |
| Accessibility | `accessibility` | WCAG compliance checking, screen reader testing, color contrast analysis, and inclusive design tooling. | WCAG auditors, contrast checkers, ARIA validators |
| Mobile | `mobile` | Mobile app development, React Native tooling, Flutter utilities, and cross-platform mobile workflows. | React Native scaffolders, Flutter generators, app store helpers |
| Skill Enhancers | `skill-enhancers` | Meta-plugins that enhance Claude Code's own capabilities, extend the plugin system, or provide cross-cutting utilities. | Plugin validators, skill composers, workflow orchestrators |
| Other | `other` | Plugins that do not fit neatly into any other category. Use sparingly and only when no other category is a reasonable fit. | Miscellaneous utilities, experimental tools |

### Category Distribution

The Tons of Skills marketplace tracks category distribution to ensure balanced coverage. As of the current release, the most populated categories are `devops`, `automation`, `code-analysis`, and `testing`. Categories like `accessibility` and `mobile` have fewer plugins, representing opportunities for new contributions.

## How Categories Are Used

### Explore Page Filtering

The [Explore](/explore) page displays category chips that allow users to filter the full plugin list. Each chip shows the category name and the count of plugins in that category. Selecting a category filters the grid to show only matching plugins.

### Search Integration

The `ccpi search` command and the marketplace search bar both index categories. Searching for "devops" returns all plugins in the `devops` category, even if "devops" does not appear in the plugin name or description.

### Plugin Detail Pages

Each plugin's detail page displays its category as a clickable badge. Clicking the badge navigates to the Explore page filtered to that category, helping users discover related plugins.

### Marketplace Catalog

The `marketplace.extended.json` file associates each plugin with its category. During the build pipeline, `sync-catalog.mjs` copies this data into `catalog.json`, which powers the Explore page and search index.

## Choosing the Right Category

Follow these guidelines to select the most appropriate category for your plugin.

### Primary Function Rule

Choose the category that matches the plugin's **primary function**, not its implementation technology. A plugin that generates Terraform configurations is `devops` or `cloud-infrastructure`, not `code-analysis`, even though it may analyze existing configs to generate new ones.

### Decision Framework

Ask these questions in order:

1. **What problem does this plugin solve?** Map the problem domain to a category.
2. **Who is the primary user?** A plugin for DevOps engineers belongs in `devops`; a plugin for frontend developers belongs in `frontend-development`.
3. **What is the primary output?** Test generation belongs in `testing`; documentation generation belongs in `documentation`.
4. **Does it fit multiple categories?** Choose the one that best describes the primary use case. Use `keywords` in `plugin.json` to capture secondary concerns.

### Category Selection Examples

| Plugin | Primary Function | Category | Reasoning |
|--------|-----------------|----------|-----------|
| Terraform Plan Analyzer | Analyzes Terraform plans for issues | `devops` | Primary audience is DevOps; primary action is infrastructure review |
| React Component Scaffolder | Generates React components with tests | `frontend-development` | Primary output is frontend code |
| SQL Query Optimizer | Suggests query performance improvements | `database` | Primary domain is database operations |
| OWASP Dependency Checker | Scans dependencies for known CVEs | `security` | Primary function is vulnerability detection |
| API Documentation Generator | Creates OpenAPI docs from source code | `documentation` | Primary output is documentation |
| Plugin Validator | Validates plugin.json and SKILL.md files | `skill-enhancers` | Enhances the plugin system itself |

### When to Use "other"

The `other` category is a catch-all for plugins that genuinely do not fit any specific category. Use it sparingly. Before defaulting to `other`, consider whether the plugin might fit into `automation` (general-purpose tools) or `skill-enhancers` (meta-tools).

Plugins in `other` receive less category-based discovery traffic because users rarely filter by "other." If possible, choose a more specific category.

## Tags and Keywords

While categories provide broad classification, tags and keywords enable fine-grained discovery. Tags are defined in two places:

| Location | Field | Purpose |
|----------|-------|---------|
| `plugin.json` | `keywords` | Plugin-level discovery terms, indexed by `ccpi search` |
| `SKILL.md` frontmatter | `tags` | Skill-level discovery terms, indexed by the marketplace search |

### Tagging Best Practices

**Be specific.** Generic tags like `code` or `tool` do not differentiate your plugin. Use technology names, problem domains, and specific frameworks:

```json
// Good
"keywords": ["terraform", "drift-detection", "aws", "infrastructure-as-code"]

// Poor
"keywords": ["code", "tool", "devops", "useful"]
```

**Cover the technology stack.** Include the primary language, framework, and platform:

```json
"keywords": ["react", "typescript", "storybook", "component-library", "design-system"]
```

**Include problem-domain terms.** Users search for problems, not solutions:

```json
"keywords": ["memory-leak", "performance-profiling", "heap-analysis", "garbage-collection"]
```

**Use synonyms and abbreviations.** Users may search for either form:

```json
"keywords": ["kubernetes", "k8s", "container-orchestration", "helm"]
```

**Limit to 3-8 keywords.** Each keyword should add discovery value. Beyond 8, the marginal benefit drops significantly.

### Tag Hierarchy

The marketplace search system indexes keywords in this priority order:

1. Plugin `name` (highest weight)
2. Plugin `description`
3. Plugin `keywords` array
4. Skill `tags` arrays
5. Plugin category name

This means keywords do not need to duplicate words already present in the name or description.

## Where Categories Are Defined

Categories are set in `marketplace.extended.json`, the marketplace source of truth. Each plugin entry includes a `category` field:

```json
{
  "name": "terraform-drift-detector",
  "category": "devops",
  "description": "Detect Terraform configuration drift",
  ...
}
```

After editing `marketplace.extended.json`, run `pnpm run sync-marketplace` to regenerate the CLI-compatible `marketplace.json`. The marketplace build pipeline then copies catalog data into the Astro site's data files.

**Do not add `category` to `plugin.json`.** The CI pipeline rejects any `plugin.json` containing fields outside the eight-field allowlist. See the [plugin.json Schema Reference](/docs/reference/plugin-json-schema) for the complete list of permitted fields.

## Category Validation

The Astro content collection schema (`marketplace/src/content/config.ts`) enforces a Zod enum for categories. If a plugin listing contains an invalid category string, the build fails with a schema validation error.

```typescript
category: z.enum([
  'automation',
  'business-tools',
  'devops',
  'code-analysis',
  'debugging',
  'ai-ml-assistance',
  'frontend-development',
  'security',
  'testing',
  'documentation',
  'performance',
  'database',
  'cloud-infrastructure',
  'accessibility',
  'mobile',
  'skill-enhancers',
  'other'
])
```

New categories cannot be added without updating this enum, the `validate-plugins.yml` CI workflow, and the Explore page filter UI. Category additions are rare and require a pull request to the core repository.

## SaaS Packs and Categories

SaaS skill packs (located at `plugins/saas-packs/*-pack`) follow the same categorization rules but tend to cluster in `business-tools`, `automation`, and `cloud-infrastructure`. Each SaaS pack is a standalone plugin with its own `plugin.json` and marketplace entry. The category should reflect what the pack helps users accomplish, not the SaaS platform itself.

For example, a Stripe integration pack that helps manage billing workflows belongs in `business-tools`, while a Datadog integration pack that helps with monitoring belongs in `devops`.
