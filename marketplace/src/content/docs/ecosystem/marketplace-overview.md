---
title: 'Tons of Skills Marketplace Guide'
description: 'Browse the generated public catalog, understand installation and static quality projections, and follow the marketplace source and build boundaries.'
section: 'ecosystem'
order: 1
keywords:
  - "Tons of Skills marketplace"
  - "Claude Code plugins marketplace"
  - "browse plugins"
  - "plugin categories"
  - "Cowork downloads"
  - "plugin verification"
  - "skill browsing"
  - "plugin comparison"
officialLinks:
  - title: 'Claude Code Plugins'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Claude Code Skills'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Overview'
    url: 'https://code.claude.com/docs/en/overview'
relatedDocs:
  - 'getting-started/installation'
  - 'ecosystem/community-resources'
  - 'ecosystem/official-anthropic-docs'
---

## Overview

Tons of Skills is a searchable marketplace for Claude Code plugins and skills, with supporting documentation and downloadable artifacts. It complements Anthropic's official marketplaces. This description does not make an unsupported worldwide-size claim.

The canonical source repository is [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace). Its editable catalog, public plugin index, and discovered skill inventory are different cohorts. Use the site's build-derived counts and provenance rather than an old hard-coded total.

## Browse and search

[Explore](/explore) searches plugin names, descriptions, categories, keywords, and generated search text. Use the available category and sort controls to narrow results. [Skills](/skills) exposes the public skill index, while site search also includes documentation.

A current plugin card presents its name, description, installation command, author, and skill count when available. Do not assume every grid card renders a version, category label, or verification badge. Detail pages and generated metadata provide additional context.

Inspect the plugin's README, runtime prerequisites, provenance, and included components before installation. A search match is a discovery aid, not approval to execute its code or send data to a provider.

## Installation and distribution

Use the native marketplace workflow for Claude Code plugins:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
claude plugin install api-test-automation@claude-code-plugins-plus --scope project
```

Review scope, permissions, and the install summary. Reload or restart only as the current native workflow requires. See [first plugin](/docs/getting-started/first-plugin/) for this actual catalog example.

A downloaded archive is a distribution artifact, not automatic native registration. Use its documented installation route or `claude --plugin-dir /absolute/path/to/reviewed-plugin` for local development. Portable skill installation is a separate bounded CLI feature; it does not install every hook, server, or other plugin component into every harness.

## Static quality projections

The skill rubric weights progressive disclosure (30), ease of use (25), utility (20), specification compliance (15), and writing style (10), with modifiers. Letter grades use A ≥90, B ≥80, C ≥70, D ≥60, and F below 60.

The current plugin verification pipeline averages available skill scores and projects gold at 90, silver at 75, and bronze at 60. These badge thresholds differ from letter-grade thresholds. Stub classification, static production checks, and optional behavioral evidence remain separate. A high score or badge does not certify provider operation, security, or production readiness.

## How data reaches the site

The site uses the Astro version pinned in `marketplace/package.json`. Its executable build pipeline is `marketplace/scripts/build.mjs`; the current sequence has eight stages:

1. Discover skills.
2. Extract README sections.
3. Synchronize site catalog data.
4. Generate unified search data.
5. Build Cowork archives.
6. Validate the Cowork manifest.
7. Copy public data.
8. Build Astro output.

These are generated snapshots of their inputs. A successful build does not prove that every deployed client cache is current, or that all catalog cohorts have identical counts. Deployment, source revision, and cache state are separate evidence.

External source synchronization is provenance-pinned and reviewed. The tracked scheduled workflow runs weekly, not daily; a scheduled job is not blanket approval for arbitrary upstream changes.

## Contributing and authority

Author source under `plugins/<category>/<plugin>/`. Do not hand-edit generated catalogs; run the canonical sync and verification/projection commands required by the repository guidelines, inspect their output, and commit legitimate derived changes.

The marketplace's eight skill fields and tier gates are stricter than the native permissive floor. Missing required metadata remains an error. Follow the canonical standards and authority map rather than treating this overview as a replacement schema, pricing policy, or new acceptance threshold.

For platform behavior, start with the [official documentation directory](/docs/ecosystem/official-anthropic-docs/). For helper limitations, use the [CLI reference](/docs/getting-started/cli-reference/).
