---
title: "Tons of Skills Marketplace Guide"
description: "Complete guide to the Tons of Skills marketplace at tonsofskills.com. Browse 418 plugins and 2,834 skills, download Cowork bundles, compare plugins, and contribute your own."
section: "ecosystem"
order: 1
keywords: ["Tons of Skills marketplace", "Claude Code plugins marketplace", "browse plugins", "plugin categories", "Cowork downloads", "plugin verification", "skill browsing", "plugin comparison"]
officialLinks:
  - title: "Claude Code Plugins"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Claude Code Skills"
    url: "https://code.claude.com/docs/en/skills"
  - title: "Claude Code Overview"
    url: "https://code.claude.com/docs/en/overview"
relatedDocs:
  - "getting-started/installation"
  - "ecosystem/community-resources"
  - "ecosystem/official-anthropic-docs"
---

## What Is the Tons of Skills Marketplace

The Tons of Skills marketplace at [tonsofskills.com](https://tonsofskills.com) is the largest curated catalog of plugins and agent skills for Claude Code. Built and maintained by Intent Solutions, it provides a searchable, browsable interface to 418 plugins and 2,834 individual skills that extend Claude Code with specialized capabilities across dozens of domains -- from DevOps automation and security auditing to frontend development, database management, and SaaS integrations.

The marketplace is not just a directory. It is a fully integrated ecosystem with one-click downloads, compliance scoring, verification badges, side-by-side comparisons, curated collections, and learning resources. Every plugin listed on the marketplace is open source and available through the `ccpi` CLI or directly via Claude Code's built-in `/plugin` command.

The site is built with Astro 5 and statically generated for fast page loads and strong SEO. Data flows from the source-of-truth catalog file in the [GitHub repository](https://github.com/jeremylongshore/claude-code-plugins), through automated build pipelines, and into the pages you see on the site.

## Browsing Plugins on /explore

The [Explore](/explore) page is the primary entry point for discovering plugins. It presents the full catalog in a filterable, searchable grid layout.

### Search

The search bar at the top of the Explore page uses a Fuse.js-powered full-text search index that covers plugin names, descriptions, keywords, author names, and skill names. Results rank by relevance and update as you type. The search index is rebuilt on every site deployment, so it always reflects the latest catalog.

### Category filtering

Plugins are organized into categories that correspond to their primary use case. The current categories include:

- **Automation** -- CI/CD pipelines, task runners, workflow orchestration
- **Business Tools** -- CRM integration, invoicing, project management
- **DevOps** -- infrastructure as code, container management, monitoring
- **Code Analysis** -- linting, static analysis, code quality metrics
- **Debugging** -- error tracing, log analysis, diagnostic tools
- **AI/ML Assistance** -- prompt engineering, model evaluation, LLM tooling
- **Frontend Development** -- component generators, design systems, accessibility
- **Security** -- vulnerability scanning, secret detection, compliance checks
- **Testing** -- test generation, coverage analysis, mutation testing
- **Documentation** -- API docs, README generation, changelog automation
- **Performance** -- profiling, bundle analysis, load testing
- **Database** -- query optimization, migration management, schema design
- **Cloud Infrastructure** -- AWS, GCP, Azure resource management
- **Accessibility** -- WCAG compliance, screen reader testing
- **Mobile** -- React Native, Flutter, native platform tooling
- **Skill Enhancers** -- meta-plugins that improve Claude Code itself

Click any category chip to filter the grid down to plugins in that domain. You can combine category filtering with search to narrow results further.

### Plugin cards

Each plugin in the grid is displayed as a card showing the plugin name, description, author, version, category badge, and skill count. Featured plugins receive a highlighted card treatment with additional metadata. Click any card to open the full plugin detail page.

### Plugin detail pages

Every plugin has a dedicated page at `/plugins/{plugin-slug}` that displays:

- Full description and README content
- List of all skills, commands, and agents included in the plugin
- Installation command (copy to clipboard)
- Author information and repository link
- License and version history
- Verification status and compliance grade
- Links to related plugins

## Browsing Skills on /skills

The [Skills](/skills) page provides a searchable index of all 2,834 individual skills across every plugin in the marketplace. While the Explore page organizes content by plugin, the Skills page organizes content by skill -- making it easy to find a specific capability without knowing which plugin contains it.

Each skill entry shows the skill name, its parent plugin, a description of when the skill activates and what it does, and the list of tools the skill is allowed to use. Skills are auto-activating by default: Claude Code reads SKILL.md files and applies the skill's instructions whenever the context matches, without requiring a slash command.

The Skills page is particularly useful when you have a specific need -- for example, "I need a skill that helps me write database migrations" -- and want to search across the entire ecosystem rather than browsing plugin by plugin.

## Cowork Downloads on /cowork

The [Cowork](/cowork) page provides one-click zip bundle downloads for teams and developers who want to install plugins without going through the CLI one at a time.

### What Cowork offers

- **Individual plugin zips** -- download any single plugin as a self-contained zip file ready to extract into your Claude Code plugins directory.
- **Category bundles** -- download all plugins in a category (e.g., all Security plugins, all DevOps plugins) as a single zip.
- **Mega-zip** -- download the entire marketplace catalog in one archive. Useful for air-gapped environments or teams that want to evaluate everything offline.
- **Manifest file** -- a machine-readable JSON manifest listing every available download with checksums, file sizes, and plugin metadata.

### Security and integrity

Every zip file generated by the Cowork build pipeline goes through automated security scanning. The `validate-cowork-security.mjs` script checks for:

- Secrets or API keys accidentally bundled in plugin files
- `node_modules` directories that should not be distributed
- Executable files that are not expected
- Files exceeding size thresholds

Additionally, every zip includes a SHA-256 checksum in the manifest for integrity verification after download.

### How to use Cowork downloads

1. Visit [tonsofskills.com/cowork](/cowork).
2. Browse or search for the plugin or category you want.
3. Click the download button.
4. Extract the zip into your Claude Code plugins directory (typically `~/.claude/plugins/` or the project-level `.claude/plugins/` directory).
5. Restart or reload your Claude Code session. The new plugins are immediately available.

Cowork is rebuilt on every site deployment, so downloads always match the latest published catalog.

## Collections and Comparisons

### Collections

The [Collections](/collections) page groups plugins into hand-curated thematic sets that go beyond single categories. A collection might combine plugins from several categories around a workflow -- for example, a "Full-Stack Starter" collection that includes a frontend component generator, a backend API scaffolder, a database migration tool, and a testing framework.

Collections are maintained by the Tons of Skills team and are updated as new plugins are added to the marketplace. Each collection page lists the included plugins with brief descriptions and provides a single install command for the entire set.

### Compare

The [Compare](/compare) page lets you place two or more plugins side by side to evaluate their features, skill counts, compliance grades, and metadata. This is useful when multiple plugins serve a similar purpose and you want to choose the best fit for your project.

The comparison view shows:

- Feature lists and skill counts
- Compliance score and verification badge status
- Author and license information
- Category and keyword overlap
- Installation commands for each plugin

## Verification Badges and Compliance Scoring

Not all plugins are created equal. The Tons of Skills marketplace applies a rigorous compliance scoring system to every plugin, and the results are visible throughout the site as verification badges and letter grades.

### The 100-point enterprise rubric

The universal validator (`validate-skills-schema.py`) evaluates plugins on a 100-point scale across multiple dimensions:

- **Frontmatter completeness** -- are all required and recommended YAML fields present and valid?
- **Body content quality** -- does the skill/command/agent have substantive instructional content, or is it a stub?
- **Documentation** -- does the plugin include a README, changelog, and supporting reference files?
- **Metadata hygiene** -- are keywords, descriptions, and author fields properly formatted?
- **Structural conformance** -- does the plugin directory layout match the expected convention?

Scores map to letter grades: A (90-100), B (80-89), C (70-79), D (60-69), F (below 60). These grades appear on plugin cards, detail pages, and in the CLI output.

### Verification badges

Plugins that pass the full enterprise compliance check with an A or B grade receive a verification badge displayed on their marketplace card. The badge signals to users that the plugin meets a high standard of quality, documentation, and structural correctness.

### Stub detection

The validator also flags "stub" skills -- skills that have frontmatter but lack meaningful instructional content in the body. Stub skills are not penalized in the grade (they are flagged separately), but they are noted on the plugin detail page so users know which skills are fully fleshed out and which are placeholders.

## How to Contribute Plugins

The Tons of Skills marketplace is open to contributions from any developer. If you have built a useful Claude Code plugin, you can publish it to the marketplace and make it available to the entire community.

### Contribution workflow

1. **Structure your plugin** according to the [plugin structure guide](/docs/concepts/plugins). At minimum, you need a `.claude-plugin/plugin.json` with the required fields (`name`, `version`, `description`, `author`), a `README.md`, and at least one skill, command, or agent file.

2. **Validate your plugin** locally using the universal validator:

   ```bash
   python3 scripts/validate-skills-schema.py --enterprise plugins/your-category/your-plugin/
   ```

3. **Add your plugin to the catalog** by creating an entry in `.claude-plugin/marketplace.extended.json` and running `pnpm run sync-marketplace`.

4. **Open a pull request** on the [GitHub repository](https://github.com/jeremylongshore/claude-code-plugins). CI runs the full validation suite, builds the marketplace site, and checks performance budgets. A maintainer reviews your PR and merges it.

5. **Your plugin is live** on the next site deployment. It appears on the Explore page, the Skills page indexes its skills, and Cowork generates downloadable zips.

For a detailed step-by-step guide, see the publishing guide in the docs.

## Other Marketplace Features

### Playbooks

The [Playbooks](/playbooks) section contains long-form, opinionated guides that walk through end-to-end workflows using combinations of plugins. A playbook might cover "Securing a Node.js API" using three security plugins together, or "Migrating a legacy codebase" using code analysis and testing plugins in sequence.

### Research

The [Research](/research) section publishes technical analyses of the Claude Code plugin ecosystem -- benchmark results, adoption trends, compliance statistics, and architectural deep dives.

### Blog

The [Blog](/blog) covers release announcements, contributor spotlights, technical tutorials, and ecosystem news. New posts are published regularly and cover both the marketplace platform and the broader Claude Code community.

### Learning

The [Learning](/learning) section provides structured educational content for developers new to Claude Code plugins. It covers foundational concepts like skills, commands, and agents, and progresses through intermediate topics like plugin authoring and advanced topics like MCP server development.

### Tools

The [Tools](/tools) section offers interactive utilities for plugin development, such as frontmatter validators and structure generators.

## Architecture and Data Flow

For those interested in how the marketplace works under the hood, the data pipeline is straightforward:

1. **Source of truth**: `.claude-plugin/marketplace.extended.json` in the GitHub repository.
2. **Sync**: `pnpm run sync-marketplace` generates the CLI-compatible `marketplace.json`.
3. **Build pipeline**: The Astro build runs six sequential steps -- skill discovery, README extraction, catalog sync, search index generation, Cowork zip generation, and static site generation.
4. **Deployment**: The built site deploys to production at tonsofskills.com.
5. **CLI integration**: The `ccpi` CLI fetches `catalog.json` from the deployed site and caches it locally.

This architecture ensures that the marketplace website, the CLI, and the Cowork downloads are always in sync and always reflect the latest state of the catalog.

## Next Steps

- [Install Claude Code Plugins](/docs/getting-started/installation) -- set up the ccpi CLI and connect to the marketplace.
- [Browse the Marketplace](/explore) -- search and filter all 418 plugins.
- [Browse Skills](/skills) -- search across 2,834 individual skills.
- [Download Cowork Bundles](/cowork) -- one-click zip downloads for teams.
- [Community Resources](/docs/ecosystem/community-resources) -- contribute, report issues, and connect with other developers.
