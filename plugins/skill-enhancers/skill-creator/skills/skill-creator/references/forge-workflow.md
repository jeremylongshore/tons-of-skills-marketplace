## Forge Mode Workflow

Triggered by `/skill-creator --forge <api-name>` or natural-language equivalents ("forge a skill from <api>", "generate plugin from <api> API"). Stricter than Create mode: NOI gate, ecosystem absorb, mandatory final validation. Intended for generating definitive plugins from external API surfaces — not hand-authored skills.

**Output anatomy** — runtime docs in `references/`, build audit trail in `.forge/`:

```
plugins/<category>/<api-name>/
├── .claude-plugin/plugin.json             ← runtime manifest fields only
├── README.md                              ← NOI framing in opening paragraph
├── .forge/                                ← BUILD AUDIT TRAIL (immutable, read once at build time)
│   ├── research.md                         ← API surface enumeration + NOI extraction notes
│   ├── ecosystem.md                        ← competitor catalog + gap analysis
│   ├── proofs.md                           ← validation results (validate-skillmd + JRig output)
│   └── discovery.md                        ← optional: HAR / sniffing artifacts when no spec exists
├── agents/                                 ← plugin-discovered agents
│   ├── <api>-expert.md                     ← domain expert agent (NOI-framed)
│   └── <api>-analyst.md                    ← compound synthesis agent
└── skills/<api-name>/
    ├── SKILL.md                            ← orchestrator skill
    ├── references/                         ← RUNTIME DOCS (read every invocation)
    │   ├── noi.md                          ← NOI statement (skill reads to stay on-mission)
    │   ├── api-surface.md                  ← live API coverage the skill operates against
    │   └── compound-commands.md            ← health/stale/bottleneck patterns
    └── scripts/
        └── sync-cache.sh                   ← optional: local SQLite cache for compound queries
```

**.forge/ vs references/ — separation of concerns**:

- `.forge/` is the build-time audit trail. How the plugin came to exist. Ships in the repo, never read at runtime. Useful for retrospectives, debugging "why was this designed this way?", and `--reforge` decisions.
- `references/` is runtime documentation. What the skill + agents pull at execution time. Kept current as APIs evolve.

### Forge Gate 1: NOI (Non-Obvious Insight) — HARD BLOCK

Before any code is written, the user must name the **NOI** — the API's "secret identity," a reframe more powerful than what the API claims to be:

| API claims to be       | NOI reveals it as                                |
| ---------------------- | ------------------------------------------------ |
| ESPN sports scores API | A betting intelligence terminal                  |
| Stripe payments API    | A business health monitor                        |
| Linear issue tracker   | A team behavior observatory                      |
| Umami page analytics   | A behavior fingerprint for your dev audience     |
| Whop marketplace       | A revenue signal scanner                         |
| Sentry error reporting | An error-rate observatory for release confidence |

**Block until answered.** Use `AskUserQuestion`:

> What is this API's NOI? In 6–10 words, name what it really unlocks that nobody talks about. (`<API> is a/an _______`)

Reject "X is a wrapper around <API>" or "X helps you query <API>" — those are feature-speak, not outcome-speak. The NOI determines every downstream design decision; without it, the output is a generic wrapper, not a definitive tool.

Write the accepted NOI to `references/noi.md` with a justification paragraph explaining what it unlocks and why this framing differentiates from the obvious wrapper interpretation. Also record it in `.forge/research.md` as the canonical decision point.

### Forge Gate 2: Ecosystem Absorb

Use `WebSearch` to catalog 3–5 competing tools targeting this API. For each, capture:

- Name + URL
- What they emphasize (the "claims to be" framing)
- What they don't do — gaps, weaknesses, missing features, missing depth
- Whether their NOI is articulated, and if so, what

Write findings to `.forge/ecosystem.md`. **Required output**: a one-paragraph "How this forge differs" statement based on the catalog — what gap this fills that the existing tools miss.

If 3+ competitors do the exact same thing this NOI claims, challenge the NOI. The forge should occupy genuinely uncovered ground; if the ground is well-covered, return to Gate 1 and refine the NOI.

### Forge Gate 3: API Surface Research

Enumerate the API's surface:

- All endpoints (URL + method + brief purpose)
- Auth method (API key, OAuth, bearer token, etc.)
- Rate limits + quotas
- Response schemas (sample JSON for each endpoint)
- Pagination model
- Webhook / streaming surface, if any
- SDK availability (official + community)

Use the live MCP for the API if one exists (e.g., `mcp__whop`, `mcp__umami`, `mcp__plane`) plus `WebFetch` against the API's published docs. Write the result to `references/api-surface.md` (canonical) and a parallel `.forge/research.md` excerpt (build-time audit).

### Forge Gate 4: Domain Archetype Detection

Auto-classify the API into a domain archetype — this determines the compound command set:

| Archetype                 | Examples                     | Default compound commands                              |
| ------------------------- | ---------------------------- | ------------------------------------------------------ |
| DevOps / Infra            | GitHub, GitLab, Vercel, AWS  | `<api>-health`, `<api>-stale`, `<api>-bottleneck`      |
| Security / Audit          | Sentry, Snyk, gitleaks       | `<api>-incidents`, `<api>-trend`, `<api>-blast-radius` |
| Analytics / Observability | Umami, Datadog, Grafana      | `<api>-pulse`, `<api>-anomaly`, `<api>-cohort`         |
| Payments / Revenue        | Stripe, Whop, Polygon        | `<api>-revenue`, `<api>-churn`, `<api>-leaks`          |
| Project / Workflow        | Linear, Plane, Asana         | `<api>-velocity`, `<api>-stale`, `<api>-bottleneck`    |
| Communication / Social    | Slack, Discord, Twitter      | `<api>-pulse`, `<api>-engagement`, `<api>-influence`   |
| Knowledge / Docs          | Notion, Confluence, Obsidian | `<api>-stale`, `<api>-overlap`, `<api>-orphan`         |
| Other                     | (uncategorized)              | derive from NOI + endpoints                            |

Document the chosen archetype in `references/api-surface.md` along with the compound-command set the next gate will design.

### Forge Gate 5: Compound Command Design

Compound commands are commands that are **only possible because multiple API calls are synthesized locally** — not just thin wrappers. They are derived from the NOI + archetype and require the same forcing function:

- Each command must answer a question that is impossible from any single API call.
- Each must have a clear "without this skill, you'd manually do N steps" framing.

Write designs to `references/compound-commands.md`. Each entry includes:

- Command name (`/<api>-<verb>`)
- One-line purpose (NOI-framed, not feature-framed)
- API endpoints called + how they're synthesized
- Output format (table / JSON / annotated narrative)
- Caching strategy (if local SQLite is needed for performance, plan it here)

### Forge Gate 6: Skill + Agent Generation

Generate the plugin per the output anatomy above:

1. `plugin.json` — use the target manifest schema for `name`, `version`, `description`, `author`, `license` and `repository`. Record forge provenance in `.forge/research.md`. The existing catalog fields `generated: true` and `author_type: forge` belong in an authorized canonical catalog entry, not the runtime plugin manifest; do not invent or rename source-classification labels.
2. `README.md` — NOI framing in the opening paragraph.
3. `skills/<api-name>/SKILL.md` — orchestrator skill, references `noi.md` + `api-surface.md` + `compound-commands.md`. Marketplace-tier compliant: 8-field frontmatter, `compatibility` free-text, `tags` populated from archetype + API category.
4. `agents/<api>-expert.md` — domain expert agent, NOI-framed system prompt, deep on the API surface.
5. `agents/<api>-analyst.md` — compound synthesis agent that orchestrates the expert across compound commands.
6. `skills/<api-name>/scripts/sync-cache.sh` (when SQLite caching is part of the design).

Use `agent-creator` skill to generate `agents/*` rather than hand-rolling — single canonical agent generator.

### Forge Gate 7: Mandatory static validation; optional behavioral evidence

Run `/validate-skillmd` on the generated SKILL.md for marketplace grading and the
static production checks. From the marketplace root, with an absolute skill path:

```bash
python3 scripts/validate-skills-schema.py --marketplace "$skill_file"
pnpm exec j-rig check "$(dirname "$skill_file")" --json
```

Require **Tier 1 Grade A (≥90/100)** and **Tier 2 GREEN**. Fix static blockers before
promotion. The deterministic package check is separate from both rubric scoring
and behavioral evidence; report missing tooling or package errors explicitly.

Run behavioral evaluation only when the user explicitly requests it and its
provider/model scope and proof destination are authorized. Follow
`/validate-skillmd` Step 2.7 through `scripts/run-jrig-eval.sh`, with the actual
catalog plugin, allocated behavioral run ID, reviewed spec and authoritative
inventory. Existing authorization is sufficient; forge mode alone does not
implicitly authorize paid provider calls.

Record behavioral **SKIPPED** when not requested and **INCOMPLETE** when requested
prerequisites or coverage are missing. A static pass, model matrix, stub result or
zero exit code is not an all-layer/JRig-Verified verdict. Preserve actual failures
and apply the repository's promotion policy to retained evidence; required
behavioral coverage must be complete before claiming that promotion gate passed.

Write the static results, behavioral scope/outcomes and retained evidence paths
to `.forge/proofs.md` as the build-time audit record.

### Forge Gate 8: Output

When all gates pass:

1. Create a feature branch: `feat/forge-<api-name>` off main.
2. Stage the new plugin directory + `pnpm run sync-marketplace` output.
3. Open a PR with title `feat(forge): <api-name> plugin (NOI: <NOI text>)`.
4. PR description includes:
   - The NOI statement (verbatim from `noi.md`)
   - Compound commands list
   - Validation results (Tier 1 grade, Tier 2 verdict, Tier 3 layer breakdown)
   - Link to `.forge/research.md` for the audit trail
   - Provenance disclosure: link the forge record and any authorized canonical catalog provenance fields
5. The PR lands in a `review/forge/` queue (anti-spam moat per Phase 5A) — manually reviewed before promotion to the catalog.

### Optional: MCP Server Scaffolding

When the API has a stable REST or GraphQL contract, ALSO scaffold an MCP server in `plugins/<category>/<api-name>/mcp/`:

- TypeScript boilerplate (per `plugins/mcp/` conventions in the repo)
- Exposes the same tools as the skill
- Closes the gap where the marketplace has 425 plugins but only ~10 with MCP servers

Skip with `--no-mcp` flag.
