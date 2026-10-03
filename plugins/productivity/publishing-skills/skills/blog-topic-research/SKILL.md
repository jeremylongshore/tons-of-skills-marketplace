---
name: blog-topic-research
description: "Stop writing blog posts nobody searches for. This skill builds your editorial backlog from real, verifiable user demand - never from AI vibes. It mines candidates from Google Suggest, People Also Ask, Reddit, Stack Overflow, GitHub issues, vendor forums, and changelogs; captures every signal as a citable URL with verbatim evidence; classifies each topic by post format (how-to-fix, x-vs-y, listicle, migration, release-recap, ...); checks against your existing backlog so you don't cannibalize what you already published; and outputs a writer-ready scaffold with primary sources, problem summary, confirmed fixes, version context, and FAQ variants. Built for content marketers, founders, indie hackers, and dev-tool teams who want a long-tail SEO pipeline backed by evidence instead of hallucinated keyword volumes. Trigger when the user says: 'research blog topics', 'find topics with real demand', 'expand the editorial backlog', 'research N long-tail topics', or any variant of growing a content pipeline with verified candidates."
version: 1.1.0
emoji: "🔎"
homepage: https://github.com/AutomateLab-tech/publishing-skills
allowed-tools: WebSearch, WebFetch, Bash(python3:*), Read, Write
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
compatibility: Designed for Claude Code
tags: [seo, content, publishing, research, blogging]
metadata:
  openclaw:
    requires:
      bins: []
---

# blog-topic-research

Generates topic candidates for a blog with documented user demand. The skill exists to fight hallucinated SEO ideas: every topic it proposes must point to a URL that proves someone is asking about it.

```
research <N> topics [for cluster <C>] [--append-to <path>]
```

- `N` - number of topics to return (default 50; cap 100)
- `cluster` - if the blog has cluster taxonomy, restrict to one cluster the user names
- `--append-to <path>` - after presenting results, ask the user before appending accepted topics as JSON to the given path (a backlog file, a CSV, whatever the blog uses)

The skill is content-only: it does no scraping of its own. It drives the agent's `WebFetch` and `WebSearch` tools to fetch sources, and (optionally) shells out to a Python similarity script for the cannibalization step.

---

## The contract

For every topic the skill emits, it captures:

| Field | What it is |
|---|---|
| `topic` | Full title shaped like a long-tail query |
| `cluster` | A bucket the user defines for their blog (e.g. `n8n`, `databases`, `react-hooks`) |
| `format` | One of `how-to-fix`, `how-to-connect`, `how-to-automate`, `x-vs-y`, `what-is`, `use-case`, `listicle`, `migration`, `release-recap` |
| `demand_signals[]` | One or more, each with `type`, `url`, `evidence` (verbatim text), `strength` (1-3) |
| `signal_score` | Sum of `strength` across all signals; topic accepted only if **>=3** |
| `primary_sources[]` | At least **1** vendor doc / GitHub issue / official changelog URL |
| `keywords[]` | Primary keyword + 3-5 LSI variants extracted from source text |
| `commentary` | 1-2 sentences on what makes this topic specific (no fluff) |
| `problem_summary` | 1-2 sentences distilling the symptom + trigger from the highest-engagement signal's body, in factual writer-voice (no marketing). Lets the writer skip re-fetching to figure out what the problem actually is. |
| `confirmed_fixes[]` | Each `{kernel, source}`: a short fix kernel (one phrase, e.g. `"set N8N_PAYLOAD_SIZE_MAX=16000000"`, `"downgrade crewai to 0.113"`) plus the source URL where that fix is reported. Empty list if no fix is documented yet (still-open issues count). The writer expands kernels into prose and re-verifies. |
| `version_context` | String like `"n8n 1.65+"`, `"Cursor 0.42 only"`, `"introduced in CrewAI 0.114"`, or `null` if no version qualifier applies. |
| `question_variants[]` | 2-4 paraphrases of the topic that real users actually post (lifted from PAA, autocomplete depth-2, sibling forum titles). Feed the writer's FAQ block + LSI keyword spread directly. **Not invented** - every variant must trace to a captured signal or autocomplete completion. |

**Hard rules:**

- **No URL, no topic.** If the skill cannot cite a verifiable demand signal, the topic is dropped. No "this seems like a good topic" reasoning.
- **No paraphrased evidence.** The `evidence` field is copied byte-for-byte from the source (PAA question text, GitHub issue title, Reddit post title, forum thread title).
- **No invented version numbers, prices, or stats.** All numbers in the topic title must come from a source URL or be omitted entirely.
- **Signal score >=3.** Each signal scores 1 (exists), 2 (engaged), or 3 (heavy engagement) per the strength tiers below. One 3-star signal is enough; three 1-stars is enough.
- **Specificity floor.** Title must be either >=7 words OR contain a concrete qualifier: a version number, an error code/string, a named integration pair (`X to Y`), or a named edge case. Reject vague titles like "n8n tutorial" or "what is automation".
- **Cannibalization check.** Three layers when the user supplies an existing-titles cache: (1) Jaccard token overlap >=0.6 against any cached title = drop. (2) Cosine similarity >=0.85 = drop. (3) Token-dupe (shared distinctive numeric/error-code + shared tool keyword, regardless of cosine rank) = drop. Cosine 0.75-0.85 with no token-dupe = REVIEW (kept but flagged). If the user has no cache, run only Jaccard and skip the rest with a one-line note in the summary footer.
- **Substance distilled, not invented.** `problem_summary`, `confirmed_fixes[]`, `version_context`, and `question_variants[]` are derived from fetched bodies - never hallucinated. If a body doesn't mention a fix, `confirmed_fixes[]` stays empty. If no version is named, `version_context` is `null`. The writer treats these as a verified scaffold and still re-fetches at least one primary source for currency.
- **No padding.** If the skill cannot reach `N` validated topics, it returns what it has and reports the shortfall.

---

## Demand-signal taxonomy

A signal is valid only if its type is one of these, and the linked URL contains the verbatim evidence text:

| Type | What counts |
|---|---|
| `paa` | "People Also Ask" question on a Google SERP. URL = the parent query SERP. Evidence = the PAA question text. |
| `autocomplete` | Google Suggest entry triggered by typing a partial query. Evidence = the suggested completion. |
| `reddit` | A Reddit post asking the question or a close variant on a relevant subreddit. Evidence = the post title. |
| `stackoverflow` | A Stack Overflow question with the same intent. Evidence = the question title. |
| `github_issue` | A GitHub issue on the tool's repo describing the problem (open or closed). Evidence = the issue title. |
| `forum` | A community-forum thread (vendor or third-party). Evidence = the thread title. |
| `vendor_doc` | A vendor docs page that exists because users ask the question. Evidence = the page heading. |
| `trends` | A Google Trends rising query. Evidence = the query string + the rising-percent label from Trends. |
| `keyword_data` | Real search-volume + keyword-difficulty from DataForSEO Labs (see [Step 3d](#step-3d---dataforseo-volume--difficulty-enrichment)). URL = `dataforseo:labs/keyword_overview`. Evidence = `"<kw>" search_volume=<N>/mo, keyword_difficulty=<KD>, main_intent=<intent>, location=US`. This is the one quantitative signal — it carries an absolute volume figure because it comes from a real API, not an estimate. |

**Strength tiers** (used to compute `signal_score`):

| Type | 1 (exists) | 2 (engaged) | 3 (heavy) |
|---|---|---|---|
| `paa` | appears once | appears across >=2 parent SERPs | appears + "More questions" expansion shows >=4 follow-ups on same intent |
| `autocomplete` | direct suggestion | suggestion at >=4-word depth | suggestion at >=6-word depth |
| `reddit` | post exists | >=10 comments OR >=20 upvotes | >=50 comments OR >=100 upvotes |
| `stackoverflow` | question exists | score >=3 OR views >=500 | score >=10 OR views >=2000 |
| `github_issue` | issue exists | >=3 reactions OR >=5 comments | >=10 reactions OR >=20 comments OR linked from changelog |
| `forum` | thread exists | >=5 replies | >=20 replies OR pinned / marked solution |
| `vendor_doc` | page exists | page in main nav | dedicated FAQ entry or "Common errors" section |
| `trends` | rising query | rising >=100% | rising >=500% or labelled "Breakout" |
| `keyword_data` | search_volume >=30 | search_volume >=100 AND KD <=25 | search_volume >=300 AND KD <=15 (high-volume, winnable) |

Engagement counts are read from the source page at fetch time. Record the count in the signal entry so the user can audit (e.g. `[strength=3, 14 reactions]`).

**Does NOT count:**

- The skill's own intuition.
- "Common pain point" with no link.
- "I've seen this on Twitter" without a specific URL.
- Doc paraphrases without a source.
- Topics extracted from another SEO blog without an underlying user-demand URL.

---

## Sources to mine

The user supplies the source list for their blog (or asks the skill to suggest one). Generic source templates per cluster type:

### Developer-tool / SaaS clusters

For each tool the blog covers, mine:

- The tool's official community forum (filter to "Questions" / "Bug reports", sort by reply count).
- The tool's GitHub issues, sorted by reactions desc, last 90 days.
- The tool's subreddit (top of week / top of month).
- Stack Overflow's tag page for the tool, sorted by views.
- The vendor's docs site (changelog, recently updated pages, "Common errors" if it exists).
- The vendor's blog (feature announcements - every new feature seeds new questions).

### Code-language / framework clusters

- Stack Overflow tag page for the language / framework, sorted by views.
- The framework's GitHub issues + discussions.
- Reddit `r/<language>` and `r/<framework>`.
- Recent docs changes (a doc page that was edited last week often answers a recurring question).

### Vertical clusters (e.g. `ecommerce`, `customer-support`, `marketing-ops`)

- Subreddits dedicated to the vertical (`r/ecommerce`, `r/customerservice`, etc.).
- Vendor template galleries (e.g. n8n's workflow gallery, Make's scenario library, Zapier's app directory) - each gallery entry is a verified user-demand signal because people search the named outcome.
- Forum threads asking "how do I [outcome]" with high engagement.

### Always also mine

- **Google Suggest autocomplete** for the tool / language / vertical names.
- **People Also Ask** boxes on SERPs for the same.
- **Google Trends** rising queries for the cluster's main terms.

If the user has a specific cluster list, ask them for the source URLs before mining; if they don't, suggest a list and let them edit it.

---

## Process

### Step 1 - Inventory existing coverage (cannibalization prep)

If the user has an existing backlog file (`backlog.json`, `posts.csv`, an RSS feed of published posts, whatever), ask for the path and a way to enumerate titles. The cannibalization step needs an embedding cache built from these existing titles.

If a Python embedding script is available, the user can build a cache (a JSON file mapping each existing title to its OpenAI `text-embedding-3-small` vector) and point the cannibalization step at it. Typical cost is ~$0.02 per 1M tokens.

If no Python / no cache, fall back to Jaccard-only cannibalization (cheap, less accurate; surfaces near-identical titles but misses synonym dupes).

Also build a token-set per existing title (lowercase, alphanumeric, stopwords stripped) for the Jaccard prefilter used in Step 4.

### Step 2 - Compute cluster targets

If the user has cluster weights (e.g. "30% n8n, 20% AI coding, ..."), apply them: subtract current backlog counts per cluster, then distribute `N` proportionally to the largest deficits.

If `cluster <C>` was specified, allocate all `N` to that cluster.

If no cluster taxonomy at all, treat the whole blog as one cluster and aim for format diversity instead (see Step 3 format matrix).

### Step 3 - Mine candidates per cluster

For each cluster, walk its source list. For each source URL:

1. Fetch via `WebFetch` (or `WebSearch` for SERP-derived signals).
2. Extract candidate query strings: GitHub issue titles, PAA questions, Reddit post titles, forum thread titles, autocomplete suggestions.
3. Record the source URL + the verbatim title text + the engagement count (reactions, comments, upvotes, replies) so a strength tier can be assigned later.
4. **Mine the body, not just the title.** For each high-engagement issue / thread / SO question, fetch the body and extract:
   - Error strings (lines like `Error:`, `TypeError:`, `Traceback`, exception class names, stack-frame headers).
   - Code blocks between triple-backticks (often contain the failing snippet that names the real edge case).
   - Version-qualified phrases ("after upgrade to 1.65", "on Cursor 0.42", "since the v3 release").
   Each extracted string becomes a candidate seed in its own right. Long-tail troubleshooting queries are usually the literal error message, which never appears in the post title.

**Google-side seeds** - use `WebSearch` with these patterns and parse for autocomplete + PAA. Run the full set per cluster, not just the troubleshooting one - long-tail diversity is what stops the corpus drifting into all-`how-to-fix`:

| Pattern | Format target |
|---|---|
| `<tool> <error string>`, `<tool> not working`, `<tool> stuck`, `<tool> fails` | `how-to-fix` |
| `<tool> how to <verb>`, `<tool> connect to <other tool>` | `how-to-connect` / `how-to-automate` |
| `<tool> vs <competitor>`, `<tool> or <competitor>` | `x-vs-y` |
| `what is <feature>`, `<feature> explained`, `how does <feature> work` | `what-is` |
| `build <outcome> with <tool>`, `<tool> for <vertical>` (`for ecommerce`, `for SaaS`, `for marketing`, `for customer support`), `<tool> agent for <task>` | `use-case` |
| `best <tool category>`, `top <N> <tool category>`, `free <tool>`, `<tool> alternatives`, `<tool> templates for <vertical>` | `listicle` |
| `migrate from <tool A> to <tool B>`, `switch from <tool A> to <tool B>`, `<tool A> to <tool B> migration` | `migration` |
| `what's new in <tool>`, `<tool> changelog`, `<tool> <recent-version> features`, `<tool> release notes` | `release-recap` |

Repeat the matrix per tool / framework / vertical in the cluster.

**Per-format source pointers** (in addition to the per-cluster source list above):

- `use-case` - vendor template galleries are the highest-signal source. Each gallery entry is a verified user-demand signal (people search the named outcome). Reddit threads like *"how do I [outcome] with [tool]"* with many comments count too. Drop any seed whose only signal is an existing SEO blog's listicle - that's a competitor signal, not a user-demand signal.
- `listicle` - Google autocomplete depth-2 on `best <category>` and `top <N> <category>`; competitor roundup SERPs (look at what the top 3 results list). Reddit posts asking *"what's the best X for Y"* with many comments score high.
- `migration` - Reddit threads with titles starting `moving from` / `switching from`; Stack Overflow questions about exporting + re-importing between two tools; vendor migration docs (the doc exists because users ask).
- `release-recap` - the vendor changelogs already in the source list, but mine for **specific versions shipped in the last 90 days**. A release-recap post for `<tool> <version>` is only worth writing if (a) that version is current or one minor behind, and (b) the changelog has at least one user-facing entry, not just internal refactors. Older recaps go stale fast.

Each extracted query becomes a candidate. The source is its first demand signal.

### Step 3b - Recursive autocomplete pass

For each candidate that survived Step 3, append one more qualifier word and re-query Google Suggest. Keep any deeper completion that returns a new variant. This is what gets you actual long-tail vs mid-tail - one autocomplete pass surfaces "how to fix n8n webhook error", a second surfaces "how to fix n8n webhook error 404 after restart".

Common qualifiers to try (try several, keep what returns a real completion):

`error`, `not working`, `after update`, `stuck`, `slow`, `timeout`, `free`, `limit`, `vs <known competitor>`, `<current year>`, `self-hosted`, `cloud`, `docker`

Cap at **2 recursive passes** to bound runtime. Each new completion inherits the parent's first signal and must still pass Step 4 on its own.

### Step 3c - Distill substance from the source body

For each candidate that survived Step 3b, build the writer-facing scaffold by re-reading the body of the **highest-engagement** demand signal (the one that scored 2 or 3 in the strength table - usually a high-reaction GitHub issue, pinned forum thread, or popular SO question). If you already fetched the body in Step 3.4, reuse it; otherwise fetch now.

Extract four fields:

1. **`problem_summary`** - 1-2 sentences in writer-voice describing the symptom + trigger. Factual, no marketing copy. Example: *"n8n's HTTP Request node returns 401 when an OAuth2 credential's access token has expired and the refresh-token grant is missing the `offline_access` scope."* Pull verbs and nouns from the body; don't paraphrase the title.

2. **`confirmed_fixes[]`** - list of `{kernel, source}` entries. Each kernel is one short phrase capturing the action (env var to set, version to downgrade to, setting toggle, code edit). The source URL is where the fix is reported (forum reply, vendor doc, GitHub commit, changelog entry). Walk the thread replies, accepted-answer block, vendor "common errors" page. **Skip noise**: ignore "have you tried restarting" or fixes contradicted by later replies. If the issue is genuinely still open with no working fix, leave `confirmed_fixes[]` empty - the writer will frame the post around "what's known so far" rather than fabricating a fix.

3. **`version_context`** - extract any version-qualified phrase the body or thread uses to scope the problem (`"after upgrade to n8n 1.65"`, `"Cursor 0.42 only"`, `"introduced in CrewAI 0.114"`, `"Power Automate desktop V2"`). If multiple versions are named, pick the one most closely tied to the failure. If the body is version-agnostic, set `null`.

4. **`question_variants[]`** - 2-4 near-paraphrases of the topic that surface in PAA boxes, autocomplete depth-2 completions, sibling forum thread titles, or SO related-questions. Each variant must be a real captured string from a source - **do not invent paraphrases**. These feed the writer's FAQ block and LSI keyword spread.

If any of these can't be filled honestly from the body, leave the field at its empty default (`""`, `[]`, `null`) rather than fabricating. A sparsely-filled scaffold is more useful than a hallucinated one - the writer can re-research, but cannot un-trust a polluted blob.

### Step 3d - DataForSEO volume & difficulty enrichment

If `DATA_FOR_SEO_API_BASE64` is configured in the environment, enrich every surviving candidate with real Google search-volume + keyword-difficulty. This is the quantitative half of demand validation — the qualitative URL signals prove *someone* asks; this proves *how many* and *how hard it is to rank*.

The env value is `base64(login:password)` and is used verbatim as the HTTP Basic credential. Batch all candidate primary keywords into **one** `keyword_overview` call (it accepts up to 700 keywords per request, ~$0.01 total — far cheaper than per-keyword lookups):

```bash
curl -s -X POST "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live" \
  -H "Authorization: Basic $DATA_FOR_SEO_API_BASE64" -H "Content-Type: application/json" \
  -d '[{"keywords":["<kw1>","<kw2>","..."],"location_code":2840,"language_code":"en"}]'
```

For each returned item read `keyword_info.search_volume`, `keyword_properties.keyword_difficulty`, and `search_intent_info.main_intent`. Attach a `keyword_data` demand signal to the matching candidate, scored per the strength tier table above, and record the volume figure in the signal's `evidence` string.

**This signal counts toward `signal_score`** — a winnable keyword (vol >=300, KD <=15) is a 3-star signal that can carry a candidate to the `>=3` threshold on its own, the same as a heavy GitHub issue. Conversely, if the target blog is a new or low-authority domain, **drop any candidate whose `keyword_difficulty` exceeds your authority ceiling** (a sensible default is KD>35 for a domain with little ranking history — check the domain's standing with `domain_rank_overview` and raise the ceiling as authority grows). Log these under `high-kd-unwinnable` in the summary footer.

**Graceful fallback:** if `DATA_FOR_SEO_API_BASE64` is unset, the API errors, or the account balance is exhausted (`status_code` 40200 / `money.balance` 0), skip this step entirely and fall back to qualitative-only scoring exactly as before. Print one line: `keyword enrichment skipped: <reason>`. The skill must never block on DataForSEO — it is an accelerant, not a gate.

### Step 4 - Classify, score, and validate

For each candidate:

1. **Cluster** - derived from the tool / framework / vertical named in the topic. If the topic spans two clusters, pick the one with the higher-strength demand signal.
2. **Format** - match phrasing (evaluate in order; first match wins):
   - `migrate from X to Y` / `switch from X to Y` / `move from X to Y` -> `migration`
   - `what's new in <tool> <version>` / `<tool> changelog` / `<tool> release notes` / `<tool> v<N> features` -> `release-recap`
   - `best X for Y` / `top N X` / `free X` / `X alternatives` / `most popular X` -> `listicle`
   - `X vs Y` / `X or Y` -> `x-vs-y`
   - `<error string>` / `not working` / `fix` / `fails` / `broken` -> `how-to-fix`
   - `connect X to Y` / `integration` / `integrate X with Y` -> `how-to-connect`
   - `build <outcome> with <tool>` / `<outcome> using <tool>` / `<tool> for <vertical/use-case>` -> `use-case`
   - `automate X` / `<tool> workflow for Y` -> `how-to-automate`
   - `what is X` / `X explained` / `how does X work` -> `what-is`

   Ambiguity rules: prefer `use-case` over `how-to-automate` when the title names a concrete artefact ("daily Slack digest", "invoice extraction agent"); prefer `how-to-automate` for generic processes ("automate email triage"). Prefer `listicle` for >=3 options and `x-vs-y` for exactly 2.

3. **Cannibalization** - three-layer check against the existing-titles cache built in Step 1:
   - **Jaccard prefilter:** token-set overlap against existing titles; drop if >=0.6 (cheap kill on obvious dupes).
   - **Semantic + token-dupe check** (only if an embedding cache was built):
     - Cosine similarity >=0.85 against any existing title -> drop, log under `cannibalization-semantic`.
     - Token-dupe: a shared distinctive numeric / error-code AND a shared tool keyword between candidate and any existing title anywhere in the cache, regardless of cosine rank -> drop. (Catches substance-dupes whose surface wording differs enough that cosine ranks them low. Example: "Make AI Agent 40-second timeout" vs "Make HTTP module 40-second timeout error" - cosine 0.51, but shared `[40-second, make]` flags it.)
     - Cosine 0.75-0.85 with no token-dupe -> REVIEW (kept but flagged). The user decides at append time.
     - Cosine <0.75 with no token-dupe -> accept.
   - If no embedding cache, run only the Jaccard prefilter and add a one-line `cannibalization: jaccard-only` note to the summary footer so the user knows the check was reduced.

4. **Score signals** - assign each signal 1-3 per the strength tier table. If `signal_score < 3`, fetch one more SERP and look for additional signals (PAA, second forum thread, SO question, vendor doc). If still `< 3`, drop under `low-signal-score`.

5. **Specificity floor** - title must be >=7 words OR contain a concrete qualifier (version number, error code/string, named integration pair, named edge case). If neither holds, try to rewrite the title using a qualifier from the source text; if that's not possible, drop under `low-specificity`.

6. **Primary source** - find at least one vendor doc / GitHub issue / official changelog URL the writer can cite. If none, drop.

7. **Keywords** - extract the primary keyword (the topic's core noun phrase) plus 3-5 LSI variants from the source text. Do not invent variants.

### Step 5 - Output

Print one block per accepted topic in this exact shape so the user can scan or pipe it:

```
[01/50] cluster=<cluster>  format=how-to-fix  priority=2
TOPIC: How to fix the n8n "Cannot read properties of undefined" error in Code node
slug:  n8n-cannot-read-properties-undefined-code-node
keywords: n8n Code node error, undefined property, JavaScript error, item access, $json
commentary: Specific to mistakes when accessing $json on the wrong item; vendor docs do not show the failure mode.
problem: The n8n Code node throws "Cannot read properties of undefined" when the script accesses $json on an item index that doesn't exist (typically the second iteration of a for-loop reading $items[1].json with only one input item).
fixes:
  - guard with $items[i]?.json before accessing  (https://github.com/n8n-io/n8n/issues/<id>#issuecomment-<n>)
  - use $input.item.json instead of $items[i] when iterating  (https://docs.n8n.io/code/builtin/data/)
version_context: n/a
question_variants:
  - "n8n Code node Cannot read properties of undefined reading 'json'"
  - "n8n JavaScript error TypeError undefined json"
  - "Code node loop fails when item missing"
demand: (signal_score=4)
  - github_issue: https://github.com/n8n-io/n8n/issues/<id>  ("Code node throws Cannot read properties of undefined") [strength=3, 14 reactions]
  - reddit:       https://www.reddit.com/r/n8n/comments/<id>  ("Help: Code node error when looping over items") [strength=1]
sources:
  - https://docs.n8n.io/code/builtin/data/  (n8n docs - Built-in data variables)
```

If `confirmed_fixes` is empty (open issue with no working fix), print `fixes: (none documented yet - frame as 'what's known so far')` instead of an empty list. If `version_context` is null, print `version_context: n/a`. If `question_variants` is empty, omit the line entirely (rare but valid).

If the topic landed in the REVIEW band of the cannibalization check, append a `dedup_review` line so the user can decide knowingly:

```
dedup_review: cosine=0.81 vs "n8n Code node returns undefined when reading $json" (backlog-queued)
```

Then a summary footer:

```
Requested: 50
Validated: <X>
Dropped:   <Y>  (cannibalization-jaccard: <a1>, cannibalization-semantic: <a2>, cannibalization-token-dupe: <a3>, low-signal-score: <b>, no primary source: <c>, off-cluster: <d>, low-specificity: <e>, high-kd-unwinnable: <f>)
Cluster mix:  <cluster1>=__  <cluster2>=__  ...
Format mix:   how-to-fix=__  how-to-connect=__  how-to-automate=__  x-vs-y=__  what-is=__  use-case=__  listicle=__  migration=__  release-recap=__
```

If `--append-to <path>` was passed: print the diff (count + cluster mix changes), ask `Append <X> topics to <path>? [y/N]`. On `y`, write each topic as JSON to the target path with:

```json
{
  "id": "<slug>",
  "topic": "<title>",
  "cluster": "<cluster>",
  "format": "<format>",
  "priority": 100,
  "status": "queued",
  "tags": ["<format-tag>", "<tool-tag>"],
  "notes": "<commentary>",
  "added_at": "<YYYY-MM-DD>",
  "research_proof": {
    "demand_signals": [...],
    "primary_sources": [...],
    "keywords": [...],
    "problem_summary": "<1-2 factual sentences from the highest-engagement signal's body>",
    "confirmed_fixes": [
      {"kernel": "<short fix phrase>", "source": "<url>"},
      {"kernel": "<short fix phrase>", "source": "<url>"}
    ],
    "version_context": "<version qualifier or null>",
    "question_variants": ["<variant 1>", "<variant 2>", "<variant 3>"]
  },
  "published_slug": null,
  "published_at": null
}
```

The `research_proof` blob is preserved on the backlog entry while `status = "queued"` so a downstream writer skill can read it later (saves re-research). When the topic ships, strip the proof blob to keep the backlog file from ballooning at scale; the published post carries the citations.

---

## Anti-hallucination guardrails

- **WebFetch / WebSearch only.** Never fabricate a URL. If a fetch fails, drop the candidate - do not invent the response.
- **Verbatim evidence.** Each `evidence` string is copied byte-for-byte. No paraphrase. Length cap 120 chars; truncate with `...` if longer.
- **No invented numbers.** Version numbers, prices, error codes in the topic title must appear in at least one source URL. If unsure, drop them from the title.
- **Date-bound the run.** Every source URL must resolve on the run date. If 404 / removed, the signal is invalid even if the URL was good last week.
- **Signal score >=3, strictly enforced.** Cumulative strength below 3 goes to `low-signal-score`. The strength tier table is the only authority - do not invent your own scoring.
- **Specificity floor enforced.** Vague titles without a concrete qualifier go to `low-specificity`. Long-tail is proven by *what's in the title*, not by hand-waving "this is specific".
- **Cluster discipline.** Stick to the user's cluster taxonomy. Never invent a new cluster mid-run; if a topic doesn't fit, drop it or ask the user.
- **Allowed-tag check.** If the blog has a tag allowlist, surface any new implied tag to the user before accepting - do not silently expand the tag set.
- **No commercial-intent topics by default.** Reject SaaS reviews, lead-gen queries, affiliate-driven comparisons unless the user explicitly says they want them. Display-ad RPM is poor for these and they get out-bid by affiliate sites anyway.

---

## What this skill does NOT do

- **Does not draft posts.** Pair with a writer skill downstream.
- **Does not *guess* search volume.** Absolute volume + difficulty figures come from one source only: the DataForSEO Labs API ([Step 3d](#step-3d---dataforseo-volume--difficulty-enrichment)), and only when `DATA_FOR_SEO_API_BASE64` is configured. A `5400 / mo` figure is allowed *only* if it traces to a real `keyword_overview` response — never hand-estimated, never carried over from an SEO blog. With no API key, demand stays qualitative (proven by source URLs).
- **Does not modify the blog's strategy docs.** Cluster targets and weights are the user's call.
- **Does not auto-publish.** With `--append-to <path>` it adds to a backlog as `queued`; the user picks what gets written next.
- **Does not run on a schedule by itself.** Pair with a scheduling skill if you want a weekly or monthly research run.

---

## One-command summary

```
research <N> topics [for cluster <C>] [--append-to <path>]
```

1. Refresh / build an embedding cache from existing titles, if the user has one.
2. Compute per-cluster target counts.
3. Mine candidates from the cluster source list, capturing verbatim text + URL + engagement count per signal. Mine issue / thread bodies for error strings and version-qualified phrases, not just titles.
4. Recursively expand surviving candidates through Google Suggest (up to 2 passes) to push from mid-tail into long-tail.
5. Distill substance per surviving candidate from the highest-engagement signal's body: `problem_summary`, `confirmed_fixes[]`, `version_context`, `question_variants[]`. Empty defaults are valid; never fabricate.
5b. Enrich each candidate with real DataForSEO volume + KD (one batched `keyword_overview` call) when `DATA_FOR_SEO_API_BASE64` is set; attach a `keyword_data` signal, drop terms above your authority ceiling. Skip gracefully if no key/balance.
6. Validate each: format match, cluster fit, three-layer cannibalization (Jaccard >=0.6 OR cosine >=0.85 OR token-dupe = drop; cosine 0.75-0.85 = REVIEW), `signal_score >= 3`, specificity floor, >=1 primary source, real keywords.
7. Print structured per-topic blocks + summary footer.
8. If `--append-to <path>`, confirm with user, then write to the backlog file with the proof blob preserved.
