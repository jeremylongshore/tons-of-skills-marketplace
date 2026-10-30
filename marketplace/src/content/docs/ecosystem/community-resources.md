---
title: 'Claude Code Community and Resources'
description: 'Connect with the Claude Code community. Contribute plugins to the Tons of Skills marketplace, file issues, join discussions, and explore learning resources across the ecosystem.'
section: 'ecosystem'
order: 3
keywords:
  - "Claude Code community"
  - "contribute plugins"
  - "open source"
  - "GitHub"
  - "Discord"
  - "Claude Code learning"
  - "plugin development"
  - "Claude Code ecosystem tools"
officialLinks:
  - title: 'Claude Code Overview'
    url: 'https://code.claude.com/docs/en/overview'
  - title: 'Claude Code Plugins'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'ecosystem/marketplace-overview'
  - 'ecosystem/official-anthropic-docs'
  - 'getting-started/installation'
---

## Overview

Tons of Skills combines a plugin repository, generated marketplace data, and a searchable website. Use the public [Explore](/explore) and [Skills](/skills) pages for their current build-derived inventories. Public search counts and editable catalog counts describe different cohorts; an old hard-coded total is not an inventory receipt.

## Repository and contributions

The canonical repository is [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace). Read its `CONTRIBUTING.md`, `AGENTS.md`, and `CLAUDE.md` before changing source or generated artifacts.

A plugin normally lives under `plugins/<category>/<plugin-name>/`. Existing starter directories include `templates/minimal-plugin`, `templates/skill-plugin`, `templates/command-plugin`, `templates/agent-plugin`, and `templates/full-plugin`. They are starting material, not a guarantee that every template matches today's validator. Inspect and update required metadata before submission.

For example, from the repository root, copy the actual skill-plugin template to a new, nonexisting destination:

```bash
cp -R templates/skill-plugin plugins/testing/example-review-plugin
```

The destination is illustrative; do not overwrite an existing plugin. Marketplace skills require `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing fields are errors. Agent and plugin manifests have their own contracts.

## Local checks and generated files

Use the documented Node and package-manager versions. These are repository checks, not a promise about elapsed time:

```bash
./scripts/quick-test.sh
python3 scripts/validate-skills-schema.py --standard /absolute/path/to/example-review-plugin
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/example-review-plugin
```

`quick-test.sh` performs build, lint, and validation work and can take longer than a short smoke test. Select the validator tier explicitly when demonstrating native-floor versus marketplace behavior.

Do not hand-edit generated catalogs or verification projections. Run the canonical commands and commit their legitimate output as required by the repository guidelines. Plugin and catalog changes require `pnpm run sync-marketplace`; score-affecting changes require verification and the corresponding projection pipeline. Inspect every generated delta rather than assuming all output is in scope.

## Marketplace implementation

The site uses Astro, with its actual version pinned by `marketplace/package.json` and the lockfile. Its build discovers skills, extracts README content, synchronizes catalog data, builds public search, and prepares downloadable artifacts. Refer to `marketplace/scripts/build.mjs` for the executable pipeline instead of an old framework version or fixed stage count.

Search includes documentation as well as public plugins and skills. Existing browser tests cover the documented search experience; a public site's deployment and caches can still lag a repository checkout.

## External-source contributions

External mirrors are governed by their source declarations, lock entries, provenance, quarantine, and review rules. The tracked `sync-external.yml` schedule is weekly (`0 6 * * 1`), not daily. A scheduled sync is not automatic approval to admit arbitrary upstream changes.

Do not edit mirror-owned code or relock sources merely to make a local check pass. Follow the source-owner and repository workflow for an actual bounded update.

## Claude Code integrations

The official [VS Code extension](https://code.claude.com/docs/en/vs-code) supports plugin management and shares relevant user settings with Claude Code. It is incorrect to say that plugins cannot load in VS Code. The [JetBrains integration](https://code.claude.com/docs/en/jetbrains) is also an official Claude Code integration, not an unrelated product operating independently of Claude Code. Features and setup differ across integrations; consult their current references.

Third-party editors and other agent harnesses have separate support boundaries. The delivered portable skill installer does not imply that every Claude plugin component, hook, or MCP server works in every harness.

## Useful starting points

- [Official documentation directory](/docs/ecosystem/official-anthropic-docs/) for platform-owned behavior.
- [First skill](/docs/getting-started/first-skill/) for a complete local authoring example.
- [Plugin concepts](/docs/concepts/plugins/) for packaging and contract boundaries.
- [CLI reference](/docs/getting-started/cli-reference/) for current helper capabilities and placeholders.

When reporting a problem, include the exact source revision, command, runtime version, and minimal redacted evidence. Do not post credentials, private source, full raw tool payloads, or unreviewed claims of security certification.
