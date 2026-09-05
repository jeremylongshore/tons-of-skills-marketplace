# Tons of Skills

**A model-agnostic agent-skills platform.** The canonical layer is harness-free by construction; [Claude Code](https://code.claude.com/docs/en/) is currently the verified-native harness. Other harnesses remain engineering candidates until their native-path integration is verified; source research alone is never presented as public support.

[![Release](https://img.shields.io/badge/release-v4.33.0-green)](https://github.com/jeremylongshore/tons-of-skills-marketplace/releases/latest)
[![CLI](https://img.shields.io/badge/CLI-ccpi-blueviolet?logo=npm)](https://www.npmjs.com/package/@intentsolutionsio/ccpi)
[![Plugins](https://img.shields.io/badge/plugins-440-blue)](https://tonsofskills.com/explore)
[![Skills](https://img.shields.io/badge/skills-2940-green)](https://tonsofskills.com/skills)
[![GitHub Stars](https://img.shields.io/github/stars/jeremylongshore/tons-of-skills-marketplace?style=social)](https://github.com/jeremylongshore/tons-of-skills-marketplace)
[![skills.sh](https://skills.sh/b/jeremylongshore/tons-of-skills-marketplace)](https://skills.sh/jeremylongshore/tons-of-skills-marketplace)
[![Sponsor: Kobiton](https://img.shields.io/badge/Sponsor-kobiton.com-0487D9)](https://kobiton.com)
[![Buy me a monster](https://img.shields.io/badge/Buy%20me%20a-Monster-FFDD00?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jeremylongshore)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

> **Version semantics:** the release badge is this marketplace's display version. npm packages, including the `ccpi` CLI and publishable plugins, retain their own package versions; they are intentionally not expected to equal the display version. The version-surface checker governs the display surfaces without rewriting package semver.

## Install

Inside Claude Code, one command installs the whole marketplace:

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
```

<!-- The slug above is a FROZEN compatibility contract (blueprint § 6A.3): it is
     hardcoded in the CLI, the website Hero snippet, and hundreds of downstream
     READMEs, and GitHub's redirect to the canonical repo name is load-bearing.
     No redesign may "normalize" it to the canonical repo name. -->

Or use the CLI:

```bash
pnpm add -g @intentsolutionsio/ccpi
ccpi install devops-automation-pack
```

**[Browse the marketplace](https://tonsofskills.com)** · **[Explore plugins](https://tonsofskills.com/explore)** · **[Download bundles](https://tonsofskills.com/cowork)**

<!-- KILLER-SKILL:START — do not edit; run `node scripts/render-spotlight.mjs` -->

> **Killer Skill of the Week** — [no-ai-slop](https://github.com/petergyang/no-ai-slop) by [Peter Yang](https://github.com/petergyang)
>
> **Strip AI slop from any draft — named-pattern edits that keep the writer's real voice**
>
> no-ai-slop does two jobs and refuses to fake a third. In Edit mode it makes the minimum effective edit — cutting throat-clearing, weak verbs, and abstract nouns while deliberately preserving the writer's cadence, bluntness, humor, and honest admissions, so a rough draft still sounds like the same person afterward. In Detect mode it names each AI-slop pattern it finds, quotes the offending line, and gives the fix in a few words — and pointedly does NOT score the draft or guess whether an AI wrote it. That restraint is the whole point: AI detectors guess; named patterns are evidence the reader can check. MIT-licensed, single focused skill, actively maintained by Peter Yang.
>
> _"AI detectors guess. Named patterns are evidence the user can check."_ — Peter Yang
>
> Grade: A | Week of July 22, 2026 (W30) | [View on GitHub](https://github.com/petergyang/no-ai-slop)
>
> Previous picks: [tonone](https://github.com/tonone-ai/tonone), [mnemos](https://github.com/polyxmedia/mnemos), [databricks-pack](https://tonsofskills.com/plugins/databricks-pack), [kobiton-automate](https://tonsofskills.com/plugins/kobiton-automate), [code-cleanup](https://tonsofskills.com/plugins/code-cleanup), [web-analytics](https://tonsofskills.com/plugins/web-analytics), [token-optimizer](https://github.com/alexgreensh/token-optimizer), [executive-assistant-skills](https://tonsofskills.com/plugins/executive-assistant-skills), [skill-creator](https://tonsofskills.com/plugins/skill-creator), [cursor-pack](https://tonsofskills.com/plugins/cursor-pack), [crypto-portfolio-tracker](https://tonsofskills.com/plugins/crypto-portfolio-tracker). See all at [tonsofskills.com](https://tonsofskills.com).

<!-- KILLER-SKILL:END -->

<!-- SCALE:START — do not edit; run `node scripts/generate-readme-toc.mjs` -->

## Scale, labeled

Every number below names the cohort it counts and the command that reproduces it — an unlabeled count is how a corpus ends up with five contradictory answers to "how many skills."

| Count | Cohort                                 | Reproduce with                                                                                                          |
| ----: | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
|   440 | catalog plugins (catalog-entry cohort) | `node scripts/generate-readme-toc.mjs` over `marketplace.extended.json`                                                 |
| 2,940 | marketplace-visible skills (distinct)  | `node -e "import('./scripts/corpus-resolver.mjs').then(m=>console.log(m.resolveCorpus('marketplace-visible').length))"` |
|   352 | agent definitions in plugins           | `git ls-files 'plugins/**' \| grep '/agents/.*\.md'`                                                                    |
|    19 | plugin categories                      | `ls -d plugins/*/`                                                                                                      |

<!-- SCALE:END -->

<!-- NPM-STATS:START — do not edit; daily cron updates this -->

### 📦 Live npm Downloads

Across **393 published packages** in the [claude-code-plugins](https://www.npmjs.com/~jeremylongshore) namespace. Updated daily by GitHub Actions.

| Window        | All packages | Established (>30d) |
| ------------- | -----------: | -----------------: |
| Last 24 hours |          637 |                637 |
| Last 7 days   |        3,250 |              3,250 |
| Last 30 days  |       11,725 |             11,725 |

<sub>"Established" excludes packages first published within the last 30 days, so a bulk-publish event doesn't dominate the headline.</sub>

**Top 10 by last 30 days:**

| #   | Package                                                                                                                  | Last 30d |
| --- | ------------------------------------------------------------------------------------------------------------------------ | -------: |
| 1   | [`@intentsolutionsio/openrouter-pack`](https://www.npmjs.com/package/@intentsolutionsio/openrouter-pack)                 |    1,026 |
| 2   | [`@intentsolutionsio/groq-pack`](https://www.npmjs.com/package/@intentsolutionsio/groq-pack)                             |      734 |
| 3   | [`@intentsolutionsio/mistral-pack`](https://www.npmjs.com/package/@intentsolutionsio/mistral-pack)                       |      264 |
| 4   | [`@intentsolutionsio/databricks-pack`](https://www.npmjs.com/package/@intentsolutionsio/databricks-pack)                 |      216 |
| 5   | [`@intentsolutionsio/wallet-security-auditor`](https://www.npmjs.com/package/@intentsolutionsio/wallet-security-auditor) |      211 |
| 6   | [`@intentsolutionsio/shopify-pack`](https://www.npmjs.com/package/@intentsolutionsio/shopify-pack)                       |      155 |
| 7   | [`@intentsolutionsio/openbb-terminal`](https://www.npmjs.com/package/@intentsolutionsio/openbb-terminal)                 |      151 |
| 8   | [`@intentsolutionsio/ccpi`](https://www.npmjs.com/package/@intentsolutionsio/ccpi)                                       |      139 |
| 9   | [`@intentsolutionsio/penetration-tester`](https://www.npmjs.com/package/@intentsolutionsio/penetration-tester)           |      125 |
| 10  | [`@intentsolutionsio/langchain-py-pack`](https://www.npmjs.com/package/@intentsolutionsio/langchain-py-pack)             |      121 |

<sub>Last refreshed 2026-09-03T04:13:59.701Z.</sub>

<!-- NPM-STATS:END -->

## Ways in

Five real questions, five doors — each resolves to a live, generated surface, never a hand-maintained list:

- **By category** — the [table below](#browse-by-category), regenerated from the catalog on every sync.
- **By plugin** — [tonsofskills.com/explore](https://tonsofskills.com/explore), the full browsable catalog.
- **By skill** — [tonsofskills.com/skills](https://tonsofskills.com/skills), searchable across the whole corpus.
- **By job to be done** — [tonsofskills.com/cowork](https://tonsofskills.com/cowork), curated bundles as one-click downloads.
- **By certification tier** — the [Certification](#certification) section below, rendered from the live report.

<!-- AUTO-TOC:START — do not edit; run `node scripts/generate-readme-toc.mjs` -->

## Browse by category

The 19 categories below link into the live marketplace. Plugin counts are the catalog-entry cohort — regenerated from `marketplace.extended.json` by this generator; the catalog itself lives on [tonsofskills.com](https://tonsofskills.com), never in this file (§ 6A of the platform blueprint).

|     | Category                                                            | Plugins |
| --- | ------------------------------------------------------------------- | ------: |
| 🤖  | [AI & Machine Learning](https://tonsofskills.com/plugins#ai-ml)     |      37 |
| 🎭  | [AI Agents & Agency](https://tonsofskills.com/plugins#ai-agency)    |       9 |
| 🔌  | [API Development](https://tonsofskills.com/plugins#api-development) |      26 |
| 💼  | [Business Tools](https://tonsofskills.com/plugins#business-tools)   |       6 |
| 👥  | [Community](https://tonsofskills.com/plugins#community)             |      20 |
| ₿   | [Crypto & Web3](https://tonsofskills.com/plugins#crypto)            |      27 |
| 💾  | [Database](https://tonsofskills.com/plugins#database)               |      26 |
| 🎨  | [Design](https://tonsofskills.com/plugins#design)                   |       2 |
| 🔧  | [DevOps & Infrastructure](https://tonsofskills.com/plugins#devops)  |      36 |
| 📚  | [Examples & Templates](https://tonsofskills.com/plugins#examples)   |       5 |
| 🧩  | [MCP Servers](https://tonsofskills.com/plugins#mcp)                 |      17 |
| 📦  | [Packages](https://tonsofskills.com/plugins#packages)               |       5 |
| ⚡  | [Performance](https://tonsofskills.com/plugins#performance)         |      25 |
| ✅  | [Productivity](https://tonsofskills.com/plugins#productivity)       |      29 |
| 🎁  | [SaaS Skill Packs](https://tonsofskills.com/plugins#saas-packs)     |     104 |
| 🔐  | [Security](https://tonsofskills.com/plugins#security)               |      27 |
| ✨  | [Skill Enhancers](https://tonsofskills.com/plugins#skill-enhancers) |      10 |
| 🧪  | [Testing](https://tonsofskills.com/plugins#testing)                 |      28 |
| 📁  | [Analytics](https://tonsofskills.com/plugins#analytics)             |       1 |

<!-- AUTO-TOC:END -->

## What the classes mean

Four artifact classes live in this repository, distinguished on sight and never blurred — provenance is a truth requirement here, not a UX nicety:

| Class                   | What it is                                         | How the reader can tell                                                       |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Canonical skill**     | First-party, harness-free, the source of truth     | No `.source.json` in its plugin directory                                     |
| **Generated adapter**   | A thin, machine-produced harness projection        | Lives under a generated path with a "generated — do not edit" header          |
| **First-party package** | An Intent Solutions distribution (npm, cowork zip) | `@intentsolutionsio` scope, IS-authored license                               |
| **Upstream mirror**     | Somebody else's work, hosted mirror-by-default     | `.source.json` present — upstream author, license, and pinned commit recorded |

## Certification

<!-- CERTIFICATION:START — do not edit; run `node scripts/generate-readme-toc.mjs` -->

**Not yet certified.** The certification program (tiers T0–T4 with retained, hash-matched evidence) is a later epic of the platform blueprint; until its report exists, no artifact on this surface claims a tier. This line is rendered from the absence of `certification-report.json` — honestly, not cosmetically.

<!-- CERTIFICATION:END -->

## Contribute

Start with the contribution guide, then the intake and review standards every submission passes through:

- [Contribution requirements](.github/CONTRIBUTING.md) — including the AI-assistance disclosure expectation.
- [Skill submission intake standard](000-docs/700-DR-GUID-skill-submission-standard.md) — the tiered document matrix new plugins ship with.
- [External-PR review standard](000-docs/709-DR-GUID-reviewing-external-prs.md) — how maintainers triage and what gets a submission merged.

## Governance

- [STANDARDS.md](STANDARDS.md) — the public spec posture and the canonical-documents index (one owner per fact class).
- [The platform master blueprint](000-docs/727-AT-ARCH-master-modernization-blueprint.md) — CI gates, release, docs governance, and this README's own landing contract.
- [GOVERNANCE.md](GOVERNANCE.md) · [SECURITY.md](.github/SECURITY.md) · [LICENSE](LICENSE)

## Provenance

External plugins are hosted **mirror-by-default**: the contributor's repository stays the source of truth, every mirrored source is pinned in a content lockfile, and upstream credit — author, license, resolved commit — is recorded in the mirror itself. Improvements flow by upstreaming to the author's repository, never by silently editing the mirror. The full decision record is [the external-sync model](000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md).

## License

MIT for the repository scaffolding and first-party tooling; each plugin carries its own license in its manifest, and mirrored plugins keep their upstream license verbatim.
