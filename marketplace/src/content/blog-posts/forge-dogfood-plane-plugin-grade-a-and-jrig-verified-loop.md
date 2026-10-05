---
title: "Forge Dogfood Ships a Grade-A Plane Plugin, JRig Loop Closes"
description: "First end-to-end /skill-creator --forge dogfood produced a Grade A 97/100 Plane plugin while the JRig-Verified provenance loop closed across schema, build pipeline, page target, homepage surface, and a new validator tier."
date: "2026-05-07"
tags: ["claude-code", "ai-agents", "automation", "release-engineering", "architecture"]
featured: false
canonical: "https://startaitools.com/posts/forge-dogfood-plane-plugin-grade-a-and-jrig-verified-loop/"
---
> **Update (October 2026):** The "JRig-Verified" badge described in this post was withdrawn in August 2026. Its data file could be changed by any merged pull request with no evidence check behind it, so it could not honestly certify a plugin. No Tons of Skills page shows a JRig verification today. Behavioral-evaluation results stay internal governed evidence until they can be published with retained, hash-matched proof. The rest of this post is the original May 2026 record.

A plugin generator is theoretical until it produces something a marketplace will actually accept. May 7 turned the `/skill-creator --forge` workflow from an 8-gate diagram into a real artifact — a Plane plugin that scored Grade A (97/100), passed Tier 2 GREEN with zero warnings, and cleared all 12 deterministic j-rig checks across the 7-layer behavioral framework. On the same day, the JRig-Verified provenance pipe closed end-to-end: a schema, a build-time enrichment step, a per-plugin verification page, and a validator tier all landed in the same window. The thesis the day proves: compound commands and build-time enrichment beat raw API surfaces and runtime joins, and the way to find that out is to run the full pipeline once on something real.

## What "theoretical" looked like on May 6

The forge workflow had eight gates defined in spec. None had been exercised together. The JRig-Verified badge UI shipped earlier in the same day in PR #696 — it rendered, but the data path behind it terminated at an empty placeholder. A plugin detail page could display "JRig-Verified · N/7 layers" if the right shape of data showed up, but nothing in the build pipeline produced that data, and the `/plugins/<name>/verification` link the badge pointed at was a 404.

The pre-May-7 state, in a sentence each:

- **Forge:** documented, scaffolded, never run end-to-end on a real API
- **JRig badge:** UI complete, no data source, dangling link target
- **Validator:** 100-point rubric, no static production checks beyond it
- **Marketplace homepage:** 422 plugins, no curated entry surface for the first five minutes
- **Provenance metadata:** spec defined `generated` and `author_type` fields; no consumers

Every one of those gaps closed on May 7.

## The forge dogfood — Plane as a team behavior observatory

The forge takes two inputs: an API spec and a one-line NOI (Notion of Intent — the answer to "what makes this plugin different from a CRUD wrapper?"). The NOI is the forcing function. Without it, an LLM-generated plugin defaults to one command per endpoint, and the result is a thinner, slower duplicate of whatever MCP server already wraps the API.

The NOI for this run rejected that framing outright:

> **Plane is a team behavior observatory.**

That sentence does most of the design work. The existing `mcp__plane` MCP server already covers CRUD — listing cycles, creating issues, updating worklogs. A plugin that wraps the same surface is dead weight. A plugin that surfaces the *behavioral signal* hiding inside JOINed Plane data is something the MCP server cannot do, because MCP tools are endpoint-shaped and behavior is JOIN-shaped.

The five compound commands the NOI produced each answer a question that no single Plane endpoint can answer:

```
/plane-cycle-velocity        — does cycle close-out match cycle planning?
/plane-stale-tickets          — which In Progress tickets quietly fail under shared ownership?
/plane-reviewer-gate-strength — which reviewers gate-keep harder than the spec demands?
/plane-priority-drift         — does the team plan high-priority and ship low-priority?
/plane-cross-project-load     — which engineers are spread across too many projects?
```

Each requires JOINing at least two Plane resources, applying a scoring formula, and producing ranked output. None of them is `GET /cycles/{id}` plus a render template.

### The 8 gates and what came out of each

| Gate | Outcome |
|---|---|
| 1. NOI | Accepted: "Plane is a team behavior observatory" |
| 2. Ecosystem absorb | 5 competing tools cataloged; behavioral-synthesis gap confirmed uncovered |
| 3. API surface | 14 [Plane API](https://docs.plane.so/api-reference/introduction) endpoints documented in `api-surface.md` |
| 4. Domain archetype | Project / Workflow tracker; default compound set adopted + extended |
| 5. Compound commands | 5 commands designed with synthesis logic + scoring formula |
| 6. Generation | SKILL.md, 2 agents, 3 references, plugin.json, README.md written |
| 7. Validation | Tier 1 Grade A (97/100), Tier 2 GREEN, Tier 3A GREEN (12/12 j-rig) |
| 8. PR + catalog | PR #703 |

The output of Gate 7 is the headline number. It is also the first piece of evidence that the workflow produces marketplace-grade output, not lab-bench output.

### Reproducibility — the receipts anyone can re-run

Both checks shipped in the PR body:

```bash
python3 scripts/validate-skills-schema.py --marketplace \
  plugins/productivity/plane/skills/plane/SKILL.md
# → Grade A (97/100), Tier 2 GREEN, 0 errors, 0 warnings

j-rig check plugins/productivity/plane/skills/plane
# → 12 passed, 0 warnings, 0 errors
```

Actual stdout from the run captured in the PR body:

```
Grade: A (97/100)
Tier 2: GREEN — 0 errors, 0 warnings
Tier 3A: 12/12 j-rig checks passed
```

Anyone with [the `claude-code-plugins` repo](https://github.com/jeremylongshore/claude-code-plugins) checked out can rerun those two commands and deterministically verify the result. Provenance without reproducibility is decoration.

### Why "compound" beats "wrapper" — the design rationale in detail

The CRUD-wrapper anti-pattern is seductive because it is easy to generate. An LLM with an OpenAPI spec can produce one command per endpoint in a few minutes. The output passes most surface-level checks: it has commands, it has parameters, it talks to the API. What it does not have is *value beyond the API*.

A user who wants to list cycles in Plane already has `mcp__plane.list_cycles`. A plugin command called `/plane-list-cycles` is a strictly worse interface — slower (slash command overhead), harder to discover (lives in plugin catalog instead of MCP tool list), and provides no transformation of the result. The user gets the raw response either way; the plugin command added one round-trip and zero insight.

A compound command flips the value equation. `/plane-cycle-velocity` calls `list_cycles`, then for each cycle calls `list_cycle_issues`, joins the planning data against the close-out data, computes a velocity ratio per cycle, and returns ranked output with a behavioral interpretation. The user could in principle do this themselves with five MCP calls and a calculator. They will not. The plugin earns its place by collapsing five mechanical steps into one named operation that produces actionable signal.

The NOI gate exists to force this distinction during generation. "Plane is a team behavior observatory" is not a marketing tagline — it is a constraint that disqualifies any command that does not surface behavioral signal. The forge uses the NOI to filter the generated command list: a command that fails to tie back to the NOI gets cut, regardless of how cleanly it wraps an endpoint.

### Architecture choices the dogfood surfaced

The forge produced AI-generated output that passed Tier 2 without post-generation edits — a first for the workflow. The PR is 1,123 lines, but the orchestrator skill is only 150. That ratio is intentional. SKILL.md routes — it does not implement. Implementation lives in two agents:

- **`plane-expert`** — API-surface specialist. Knows endpoints, parameters, auth shape. Does not call live Plane. Used for design questions and shape verification.
- **`plane-analyst`** — behavioral synthesis. Calls `mcp__plane` endpoints, applies JOIN logic and scoring formulas, returns ranked output. The five compound commands all delegate here.

Three references back the agents: `noi.md` (the design anchor every output ties back to), `api-surface.md` (the 14 endpoints), and `compound-commands.md` (the synthesis logic and scoring formulas).

MCP server scaffolding got skipped. The forge offers to scaffold an MCP server when the API has no existing wrapper; `mcp__plane` already exists. Producing a duplicate would have been the exact CRUD-wrapper anti-pattern the NOI rejected.

### Provenance metadata — the seam that wires this to JRig

Two fields landed in the plugin's `plugin.json`:

```json
{
  "generated": true,
  "author_type": "forge"
}
```

These are read by the marketplace renderer (PR #696's earlier work) to display the "Forge-generated" pill on the plugin page. They are also the inputs the JRig data flow keys on, which is the next half of May 7's story.

## Closing the JRig-Verified loop

PR #696 landed the badge UI earlier the same day. The badge rendered conditionally on a `plugin.jrig` overlay that nothing wrote. The next four PRs closed the gap.

### Schema — `forge_proofs` and three new columns (PR #699)

Three columns added to `skill_compliance`, all nullable, all idempotent:

| Column | Type | Purpose |
|---|---|---|
| `jrig_passed` | INTEGER, nullable | Boolean — did all 7 JRig layers pass on the model matrix? |
| `jrig_tier_blocked` | INTEGER, nullable | Which JRig layer (1–7) failed |
| `jrig_baseline_delta` | REAL, nullable | Performance delta vs. naked Claude. >0 helps, <0 hurts |

A new table holds verification artifacts:

```sql
CREATE TABLE forge_proofs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plugin_name TEXT NOT NULL,
  run_id INTEGER,
  verification_type TEXT NOT NULL,    -- 'tier1' / 'tier2' / 'tier3-jrig' / 'dogfood'
  passed INTEGER NOT NULL,
  evidence TEXT,
  layers_passed INTEGER,
  total_layers INTEGER DEFAULT 7,
  baseline_delta REAL,
  verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(plugin_name, verification_type, run_id)
);
```

The migration only ADDs — never DROPs, never RENAMEs. Re-runs are no-ops. PRAGMA-check guards prevent duplicate column adds. The schema is forward-compatible by construction.

### Build pipeline — `enrich-jrig-data` step (PR #700)

The data path that wires `forge_proofs` rows into the rendered marketplace page:

```
forge_proofs (freshie/inventory.sqlite)
    │  SELECT … WHERE verification_type='tier3-jrig' AND passed=1
    ▼
enrich-jrig-data.mjs  ←  jrig:enrich build step (new)
    │  writes flat plugin_name → {verified, layers_passed, total_layers,
    │  baseline_delta, verified_at} map
    ▼
marketplace/src/data/jrig-data.json
    │  imported by [name].astro at static-build time
    ▼
plugin.jrig overlay  ←  PR #696's existing optional-chain rendering
    ▼
"JRig-Verified · N/7 layers" pill on plugin detail page
```

The build pipeline order post-merge:

```
1. discover-skills         → skills-catalog.json
2. extract-readme-sections → readme-sections.json
3. sync-catalog            → catalog.json
4. enrich-jrig-data        → jrig-data.json     ← NEW
5. generate-unified-search → unified-search-index.json
6. build-cowork-zips       → cowork zips + manifest
7. astro build             → static site
```

### The sqlite driver decision

`enrich-jrig-data.mjs` reads `freshie/inventory.sqlite` to produce `jrig-data.json`. Two driver options were on the table:

- **`better-sqlite3`** — native module, single-call query, ~1 ms per read
- **`sqlite3` CLI subprocess** — already on every dev machine and CI runner, ~50 ms per query

`better-sqlite3` would add a postinstall native build step on every CI run. That step adds 30–90 seconds, fails on architecture mismatches, and has bitten enough Node projects to be a known smell. The `sqlite3` CLI is already installed everywhere the build runs — `sqlite3 -json` returns parseable JSON natively. Trade: ~50 ms subprocess overhead per query, dwarfed by the 20-second astro pipeline that follows.

Today's `jrig-data.json` content: `{}`. Empty by design — no `forge_proofs` rows have landed yet. The build degrades to "no badge rendered" for every plugin, which is the correct fallback. As soon as the first JRig run writes a `tier3-jrig` row, the next site build picks it up automatically.

### Why build-time, not request-time

Two build-time vs. request-time architectures were on the table for getting `forge_proofs` data onto plugin pages:

- **Request-time JOIN** — plugin page fetches `forge_proofs` rows on each render, joins against catalog data, renders the badge inline
- **Build-time enrichment** — `forge_proofs` rows pre-computed into a flat JSON map at build time, imported by the static page renderer

Request-time wins on freshness — the moment a JRig run writes a row, the next page view sees it. Build-time wins on everything else. The marketplace is a static site ([Astro SSG](https://docs.astro.build/en/concepts/why-astro/) output, served from CDN). Putting a database in the request path of a static site means giving up the static-site benefits: no edge caching, no instant cold start, no "drop the build into any object store and it works." The freshness gap from build-time is bounded by the deploy cadence — currently sub-hourly on commit, more than fast enough for a verification badge that does not need to update in real time.

The data flow shape is also worth noting: `enrich-jrig-data.mjs` produces a *flat map keyed by plugin name*. Not a relational join, not a graph, not nested objects — a flat key/value map small enough to import in full at render time. That shape was chosen because Astro's SSG model imports static JSON at the top of the render function. A flat map adds zero query logic to the page; a nested or relational structure would have forced filtering or joining inside the page template, which is the wrong place for that work.

### Page target — `/plugins/<name>/verification` (PR #702)

The badge in PR #696 was a link. The link target was a 404. PR #702 shipped the destination page (306 lines of Astro) with two states:

- **Verified** — green pill, baseline delta vs. naked Claude, verified-at timestamp, 7-layer breakdown
- **Pending** — neutral status, two paths to JRig (forge generation or manual `j-rig eval`), reassurance that grade and Tier 2 results remain authoritative when JRig data is absent

Graceful degradation is built in: the `jrig-data.json` import is wrapped in a try/catch with an empty-object fallback. Environments without the data file still build the site; the verification page just renders the pending state for everyone.

### Homepage starter pack (PR #701, Phase 4C)

Five curated Grade-A plugins now anchor the homepage:

| Plugin | Persona |
|---|---|
| `ai-commit-gen` | productivity |
| `conversational-api-debugger` | debugging |
| `ci-cd-pipeline-builder` | ops |
| `design-to-code` | frontend |
| `excel-analyst-pro` | business |

The marketplace had 422 plugins and no first-five-minutes surface. The starter pack is editorial cadence — quarterly rotation, not algorithmic ranking. Curation beats search when the catalog is too large to skim and the visitor has no query yet.

### Validator Tier 2 gate — +273 lines of Python (PR #698)

Five deterministic checks now fire alongside the standard 100-point rubric:

```
tier2:allowed-tools-accuracy   — declared tools must appear in body          (warn)
tier2:auth-documented           — API surfaces require auth method documented (warn)
tier2:dead-code                 — literal-false branches detected             (warn, capped at 3 surfaces)
tier2:tool-safety               — unscoped Bash + Write/WebFetch needs        (error at marketplace)
                                  Safety Justification
tier2:orchestration-bounds      — skills shouldn't claim cross-skill          (error at marketplace)
                                  orchestration
```

The first three warn. The last two error at the marketplace tier. That split matches risk: shipping a skill that says "I orchestrate other skills" is a behavioral hazard; shipping one with a stale `allowed-tools` line is sloppy but not dangerous.

### The false-positive guard — a generalizable pattern

The `tier2:orchestration-bounds` check initially flagged `/validate-skillmd` itself. That skill *documents* the anti-pattern in its body — it has a section explaining "skills shouldn't orchestrate other skills." The check, scanning prose for orchestration claims, hit those sentences and emitted an error.

The wrong fix would have been to special-case `/validate-skillmd`. The right fix was a generic guard on every Tier 2 prose check:

- Skip lines inside code fences
- Skip lines starting with `>` (block quotes) or `|` (table cells)
- Skip lines containing negation markers: `" not "` (space-padded so it does not match "annotate" or "notable"), `never`, `avoid`, `don't`, `do not`, `must not`, `should not`, `forbidden`, `disallow`, `anti-pattern`, `antipattern`, `wrong:`, `bad:`

That guard generalizes to any static-analysis check that runs over prose. A document might describe the very pattern a check is looking for — to teach against it, to warn about it, to compare alternatives. The check has to recognize description versus assertion. The negation-marker list is a cheap heuristic that handles the common cases without an NLP dependency.

This pattern is reusable. Every prose-level lint rule on a documentation site eventually hits it.

## Tradeoffs the day shipped

Nothing free landed. Each piece carries a cost:

- **sqlite3 CLI subprocess** — ~50 ms per query overhead. Acceptable inside a 20 s build, would not be acceptable at request time.
- **`jrig-data.json` starts as `{}`** — degrades gracefully today, but a misconfigured CI runner that fails the `enrich-jrig-data` step silently produces an empty file and every JRig badge disappears. The fallback is friendly; the failure mode is silent.
- **Plane plugin compound commands** — JOIN logic and scoring formulas match the playbooks, but no live Plane workspace has run them yet. The math is correct on paper. Behavior under real data drift is unverified until someone runs them against a real workspace.
- **Validator Tier 2 negation-marker guard** — list-based, not parser-based. Documents that paraphrase negation in unusual ways could still trip false positives. The fix when that happens is to extend the list, not to switch to a heavier parser.

## Spec docs that landed alongside

Four spec PRs framed the day's work:

- **PR #693** — master skills spec bumped from 3.1.0 to 3.3.1
- **PR #695** — JRig Tier 3A spec snapshots added, with `.gitignore` exceptions to keep the snapshots tracked
- **PR #696** — tagline plus JRig-Verified plus forge-generated badges added to plugin pages (the UI that PRs #700 and #702 wired to data on May 7)
- **PR #697** — IS-extension fields for forge provenance landed (`generated`, `author_type`) — Phase 5A of the "Use the Printing Press to Learn" plan

Phase 4C (homepage starter pack) and Phase 5A (forge provenance schema) both closed on May 7. The forge dogfood itself was Phase 3 of the same plan. Three phases of a multi-phase plan, all converging in one window — not a coincidence. The plan was structured so the dogfood and the provenance pipeline would close together. Running the dogfood without the provenance pipeline produces a plugin nobody can verify; shipping the provenance pipeline without a dogfood produces a UI for data that does not exist. Both halves had to land at once for either to mean anything.

## Why this matters beyond the marketplace

Three patterns from May 7 generalize past the immediate work.

**Compound commands beat endpoint wrappers when the value is in the JOIN.** The Plane plugin proves the design. An MCP server plus an LLM gives you `GET` per resource. A compound command gives you `WHICH cycles closed late AND had reviewer churn AND had priority drift?`, which no API endpoint exposes directly. The forge's NOI gate exists to force that question.

**Build-time enrichment beats runtime joins for static marketplaces.** `jrig-data.json` is computed once per build, served as static JSON, and read by Astro at SSG time. Runtime joining `freshie/inventory.sqlite` against the page render would have meant a database in the request path of a static site. The build step keeps the runtime simple and the cache cold-key small.

**Provenance metadata is structural, not cosmetic.** The `generated: true, author_type: "forge"` fields are not just for the badge. They are the seam that lets the JRig pipeline filter, the marketplace render, the validator behave differently, and future tooling cite the origin. Two boolean-ish fields, multiple downstream consumers — that is a metadata investment that pays compounding interest.

**False-positive guards are part of the gate, not an afterthought.** The Tier 2 orchestration check that flagged `/validate-skillmd` could have been dismissed as "fix it later." The decision to ship the negation-marker guard *with* the check is the difference between a gate that earns trust and a gate that gets bypassed because it cries wolf. Static-analysis checks live and die on their false-positive rate; once that rate goes above a small threshold, engineers route around them and the gate stops being a gate.

## The Intent Solutions thread

The forge dogfood and the JRig loop close the same theme that has run through this site for the past month: turning policy into mechanism, then turning mechanism into evidence. The validator is policy. Tier 2 is mechanism. Grade A (97/100) is evidence. JRig is policy. `forge_proofs` is mechanism. The verification page is evidence. None of the three is sufficient alone, and the chain is what makes a marketplace claim defensible.

## Also shipped — same day

The day did not stop at the marketplace and the forge.

- **`intent-solutions-landing`** — PR #18 migrated `intentsolutions.io` off Firebase to the Contabo VPS (the canonical VPS-as-the-home pattern). PR #19 disabled `compressHTML` and bumped the line-length cap to 50k to fix a deploy regression. PR #20 dropped the Resend/SQLite form-flow notes — Slack-only is the final shape. Umami tracker landed alongside the existing Firebase Analytics. The trustbar gained a "53k+ npm Downloads" stat badge.
- **Umami analytics rollout across three sites** — claude-code-plugins (PR #692, with `data-domains` spam guard), `jeremylongshore.com`, and `intent-solutions-landing` all wired to the self-hosted Umami instance in one day.
- **`contributing-clanker`** — URL-or-repo argument now drives a two-branch onboarding-and-briefing flow.
- **`partner-portals`** — Kobiton portal got an editorial pass (engagement-structure table tightened, status pills dropped, upcoming-work cards added).
- **`kobiton`** — CLAUDE.md sync absorbed engagement history and the sub-bead table.
- **`intent-eval-lab`** — umbrella repo scaffolded.
- **`j-rig-binary-eval`** — skill-spec sources of truth pulled into the repo.
- **Marquee fixes** — PR #689 throttled the npm fetch to dodge registry rate limits and restored the live total. PR #691 relabeled the marquee from '30d' to 'total downloads'.

## Related Posts

- [Guidewire MCP v0.1.0 → v0.1.1 in 76 minutes](/blog/guidewire-mcp-v0-1-0-v0-1-1-76-minutes/) — release engineering with the same evidence-first discipline
- [The Anti-Slop Framework Found Three Bugs Inside Itself](/blog/anti-slop-framework-found-three-bugs-inside-itself/) — validator dogfooding, the same pattern that produced today's false-positive guard
- [Propagation Day: When the Spec Becomes the Migration Plan](/blog/propagation-day-when-the-spec-becomes-the-migration-plan/) — spec-to-execution arcs, the same shape this dogfood follows
