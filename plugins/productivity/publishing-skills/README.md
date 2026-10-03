# publishing-skills

Four composable skills that turn an AI coding agent (Claude, Cursor, Codex, Gemini, Copilot, ...) into a long-tail SEO publishing pipeline. **Platform-agnostic** - works against Ghost, WordPress, Webflow, Sanity, Strapi, or any static-site generator (Hugo, Astro, Eleventy, Jekyll, Next-MDX).

Built for indie hackers, founders, content marketers, and dev-tool teams who want AI to draft blog posts that actually rank in search and get quoted by AI assistants - not paraphrased docs, not hallucinated benchmarks, not generic "ultimate guide" filler.

| Skill | What it does | Who it's for |
|---|---|---|
| **`blog-topic-research`** | Validates a topic has real, verifiable demand (People Also Ask, Reddit, Stack Overflow, GitHub issues, vendor forums, changelogs) before you spend tokens drafting. Every accepted topic carries citable evidence URLs, a problem summary, confirmed fixes, version context, and FAQ variants the writer can use directly. | Anyone tired of writing posts nobody searches for, and editorial pipelines that need an evidence-backed backlog. |
| **`seo-blog-writer`** | End-to-end pipeline for a single post: classify → research → outbound interlinks → draft clean HTML → scrub LLM tells → AI-SEO audit → optional glossary auto-link → publish. Adds FAQPage + BreadcrumbList + HowTo JSON-LD for AI-citation extractability. Pre-publish gate asserts H2-question shape, figure count (`max(1, words // 500)` for 800+ word posts), bullet discipline (3-9 items), and currency (`as of <YYYY>` qualifier on stale years). Ships a glossary auto-linker that wraps the first mention of each known technical term in an internal link with hover-tooltip metadata. **Platform-pluggable publish step** - ships with Ghost Admin API, WordPress REST, and static-site adapters; any other CMS is a ~20-line snippet. | Founders and marketers who want to ship one ranking post a day without paying a writer or a designer. |
| **`blog-figure-svg`** | Generates accessible SVG figures (flow, comparison bars, taxonomy, terminal mocks, 1600x840 OG feature cards) with a consistent palette, screen-reader metadata, and figcaption-ready output. Rasterizes to compressed PNG for upload to any CMS. | Anyone shipping more than 3 posts a month who doesn't want stock photos or Midjourney filler on every article. |
| **`blog-editorial-calendar`** | The orchestration layer over the other three. Keeps an evidence-backed backlog, picks the next topic so your corpus drifts toward the cluster + format mix you defined in `config.json`, schedules posts into a rolling daily cadence, reconciles the backlog against what's live on your CMS, and auto-refills via `blog-topic-research` when the queue runs dry. Drives whatever adapter `seo-blog-writer` is configured for. | Teams who want a hands-off cadence that publishes on schedule and stays balanced - not a pile of posts in one category. |

Together, they form a complete pipeline: **plan the cadence → research the topic → write the post → illustrate it → publish to your platform of choice**.

## Installing

### Via skills.sh (any agent runtime)

Installs all 4 skills into Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, and 50+ other runtimes at once:

```bash
npx skills add AutomateLab-tech/publishing-skills
```

### Via clawhub CLI (Claude / OpenClaw runtimes)

```bash
npm i -g clawhub
clawhub login
clawhub skill install blog-topic-research
clawhub skill install seo-blog-writer
clawhub skill install blog-figure-svg
clawhub skill install blog-editorial-calendar
```

### Manually

Each skill is a single `SKILL.md` file with YAML frontmatter. Drop it into your project's `.claude/skills/<name>/` directory (or your agent runtime's equivalent skill folder) and reload.

```bash
git clone https://github.com/AutomateLab-tech/publishing-skills.git
cp -r publishing-skills/skills/* .claude/skills/
```

## How they compose

```
+----------------------+      +--------------------------+      +-------------------+      +-------------------+
| blog-topic-research  | ---> | blog-editorial-calendar  | ---> |  seo-blog-writer  | <--- |  blog-figure-svg  |
| 'is the topic worth  |      | 'pick the next topic to  |      | 'write + publish' |      | 'illustrate the   |
|  writing about?'     | <--- |  balance the corpus +    |      |                   |      |   post'           |
+----------------------+ refill  schedule the cadence'   |      +-------------------+      +-------------------+
                              +--------------------------+               |
                                                                         v
                                              +----------------------------------+
                                              | platform adapter (one of):       |
                                              |   - Ghost Admin API              |
                                              |   - WordPress REST API           |
                                              |   - static-site file output      |
                                              |   - bring-your-own (~20 lines)   |
                                              +----------------------------------+
```

- **`blog-topic-research`** runs first - it answers "does anyone actually search this?" before you spend tokens drafting.
- **`blog-editorial-calendar`** picks the next topic to keep the corpus balanced against your target mix, schedules it into a rolling cadence, and calls `blog-topic-research` to refill when the backlog runs dry. (Optional - you can drive the writer by hand instead.)
- **`seo-blog-writer`** consumes the research-proof scaffold (or runs from scratch), drafts the HTML, validates the bundle, and ships it through a platform adapter.
- **`blog-figure-svg`** is invoked from within the writer's illustration step (or standalone) when a post needs charts, diagrams, or a feature card.

## Requirements

- **`blog-topic-research`** - no system dependencies beyond `WebSearch` / `WebFetch` in the agent runtime.
- **`seo-blog-writer`** - Python 3. Platform-specific extras:
  - **Ghost adapter**: `pip install requests pyjwt`; `GHOST_URL` + `GHOST_ADMIN_KEY` env vars.
  - **WordPress adapter**: `pip install requests`; `WP_URL` + `WP_USER` + `WP_APP_PASSWORD` env vars.
  - **Static-site adapter**: no credentials; just a target directory in your SSG repo.
- **`blog-figure-svg`** - Python 3, plus one SVG rasterizer (ImageMagick / `rsvg-convert` / Inkscape / `cairosvg`) and optionally `pngquant` for compression.

### Optional - ai-seo MCP (programmatic citation scoring)

`seo-blog-writer` Step 5 (AI-SEO audit) runs a programmatic citation-worthiness and schema pass when the [**ai-seo MCP**](https://github.com/AutomateLab-tech/ai-seo-mcp) (`@automatelab/ai-seo-mcp`) is connected. The skill checks at preflight and prompts you to install it if it's missing. Without it, Step 5 falls back to a manual reasoning pass covering the same ground.

```bash
npx -y @automatelab/ai-seo-mcp
```

Then register it in your agent's MCP config. See the [ai-seo-mcp README](https://github.com/AutomateLab-tech/ai-seo-mcp) for one-line configs for Claude Code, Cursor, and Cline.

## Maintenance scripts

The per-post audit inside `seo-blog-writer` catches structural problems before publish. For corpus-wide drift - characters or banlist phrases that crept back across many posts - run [`scripts/audit-corpus.py`](scripts/audit-corpus.py) against your content directory:

```bash
python3 scripts/audit-corpus.py path/to/your/content/
python3 scripts/audit-corpus.py content/posts/ --extra "synergy,best-in-class"
```

Exits `0` clean / `1` on hits - composes with CI for a pre-deploy drift gate.

## Glossary auto-link

`seo-blog-writer` Step 7i (optional) pipes the draft HTML through [`scripts/inject-glossary-links.py`](scripts/inject-glossary-links.py), which wraps the first mention of each known technical term in an internal link to its definition page and writes a `data-definition` attribute for hover tooltips. Schema and starter file in [`skills/seo-blog-writer/references/glossary-schema.md`](skills/seo-blog-writer/references/glossary-schema.md); a self-contained tooltip-rendering snippet for your site `<head>` is at [`skills/seo-blog-writer/references/decorate.js`](skills/seo-blog-writer/references/decorate.js).

```bash
python3 scripts/inject-glossary-links.py post.html \
    --glossary glossary.json --base-url /glossary/ > post.linked.html
```

The injector handles the awkward edges automatically: first-occurrence-only per post, longest-alias wins, skips headings / code / tables / blockquotes / TL;DR, and rejects matches embedded in identifier-like compounds (`user-agent` won't match `agent`, `@scope/ai-seo-mcp` won't match `mcp`). You bring the glossary file and the definition pages; the injector handles the linking.

## Why platform-agnostic?

The writing pipeline (research, classify, draft, scrub, AI-SEO audit, JSON-LD generation) is the hard part. The publish step is glue. Coupling the two means you're locked into one CMS forever - and if you move from Ghost to WordPress, you rewrite the whole skill.

This repo separates them. The writer produces a stable bundle (`<slug>.draft.html`, `<slug>.schema.html`, `<slug>.metadata.json`) and the adapter ships it. Add Webflow, Sanity, or Strapi in an afternoon without touching the pipeline.

## License

[MIT-0](LICENSE) - public domain equivalent. Use, modify, redistribute without attribution.
