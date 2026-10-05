---
name: seo-blog-writer
description: "Turn a single long-tail query into a publish-ready blog post that ranks in search and gets quoted by AI assistants. Runs the full pipeline: classify the topic, research it against real sources, draft clean HTML, scrub LLM-tell vocabulary and typography, audit for AI-SEO (TL;DR block, query-phrased H2s, FAQ section, FAQPage + BreadcrumbList + HowTo JSON-LD), then publish through a platform adapter (Ghost Admin API, WordPress REST, or static-site file output). Platform-agnostic core; swap the publish step without rewriting the writing pipeline. Built for indie hackers, founders, and content marketers who want AI to draft posts that are actually citable - not paraphrased docs, not hallucinated benchmarks. Trigger when the user says: 'write a blog post on X', 'draft an article about X', 'publish a post on X to Ghost / WordPress / the static site', or any request to ship editorial content for a long-tail query."
version: 2.2.0
emoji: "✍️"
homepage: https://github.com/AutomateLab-tech/publishing-skills
allowed-tools: WebSearch, WebFetch, Bash(python3:*), Read, Write
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
compatibility: Designed for Claude Code
tags: [seo, content, publishing, blogging, ghost]
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# seo-blog-writer

End-to-end pipeline for shipping a single long-tail blog post: **topic -> research -> draft -> scrub -> AI-SEO audit -> publish**. Designed for SEO and AI-citation extractability (FAQ blocks, BreadcrumbList + FAQPage + HowTo schema, query-phrased headings).

The **writing pipeline is platform-agnostic** — it produces a publish-ready bundle (clean HTML, slug, meta, JSON-LD blocks, feature-image alt). The **publish step is pluggable**: out-of-the-box adapters for Ghost Admin API, WordPress REST, and static-site file output. Adding another CMS (Webflow, Sanity, Strapi, Contentful, Hugo, Astro) is a matter of writing a 20-line POST snippet.

The skill takes **one required argument**: the topic. Optional flags control the publish target and state.

```
/seo-blog-writer <topic>
/seo-blog-writer <topic> --target ghost                     # publish via Ghost adapter
/seo-blog-writer <topic> --target wordpress                 # publish via WordPress REST
/seo-blog-writer <topic> --target static --out posts/       # write files into a static-site repo
/seo-blog-writer <topic> --target ghost --publish           # actually publish (default: draft)
/seo-blog-writer <topic> --target ghost --publish-at <ISO>  # schedule for future publish
/seo-blog-writer <topic> --angle "<angle>"                  # narrow the angle
```

Default state is **draft** — the post lands in the platform's editor for human review before going live, unless `--publish` or `--publish-at` is passed. `--publish-at` accepts an ISO 8601 UTC timestamp (e.g. `2026-05-10T07:42:00Z`) and is mutually exclusive with `--publish`.

Default `--target` is `static` — writes a self-contained HTML file + a `metadata.json` next to it so you can wire any platform yourself.

---

## Before you start — preflight

The platform-agnostic checks:

```bash
# 1. Python available (rasterizer, scrubber, schema builder)
command -v python3

# 2. Working directory writable
mkdir -p tmp/blog-drafts && touch tmp/blog-drafts/.touch && rm tmp/blog-drafts/.touch
```

**3. (Optional) ai-seo MCP — check before continuing**

Check whether the current agent session has access to a tool named `audit_page` from the ai-seo-mcp server (`@automatelab/ai-seo-mcp`). That MCP provides a programmatic citation-worthiness and schema score that Step 5 uses automatically when available.

- **If the MCP is connected:** nothing to do — Step 5 will call `audit_page` automatically.
- **If the MCP is not connected:** ask the user:

  > "The **ai-seo MCP** (`@automatelab/ai-seo-mcp`) is not connected. Step 5 can run a programmatic citation-worthiness and schema score on your draft in addition to the manual audit. To install it:
  > ```
  > npx -y @automatelab/ai-seo-mcp
  > ```
  > then register it in your MCP config. See the [ai-seo-mcp README](https://github.com/AutomateLab-tech/ai-seo-mcp) for one-line configs for Claude Code, Cursor, and Cline. Type **skip** to continue with the manual-only audit."

  Wait for the user's response before continuing to Step 0. Any response other than a config/install action counts as skip — proceed without the MCP.

Platform-specific credential checks live in the per-adapter sections at the end of this skill. The writing pipeline (Steps 0-7) runs without any platform credentials — credentials are only needed at Step 8.

---

## Step 0 — Parse and classify the topic

The topic is the one thing the skill cannot invent. It must arrive as an argument.

| Shape | Example | Treatment |
|---|---|---|
| **Long-tail how-to** | `"how to fix n8n HTTP Request 401 error"` | Ideal. Format = troubleshooting (template 1). |
| **Integration walk-through** | `"how to connect Airtable to Slack with Zapier"` | Format = integration (template 2). |
| **Workflow tutorial** | `"automate invoice processing with Make"` | Format = workflow tutorial (template 3). |
| **Comparison** | `"Zapier vs Make vs n8n"` | Format = comparison (template 4). |
| **Definition / explainer** | `"what is an AI agent"` | Format = explainer (template 5). |
| **Use case / outcome** | `"build a daily Slack digest from RSS with n8n"` | Format = use-case (template 6). |
| **Listicle / roundup** | `"12 best n8n templates for marketing teams"` | Format = listicle (template 7). |
| **Migration guide** | `"migrate from Zapier to n8n"` | Format = migration (template 8). |
| **Release recap** | `"what's new in n8n 1.80"` | Format = release-recap (template 9). |
| **Too vague** | `"AI"`, `"automation"` | **Stop.** Ask the user to narrow it. Suggest 2-3 candidate long-tail variants. |

If `--angle` was passed, append it to the topic. The classification picks the structural template used in Step 3.

---

## Step 1 — Research

The piece must be specific. Real version numbers, real error messages, real screenshots — not generic "best practices."

### 1a. Identify the search intent

What does someone typing this query want? One sentence — the implicit desire behind the words.

- `"how to fix n8n HTTP 401"` -> wants the exact change to make in the UI to stop the error
- `"Zapier vs Make"` -> wants a quick decision, then a longer breakdown
- `"what is an AI agent"` -> wants a one-paragraph explanation, then how it differs from a workflow

If you can't write one sentence describing the intent, the topic is too vague — go back to Step 0.

### 1b. Seed search and SERP teardown

```
WebSearch("<topic>")
WebSearch("<topic> <current-year>")  # force a fresh lens
```

Extract three structured signals from the page-1 results:

1. **Word count distribution** — eyeball the top 5 results' length. Target 1.1–1.3x the median, not the longest. If the median is 600 words, don't write 1500 — that's padding.
2. **People Also Ask boxes** — Google surfaces 4-8 PAA questions for most queries. These are free FAQ content. Capture verbatim into the FAQ-variant list.
3. **Currently-winning featured snippet** — if there is one, note its format (paragraph, list, table). Write the lead paragraph in that exact shape; that's how you challenge for the snippet.

Goal: write something **more specific or more current** than the existing top results, not a paraphrase.

### 1c. Deep fetch

Pick **2-4 URLs** from the SERP. Prioritize:

- **Vendor docs** — primary sources for the tool being discussed.
- **GitHub issues / changelogs** — for "fix X error" topics, the actual issue thread is gold.
- **Reddit / community forums** — for confirming a workaround actually works in the wild.
- **Existing top-ranked posts** — to see the bar you're clearing.

```
WebFetch(url, "Return the full article body as clean prose. Include code snippets,
error messages, and screenshot references verbatim. Do NOT summarize.")
```

Skip SEO-farm rewrites and listicles with no specifics.

### 1d. Five-question gate before drafting

Before writing, you must be able to answer all five.

1. **What is the exact query intent?** (one sentence from 1a)
2. **What is the direct answer?** (one to two sentences — the lead paragraph in compressed form)
3. **What's the canonical primary source?** (vendor doc, GitHub issue, official changelog — at least one URL)
4. **What's the gotcha most existing posts miss?** (the specific detail that makes this post worth writing). **Hard rule:** if the honest answer is "nothing, I'm summarizing the docs," **abort and tell the user**. A doc paraphrase will rank below the actual docs.
5. **What 3-6 follow-on questions belong in the FAQ?** (long-tail variations of the main query, ideally lifted from the PAA boxes captured in 1b)

If any answer is `?`, keep researching or ask the user for a specific source.

### 1e. Save research artifacts

```bash
mkdir -p tmp/blog-drafts
# <slug> = kebab-case of the topic, e.g. n8n-http-401-fix
```

Files (gitignored):
- `tmp/blog-drafts/<slug>.research.md` — 5-question answers, source list, key quotes
- `tmp/blog-drafts/<slug>.interlinks.json` — written in Step 1f (outbound interlink targets)
- `tmp/blog-drafts/<slug>.draft.html` — written in Step 3
- `tmp/blog-drafts/<slug>.schema.html` — written in Step 7b (JSON-LD `<script>` blocks)
- `tmp/blog-drafts/<slug>.metadata.json` — written in Step 7f (title, slug, tags, meta, etc.)
- `tmp/blog-drafts/<slug>.refresh.json` — written in Step 7h (versions, prices, years cited; for future refresh runs)

### 1f. Outbound interlinks (recommended; required for >800-word posts)

Pick **2-3 prior posts** on the same site whose topic genuinely overlaps with this one. Bake the links into the draft in Step 3 on topical noun phrases (not "see this post"). Internal links don't carry `nofollow`; outbound links to other domains do (see Step 3 link policy).

Where the candidate list comes from depends on the platform:

- **Ghost** — `GET /ghost/api/admin/posts/?limit=all&filter=status:published&fields=id,slug,title,published_at,custom_excerpt&order=published_at%20desc` (same `GHOST_ADMIN_KEY` Step 8 uses).
- **WordPress** — `GET /wp-json/wp/v2/posts?per_page=100&_fields=id,slug,title,date,excerpt&orderby=date&order=desc` (same `WP_APP_PASSWORD` Step 8 uses).
- **Static-site** — read the SSG's content directory directly (`ls content/posts/*.md`) or maintain a hand-curated `posts-inventory.json` in the repo.

Save the chosen targets so Step 3 can splice them in and Step 7g can verify they survived the audit:

```bash
cat > tmp/blog-drafts/<slug>.interlinks.json <<'EOF'
{
  "outbound": [
    {"slug": "<prior-slug-1>", "url": "https://<your-host>/<prior-slug-1>/", "anchor_phrase": "<noun phrase>"},
    {"slug": "<prior-slug-2>", "url": "https://<your-host>/<prior-slug-2>/", "anchor_phrase": "<noun phrase>"}
  ]
}
EOF
```

Step 7g verifies that every `outbound[].url` appears at least once as an `href` in the final draft. If you decided mid-draft to drop a link, edit the file before re-running 7g. Posts under 800 words can skip this step; long posts ship with outbound links or they look orphaned to both the reader and the site graph.

> **Note on inbound links.** Editing prior posts after publish to add a forward link back to the new one (inbound splicing) is a separate concern that depends on having write access to historical posts and a state file to keep the operation idempotent. This skill does not handle it — too platform-specific to generalize. If you want it, run it as a cron against your platform's API after publish.

---

## Step 2 — Pick the format and length band

Each query type maps to a structural template:

| Format | Length band |
|---|---|
| `how-to-fix` (troubleshooting) | 600-1200 |
| `how-to-connect` (integration) | 1000-1500 |
| `how-to-automate` (workflow) | 1000-1500 |
| `x-vs-y` (comparison) | 1200-1500 |
| `what-is` (explainer) | 600-1200 |
| `use-case` (outcome) | 1000-1500 |
| `listicle` (roundup) | 1500-2500 |
| `migration` | 1200-1800 |
| `release-recap` | 800-1400 |

**Hard length range: 600-1500 words for most formats.** Word count = prose inside `<p>` tags + heading text. Excludes code blocks, table cells, figcaptions.

Use the SERP word-count signal from Step 1b to pick a target inside the band (1.1–1.3x the SERP median). Under the floor means the answer is genuinely too thin — add an FAQ expansion, a "common errors" section, or a "how to verify" section. Over the ceiling means the post is sprawling — cut the weakest section. **Never pad to hit a floor.** Google rewards directness; AI Overviews preferentially extract from concise answers.

---

## Step 3 — Draft the post

Write directly in HTML. Allowed tags:

`<p>`, `<h2>`, `<h3>`, `<a>`, `<strong>`, `<em>`, `<code>`, `<pre>`, `<blockquote>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`, `<figure>`, `<figcaption>`, `<img>`.

No inline styles. No `<div>`, no `<span>`, no `<br>`. No H1 (most platforms emit the post title as H1; emitting your own creates a duplicate).

### Link policy — internal vs. outbound, follow vs. nofollow

| Destination | `rel` attribute |
|---|---|
| Your own blog (other posts on the same host) | none — internal, follow |
| Anything else (vendor docs, GitHub, news, social, all third-party) | `rel="nofollow noopener"` |

Do not use `target="_blank"` — most blog themes handle outbound link UX themselves. Set `CANONICAL_HOST=blog.example.com` in the shell before running the audit in Step 5 so the validator knows which links are internal.

### Voice checks while drafting

- **Open with a TL;DR block.** First child of the body is `<p><strong>TL;DR:</strong> ...</p>` — a single sentence, 8-40 words, that answers the query directly with specific nouns (tool name, version, error code, command). LLM citation hook. Asserted in Step 7g.
- **Lead paragraph follows the TL;DR** with one or two sentences of context (when this hits, who it bites, why other guides miss the cause). It is not a re-statement of the answer.
- **H2 as a question or operational label.** Every `<h2>` either ends with `?` (e.g. `## How do you fix the "ECONNREFUSED" error in n8n?`) **or** is one of the allowlist: `Install`, `Prerequisites`, `Links`, `TL;DR`, `FAQ`, `Frequently asked questions`, `Summary`, `References`, `Further reading`, `Sources`, `Bottom line`. `<h3>` follows the same convention. Question-shaped H2s are how Google AI Overviews and Perplexity slice the page into citable chunks. Asserted in Step 7g.
- **Specific over general.** Real version numbers, real error messages, real prices. No "modern", "powerful", "robust", "seamless."
- **Impersonal voice.** "Here's the fix." Not "we found that" and not "I tried this."
- **Forensic linking.** Every external claim links on the noun phrase that names the source. Every external link has `rel="nofollow noopener"`.
- **Bullet discipline.** No `<ul>` or `<ol>` under 3 items — convert to prose. No list over 9 items without a sub-grouping (split into 2 lists under separate H3s, or fold into a `<table>`). Every `<li>` carries a data point, recommendation, or argument; each ends with a period; parallel grammar across items. Asserted in Step 7g.
- **Structured-spec labels for diagnostic posts.** Troubleshooting roundups, "N reasons X is broken", and cause/effect listicles repeat a labeled triple inside every item — the default is `**Symptom:**` / `**Diagnostic:**` / `**Fix:**` (one paragraph each). The bold-keyword-colon form is allowed here and only here. For migration posts use `**Before:**` / `**After:**` / `**Migration step:**`; for comparison posts use `**When to pick:**` / `**Avoid if:**` / `**Cost:**`. This is what gets AI assistants to extract per-item structured citations instead of mashing the whole list into one quote.
- **Recap checklist before the FAQ for enumerative posts.** Posts with **three or more enumerated items** close with an `<ol>` of one-sentence imperative steps under a question-shaped H2 (e.g. `<h2>How do you test all seven blockers in 20 minutes?</h2>`). One step per body item, no sub-bullets. Skip for posts under 800 words or fewer than three items. The recap is what gets quoted as the AI-answer "summary" — without it the model has to invent one.
- **Currency where it matters.** Any version number, year, or price in a load-bearing claim either is current (cross-check against vendor docs in Step 5) or carries `as of <YYYY-MM>` next to it so a reader knows the time-context. Step 7g flags any year > 1 year stale without an explicit `as of` qualifier.
- **End with a `<h2>FAQ</h2>` block** — 3-6 H3 questions, each with a 1-3 sentence answer.
- **Self-check:** *Does the TL;DR stand alone as a quotable answer? Does the lead paragraph add context the TL;DR doesn't have? If either fails, rewrite.*

Save to `tmp/blog-drafts/<slug>.draft.html`.

---

## Step 4 — Scrub LLM tells

Run **before** the AI-SEO audit. The audit may add vocabulary the scrub would then need to remove; do the order this way.

### 4a. Character scrub (automatic)

Replace common LLM-tell characters with ASCII equivalents:

```bash
python3 -c "
import sys, pathlib
p = pathlib.Path(sys.argv[1])
t = p.read_text(encoding='utf-8')
# em-dash/en-dash -> hyphen
t = t.replace('—', '-').replace('–', '-')
# smart quotes -> straight quotes
t = t.replace('“', '\"').replace('”', '\"')
t = t.replace('‘', \"'\").replace('’', \"'\")
# ellipsis -> three dots
t = t.replace('…', '...')
# zero-width / non-breaking space -> regular space or empty
t = t.replace('​', '').replace(' ', ' ')
p.write_text(t, encoding='utf-8')
print('scrubbed', sys.argv[1])
" tmp/blog-drafts/<slug>.draft.html
```

### 4b. Prose-level tells (manual)

Search the draft for these banned phrases and rewrite:

- "delve into", "delving"
- "in today's fast-paced world", "in the ever-evolving"
- "robust", "seamless", "powerful", "cutting-edge"
- "harness the power of"
- "it's worth noting that", "it's important to note"
- "navigate the landscape", "navigating the complexities"
- "unlock the potential of", "unleash"
- "game-changer", "revolutionize"
- "leverage" (as a verb)

Rewrite every hit — do not just delete; the surrounding sentence is usually also lazy.

---

## Step 5 — AI-SEO audit

### Programmatic pass (if ai-seo-mcp is connected)

If the ai-seo-mcp server is connected, call `audit_page` on the draft before running the manual passes:

```
audit_page(url_or_path="tmp/blog-drafts/<slug>.draft.html")
```

Feed the score and any flagged issues into the manual passes below as additional signal. The MCP output is advisory — the six manual passes are still required gates.

### Manual passes

Run the audit against the draft, checking each pass:

1. **Structure pass** — does the lead answer the query in the first paragraph; do H2s match query phrasing; is each section self-contained.
2. **Authority pass** — at least one cited primary source (vendor doc / GitHub issue / changelog) on a relevant noun phrase.
3. **Freshness pass** — current year referenced where it makes sense; version numbers are current. **Currency check, mandatory:** any version number cited must still be the current (or one of the still-supported) versions per vendor docs. A 6-month-old "introduced in CrewAI 0.114" may now read as historical context, not present-tense scope. If the version has rolled forward, either update the framing or add `as of <YYYY-MM>` next to the claim so the reader knows the time-context. Vendors ship fast; stale qualifiers tank citation quality.
4. **Schema readiness** — most platforms emit Article + Person + Organization schema automatically. Step 7b adds FAQPage + BreadcrumbList (always) and HowTo (procedural posts only). Confirm the FAQ block has H3 question + paragraph answer pairs the 7b extractor can parse.
5. **Long-tail coverage** — does the FAQ block capture 3-6 long-tail variants of the main query.
6. **Platform-fact pass** — any claim about a specific shell, OS, language runtime, or tool is a verifiable fact, not a vibe. Verify the load-bearing ones against vendor docs before publish.

Apply recommendations **in place** in the draft, then re-run Step 4a (the audit may have re-introduced smart quotes).

### Non-negotiable invariants

- **Body is within the format's length band** (Step 2). Count via the snippet below.
- **TL;DR is the first `<p>` of the body**, opens with `<strong>TL;DR:</strong>`, 8-40 words, single sentence.
- **Lead paragraph (second `<p>`) answers the query** in 1-2 sentences.
- **At least one primary-source link** with `rel="nofollow noopener"`.
- **FAQ block at the end** with 3-6 H3/p pairs.
- **Every external `<a>` carries `rel="nofollow noopener"`.**
- **Zero U+2014, U+201C, U+201D, U+2018, U+2019, U+2026, U+00A0, U+200B.**

```bash
# Word count (excludes code blocks, table cells, figcaptions)
python3 -c "
import sys, re, pathlib
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
no_code = re.sub(r'<pre\b[^>]*>.*?</pre>', ' ', html, flags=re.S|re.I)
no_table = re.sub(r'<table\b[^>]*>.*?</table>', ' ', no_code, flags=re.S|re.I)
no_fig = re.sub(r'<figure\b[^>]*>.*?</figure>', ' ', no_table, flags=re.S|re.I)
text = re.sub(r'<[^>]+>', ' ', no_fig)
words = re.findall(r\"[A-Za-z0-9][A-Za-z0-9'-]*\", text)
print(f'{len(words)} words')
" tmp/blog-drafts/<slug>.draft.html
```

```bash
# nofollow coverage on external links — expected: 0 violations.
# Set CANONICAL_HOST to your blog's hostname (e.g. blog.example.com).
python3 -c "
import re, sys, pathlib, os
from urllib.parse import urlparse
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
host = os.environ.get('CANONICAL_HOST', '')
internal = {host, f'www.{host}' if host else ''}
internal = {h for h in internal if h}
violations = []
for m in re.finditer(r'<a\b([^>]*)>', html, flags=re.I):
    attrs = m.group(1)
    href = re.search(r'href=\"([^\"]+)\"', attrs, flags=re.I)
    if not href: continue
    h = urlparse(href.group(1)).hostname or ''
    if h and h not in internal:
        rel = re.search(r'rel=\"([^\"]+)\"', attrs, flags=re.I)
        rel_val = (rel.group(1) if rel else '').lower()
        if 'nofollow' not in rel_val:
            violations.append(href.group(1))
for v in violations: print('MISSING nofollow:', v)
print(f'{len(violations)} violation(s)')
" tmp/blog-drafts/<slug>.draft.html
```

---

## Step 6 — Illustrate the post (optional)

Figures are not required for short posts, but **mandatory for posts >=800 words**. The rule: `figures >= max(1, words // 500)` whenever body word count >=800. An 800-word post -> 1-2 figures. A 1200-word post -> 2-3. A 1500-word post -> 3. Step 7g asserts this. Past failure mode this rule is fixing: long troubleshooting posts (1000+ words) shipped with zero figures because the agent declared the topic "too definitional" — the assert refuses those bundles.

For figure generation (SVG flow diagrams, comparison charts, taxonomy diagrams, OG feature cards) see the companion `blog-figure-svg` skill — it generates accessible SVGs with consistent styling and rasterizes them for upload. The skill is CMS-agnostic; it produces PNG files that any adapter in Step 8 can upload.

For screenshots, capture from the live tool (Playwright, real session, etc.), crop to the relevant region, redact tokens or personal data. Save as `tmp/blog-drafts/<slug>-<N>-<short-name>.png`.

### Splice figure tags into the draft

```html
<figure>
  <img src="<image-url-or-path>" alt="<full description with all numbers and labels>" loading="lazy">
  <figcaption>One sentence restating the takeaway in plain English (15-30 words).</figcaption>
</figure>
```

**Caption rules:**
- Required on every figure. Step 7g asserts this.
- 15-30 words, restating the takeaway (not "Figure showing X" — say what the reader should conclude).
- Allowed tags inside `<figcaption>`: `<a>` (with `rel="nofollow noopener"` for external), `<em>`.

The `<img src>` value depends on the publish target:
- **Ghost / WordPress**: upload first (per-adapter snippet in Step 8), then splice the returned CDN URL.
- **Static-site**: copy the PNG into the site's image directory and use a relative path.

---

## Step 7 — Build the publish bundle

The bundle is three files that every adapter consumes:

| File | Contents |
|---|---|
| `<slug>.draft.html` | Body HTML (already produced in Step 3, scrubbed and audited). |
| `<slug>.schema.html` | JSON-LD `<script>` blocks (FAQPage + BreadcrumbList + optional HowTo). |
| `<slug>.metadata.json` | Title, slug, tags, author, meta title/description, excerpt, feature image, status, publish-at. |

### 7a. Headline and slug rules

**Headline** (becomes the SEO title unless `meta_title` overrides):

- Under **70 chars**.
- Match the search query closely.
- Lead with the verb / noun the searcher typed.

**Slug** (URL fragment):

- **<=60 chars.**
- **Strip stop words** — drop `the`, `a`, `an`, `for`, `with`, `in`, `to`, `of`, `on`, `and`, `or`, `is`, `are`.
- **No version numbers** — `n8n-1-45-2-fix` goes stale; `n8n-http-401-fix` does not.
- **Match the primary keyword**, not the full headline.

```python
import re
STOP = {'the','a','an','for','with','in','to','of','on','and','or','is','are'}
slug = "-".join(t for t in re.findall(r'[a-z0-9]+', topic.lower()) if t not in STOP)
slug = slug[:60].rstrip('-')
```

### 7b. Build JSON-LD schema (FAQPage + BreadcrumbList + HowTo)

Most platforms emit Article/BlogPosting/Person/Organization schema by default. This skill **adds three more** for AI-citation extractability:

- **FAQPage** — mandatory. Every post has a FAQ block (Step 3 rule).
- **BreadcrumbList** — mandatory. `Home > <Primary Tag> > <Post Title>`.
- **HowTo** — only for procedural formats with >=3 step-shaped H2s.

**Critical gotcha for rich-text editors:** several CMSes (Ghost's Lexical, WordPress's block editor under some configurations) convert the source HTML into a structured format on save and silently drop `<script>` nodes — so JSON-LD inlined in the draft body **disappears in the live page** even though it was present in the POST payload.

The blocks must go in a platform-specific "head injection" slot:

| Platform | Where the schema goes |
|---|---|
| Ghost | `codeinjection_head` field on the post payload |
| WordPress | `<head>` via a theme hook, or the Yoast / Rank Math "schema" panel |
| Static-site | written directly into the rendered HTML's `<head>` by your build step |

**Never append `<script type="application/ld+json">` to the body HTML.** Build it once via this step into `<slug>.schema.html`; the platform adapter in Step 8 reads that file and writes it into the correct field.

```bash
# Args: slug, headline, format, primary-tag-name, canonical-base-url
python3 scripts/seo-blog-writer/build-schema.py "<slug>" "<headline>" "<format>" "<primary-tag>" "<canonical-base-url>"
```

### 7c. Feature image (recommended)

A feature image is shown at the top of the post and as the OG image in social shares. Strongly recommended for any post you intend to promote.

Options:
- **Upload a custom image** — per-adapter upload snippets are in Step 8.
- **Generate a templated title card** — see the companion `blog-figure-svg` skill (`feature` variant) for a 1600x840 OG card with a clean headline + brand mark.
- **Skip it** — the post will render without a hero image; social previews fall back to the site default.

Whatever path you pick, capture the URL (or filesystem path for static targets) plus a one-line alt-text in `metadata.json`. **Cap alt text at 191 chars** — Ghost silently truncates at varchar(191), and the limit is a reasonable upper bound for any platform.

### 7d. Author byline

Every post needs an author. The shape varies by platform; capture it generically in metadata:

```json
"author": {"slug": "<author-slug>", "name": "<display name>"}
```

The adapter in Step 8 translates this to the platform's API shape:
- **Ghost** — `authors: [{"slug": "<slug>"}]`. Slug must match an existing user; otherwise Ghost silently substitutes the integration owner.
- **WordPress** — `author: <user-id>` (numeric). Resolve slug -> id once and cache.
- **Static-site** — written into the front-matter `author:` field of the generated file.

### 7e. Tags

Use a flat list of tag name strings:

```json
"tags": ["How To", "n8n"]
```

**Pick 1-3 tags per post.** The first tag is the **primary tag** — it becomes the breadcrumb segment in 7b and is used by most themes for category labelling.

Maintain a small canonical tag list in your project (don't let the AI invent new tags every post — duplicates dilute SEO). Common patterns: format tags (`How To`, `Tutorial`, `Comparison`, `What Is`) + topic tags (your tool/category names).

### 7f. Build the metadata bundle

Write the per-post fields into `tmp/blog-drafts/<slug>.params.json`, then run the
builder. It validates required fields and maps the status flags to every adapter.

`params.json` shape:

```json
{
  "title": "<headline>",
  "tags": ["How To", "n8n"],
  "author": {"slug": "<author-slug>", "name": "<author display name>"},
  "meta_title": "<SEO title under 60 chars>",
  "meta_description": "<SEO description, 140-160 chars>",
  "custom_excerpt": "<dek shown on index page>",
  "feature_image": "",
  "feature_image_alt": "",
  "feature_image_caption": "",
  "publish": false,
  "publish_at": null
}
```

First tag is the primary tag (passed to 7b for the breadcrumb). Set `publish: true`
for `--publish`; `publish_at` (ISO-UTC) for `--publish-at` (mutually exclusive).

```bash
python3 scripts/seo-blog-writer/build-metadata.py "<slug>"
```

### 7g. Pre-publish bundle validation

Before invoking the platform adapter, all of these must hold:

```bash
python3 scripts/seo-blog-writer/validate-bundle.py "<slug>"
```

If any assert fires, fix and re-build before Step 8.

### 7h. Refresh metadata snapshot

Save a small JSON snapshot of the post's facts so a future refresh pass can identify staleness without re-reading the prose. Cheap to write now; expensive to backfill at 500 posts.

```bash
python3 scripts/seo-blog-writer/refresh-meta.py "<slug>" "<format>"
```

When a topic refresh comes due (typically every 6-12 months for high-traffic posts), the refresh skill (future / your-own) diffs the snapshot's `versions_cited` against current vendor docs. Versions that have rolled forward by a major release are flagged for rewrite; everything else is left alone.

### 7i. Glossary auto-link (optional)

If you maintain a glossary of technical terms with definition pages on your site, pipe the draft HTML through `scripts/inject-glossary-links.py` to turn the first mention of each known term into an internal link to its definition page. Each link also carries a `data-definition` attribute that the bundled `references/decorate.js` snippet renders as a hover tooltip on the published page.

**Skip this step if** you don't have a `glossary.json` file yet — there's no default. See [references/glossary-schema.md](references/glossary-schema.md) for the file shape and a starter example.

```bash
python3 scripts/inject-glossary-links.py \
    tmp/blog-drafts/<slug>.draft.html \
    --glossary path/to/glossary.json \
    --base-url /glossary/ \
    --max-links 6 \
    > tmp/blog-drafts/<slug>.draft.linked.html

mv tmp/blog-drafts/<slug>.draft.linked.html tmp/blog-drafts/<slug>.draft.html
```

The injector:

- Links **first occurrence only** per term per post (Wikipedia rule).
- Caps at `--max-links` (default 6), priority-sorted from the glossary.
- Skips headings, code/pre, tables, blockquotes, asides, existing links, and the TL;DR paragraph.
- Rejects matches embedded in identifier-like compounds (`user-agent` won't match `agent`, `@scope/ai-seo-mcp` won't match `mcp`).
- Writes a `data-definition` attribute on each link for the tooltip.

Run order: **after Step 7g validates the draft** so the validator's structural asserts run on clean HTML; **before Step 8 publishes** so the linked HTML is what ships. Glossary links count as internal navigation, not outbound — the Step 7g outbound-survival assert ignores them.

To enable the hover tooltip on the live site, copy `skills/seo-blog-writer/references/decorate.js` into your theme bundle (or paste it inline in a `<script>` tag in your site `<head>`) once. It's self-contained, ~1 KB, no dependencies, and skips itself on `/glossary/*` pages.

---

## Step 8 — Publish via the platform adapter

Pick one adapter per run. Each adapter reads the same bundle (`<slug>.draft.html`, `<slug>.schema.html`, `<slug>.metadata.json`) and writes the post to its target platform.

---

### Adapter A — Ghost (Admin API)

The Ghost adapter uses the Admin API over HTTPS. No Docker, no SSH — just authenticated POST to `/ghost/api/admin/posts/`.

**Credentials**:

| Env var | Source | Shape |
|---|---|---|
| `GHOST_URL` | Your Ghost site URL | `https://blog.example.com` (no trailing slash) |
| `GHOST_ADMIN_KEY` | Ghost admin -> Settings -> Integrations -> (your integration) -> **Admin API Key** | `<24-hex>:<64-hex>` combined |

Preflight:

```bash
curl -sS "$GHOST_URL/ghost/api/admin/site/" | head -c 80
[ -n "$GHOST_URL" ] && [ -n "$GHOST_ADMIN_KEY" ] && echo "keys present" || echo "MISSING"
```

**Image upload** (call once per figure, then splice the returned URL into the draft):

```bash
python3 scripts/seo-blog-writer/ghost-upload-image.py "<image-path>"
```

**Publish the post**:

```bash
python3 scripts/seo-blog-writer/publish-ghost.py "<slug>"
```

`?source=html` tells Ghost to convert the `html` field into Lexical. Without it, Ghost treats the field as Lexical JSON and the POST fails with a 422.

**Python deps**: `pip install requests pyjwt`. PyJWT 2.x required.

---

### Adapter B — WordPress (REST API)

Uses the WordPress REST API with **Application Password** auth (Users -> Profile -> Application Passwords). Works on any WP site with REST exposed at `/wp-json/wp/v2/`.

**Credentials**:

| Env var | Source | Shape |
|---|---|---|
| `WP_URL` | Your WordPress site URL | `https://blog.example.com` (no trailing slash) |
| `WP_USER` | The WP username the app password belongs to | `admin` |
| `WP_APP_PASSWORD` | Profile -> Application Passwords -> new -> "seo-blog-writer" | `xxxx xxxx xxxx xxxx xxxx xxxx` |

Preflight:

```bash
curl -sS "$WP_URL/wp-json/wp/v2/" | head -c 120
[ -n "$WP_URL" ] && [ -n "$WP_USER" ] && [ -n "$WP_APP_PASSWORD" ] && echo "keys present" || echo "MISSING"
```

**Image upload** (returns the media id and URL):

```bash
python3 scripts/seo-blog-writer/wp-upload-image.py "<image-path>"
```

**Publish the post**:

```bash
python3 scripts/seo-blog-writer/publish-wordpress.py "<slug>"
```

**Notes**:
- `featured_media` in the post payload is a media **id**, not a URL. Upload the feature image first, capture the id, then set `post["featured_media"] = <id>`.
- WordPress accepts `<script>` in `content` only if the user has the `unfiltered_html` capability (admins do by default; editors may not). If your user lacks it, install a small theme snippet that reads the schema from a post meta key into `wp_head`.

---

### Adapter C — Static-site (file output)

For Hugo / Astro / Eleventy / Jekyll / Next-MDX style setups where posts live as files in a git repo. The adapter writes the bundle into the target directory; your usual build + deploy takes it from there.

**No credentials.** Just a target path.

```bash
python3 scripts/seo-blog-writer/publish-static.py "<slug>" "<out-dir>"
```

Your SSG's layout template needs one line to include the schema in `<head>` — e.g. for Hugo:

```html
{{ if (fileExists (printf "content/posts/%s.schema.html" .File.BaseFileName)) }}
  {{ readFile (printf "content/posts/%s.schema.html" .File.BaseFileName) | safeHTML }}
{{ end }}
```

For Astro / Eleventy / Next, do the equivalent (read file at build time, inject into the layout head).

---

### Adapter D — bring-your-own

The bundle is a stable contract. Any platform with an "upload an image" and a "create a post" endpoint can be adapted in ~50 lines. The contract:

- `<slug>.draft.html` — body HTML, post-scrub, post-audit.
- `<slug>.schema.html` — JSON-LD `<script>` blocks to inject in `<head>`.
- `<slug>.metadata.json` — title, slug, tags (string list), author (slug + name), meta title/desc, excerpt, feature image (URL or local path), status (`draft` / `published` / `scheduled`), published_at (ISO).

Adapter examples shipped above (Ghost, WordPress, static) cover ~90% of small-publisher use cases. Webflow CMS, Sanity, Strapi, and Contentful each take a similar shape: POST to the platform's content endpoint with their auth header, body field, and metadata fields.

---

### Step 8b. Report back to the user

Whatever adapter ran, the final report includes:

- Draft URL or live URL (`<base-url>/<slug>/` if published; admin edit URL if draft).
- Platform admin / repo edit URL.
- Word count, tag list, author slug.
- Confirmation: scrub passed, AI-SEO audit applied, FAQ block present, JSON-LD injected.
- Figure URLs and captions.

---

## Step 9 — Verify live post (only if `--publish`)

```bash
# Post is reachable
curl -sSI "<base-url>/<slug>/" | head -5

# Post in RSS
curl -sS "<base-url>/rss/" | grep -o "<title>[^<]*</title>" | head -5

# Post in sitemap (path varies by platform — Ghost: /sitemap-posts.xml; WP: /sitemap.xml; SSG: as configured)
curl -sS "<base-url>/sitemap-posts.xml" | grep "<slug>"

# OG + full schema set rendered
curl -sS "<base-url>/<slug>/" | grep -o 'property="og:[^"]*"' | sort -u
curl -sS "<base-url>/<slug>/" | grep -oE '"@type":\s*"[^"]+"' | sort -u
```

**Expected:** `HTTP/2 200`, slug in RSS and sitemap, `og:title`/`og:description` present. The `"@type"` set must include **`Article`** (or `BlogPosting`), **`FAQPage`**, and **`BreadcrumbList`**; procedural how-to posts must also include **`HowTo`**. Missing FAQPage/BreadcrumbList means the schema slot wasn't wired correctly — check the platform-specific head-injection field.

---

## What this skill does NOT do

- **Does not commit to git.** Adapters write to CMS APIs or to your static-site directory; the latter you commit yourself.
- **Does not schedule posts by default.** Pass `--publish-at <ISO-UTC>` to schedule. Without it the post lands as draft (default) or live (`--publish`).
- **Does not handle member-only posts, newsletters, or email sends.** Each platform's newsletter flow is manual via its admin UI.
- **Does not generate figures.** Use the companion `blog-figure-svg` skill for SVG charts, taxonomies, and flow diagrams.
- **Does not research topics from scratch.** Use the companion `blog-topic-research` skill to validate a topic has real demand signals before drafting.

---

## Failure modes

| Symptom | Adapter | Cause | Fix |
|---|---|---|---|
| `401 Unauthorized` | Ghost / WordPress | Key expired / wrong key / wrong app-password | Regenerate the integration / app password |
| Ghost `422 Validation failed: Value in [posts.html] cannot be blank` | Ghost | Missing `?source=html` | Add the query param |
| Ghost `422` with `feature_image_alt` in message | Ghost | Alt text >191 chars | Trim to <=191; Step 7g asserts this |
| `404` on slug after publish | any | Post saved as draft (default) | Drafts only reachable via admin editor URL |
| Body shows as one HTML blob | Ghost | Ghost fell back to plain-text mode | Re-post with `?source=html` |
| Smart quotes reappear in rendered post | Ghost | Ghost typographer auto-conversion | Settings -> Publication: turn off "Use typographer's quotes" |
| Wrong slug | any | Platform auto-slugged from title | PUT/PATCH the post with the corrected slug |
| Ghost `409 Conflict` on PUT | Ghost | Stale `updated_at` | Re-GET to refresh, retry |
| Author silently substituted | Ghost / WordPress | Author slug doesn't exist / user lacks `publish_posts` | Create the user; PUT correction with correct slug or user id |
| Live page missing FAQPage / HowTo `@type` (Step 9) | Ghost | JSON-LD was inlined in the body and stripped by Lexical conversion | PUT with `codeinjection_head` set to `<slug>.schema.html`; echo current `updated_at` to avoid 409 |
| WordPress strips `<script type="application/ld+json">` from body | WordPress | User lacks `unfiltered_html` | Move schema injection to a theme hook reading a post meta key |

---

## Companion skills

- **`blog-topic-research`** — validate a long-tail topic has real demand signals (PAA, Reddit threads, GitHub issues) before drafting. Run this *before* this skill.
- **`blog-figure-svg`** — generate accessible SVG figures (flow diagrams, comparison charts, taxonomy diagrams) with consistent styling. Run this *during Step 6* if the post needs illustrations.

Together, the three form a complete long-tail SEO publishing pipeline: research the topic, write the post, illustrate it, publish.

---

## Maintenance scripts

The per-post scrub in Step 4a covers the common LLM-tell characters and the per-post audit in Step 7g enforces the structural rules. For corpus-wide drift — characters or banlist phrases that crept back in across many posts — there's a separate audit script in the repo:

```bash
# Sweep your published-content directory for non-ASCII chars + prose banlist
python3 scripts/audit-corpus.py path/to/your/content/

# Examples (per platform):
python3 scripts/audit-corpus.py tmp/blog-drafts/                  # current drafts
python3 scripts/audit-corpus.py content/posts/                    # Hugo / Astro / 11ty
python3 scripts/audit-corpus.py site/source/_posts/               # Jekyll

# Add domain-specific terms you want flagged (comma-separated):
python3 scripts/audit-corpus.py content/posts/ --extra "synergy,best-in-class"

# CI mode: exit 1 on any hit, pipe to your notifier or fail the build
python3 scripts/audit-corpus.py content/posts/ >/dev/null || echo "drift detected"
```

Default scan covers `*.html` and `*.md`. The script exits `0` clean / `1` on hits / `2` on bad invocation, so it composes with CI. Run it weekly (or as a pre-deploy step) — much cheaper than re-reading every post by hand.

Don't point it at the publishing-skills repo itself or at the seo-blog-writer SKILL.md: both contain the banlist literals as data and will self-flag. Target your *content* directory, not your *tooling* directory.
