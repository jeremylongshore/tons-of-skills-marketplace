---
title: 'Plugin Categories and Tags'
description: 'Complete reference of all allowed plugin categories in the Tons of Skills marketplace, with descriptions, selection guidance, and tagging best practices for maximum discoverability.'
section: 'reference'
order: 3
keywords:
  - "categories"
  - "tags"
  - "marketplace"
  - "discovery"
  - "filtering"
  - "plugin categories"
  - "keywords"
officialLinks:
  - title: 'Claude Code Plugins Documentation'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Tons of Skills Marketplace'
    url: 'https://tonsofskills.com/explore'
relatedDocs:
  - 'guides/build-a-plugin'
  - 'guides/publish-to-marketplace'
  - 'reference/plugin-json-schema'
---

## Category authority

Each catalog entry has a category. The authored source is `.claude-plugin/marketplace.extended.json`; the published site catalog is a derived, filtered projection. Consult the current [Explore page](/explore) and catalog rather than treating an old table as a permanent enum.

At the reviewed repository snapshot, the published catalog uses these 19 slugs:

| Slug              | Typical focus                                 |
| ----------------- | --------------------------------------------- |
| `productivity`    | Authoring and everyday development workflows  |
| `security`        | Security review and hardening                 |
| `testing`         | Test authoring and analysis                   |
| `ai-agency`       | Agency-oriented workflows                     |
| `ai-ml`           | AI and machine-learning work                  |
| `mcp`             | Plugins with MCP runtime integrations         |
| `packages`        | Packaged tooling                              |
| `performance`     | Performance analysis and optimization         |
| `devops`          | Build, infrastructure, and delivery workflows |
| `api-development` | API authoring and integration                 |
| `crypto`          | Cryptocurrency and blockchain workflows       |
| `skill-enhancers` | Skill and agent development utilities         |
| `database`        | Data modeling and database workflows          |
| `business-tools`  | Business operations                           |
| `community`       | Community-source integrations                 |
| `examples`        | Explicit examples and demonstrations          |
| `saas-packs`      | Vendor-specific skill packs                   |
| `analytics`       | Analytics workflows                           |
| `design`          | Design-oriented workflows                     |

This is a dated description of the catalog, not a new permission to add categories or a replacement for its schema. The legacy plugin content collection in `marketplace/src/content.config.ts` still contains a different 17-value enum; it is not an accurate list of the current generated catalog's categories. Do not edit that schema merely to make this documentation pass.

## Choose a category

Choose the primary published artifact's function and follow existing catalog conventions. Use keywords and skill tags for secondary concerns. For example, an existing SaaS pack belongs to `saas-packs`; do not move it to an obsolete `cloud-infrastructure` slug because an old guide suggested that name.

Check the intended source path, current category, and comparable entries before submitting a category change. Category placement is not a quality grade, provider endorsement, or runtime security property.

## Keywords and tags

- `plugin.json` uses a `keywords` array for plugin metadata.
- `SKILL.md` uses a `tags` array required by the marketplace frontmatter contract.
- Search projections can derive additional terms from authored catalog and skill content.

These are JSON property fragments, not complete manifest files:

```json
"keywords": ["terraform", "configuration-review", "infrastructure"]
```

```json
"keywords": ["react", "typescript", "component-testing"]
```

Use specific technologies and operator tasks. Synonyms can help readers; a fixed keyword count or ranking order is not an enforced acceptance rule. Do not claim that a particular number of keywords guarantees traffic or featured placement.

The shipped website search is distinct from `ccpi search`, which currently prints a coming-soon message. No companion fuzzy ranking or cache implementation should be inferred from the website index.

## Catalog entry fragment

The following illustrates category placement. It is not a complete catalog entry or a plugin manifest:

```json
{
  "name": "example-review",
  "source": "./plugins/devops/example-review",
  "category": "devops"
}
```

Do not add `category` to a plugin manifest as a substitute for the catalog entry. The native manifest supports more than the historic eight-property list, but category ownership remains with the marketplace catalog.

After an approved authored catalog edit, run its canonical sync workflow:

```bash
pnpm run sync-marketplace
```

Other affected site, search, curated, or measurement projections may also need their declared producers. A successful sync is not proof that every projection or provider integration is current. Follow [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md) and the repository contribution guide.
