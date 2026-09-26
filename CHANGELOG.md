# Changelog

## 2026-09-26

- **feat(cli)!: `@intentsolutionsio/ccpi` 3.0.0 requires Node.js 22 or later.**
  Breaking: Node 18 and 20 are no longer supported (both are end of life);
  `engines.node` is `>=22.0.0` and the CLI is tested on Node 22 and 24. On
  Node 18 or 20, stay on `@intentsolutionsio/ccpi@2`. `ccpi doctor` now reports
  those runtimes as unsupported and names the 2.x fallback. 3.0.0 also carries
  every change made since the last published release, 2.0.3; versions 2.1.0
  through 2.1.2 were never published.

## 2026-08-18

- **docs(governance):** correct every live documented number that disagreed
  with the code (E2.6): the merge gate is three required contexts, the
  aggregate needs twenty-one jobs, and ratified records received dated
  correction appendices instead of rewritten baselines.
- **feat(governance):** pin the documented `ci-required` contract and schema
  version to the code with fail-loud prose-anchor assertions (E2.7+E2.8).
- **docs(governance):** point STANDARDS, CLAUDE, and AGENTS at the blueprint's
  one-owner-per-fact-class authority map instead of restating ownership
  (E2.10).
- **feat(governance):** rebuild the root README as a governed landing contract
  — category-only TOC, byte budgets, cohort-labeled scale block, certification
  honesty block, frozen install slug pinned by red-run tests (E2.13).
- **fix(marketplace):** label search-result and entity-local skill counts with
  their local population and provenance instead of presenting them as global
  marketplace totals.
- **fix(marketplace):** make spotlight, plugin, community, and plugin-detail
  counts identify their entity-local population with fail-closed registry
  contracts; numeric values are unchanged.
- **fix(cowork):** label downloadable bundle, package, landing-page, and
  archive counts as `Cowork-package-local` with exact fail-closed contracts.
- **fix(learning):** label vendor pack and category counts as
  `vendor-pack-local`, remove unscoped metadata totals, and register all 60
  rendered claims with the fail-closed count contract.
- **fix(learning):** separate learning-hub aggregate totals from per-pack
  counts with four exact population-labeled contracts.
- **docs(research):** mark the research index and published analyses as a
  dated historical snapshot with an exact source-commit evidence boundary.
- **docs(research):** distinguish the original index analysis claim from the
  source commit's separately documented evidence-corpus size.
- **docs(counts):** mark the documentation CTA's retained totals as historical
  copy and distinguish grading thresholds from corpus counts.
- **docs(counts):** record the completed E1.6 count-cohort inventory and
  closure evidence.
- **docs(governance):** classify every tracked `000-docs/*.md` file as
  `canonical`, `generated`, `frozen`, or `record`; enforce frozen-body and
  generated-index boundaries in the existing `doc-governance` gate.
- **fix(marketplace):** label generated social-card counts with the
  `marketplace-visible` cohort, canonical source, and reproducible resolver
  command; reject unreadable or malformed count inputs.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed (2026-08-17 — published count cohort labels)

- **Live marketplace skill totals now identify the population they count.** The homepage, explore,
  comparison, sponsor, and skills-directory pages label their unchanged totals as
  `marketplace-visible` and expose the canonical corpus-resolver command beside the value. A
  machine-readable registry and fixture-driven, fail-closed CI gate discover count expressions by
  meaning rather than one variable name across public Astro pages and components, rejecting any
  unregistered rendered expression—including unfamiliar or multiline identifiers split from the
  `skills` noun by adjacent markup—or pre/post-noun literal count, collection length, catalog count,
  unsafe or unreadable path,
  comment-only labels, and missing provenance without adding another required status context. The
  first inventory finds 51 public Astro source files. Forty-six non-global or point-in-time files
  plus the generated social image remain path-level deferrals; three local/query expressions on
  otherwise enforced pages are separately owned, expression-level deferrals. The gate binds every
  detected expression to its exact normalized registration—including any formatter call. Simple
  brace/interpolation wrappers normalize; compound outer expressions do not inherit an inner
  registration. Adding a second count or extending a registered expression therefore cannot bypass
  cohort governance. Frontmatter, script/style bodies, comments, and markup
  attributes are masked for the rendered count/label contract; provenance must be a standalone
  top-level component tag parsed outside quoted attributes and Astro expression strings, while
  self-closing head scripts remain correctly parsed. Quote- and brace-aware raw-text parsing prevents
  a quoted `/>` attribute from exposing paired script content as visible evidence and refuses
  malformed raw-text elements. Fixtures distinguish `/skills/` paths, prose durations, and adjacent
  time units, stars, notebook/agent populations, narrative heading shapes, collection renderers, and
  unrelated attributes from actual published skill totals without relying on count-like identifier
  names. Plain, canonical, and hyphenated count-label headings remain associated with adjacent
  counts. Nested object syntax remains part of its enclosing registered expression rather than
  being misclassified as a second rendered count.

### Fixed (2026-08-17 — canonical catalog name uniqueness)

- **The editable plugin catalog now contains 467 rows with 467 unique names.** Three redundant
  `claudebase` rows and one duplicate `geepers-agents` row were collapsed without renaming either
  plugin; the retained Geepers record preserves its richer component metadata and upstream links.
  The existing catalog invariant validator now fails closed on exact or normalization-equivalent
  duplicates, empty names, and non-string names, while `marketplace.json` and the README catalog
  navigation are regenerated from the corrected source.

### Fixed (2026-08-17 — README star-history chart)

- **The README star-history chart now uses the working `star-history.dera.page` mirror.** The
  image and its destination no longer depend on the broken tokenless upstream endpoint.

### Fixed (2026-08-17 — blog Markdown validation)

- **The newly published failure-diagnostics article now preserves blank-line boundaries around its
  numbered list.** This restores the repository-wide blocking Markdownlint gate without changing
  article wording or weakening MD032.

### Fixed (2026-08-17 — Actionlint bootstrap availability)

- **Actionlint now downloads its pinned release archive directly and verifies the upstream
  SHA-256 before extraction.** This removes the executable installer-script dependency on
  `raw.githubusercontent.com`, which returned HTTP 429 before lint execution in three consecutive
  PR runs, while preserving the blocking v1.7.4 lint command and fail-closed behavior.

### Added (2026-08-17 — deterministic generated skill projections)

- **The marketplace L0 skill index now has a fail-closed regenerate-and-diff gate.** A dedicated,
  unconditional `Validate Plugins` job renders `skills-index.json` in memory and byte-compares it
  with the Git index without touching the working tree, receiving no credentials and performing no
  network calls. Fixtures refuse mutated, untracked, symlinked, duplicate, and path-escaping
  candidates. Skill names now use a fixture-pinned ordinal sort instead of host-locale ordering, and
  any unreadable source aborts generation rather than emitting a partial artifact. The
  generated-artifact registry now separates four deterministic local
  projections from three external-stat snapshots and editorial marketplace data; this first E1.8
  slice gates one of four and leaves the full skill catalog, plugin catalog, and unified search
  projection explicitly pending rather than treating unlike populations as interchangeable.

- **The full marketplace skill catalog now has the same fail-closed content gate.** The reviewed
  baseline moves from 3,008 to 3,068 marketplace-visible skills: 96 source paths entered, 36 left,
  and 2,943 of 2,972 shared records changed as current skill and parent-plugin metadata replaced the
  stale 2026-06-02 projection. CI renders both skill projections in memory, compares both with
  stage-0 Git-index bytes, and refuses if either drifts; a matching L0 index cannot hide a stale L1
  catalog. Of the added and removed paths, 73 and 7 respectively are provenance-marked mirrors;
  only the generated projection changed, with zero mirrored `SKILL.md` edits. E1.8 deterministic
  content-drift coverage is now two of four. Plugin catalog and unified search remain separate
  follow-up slices.

- **The website plugin catalog is now a deterministic projection instead of its own historical
  input.** Its renderer no longer preserves stale rows or flags from `catalog.json`, emits runtime
  timestamps, or silently ignores malformed skill data. It derives 467 plugins in canonical
  catalog order and 3,068 distinct skill paths from the extended catalog plus the full skill
  projection; aliases that share one source receive the same source-derived count without
  double-counting the global total. The projection preserves the legacy default author for the two
  canonical rows without one and applies the governed retired-domain normalization to every output
  field. Fixture tests reject duplicate identities and paths, contradictory ancestry, traversal,
  malformed inputs, and staged drift. The unconditional
  generated-content job now byte-checks three of four deterministic marketplace projections with
  no new required context; unified search remains the final E1.8 slice.

- **Unified marketplace search now completes the deterministic projection gate.** The renderer
  removes its wall-clock timestamp and never reads the tracked output, then derives the current
  plugin, skill, documentation, agent, and hook search surface from governed repository inputs.
  It preserves the public item order and consumer fields, parses the repository's scalar, block,
  and inline-list documentation frontmatter forms, rejects malformed identities and symlinked or
  unreadable surfaces, writes atomically, and compares exact stage-0 Git-index bytes in `--check`
  mode without repairing drift. The shared unconditional `Validate Plugins` job now gates all four
  deterministic marketplace projections without adding a required status context or path filter.

### Fixed (2026-08-17 — release-note coverage evidence)

- **Release-note coverage now fails closed when Git tag evidence is absent or incomplete.** The
  newly pinned changelog-coverage check runs with fetched tags inside `Validate Plugins`, rejects tag
  enumeration failures, tagless or floor-incomplete clones, missing or duplicate release notes,
  non-regular note paths, and malformed version metadata, and carries deterministic red fixtures.
  Every release from v4.14.0 onward must have exactly one public changelog entry; older tags remain
  explicitly grandfathered.

### Fixed (2026-08-17 — JRig/Freshie authority boundary)

- **First-party operator guidance can no longer send JRig's runtime tables into the Freshie
  inventory.** The public validation skill and Plane evidence note now use
  `scripts/run-jrig-eval.sh`, which evaluates against a `/dev/shm` scratch database and delegates
  the governed `forge_proofs` write to the repository recorder. A provenance-aware, fail-closed
  check rejects direct `j-rig eval --db ...freshie/inventory.sqlite` commands and equivalent prose
  directives across active first-party operator surfaces, including `npx` invocations, folded
  and flow-style YAML commands, shell-escaped executable and flag spellings, statically resolvable
  executable/verb/flag/value indirection, ad hoc shell-function aliases, command substitution,
  parameter assignment, brace expansion, parsed YAML tags/keys/anchors, and active filesystem-glob
  path spellings. Command state follows shell ordering while assignments isolated by subshells,
  pipelines, background jobs, or skipped `&&`/`||` branches cannot overwrite parent state; quoted
  or escaped literal glob characters remain literal, and mirrors remain upstream-owned.
  The check runs inside the existing
  documentation-governance job and adds no required status context.

### Changed (2026-08-16 — build-derived marketplace data ownership)

- **Two build-only marketplace JSON projections no longer have a second committed claimant.**
  `readme-sections.json` is regenerated before both Astro build and local development, while the
  now-unconsumed `jrig-data.json` is generated only from local `forge_proofs` evidence and writes a
  deterministic empty map when that untracked database is absent. The shared generated-artifact
  registry and fail-closed tracking gate reject either file if it is committed again. Four audited
  build-derived files remain tracked because supported non-build consumers or prior-state semantics
  still read their committed bytes; Epic 1.8 owns their regenerate-and-diff controls. The unconsumed
  JRig projection is temporary: blueprint bead E9.2 still owns deleting it and its build step.

### Changed (2026-08-16 — retired public-domain containment)

- **First-party and generated surfaces now use only the live Tons of Skills domain.** A
  case-insensitive, fail-closed policy classifies every tracked occurrence before allowing it:
  editable sources and registered generated projections must be clean, while frozen standards,
  provenance-owned mirrors, and registered point-in-time exports remain byte-identical. The exact
  base contained 356 occurrences across 125 files: 292 actionable and 64 retained by policy.
  The existing documentation-governance job now runs the fixture-backed lint so mixed case,
  symlinks, malformed provenance, path traversal, and unregistered frozen paths cannot bypass it.
  Retained frozen and Freshie evidence is path-and-byte pinned, and the generated postprocessor
  skips every `.source.json` ancestry boundary. Historical claims use neutral redaction instead of
  rewriting past evidence; command and URL examples use the reserved non-resolving
  `retired-domain.invalid` host so they remain syntactically clear without reviving the dead
  property. Unsupported email identities are removed or mapped to the existing
  Intent Solutions contact, CLI catalog repair uses the verified canonical GitHub artifact, and
  the MCP preset catalog no longer advertises an unserved remote schema URL.
  [Exact-path supply-chain waivers](scripts/scan-allowlist.txt) record review of seven pre-existing
  dual-use capabilities whose files have only domain or contact changes in this slice; the
  underlying capabilities and scanner remain unchanged. The catalog schema permits an author
  email and author URL to be omitted, so the unsupported Mattyp address and marketplace attribution
  URL are removed while contributor credit is retained; the first-party Excel listing uses the
  matching Intent Solutions identity and contact.
  Retained-evidence, provenance, and generated-projection I/O is descriptor-bound with
  no-follow semantics where available, closing metadata-check/file-use races without weakening
  refusal behavior. Provenance absence is accepted only when the initial descriptor open reports
  no path; disappearance after a successful open is refused as a concurrent mutation.
  Cross-platform CLI validation now installs only the CLI package and its
  dependencies, avoiding unrelated native-workspace build failures while preserving every CLI
  runtime, package-manager, and operating-system assertion. Windows jobs use the maintained
  Node-20-compatible `node-gyp` release that recognizes the hosted runner's Visual Studio 2026
  toolchain when a transitive native dependency has no prebuilt binary. The production redirect
  assertion for the retired external domain is removed intentionally: the dead property is no
  longer an owned compatibility surface, while `tonsofskills.com` remains the governed live site.

### Fixed (2026-08-16 — curated asset content-type integrity)

- **Curated promotion now validates file content instead of relying on a NUL-byte prefix.**
  Recognized image, archive, document, font, and executable signatures are omitted from the
  text-only `skills/.curated/` projection, while misleading extensions, unreadable paths,
  symlinks, NUL-bearing data, non-UTF-8 payloads, and failed `git ls-files` enumeration fail
  closed in both build and drift-check modes instead of silently producing an empty mirror. The
  paired corpus correction replaces seven first-party text placeholders that masqueraded as
  `.png`, `.pdf`, or `.zip` files with truthful Markdown briefs or removes them, then rebuilds
  all 1,915 curated skills. The pre-change scorecard found 11 extension/byte mismatches: seven
  source artifacts and four generated curated copies; the corrected tree reports zero.

### Added (2026-08-16 — required supersession records)

- **Document supersession now has one reviewable record shape.** A filed template binds the frozen
  class marker, `SUPERSEDED–FROZEN` banner, per-section disposition, and `STANDARDS.md` canonical
  pointer into one pull request. A fixture-driven checker rejects missing components, placeholders,
  and fenced or commented decoys inside the existing documentation-governance gate. The same gate
  discovers every tracked completed record or malformed attempt; the five-document 6767 to 727
  reconciliation is the worked example. The corpus gate fails closed if no completed record remains,
  so removing that example requires filing a replacement record in the same change.

### Changed (2026-08-16 — single README metrics writer)

- **README counts now have one enforced writer.** The orphaned
  `scripts/update-metrics.mjs` command was removed, leaving
  `scripts/generate-readme-toc.mjs` as the only governed writer for catalog,
  skill, and agent counts. The Epic 1 measurement gate searches the full tracked
  executable tree, excluding explicit test and provenance-owned mirror surfaces,
  and fails closed if another production writer appears. A package-level planted
  writer proves the duplicate path cannot return silently.

### Changed (2026-08-16 — canonical skill cohorts)

- **Four binding skill-count surfaces now use one corpus resolver.** README
  metrics, marketplace discovery, canonical validation, and curated promotion
  consume sorted tracked paths from the named `marketplace-visible`, `graded`,
  `first-party`, `curated-mirror`, and `curriculum` cohorts. Fixture-tree tests
  pin provenance, hidden-path, traversal, and malformed-record behavior without
  freezing live corpus totals. The README badge now reports the 3,068
  marketplace-visible skills the site can render; the broader graded and
  first-party cohorts remain available under their own names. Status-quo
  compatibility is explicit: an orphan plugin with neither provenance nor a
  manifest remains first-party rather than being silently reclassified.
  Scorecard consumers must migrate row 1 from `plugin_skill_files` to the
  explicit `raw_tracked_plugin_skill_files` key; row 24 owns governed cohort
  counts. Both direct Git scans and caller-supplied tracked inventories reject
  `SKILL.md` symlinks before cohort membership is computed.

### Added (2026-08-16 — Epic 1 measurement harness)

- **All 62 modernization scorecard rows now have one deterministic evidence
  command.** `pnpm run measure:e1` measures the exact staged Git tree, preserves
  distinct plugin, validator, Freshie, generated-index, and terminal cohorts,
  and records explicit `not_reproducible` reason codes instead of copying stale
  numbers where the repository lacks committed evidence. Per-row commands are
  valid, `pnpm run measure:e1:check` is enforced inside the existing required
  validation aggregate, and fixtures prove ignored mirrors, unstaged edits,
  malformed protocols, bad signatures, missing inputs, and one-value drift fail
  closed.

### Fixed (2026-08-16 — malformed tool-allowlist enforcement)

- **Structurally malformed `allowed-tools` entries now fail closed.** Validator
  schema 4.0.0 reports malformed entries as errors at every tier while keeping
  well-formed unknown tool names advisory. Empty CSV fields and non-string or
  blank YAML-list members can no longer be normalized away. Corpus regression
  coverage proves zero first-party baseline debt and preserves the ten parseable
  mirror-owned Kobiton folded-scalar copies without editing mirrored content.

### Added (2026-08-15 — frozen prose-anchor gate)

- **Frozen 6767-h section anchors are now regression-gated.** The existing `doc-governance` job
  verifies the exact 21-section manifest, exercises valid and invalid citation fixtures, and proves
  that renaming a cited heading fails closed before schema references can silently drift.

### Added (2026-08-15 — generated documentation index)

- **The documentation estate index is now generated and drift-gated.** A deterministic generator
  builds `000-docs/000-INDEX.md` from Git's tracked documentation inventory, preserves archived and
  non-Markdown artifacts, and fails the existing `doc-governance` job when any count, row, order, or
  generator-owned reference text is stale.

### Added (2026-08-15 — document authority gate)

- **Documents can no longer self-grant canonical authority.** The existing
  `doc-governance` job now rejects an effective `AUTHORITATIVE` or `CANONICAL`
  declaration unless `STANDARDS.md` § Canonical documents links the claimant. The gate's first
  live run also demoted the subordinate schema 3.6.0 configuration guide from self-declared
  authority to a reference that points at its existing schema owners.

### Changed (2026-08-15 — documentation authority consolidation)

- **Superseded standards are explicitly frozen.** Documents 6767-a/c/d/e/h now identify
  their known-false authority or schema rules with evidence from the ratified modernization
  blueprint, while scaffold diagrams 6767-f/g are reference-only and the canonical 6767-b
  skill rubric remains untouched. ([#1197](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1197))

### Added (2026-08-15 — governed-brain v1.2.0)

- **The governed-brain mirror now documents hybrid local search and provenance limits.**
  Upstream v1.2.0 describes native FTS5 plus `qmd` reciprocal-rank fusion with a
  freshness/category rerank, and makes explicit that authenticated origin proves where a
  capture came from—not that its content is true. ([#1195](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1195))

### Fixed (2026-08-15 — governed-brain MCP startup)

- **`governed-second-brain` now provisions and probes all three pinned native modules before
  MCP initialization.** The v1.2.0 upstream mirror adds `sqlite-vec` to the runtime manifest,
  lockfile, and native-dependency readiness probe so partial dependency sets cannot skip
  provisioning and fail before the initialize response. Its install guide, plugin and marketplace
  manifests, and bootstrap guidance now describe all three lockfile-pinned native modules accurately.
  ([#1195](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1195))

### Fixed (2026-08-15 — catalog source-of-truth protection)

- **Tracked catalog shadows are forbidden.** The stale
  `.claude-plugin/marketplace.extended.json.backup` copy is removed, and the catalog
  invariant validator now fails closed if either canonical catalog is untracked or any
  additional tracked `marketplace*.json*` variant appears beside them. ([#1196](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1196))

### Added (2026-08-03/06 — site correctness gates)

- **`scripts/generate-og-image.mjs`** — renders the social card and gates it. `BaseLayout`
  had emitted `og:image` → `/og-image.png` on 3,830 pages since **2026-03-09**; the file was
  never committed, so every link preview of the site rendered imageless for five months.
  `--check` validates PNG signature, IHDR dimensions and minimum size — an earlier
  existence-only version was correctly flagged in review as reproducing the original failure
  one level up. ([#1156](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1156))
- **`scripts/check-security-headers.mjs`** — asserts the LIVE response carries the security
  headers. Not wired as a blocking gate: the headers are set in Caddy on the VPS, and a gate
  nobody in this repo can fix is a gate that gets disabled.
- **`scripts/check-changelog-coverage.mjs`** — every released tag at or above a pinned floor
  (v4.14.0) must have release notes. `/changelog` had 3 entries, newest v4.16.0, while the
  site ran v4.33.0. ([#1162](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1162))
- **`scripts/name-leak-gate.sh`** — anonymity gate for the rebrand's design reference,
  ported from the sibling blog repo; base64 patterns, scans untracked files.

### Changed (2026-08-02/04 — neobrutalist rebrand)

- **Marketplace visual system rebranded.** `--radius-*` → `0`; JetBrains Mono as the single
  typeface (Inter and Inter Tight removed, a strictly smaller font request); `--shadow-hard`
  as the only elevation device, rationed to one element per page. 373 hardcoded radius
  declarations flattened and 261 font references tokenised across 82 files; 9 genuine
  circles preserved after individual audit. `marketplace/DESIGN.md` §§ 1/3/4/6/8 amended
  first — § 8 previously banned the very device being adopted.
  ([#1152](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1152))
- **Homepage cut to a single action.** 1,742 lines → ~9 elements, leading with the
  Claude-Code-native `/plugin marketplace add …`. Nothing deleted: Killer Skill of the Week,
  Jeremy's Stash and the Stack Builder moved to `/collections`, the partner bar to
  `/community`.
- **Site chrome made model-agnostic** — third-party tool names dropped from the footer, hero
  subhead, meta description and social card. `Claude Code` retained only where it is the
  literal mechanism. ([#1159](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1159))
- **Retired URLs now served as real HTTP 301s** from Caddy rather than Astro `redirects`,
  which emit one thin meta-refresh page per entry (3 → 85 in one deploy). Three pre-existing
  entries stay in Astro because `check-routes.mjs` asserts those files exist.
  ([#1158](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1158))

### Fixed (2026-08-03/04 — defects found by probing the deployed site)

- **Security headers were inert.** `X-Frame-Options` and `X-Content-Type-Options` were
  declared as `<meta http-equiv>`, which browsers ignore outright — the site had no
  clickjacking or MIME-sniffing protection since **2025-12-24** while appearing to have both.
  Only `<meta name="referrer">` is a valid HTML form; the real headers now come from Caddy.
- **`/research/` had no design system.** It linked `/styles/global.css`, a source path never
  published (404 since **2026-03-04**), and lacked `tokens.css` entirely — so every
  `var(--*)` was undefined and six pages rendered as browser-default serif on a transparent
  background while loading a webfont they never applied. Also had no analytics tag, so that
  traffic was invisible in Umami.
  ([#1156](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1156),
  [#1157](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1157))
- **104 dead URLs**, 177 pageviews/week, the 404 page the 3rd most-served on the site — 76%
  under `/skills/` from rewritten SaaS packs. 81 now redirect to their vendor pack page.
- **42 dead in-content blog links** across 29 posts, each verified 200 at its new target
  before rewriting.
- **Homepage version resolution** walked a fixed `../../../../` from `import.meta.url`, which
  is a bundler path during an Astro build — it broke the VPS deploy. Now searches upward for
  the manifest that names itself the monorepo root, and fails soft.
  ([#1153](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1153))
- **Mobile footer collapsed to one 17-link column** below 480px; now 2-up with 44px touch
  targets, 1291px → 979px.
  ([#1154](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1154))
- **Stale fallback meta description** claiming "244 searchable agent skills and 259 plugins"
  against an actual 3,000+/470+. Rendered on zero pages, which is why it rotted unnoticed.

### Infrastructure (2026-08-03/04 — VPS, recorded in intent-os)

- **Security headers added to 8 of 16 hosts** that never imported the existing
  `(security-headers)` Caddy snippet, including the authenticated `erp.intentsolutions.io`
  and `mandy.intentsolutions.io`.
- **VPS build log made legible on failure.** `pnpm … | tail -3/-5` discarded the error, which
  a failing build reports early; now captured to a log, tailed on success and dumped in full
  on failure, with `CI=true` to stop pnpm's interactive prompt overwriting output.

### Fixed (2026-07-26 kernel-vendor-hash fail-open)

- **`kernel-vendor-hash` fail-open — the drift-watch was blind locally and printed a
  green check for a check that never ran.** Two defects, one symptom:
  1. **Wrong kernel path.** `KERNEL_REPO_PKG` resolved `REPO_ROOT/../../intent-eval-platform/...`
     → `~/intent-eval-platform/`, which does not exist. The canonical layout is
     `~/000-projects/{claude-code-plugins,intent-eval-platform}/` — the umbrella is **one**
     level up, not two. `K` therefore never resolved on a local run, so the `C ≤ K` and
     staleness legs were silently skipped. Replaced with a candidate list covering all
     three plausible layouts.
  2. **Dishonest verdict.** With `K` unresolved and no violations recorded, the CLI printed
     `✅ ordering + staleness OK (or skipped where inputs absent)` — a checkmark for a
     skipped check. Skipped legs now report `⚠️ INCONCLUSIVE … This is NOT a pass`, naming
     which of V/C/K was unresolved. The decision moved out of `printHuman` into an exported
     pure `verdictFor()` so presentation cannot fork from what the corpus asserts (the same
     no-logic-fork rule that keeps `evaluateCoupling` pure), with 5 new tests —
     **mutation-verified**: restoring the fail-open turns exactly 2 of them red.

  Consequence: a **real 17-day staleness breach** was reading as clean on every local run.
  CI was unaffected (it passes `--kernel-latest` explicitly) and had been correctly
  reporting `❌ VIOLATION: STALENESS` on the daily sweep since ~2026-07-16 — advisory,
  exit 0, so nobody saw it.

- **Stale hardcoded kernel-currency claims.** The report footer asserted
  `kernel pin tracks latest published (0.9.0)` as a string literal; that went false the
  moment `0.10.0` shipped, printing misinformation under a green check. It is now derived
  from live `C`/`K` state each run. The same false claim was corrected in the script's
  header docblock and in two places in `CLAUDE.md`, which now records that the pin is
  **behind** (`0.9.0` vs `0.10.0`, published 2026-07-09) and that catching up is a
  **lockstep** bump with `@intentsolutions/jrig-cli` (`0.1.2` → `0.2.0`), since jrig-cli
  pins `core` exactly and the two must stay hoisted to one copy.

  Not done here on purpose: **the pin itself is unchanged.** Bumping it re-baselines the
  DR-049 shadow-soak agreement numbers and is the owner's call, separate from this fix.

### Added

- **Required `skill-conform` gate** (`.github/workflows/skill-conform.yml`) — own
  branch-protection context running `audit-harness conform --strict` over the full
  marketplace corpus. Never inside `ci-required`'s `needs:` (doc 110 § 5).
  Companion **advisory** `skill-eval-advisory.yml` for changed skills with
  `eval-spec.yaml` (kill-switch `ENABLE_SKILL_EVAL`).
  ([#1118](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1118)).
- **`skill-creator` hand-authored `eval-spec.yaml`** (+ curated mirror + harness
  re-pin) so the j-rig nightly roster can grow 13→14
  ([#1118](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1118);
  j-rig [#234](https://github.com/jeremylongshore/j-rig-skill-binary-eval/pull/234)).
- **Eval-spec harness pin** — `.harness-hash-extra-patterns` pins
  `plugins/**/eval-spec.yaml` so `audit-harness verify` is a real gate
  ([#1117](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1117)).
- **`intent-labs-pack`** public skills (`audit-tests`, `validate-skillmd`) for the
  nightly roster
  ([#1116](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1116)).
- **Deterministic fork-safe CI failure-explainer** reusing j-rig `CheckResult`
  ([#1107](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1107)).

### Fixed (2026-07-23 marketplace gates)

- **VALID_TOOLS expanded to the canonical 43** + `Task`→`Agent` legacy alias
  (schema 3.16.0)
  ([#1115](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1115)).
- **Conform advisories cleared + escape-scan fail-open closed** via
  `audit-harness@1.3.1`
  ([#1108](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1108)).
- **Ruff pinned to 0.15.22** in `validate-plugins.yml` after 0.16.0 reformatted
  ~1132 SKILL.md files mid-flight (#1118 fix-up).

### Added (prior unreleased)

- **Operator guidance for the `dolt-mcp-vcs` MCP plugin** in `CLAUDE.md` (Freshie
  Inventory) — how to query the freshie Dolt run-history over MCP instead of raw
  `dolt sql`: start the `127.0.0.1:3308` sql-server first (it is not auto-started),
  load the `mcp__dolt-mcp-vcs__*` tools, the ⚠️ stop-the-server-before-`dolt-sync.py`
  lock caveat, and the recommend-only mutation gate (`push`/`merge`/`reset` never
  execute via MCP — DoltHub pushes stay on the one-way `dolt-sync.py` exporter).
- **Marketplace version reconstruction** (`scripts/reconstruct-versions.mjs`) —
  deterministic, idempotent tool that rebuilds every in-repo plugin's DISPLAY
  version from full first-parent git history (`minor` = lifetime update count,
  bulk sweeps counted once, `final = semver-max(existing, derived)`, never a
  downgrade) and writes the three browse-visible surfaces (`plugin.json`, the
  `marketplace.extended.json`/`marketplace.json` entries, and SKILL.md
  frontmatter) — leaving `package.json` and the external mirrors untouched. Fixed
  381/470 catalog entries + 2,463 SKILL.md files frozen at `1.0.0` while only the
  never-displayed `package.json` surface ever moved. Audit trail:
  `000-docs/708-AT-AUDT-version-reconstruction-report.json`
  ([#1086](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1086)).
- **Freshie inventory grading — notion-pack + supabase-pack raised to A-grade.**
  All 32 notion-pack skills (avg **80.8 → 94.6**, min 90) and all 30 supabase-pack
  skills (avg **88.7 → 93.6**, min 90) remediated to the 90+ marketplace bar via
  genuine progressive-disclosure extraction — deep code moved verbatim into 115
  new per-skill `references/` files, lean SKILL.md bodies (~140-160 lines), plus
  `Use when …` discoverability clauses and Authentication sections. snowflake-pack
  (75.6) is separately **waived** with a filed raise-later task — recorded, not
  delisted — settling issue #941 item 13 / closing #938
  ([#1092](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1092)).
- **`databricks-workspace-mcp` plugin** (mcp) — a TypeScript MCP server giving
  Claude Code typed, live access to the Databricks **control plane**: 8 read-only
  tools across clusters (list/get/events), instance pools, DLT pipelines
  (get/event-log), and Unity Catalog external-locations / storage-credentials —
  the endpoint families no managed Databricks MCP exposes
  ([#891](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/891)).
- **`beads-dolt` plugin** (mcp) — Dolt/DoltHub-aware upgrade to the beads (bd)
  task tracker: a diagnostic skill, five expert agents, and a wired dolt-mcp
  server. Registered for external-repo sync
  ([#892](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/892))
  and vendored into the catalog
  ([#895](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/895)).
- **`governed-second-brain`** (mcp) — local-first governed second brain, listed
  via `sources.yaml`
  ([#873](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/873)).
- **`.greptile/` advisory code-review config** — `config.json` + `rules.md` +
  `files.json` encoding the repo's structured review invariants
  ([#897](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/897)).
- **Synced-plugin lint-exclusion drift gate** (`scripts/check-synced-lint-exclusions.mjs`)
  — CI gate asserting every external-synced plugin is excluded from markdownlint
  and ruff, failing with the exact lines to add
  ([#898](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/898)).
- **kernel-vendor V≤C≤K version-coupling gate** (advisory) + ordering-invariant
  test corpus
  ([#868](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/868),
  [#888](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/888)),
  and **kernel-shadow validation** (advisory soak, DR-049)
  ([#855](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/855),
  [#862](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/862)).
- Marketplace **`/grading` rubric page** + drift-detection test
  ([#847](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/847)).

### Changed

- **CI/CD — auto-bump now moves all four version surfaces (recurrence fix).**
  `scripts/auto-bump-changed-plugins.mjs` previously edited only `package.json`
  (the npm-publish surface nothing browsable reads), so every display surface
  re-froze after each PR. It now also minor-bumps `plugin.json`, both catalog
  entries, and the PR's changed SKILL.md frontmatter on every bump — riding the
  same `bumpDecision` idempotency guard — so the version freeze cannot regrow.
  Unit tests extended 6 → 14
  ([#1086](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1086)).
- **Kernel coupling — declared `@intentsolutions/core` pin `0.4.1` → `0.9.0`.**
  Bumped the exact (no `^`/`~`) `C` (CCPI-declared kernel) in `package.json` to the
  latest published kernel, re-vendored `V` (the installed snapshot in
  `node_modules`) via `pnpm install`, and re-mirrored the `KERNEL_PIN` literal in
  `scripts/kernel-shadow-validation.mjs`. The `authoring/v1` schema family is
  byte-frozen across kernel versions, so the shadow lane reads an identical
  frontmatter contract and the V≤C≤K coupling is consistent at `V=C=K=0.9.0`. This
  is a governance/coupling update only — both kernel lanes stay **advisory**; the
  advisory→authoritative flip remains a separate, gated step.
- **Schema 3.10.0 → 3.11.0 — kernel-strict agent gate.** Every authored agent
  must carry the kernel-floor 8 fields + the enterprise live set (errors at every
  tier); banned fields are errors; added a body-vs-allowlist consistency check
  (an agent invoking an `mcp__server__tool` outside its `tools` allowlist is an
  error). All 317 in-repo agents elevated to A-grade
  ([#878](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/878),
  [#881](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/881),
  [#883](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/883),
  [#887](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/887)).
- **AI PR reviewer churn** — adopted Greptile (replacing CodeRabbit + Gemini),
  then paused Greptile on its 50-review/month quota and re-enabled Gemini Code
  Assist; CONTRIBUTING wording made tool-agnostic. The PR pre-screen LLM also
  switched Groq → DeepSeek
  ([#852](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/852),
  [#893](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/893),
  [#899](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/899)).
- **`databricks-pack` v1.1.0 deprecation release** — deprecation banners on all 24
  v1 skills + a v1→v2 migration map, ahead of the live-detection v2 rebuild
  ([#889](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/889)).
- **Branding** — purged the "CCP" acronym → "CCPI" across live surfaces
  ([#885](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/885));
  removed Nixtla branding from eval tools, catalog data, and sponsor surfaces
  ([#853](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/853),
  [#858](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/858)).
- Re-pinned `@intentsolutions/core` to exactly `0.4.1`; the kernel `authoring/v1`
  CHANGELOG is now canonical for kernel-tracked fields
  ([#857](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/857),
  [#864](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/864)).

### Fixed

- **Version-surface completeness** — an adversarial re-audit of the reconstruction
  (#1086) found its `--check` verified only `plugin.json` vs the catalog (never
  SKILL.md frontmatter or `marketplace.json`), so it falsely reported "all surfaces
  agree" while 33 pack SKILL.md files (clerk/supabase/notion) had drifted a minor
  behind and 3 plugins had been silently downgraded a full major
  (`claude-never-forgets` 1.0.0→0.21.0, `formatter` 2.1.0→1.26.0,
  `browser-compatibility-tester` 2.0.0→1.20.0 — the reconstruction floored on the
  catalog value alone). `--check` now verifies **all three** display surfaces and
  reports catalog dirs lacking a `plugin.json`; the reconstruction floor is
  `max(catalog, plugin.json)`; and `auto-bump-changed-plugins.mjs` stamps **every**
  SKILL.md in a bumped plugin (via `findSkillFiles`), not just diff-changed ones, so
  sibling skill versions can no longer strand. Drifted files restamped and the three
  downgrades restored to `1.21.0` / `2.26.0` / `2.20.0`
  ([#1098](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1098)).
- **CI/CD — supply-chain scanner skips version-only diffs.**
  `scripts/scan-synced-content.mjs` (`--changed-only`) now excludes any changed
  `plugins/**` file whose entire diff vs base is the version string
  (`isVersionOnlyChange` + 7 regression tests). A mass version reconstruction /
  auto-bump edits the version line in thousands of first-party SKILL.md +
  plugin.json files, which previously pulled every one into a full re-scan and
  surfaced pre-existing documented dual-use examples (the `secret-exfil-cooccur`
  own-service-API false positive) as fresh CHALLENGEs — 820 on the reconstruction
  PR. The skip is precise, not a bypass: any other changed line keeps the file in
  full scope, so a payload cannot hide behind a co-changed version bump; REFUSE
  grading and fail-closed behavior are untouched
  ([#1086](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1086)).
- **External-plugin sync pipeline hardening** — a multi-agent audit found 16 bugs;
  all fixed across two passes
  ([#896](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/896),
  [#898](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/898)):
  preserve the executable bit + exact bytes (Buffer read + chmod — no more binary
  corruption), run the full `pnpm run sync-marketplace` onboarding (package.json +
  README TOC), a unique per-run `automation/` branch (no shared-branch clobber, no
  auto-bump version drift, no PR-create strand), serialized concurrency, orphan
  prune via a persisted manifest, a partial-sync gate, and catalog-seam formatting.
- **CI / workflow hygiene** — resolved all 75 actionlint/shellcheck findings across
  15 workflows; per-domain lint workflows + path-routing; PR-noise reduction + dead
  workflow pruning
  ([#839](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/839),
  [#861](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/861),
  [#869](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/869)).
- **plane-sync** — HTML-escape the issue body before `description_html` injection
  ([#882](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/882)).
- **claude-never-forgets** — quote plugin paths to handle spaces on Windows
  ([#880](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/880)).
- Real `allowed-tools` validation + missing-name diagnostic in the validator
  ([#860](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/860)).

## [4.33.0] - 2026-05-25

Cowork pipeline correctness pass — the `/cowork/` page is now a
deterministic function of the catalog from disk through deploy, with
a CI gate that fails the build if anyone regresses the contract. Plus
the agency-os plugin lands, a new Unicode hygiene CI gate hardens
contributor PRs against [Trojan Source](https://trojansource.codes/)
attacks (CVE-2021-42574), and the `/cowork/` page itself gets the
prereq banner + setup-guide rewrite that users have been missing.

### Added

- **agency-os plugin** (productivity) — AI agency + Notion board
  orchestrator. Adds the first `productivity/agency-os/` entry to the
  catalog ([#709](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/709)).
- **Unicode hygiene CI gate** (`scripts/validate-unicode-hygiene.py` +
  `.github/workflows/validate-unicode-hygiene.yml`) — blocking gate
  that rejects bidi-override + tag-character abuse in `SKILL.md`,
  `plugin.json`, agent, and command files. Defends against
  [Trojan Source](https://trojansource.codes/) (CVE-2021-42574) and
  the [trapdoor / tag-character class](https://www.unicode.org/reports/tr39/#bidirectional_controls)
  of homoglyph attacks. `--strict` mode also blocks zero-width and
  format characters outside the BOM position. Full regression suite
  at `tests/test_validate_unicode_hygiene.py`
  ([#777](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/777)).
- **Idempotent cowork build pipeline + drift gate** — three changes
  that make the cowork download backend self-healing
  ([#780](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/780)):
  - `scripts/build-cowork-zips.mjs` now wipes
    `marketplace/public/downloads/{plugins,bundles}` before each run.
    Output state is exactly what `marketplace.extended.json` declares
    — no more, no less. Removes accumulated orphans in local dev
    (six found this session: `general-legal-assistant`, `langchain-pack`,
    `windsurf` + `automation`, `code-quality`, `finance` bundles).
  - `scripts/validate-cowork-manifest.mjs` (new) — drift gate. Seven
    checks for catalog ↔ manifest ↔ disk alignment, including the
    orphan-zip direction that the existing `validate-cowork-downloads.mjs`
    doesn't cover. Wired into `marketplace/scripts/build.mjs`
    (`cowork:validate` after `cowork:zips`) AND
    `.github/workflows/validate-plugins.yml` as the named
    `Validate Cowork Manifest Drift` step.
  - `CLAUDE.md` § "Auto-cowork contract" — documents the author
    flow (catalog edit + `pnpm run sync-marketplace` is the entire
    authoring step), pipeline determinism, deploy propagation via
    `rsync --delete`, and the deliberate decision NOT to wire
    `cowork:zips` into `sync-marketplace` (cadence mismatch).

### Fixed

- **`/cowork/` page content gap** — adds an amber prereq banner above
  the hero surfacing install prerequisites, rewrites the setup guide
  for clearer step ordering, and adds an official-resources block
  linking to upstream Anthropic Cowork docs so users aren't routed
  only through this marketplace
  ([#781](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/781)).
- **`.gitleaks.toml` allowlist drift** — extends the existing
  `marketplace/src/data/*.json` allowlist scope to
  `marketplace/public/data/*.json` (the runtime mirror produced by
  `marketplace/scripts/build.mjs`). Both copies bundle SKILL.md body
  HTML (which is allowlisted directly); the bundled mirror must
  follow suit or every catalog regen turns CI red on benign
  documentation examples (e.g., Supabase local-dev demo JWTs with
  `iss: supabase-demo`)
  ([#781](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/781) co-fix).

### Changed

- **CHANGELOG, CLAUDE.md, AAR docs, blog posts** — repo-side records
  of the 2026-05-22 → 2026-05-24 CI hardening campaign filed as
  `000-docs/270-AT-AACR-2026-05-22-to-24-ci-hardening-9pr-arc.md`
  ([#775](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/775)).
  Two tonsofskills.com blog posts published documenting the
  self-expiring report-only CI gate pattern and the Unicode hygiene
  gate as same-day trapdoor defense.

## [4.32.0] - 2026-05-24

Single-session CI hardening campaign — 9 sequential PRs took main from
2 required gates to 10, with the underlying violations fixed in-PR
(no report-only crutch left in the pipeline). External contributor
PRs now hit a real bar before merging. Plus ~970 MB of dead
scaffolding removed from the repo root.

### Added

- **10 blocking required CI gates on `main`** (was 2: `validate` +
  `marketplace-validation`). New gates: `eslint-check`, `format-check`
  (prettier), `ruff-check`, `ruff-format-check`, `shellcheck-skills`,
  `typescript-coverage-audit`, `skill-codeblock-syntax`, `markdownlint`.
  Cleanup-arc PRs #764 → #772.
- **`ruff.toml` at repo root** — single source of truth for Python lint
  policy. Selects E4/E7/E9/F curated default; ignores E402 (legit
  sys.path manipulation in plugin entry points) and E741 (short loop
  counters in generator scripts) (#765).
- **`.shellcheckrc` at repo root** — disables SC1090/SC1091 (dynamic
  source paths in plugin entry points), SC2155 (declare-and-assign
  stylistic), SC2034 (unused-var analysis too imprecise across sourced
  files) (#768).
- **`.markdownlint-cli2.jsonc` at repo root** — single source of truth
  for markdown lint policy across 10,468 markdown files (#767 + #772).
- **`tests/lib/.gitignore` allowlist for AA-AACR session reviews**
  (already merged in #760, retained).

### Changed

- **730 ruff errors → 0** across plugins/, scripts/, freshie/. 562
  auto-fixes + 33 unsafe-fixes + 33 typing imports added to mass-
  generated scripts + 1 real bug fix (`webhook_handler_template.py`
  needed `nonlocal delay` in a retry-decorator closure) + 374 files
  reformatted via `ruff format` (#765).
- **244 ruff errors → 0** on PR E's 47 renamed `.sh` → `.py` files
  (mis-extensioned Python scripts that had never been ruff-checked)
  (#770).
- **223 shellcheck issues → 0**. 47 `.sh` files renamed to `.py` (per
  shebang), 11 real bug fixes (`pip install pkg[x]>=1.0` interpreted
  as redirection, `trap` quoting, `[ -f X -o -f Y ]` POSIX bug, getopts
  spec duplications in nmap template, etc.) (#768).
- **~60,000 markdownlint errors → 0** across 10,468 files. Bulk
  `--fix` pass (PR #767) handled ~58k mechanical fixes; PR #772
  cleaned the residual 80 (broken anchors in wondelai case-studies via
  TOC-link regeneration, `|` escaping in backtick code spans, table
  column-count fixes, heading-increment demotions, missing image
  alt-text on shield badges).
- **97 codeblock-syntax failures → 0** across SKILL.md / README.md
  files. All were mislabeled language tags: 66 bash blocks that were
  CLI usage with `<placeholder>` brackets (relabeled to `text`), 24
  javascript blocks containing Firestore Security Rules DSL or
  pedagogical vulnerable+secure comparisons, 7 python blocks
  containing ASCII trees / JSON / shell. TypeScript dropped from
  `CHECKABLE` (illustrative fragments reference external types) (#769 and #771).
- **9 plugin-test failures → 0** in `widened-test-loop` across the 10
  candidate plugins (concentrated in `web-to-github-issue`). 4 stale
  error-message expectations updated, 4 `verifyRepo` calls refactored
  to return `{exists: false, error}` instead of throw (cleaner API +
  matched test contract; sanitization preserved), 1 `parseSearchResults`
  test updated to match safer URL-validation behavior (#770).
- **TypeScript coverage**: 9 uncovered packages → 0. Added
  `"typecheck": "tsc --noEmit"` to 7 MCP packages with existing
  `tsconfig.json`; `audit-typescript-coverage.py` updated to exclude
  `**/assets/**` (illustrative skill-doc examples) and
  `**/.vitepress/**` (docs-site config) (#769).
- **47 `.sh` → `.py` file renames** for mis-extensioned scripts in
  ai-ml/, database/, devops/, productivity/ skill directories (#768).
- **374 Python files reformatted** via `ruff format` for project-wide
  consistency (#765).
- **9 historical AA-AACR session reviews committed** to `000-docs/`
  per #760's allowlist (Lumera memory impl, Beads epic AAR, CLI v2.0
  release, phase 1-6 AARs, metrics canonicalization — all from Dec 2025).
- **148 `implementation.md` files: leading `# Title` → `## Title`**
  to fix MD001 heading-increment violations en masse (#767).
- **6 indented code blocks → fenced** in 3 deprecated `commands/`
  files; 4 setext headings → atx; 3 image alt-text additions.

### Removed

- **~970 MB tracked content + ~1.2 MB working-tree cruft** (#766):
  - `backups/` 882 MB — old migration backups, replaced by git history
  - `functions/` 83 MB — Firebase functions, dead post-VPS-migration
  - `planned-skills/` 4.6 MB — skill-generation scratch
  - `archive/` 416 KB — old release zips
  - `workflows/` 32 KB — legacy bmad metadata
  - `consistency-reports/` 20 KB — one-off audit output
  - `redirects/` 12 KB — empty stub
  - `prompts/` 4 KB — single vertex-life-sciences file
  - Tracked legacy files: `config.zcf.json`, `Dockerfile.test`,
    `docker-compose.test.yml`, `firebase.json`, `firestore.rules`,
    `.firebaserc`, `test_youtube_strategy.py`, `setup.sh`,
    `create-tasks.sh`
  - Untracked cruft: `asset_generation*.log` (280 KB), `package.json.tmp`,
    `_PRESERVE_MIGRATION/`, `reports/`, `test-results/`, `claudes-docs/`,
    `__pycache__/`
- **Human-triggered auto-merge** disabled at the repo level
  (`allow_auto_merge=false`). Workflow `maintainer-ready-automerge.yml`
  removed. Only `automerge.yml` for dependabot minor/patch bumps
  remains. Human-author PRs have no auto-merge path (#763).
- **Repo `CLAUDE.md` "Legacy Root Files" section** — no longer
  accurate, nothing legacy at the root.

### Fixed

- **`maintainer-ready-automerge.yml` workflow** removed entirely (#763).
- **`catalog-format-guard` CI step**: `actions/checkout@v6` no longer
  persists credentials reliably for subsequent git-fetch operations.
  Added explicit `fetch-depth: 2` + `persist-credentials: true` to
  the validate job's checkout (#770).
- **`auto-bump-on-pr.yml`** — pre-existing patch-bump automation
  retained, now coexists with the larger blocking-gate stack.

### Security

- All 47 `.sh` files renamed to `.py` (mis-extensioned Python scripts)
  no longer mislead readers about their executable shape.
- Markdownlint enforcement catches `Authorization: Bearer ...` patterns
  in skill docs going forward via the regex-escape fix on table cells.

## [4.31.0] - 2026-05-08

Four-day sprint after v4.30.0 — single-session execution of the "Use the
Printing Press to Learn" plan, which mapped Matt Van Horn's CLI Printing
Press against the IS stack and shipped the four real gaps it surfaced:
generation capability (`/skill-creator --forge`), NOI cultural gate,
JRig behavioral evaluation integration end-to-end, and marketplace trust
signals (JRig-Verified badge + forge-generated provenance pill). The
forge workflow is no longer theoretical — `plugins/productivity/plane/`
is a Grade A (97/100) plugin produced through all 8 forge gates with a
full `.forge/` audit trail. JRig itself got real TypeScript code
(`spec-sources` module + 22 tests, ships in `j-rig-skill-binary-eval`).

### Added

- **`/skill-creator --forge` mode** (local skill, v8.1.0) — 8-gate workflow
  for generating plugins from API surfaces: NOI hard block (the API's
  "secret identity" must be named in 6–10 words before any code is
  written), ecosystem absorb (catalog 3–5 competing tools, gap analysis),
  API surface research, domain archetype detection, compound command
  design, generation, mandatory `/validate-skillmd --thorough`,
  PR + catalog wiring. Produces a `.forge/` audit trail (research.md,
  ecosystem.md, proofs.md) alongside the standard skill scaffold.
- **`/skill-creator --reforge` mode** (local skill, v8.1.0) — Regenerate
  an existing forge-generated plugin against the current API surface to
  fight catalog rot. Preserves NOI from `references/noi.md`, re-runs
  gates 3–7, auto-bumps version per detected change scope (patch for
  endpoint adds, minor for new compound commands, major for breaking
  surface changes).
- **`plugins/productivity/plane/`** (#703) — First end-to-end forge
  dogfood. NOI: "Plane is a team behavior observatory." Five compound
  commands (`/plane-cycle-velocity`, `/plane-stale-tickets`,
  `/plane-reviewer-gate-strength`, `/plane-priority-drift`,
  `/plane-cross-project-load`) that JOIN across multiple Plane endpoints
  to surface observations no single endpoint exposes. Validates Grade A
  (97/100), Tier 2 GREEN, JRig 12/12 deterministic checks. 1,123 lines
  across 8 files; full `.forge/` audit trail visible to anyone reviewing
  how the plugin came to exist.
- **Tier 2 static production gate in the validator** (#698) — Five
  deterministic checks added to `scripts/validate-skills-schema.py` (273
  lines Python). Run alongside the standard 100-point rubric: (1)
  `allowed-tools` accuracy — declared tools must appear in the body;
  (2) auth-documented — API surface mentions require an auth method
  documented; (3) dead-code — literal-false branches detected; (4) tool
  safety — unscoped Bash + Write/WebFetch requires Safety Justification
  section; (5) orchestration bounds — skills shouldn't claim cross-skill
  orchestration (with negation-marker guards to avoid false-positives on
  documentation). 180 new errors surfaced across the 3,535-skill catalog
  on first run; grade distribution unchanged at 68.9% A+B.
- **JRig-Verified marketplace badge data flow** (#696, #699, #700) —
  Three-PR trio that lights up the badge end-to-end: (1) plugin detail
  page renders `plugin.jrig?.verified` as a green "JRig-Verified · N/7
  layers" pill; (2) Freshie schema migration adds `jrig_passed`,
  `jrig_tier_blocked`, `jrig_baseline_delta` columns to `skill_compliance`
  - new `forge_proofs` table for per-plugin verification evidence;
    (3) new build step `enrich-jrig-data.mjs` reads `forge_proofs` via
    sqlite3 CLI, writes `marketplace/src/data/jrig-data.json` for the
    detail-page overlay. Build pipeline now 7 steps (added `jrig:enrich`).
- **Per-plugin `/plugins/<name>/verification` route** (#702) — 316-line
  Astro page that the JRig-Verified badge clicks through to. Two
  states: VERIFIED (shows passing-layer fraction, baseline delta, 7-layer
  framework breakdown) or PENDING (explains the two paths plugins reach
  JRig — forge generation or manual `j-rig eval`).
- **NOI tagline + forge-generated provenance pills** (#696) — Optional
  fields on plugin detail pages: italic NOI-framed subtitle under plugin
  name; indigo "Forge-generated" pill when `plugin.json` carries
  `"generated": true` or `"author_type": "forge"`. Anti-spam moat per
  Phase 5A: marketplace surfaces forge provenance for reviewer + end-user
  visibility.
- **Curated "Start here" homepage section** (#701) — 5-plugin onboarding
  pack between Hero and Jeremy's Stash. Eliminates "what should I
  install?" friction with 343 plugins to choose from. Each card: NOI
  tagline, "why this is in the pack" paragraph, copy-friendly install
  command. Editorial picks; quarterly rotation; re-evaluation against
  install velocity once Phase 5B telemetry lands.
- **JRig spec snapshots in `000-docs/`** (#695) —
  `anthropic-skills-spec-snapshot.md` + `agentskills-spec-snapshot.md`
  capture the source-of-truth specs JRig and the IS validator validate
  against. Versioned; refresh quarterly via PR cadence (live-fetch from
  CI is a rate-limit + flakiness risk). Same files mirror in
  `j-rig-skill-binary-eval/references/specs/`; future enhancement: sync
  script that diffs the two locations and fails CI on divergence.
- **JRig spec-sources TypeScript module** (j-rig PR #41, real TS code) —
  192-line module + 22 passing tests (full repo suite still green at
  173/173). Public API: `loadSpecAuthority()`, `classifyField(name)`,
  `isValidEffort(value)`. Records snapshot IDs so eval reports can detect
  spec drift in either direction. Quarterly refresh becomes a single PR
  cadence with the test suite catching divergence between the snapshot
  files and the embedded TypeScript constants.
- **IS-extension fields documented in `plugin-schema.md`** (#697) — Two
  provenance fields (`generated`: boolean, `author_type`:
  "human" | "forge") set by `/skill-creator --forge`. Documented
  alongside the 15 Anthropic spec fields. Stripped from `marketplace.json`
  (CLI catalog) by `sync-marketplace.cjs`'s `DISALLOWED_KEYS` set so the
  CLI never sees website-only metadata.
- **Master skills spec 3.1.0 → 3.3.1** (#693) —
  `000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md` brought into
  alignment with the validator's actual schema 3.3.1 behavior: 8-field
  enterprise required set (`name, description, allowed-tools, version,
author, license, compatibility, tags`) is the IS marketplace tier
  requirement; missing any of these = ERROR (not warning). The 3.0.0–
  3.2.0 demotion-to-polish direction was reverted in 3.3.0; the doc never
  absorbed that revert until this PR. `allowed-tools` documented to
  accept all three forms (CSV string, space-separated string, YAML list).
- **Freshie discovery run 7 + compliance population under v7.0** (#694) —
  Refreshed `freshie/inventory.sqlite` with current validator scores.
  Anomalies dropped 44 → 7; duplicate file groups 41 → 0; cross-references
  301 → 684. 2,429 of 3,535 skills (68.9%) production-ready (A+B grade)
  at marketplace tier under schema 3.3.1.

### Changed

- **`scripts/sync-marketplace.cjs` `DISALLOWED_KEYS`** (#697) — Extended
  to strip 4 new website-only display fields from `marketplace.json`:
  `tagline`, `jrig`, `generated`, `author_type`. The website renders
  these from `marketplace.extended.json`; the CLI catalog never sees them.
- **`marketplace/scripts/build.mjs` step count** (#700) — 6 → 7 steps;
  added `jrig:enrich` after `catalog:sync`, before `search:generate`. New
  step reads `forge_proofs` from Freshie and writes `jrig-data.json` for
  the plugin detail page overlay.
- **`/validate-skillmd` v4.0.0 → v5.0.1** (local skill) — Four-tier
  validation framework: Tier 0 (locate), Tier 1 (standard or marketplace
  grading), Tier 2 (static production gate), Tier 3 (JRig opt-in via
  `--thorough`). Reconciled with JRig's actual CLI surface (`j-rig` with
  hyphen, `j-rig check`, `j-rig eval`) after initial documentation
  documented imaginary flags.
- **`/skill-creator` v7.0.0 → v8.1.0** (local skill) — Added `--forge`
  and `--reforge` modes (see Added section). Default `--create` mode
  unchanged for hand-authored skills.
- **`CLAUDE.md`** (#704) — Refreshed after the plan landed: plugin count
  425 → 427, schema 3.0.0 → 3.3.1, build pipeline 6 → 7 steps, new
  "Forge-Generated Plugins" subsection documenting `.forge/` pattern,
  new top-level "JRig — Behavioral Evaluation Integration" section
  explaining the full data flow. +70 / -13 lines, 22-section structure
  preserved.

### Fixed

- **JRig epic-index README accuracy** (j-rig PR #40) — The README said
  "Currently Active: Epic 01" with epics 02–10 marked Pending; reality
  was all 10 epics shipped 2026-03-29 at v0.14.0 with 6 CLI commands
  wired. Stale README triggered a false "JRig isn't ready" red-team
  finding in the downstream IS plan. Updated with merge dates per epic
  and a CLI-surface section.
- **Umami custom events + data-domains spam guard** (#692) — Wires
  marketplace events through Umami analytics; adds the data-domains
  guard to the analytics config so spam events don't pollute the
  legitimate signal.
- **Homepage npm-marquee total downloads relabel** (#691) — "30d" →
  "total downloads" reflects what the badge actually shows.
- **npm-stats fetch throttling** (#689) — Restores live total on the
  marquee; throttles fetch to dodge registry rate limits.
- **Homepage 30d total drop** (#688) — Dropped the "last 30d" segment
  from the npm marquee.
- **Header navigation cleanup** (#686) — Removed the ⌘ icon box from
  the header per design review.

### Security

- No new vulnerabilities introduced. Validator's Tier 2 tool-safety
  check now flags unscoped `Bash` + `Write`/`WebFetch` declarations
  without a Safety Justification section as ERROR at marketplace tier
  — surfaces the curl-pipe-shell exploit surface for review on every
  validation run.

### Plan reference

This release is the materialization of the "Use the Printing Press to
Learn" plan into shipped code. Full session breakdown in the email
record `<2282a9fe-14e1-d228-ded3-fd85c18aa1f7@intentsolutions.io>` and
in the AAR at `000-docs/032-RL-REPT-claude-code-plugins-release-v4.31.0.md`
(generated alongside this release).

## [4.30.0] - 2026-05-04

Two-day sprint following v4.29.0 — landed the same-session "ship workaround
→ file tracking issue → ship the real fix" loop several times in public, plus
the **guidewire-pack v2.0.0 rebuild** (24 skills → 10 production-engineer
skills), a new marketplace plugin (`engineer-design-diagram`), enforcement
of the lessons learned during v4.29.0 (pre-commit hook, sync-marketplace
orchestrator, pre-push warning), and post-release Freshie + compliance work
that surfaced + partially remediated 115 D+F skills.

### Added

- **`engineer-design-diagram` marketplace plugin** (#665) — Ports the global
  skill at `~/.claude/skills/engineer-design-diagram/` (live since 2026-04-19)
  into `plugins/devops/engineer-design-diagram/` so any Claude Code user can
  install it. Generates production-grade architecture/sequence/delta/drift
  diagrams as self-contained dark-themed HTML with inline SVG, grounded in
  real repo topology via DCI. Four modes (`/design:generate`, `/design:diff`,
  `/design:trace`, `/design:watch`). v0.2.0, A-grade (96/100). Closes
  `claude-2rb6.2` and `claude-2rb6.10`.
- **`guidewire-pack v2.0.0`** (#668-#678) — 11-PR coordinated rebuild of the
  Guidewire InsuranceSuite skill pack. **24 skills → 10 production-engineer
  skills**, each addressing real production failure modes. Highlights:
  - Rebuilt to A-grade: `install-auth`, `sdk-patterns`, `local-dev-loop`,
    `core-workflow-a` (PolicyCenter), `core-workflow-b` (ClaimCenter)
  - New unified skills (merging multiple v1 skills):
    `security-and-rbac` (basics + enterprise-rbac),
    `observability-and-incident-response` (3-skill merge),
    `ci-cd-pipeline` (4-skill merge: ci-integration + deploy-integration
    - multi-env-setup + prod-checklist),
      `migration-and-upgrade` (2-skill merge),
      `webhooks-integrations` (rename + deepen of webhooks-events)
  - Cuts (deferred or removed with rationale): `data-handling`,
    `reference-architecture`, `performance-tuning`, `cost-tuning`
  - Pack-level: `package.json` 1.0.x → 2.0.0, README rewritten to 10-skill
    production-problem framing
- **`contributing-clanker` v0.1.x community plugin** — New scaffold under
  `plugins/community/`, three patch releases (v0.1.0, v0.1.1, v0.1.2) over
  the two days for runtime correctness fixes synced to the marketplace.
- **Repo-wide automation** (#667) — `pnpm run sync-marketplace` is now an
  orchestrator that chains `sync-marketplace.cjs` + `generate-plugin-package-jsons.mjs`
  - `generate-readme-toc.mjs`. New pre-commit hook auto-runs the chain when
    `marketplace.extended.json` is staged and auto-stages derived files. New
    pre-push hook warns when the local branch is behind `origin/main`. The
    legacy single-step JSON-strip is preserved as `pnpm run sync-marketplace:json-only`.
- **2026-05-03 case study** (`marketplace/src/content/blog-posts/`) —
  Tier-3 case study post on the v4.29.0 release ceremony + the same-session
  loop closure pattern.

### Fixed

- **README ↔ Prettier ↔ generator 3-authority conflict** (#658) — Closes
  issue #657 in the same session it was opened. Both
  `scripts/generate-readme-toc.mjs` and `scripts/render-spotlight.mjs` now
  pipe their spliced output through `prettier.format()` (with
  `prettier.resolveConfig()` for project settings) before writing/comparing.
  Removes the README.md exclusion from `.prettierignore`. All three gates
  (`prettier --check`, generator `--check` modes) pass simultaneously, in any
  order. Workaround → real-fix loop closed in ~2 hours.
- **D+F skill remediation, partial** (#661) — Schema 3.3.1's stricter rubric
  surfaced 115 D+F skills (regression from the post-v4.24.0 "Zero D/F"
  baseline). Added `tags` + `compatibility` frontmatter to **102 skills**
  missing both fields (94 in `plugins/ai-agency/tonone/`, 8 across
  saas-packs). Result: 115 → 89 D+F (-26 grade improvements). Remaining 89
  are score 67-69 (1-3 points below C threshold) blocked by missing
  `references/`, `examples/`, `scripts/` subdirectories — a SaaS pack
  scaffolding template defect tracked in #660.
- **Post-v4.29.0 quality sweep** (#656) — Cleared pre-existing ESLint errors
  (`scripts/bulk-bump-versions.mjs:277` control-char regex,
  `scripts/check-official-links.mjs:138` unnecessary-escape) that the new
  root config from #629 surfaced for the first time. Plus a repo-wide
  Prettier `--write` sweep (40 files, all cosmetic — `*em*` → `_em_`,
  blank-line normalization). Plus `jeremy-adk-software-engineer` description
  no longer claims "placeholder - to be implemented" (the skill ships real
  content). Plus `repository`/`homepage`/`bugs` added to root `package.json`
  for npm provenance metadata.

### Changed

- **Freshie discovery run 6** (#659) — First inventory refresh since
  2026-04-06 (run 5). Captures the post-v4.29.0 ecosystem state on commit
  `531631f9d`: 17 packs / 423 plugins / 3,000 skills / 7,800 files.
  Compliance grade distribution: A 25.6% / B 42.9% / C 28.9% / D 2.5% / F
  0.0%. Average score 84.1/100. SQLite DB grew 53 MB → 63 MB (over GitHub's
  50 MB recommended limit; LFS plan tracked in #660). Surfaced three real
  issues hidden by the staleness — D+F regression, three-different-skill-counts
  inconsistency, and DB size — all with acceptance criteria documented in
  #660.
- **`CLAUDE.md`** updated:
  - "Two Catalog System" section explains the new sync-marketplace as
    orchestrator (the three chained steps + when to use the json-only variant)
  - "Auto-Generated Data Files" table now lists `plugins/**/package.json`
    and the README TOC block as chained from sync-marketplace
  - New "Git Hooks" section documents pre-commit + pre-push behavior +
    bypass instructions

### Tracking

- Issue #657 (closed by #658) — README.md generator/Prettier 3-authority conflict
- Issue #660 (open) — Post-Freshie-run-6 follow-ups (D+F regression second
  half, 250 orphan skills + 19 duplicate slugs catalog hygiene, Freshie LFS
  plan, Freshie compliance-snapshot design quirk)

### Stats

- 22 commits, 314 files changed, +16,124 / −10,545 lines
- 11-PR coordinated guidewire-pack v2.0.0 rebuild
- 8 PRs total merged this cycle (5 chore/fix + 3 features) plus the 11
  guidewire PRs = 19 PRs landed since v4.29.0

## [4.29.0] - 2026-05-02

This release bundles a major validator overhaul (schema 3.3.1), a fleet-wide
`compatible-with` → `compatibility` migration across ~3,200 skills, the testing
infrastructure rollout (husky, lint-staged, commitlint, audit-harness, a11y,
RTM/PERSONAS/JOURNEYS), the npm publish pipeline that broke the v1.0.0 freeze,
the Umami analytics tracker, two new external plugin sources (Skyvern,
ali5ter/claude-workflow-skills), and a long tail of CI hardening + sync-workflow
fixes. The validator section below is the original 4.29.0 entry from 2026-04-28
(the version was documented but never tagged); everything in subsequent sections
landed between 2026-04-28 and 2026-05-02 and is included in this release.

---

### Added (post-2026-04-28)

- **Release automation pipeline** (#647) — Broke the v1.0.0 plugin-freeze by adding three workflows: `auto-bump-on-pr.yml` (per-PR patch bumps for changed plugins), `publish-changed-packages.yml` (per-merge `npm publish --provenance` + per-package git tags + GitHub Releases), and a one-shot `publish-all-packages.yml` recovery workflow. Per-package tag convention is `@scope/name@version`. Full operator flow lives in `RELEASING.md`.
- **Umami analytics tracker** (#651) — Wired into `BaseLayout.astro` via env-driven script tag (`UMAMI_WEBSITE_ID` + `UMAMI_SCRIPT_URL`). Fail-soft: missing env = no tracker, no console error. Closes the empty-data gap that the `/analytics` skill kept hitting.
- **Testing infrastructure rollout** (#621, #629, #631) — Three-PR sequence installing the canonical Intent Solutions testing stack:
  - `@intentsolutions/audit-harness` as a dev dependency, `tests/TESTING.md` policy doc, coverage thresholds, hash-pinning manifest (#621)
  - Husky + lint-staged + commitlint + root ESLint/Prettier on every commit/PR (#629)
  - Marketplace a11y suite, RTM/PERSONAS/JOURNEYS files, CLI performance budget (#631)
- **External plugin sources** — Two new third-party repos added to the daily sync:
  - Skyvern (browser-automation MCP) — `productivity/skyvern` (#547, #650)
  - `ali5ter/claude-workflow-skills` (#649)
- **Killer Skill of the Week tooling** (#648) — Promoted Skyvern. Added `scripts/promote-spotlight.mjs` (atomic rotation: previous spotlight → top of hallOfFame) + `scripts/render-spotlight.mjs` (generates the README KILLER-SKILL block from `marketplace/src/data/spotlights.json`). CI enforces drift between `spotlights.json` and the README block.
- **Blog content** — Two case-study posts to `tonsofskills.com/blog`: `vps-as-the-home-day-1` (Contabo VPS migration program kickoff) and `propagation-day` (the harness/skills version-lock pattern). Plus 6 backfilled engineering posts covering 2026-04-23 → 2026-04-29 (#632).
- **ADRs declining audit-tests roadmap recommendations** (#619) — Four architectural decision records explaining why specific audit-tests roadmap items are not adopted in this repo.

### Fixed (post-2026-04-28)

- **Hero marquees** (#653) — Vertical spacing tightened and partner/npm-stats scroll speeds normalized so neither marquee runs in a visible "wait then jump" pattern.
- **`update-npm-stats` accuracy + Slack channel hygiene** (#646) — Drift fixes for `marketplace/src/data/npm-stats.json` (rate-limit was undercounting on retries), and the daily Slack download digest now posts to the correct channel only.
- **Orphaned plugins exposed** — `jeremy-google-adk` and `jeremy-vertex-ai` were on disk but absent from the catalog (#634, closes #597). Plus `plugins/**/skills/` orphan paths cleaned up + stragglers migrated to `compatibility` (#644, closes #630).
- **`x-bug-triage` SKILL.md compliance** (#633) — Five files brought to marketplace tier (frontmatter + body fixes).
- **Sync-external workflow stabilized** — Six-PR sequence working through cascading failures in the daily external-source sync workflow:
  - Replaced `peter-evans/create-pull-request` with hand-rolled `gh pr create` (#642) — eliminated the GHA-bot signature mismatch that was breaking branch protection
  - Disabled husky in the auto-PR step (#639) — pre-commit hook was rejecting bot commits
  - Switched to `--no-frozen-lockfile` for post-sync installs (#638) — synced packages can introduce dep changes
  - Graceful handling of empty files, submodules, and partial-failure scenarios (#637)
  - Workspace-aware install instead of bare `pnpm add` (#636)
  - Removed the duplicate pnpm version pin (#635) — was conflicting with the root `packageManager` field
- **Freshie anomaly detector + populator drift** (#618) — Run-versioning now correctly stamps `run_id` and normalizes paths. `x-bug-triage` template hardened.

### Changed (post-2026-04-28)

- **`compatible-with` → `compatibility` fleet migration** (#620, #622–#628) — The schema 3.3.1 migration from the original 4.29.0 work was applied across the entire skill catalog in eight batches: `ai-ml` category (34 skills, #620), 18 other categories (300 skills, #622), saas-packs 1/6 through 6/6 (~2,500 skills total, #623–#628). Total: ~2,850 skills now use the AgentSkills.io free-text `compatibility` field. The IS-invented closed-CSV `compatible-with` field is fully deprecated repo-wide; it still parses with a deprecation warning for any external sync that drags in legacy frontmatter.
- **Doc-filing standard v4.3** (#640) — Pulled the latest standard from `~/.claude/skills/doc-filing` and fixed a `.gitignore` re-include bug that was hiding `000-docs/*.md` files from `git status` after standard-driven renames.
- **CI: trust Gemini workspace + install bun for mcp-plugins tests** (#617) — Gemini PR Reviewer's GCP workspace is now in the trusted list; the mcp-plugins matrix job installs `bun` so the deno-style test entry-points actually run.

---

### Validator: spec-compliance fixes + `compatible-with` → `compatibility` migration

This release lands on **schema 3.3.1** of the validator after a one-day churn that
went through schema versions 3.0 → 3.1 → 3.2 before stabilizing. The full
back-and-forth is preserved in [`000-docs/SCHEMA_CHANGELOG.md`](000-docs/SCHEMA_CHANGELOG.md)
including a "Non-negotiables" section and a "How we got here — the 2026-04-28
schema debacle" post-mortem so the same dance doesn't get repeated.

The IS enterprise standard (8 required fields at marketplace tier — `name`,
`description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`,
`tags`) is **unchanged**. Earlier intra-day attempts to relax this to Anthropic's
2-field spec floor were reverted.

### Changed

- **`compatible-with` → `compatibility`** — the IS-invented closed-CSV platform list (`compatible-with: claude-code, codex, openclaw`) is replaced by the AgentSkills.io free-text `compatibility` field (max 500 chars per spec). Old field still parses as a deprecated alias with a per-file migration suggestion. New ALWAYS_REQUIRED set substitutes `compatibility` for `compatible-with`. This is the only structural change to ALWAYS_REQUIRED in this release.
- **Validator script v6.0 → v7.0** — spec-source citations updated, deprecation messaging cleaned up.

### Fixed (spec-compliance bugs)

- **`allowed-tools` accepts YAML list** per `code.claude.com/docs/en/skills` ("Accepts a space-separated string or a YAML list"). Old validator rejected YAML lists with _"must be a comma-separated string (CSV)"_.
- **`allowed-tools` parses space-separated form** per Anthropic's canonical example `Bash(git add *) Bash(git commit *) Bash(git status *)`. Old parser only split on commas. New parser is paren-depth-aware so multi-word tools stay as one token.
- **`when_to_use` reclassified as documented Anthropic optional** — earlier IS rubrics flagged it as deprecated, but Anthropic documents it explicitly. Validator now only warns when combined `description` + `when_to_use` exceeds the 1,536-char listing cap.
- **`agent` field no longer triggers "missing" warning when defaulting** — Anthropic doc states _"If omitted, uses general-purpose"_. Old validator warned that `agent` was missing whenever `context: fork` was set.
- **`argument-hint` conditional** — was incorrectly suppressed by `disable-model-invocation: true`, but the user can still invoke via `/`, so the hint is still relevant. Now tied to `user-invocable=true` only.

### Added

- **`scripts/batch-remediate.py`** — bulk-fix script for spec migrations. `--migrate-compatible-with` flag translates `compatible-with: claude-code, codex` → `compatibility: Designed for Claude Code, also compatible with Codex` per AgentSkills.io spec. Idempotent — safe to run twice.
- **`arguments`, `paths`, `shell` added to schema registry** — all documented Anthropic optional fields that were missing from `SKILL_FIELDS`. Type-validated.
- **`effort: xhigh`** added to valid values per Anthropic doc (`low/medium/high/xhigh/max`).
- **`${CLAUDE_EFFORT}`** added to `YAML_VALUE_ALLOWED_VARS` substitution allow-list.
- **`Skill()` permission rule documentation** in `references/frontmatter-spec.md` (`Skill(name)` exact match, `Skill(name *)` prefix match, `Skill` deny-all).
- **`000-docs/SCHEMA_CHANGELOG.md`** — new doc tracking validator schema versions independently from this main CHANGELOG. Includes the "Non-negotiables" rules and the "2026-04-28 schema debacle" post-mortem.

### Important: what was NOT changed (and won't be without explicit approval)

Per the new "Non-negotiables" section in `SCHEMA_CHANGELOG.md`:

- `ALWAYS_REQUIRED` is the IS enterprise 8-field set. Not reducible to Anthropic's 2-field spec floor without explicit user approval.
- Marketplace tier produces ERRORS for missing required fields, not warnings.
- The IS rubric SITS ON TOP of Anthropic's spec — additive, never subtractive.
- Tracking metadata (`version`, `author`, `license`) is REQUIRED at marketplace tier, not optional polish.

### Migration

Skills using the deprecated `compatible-with` field continue to validate (with a deprecation warning). Bulk-migrate via:

```bash
python3 scripts/batch-remediate.py --migrate-compatible-with --root <path>
```

Migration translation table:

```diff
 ---
 name: my-skill
 description: Does the thing. Use when ...
-compatible-with: claude-code, codex, openclaw
+compatibility: Designed for Claude Code, also compatible with Codex and OpenClaw
 ---
```

The 3,385 public-repo `SKILL.md` files under `plugins/` are **not** migrated in this release. Bulk migration tracked in #610.

### Tracking issue

[#610](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/issues/610) — `[spec] Realign skill validator + master spec to Anthropic's authoritative sources`. Note: the issue title still says "Realign" — the actual outcome was "fix bugs and add tooling without realigning." See `000-docs/SCHEMA_CHANGELOG.md` for the corrected story.

## [4.28.0] - 2026-04-23

### Added

- **Gemini PR Review revival** (#602) — Fixed a 4-month silent-fail regression. Workflow was running green on every PR but posting zero review comments because of a broken MCP bridge pattern. Full fix:
  - Switched trigger from `pull_request` → `pull_request_target` so fork-PRs actually get CI + Gemini feedback (previously fork PRs received zero feedback of any kind)
  - SHA-pinned checkout of PR HEAD with `persist-credentials: false` for safe fork-PR handling
  - Extended `.gemini/commands/gemini-review.toml` with an "Intent Solutions Philosophy" section so Gemini frames failures in the context of the marketplace's enterprise-grade bar
  - Updated the prompt to lead with validator failures and link CONTRIBUTING.md anchors rather than re-explaining rules inline
  - Added Slack notification step on every review completion (pings `#operation-hired`)
- **Plane sync workflow** (#529) — New GitHub Actions workflow syncing CCP issues to `projects.intentsolutions.io` Plane project. Fires on `issues: opened` (creates matching Plane issue in Backlog) and `pull_request: closed` (parses close refs, flips Plane issues to Done)
- **CONTRIBUTING.md "Before You Submit" section** (#602) — Top-of-file philosophy framing that sets expectations upfront about the Intent Solutions "ship the full-capability version" standard
- **CODEOWNERS** (#602) — Jeremy as sole owner on every path, with emphasis paths (`.github/`, `.gemini/`, validator scripts, catalog files, dependency manifests). Combined with branch protection "require code owner reviews", external contributions cannot merge without his approval
- **Blog backfill** — 4 posts cross-posted from `startaitools.com` (Apr 19-22 window)
- **External audit response (NLPM, xiaolai)** — Expanded validator and CI coverage in response to the NLPM audit (issue #540).
  - `scripts/validate-skills-schema.py` now scans `.claude/agents/` and `workspace/**/agents/` in addition to `plugins/`, and flags shell-substitution patterns (`$(...)`, backticks, unguarded `${VAR}`) in YAML frontmatter values
  - `.github/workflows/validate-plugins.yml` PR trigger paths extended to `scripts/**`, `.claude/**`, and `workspace/**`
  - Credit to [xiaolai](https://github.com/xiaolai), author of [NLPM](https://github.com/xiaolai/nlpm-for-claude), for the audit and fix PRs (#535-#539)

### Changed

- **PR template callout** (#602) — Top-of-file disclosure pointing first-time contributors at the CONTRIBUTING.md philosophy section
- **`maintainer-ready-automerge.yml` triple-guarded** (#602) — Fires only on `labeled` event (not synchronize/reopened/ready_for_review), only when the label is exactly `maintainer-ready`, AND only when the sender is `jeremylongshore`
- **Marketplace playbooks layout** (#601) — Wrapped in `BaseLayout`; retired `/spotlight` page
- **`ccpi validate --strict` step** (#603, #604) — Temporarily degraded from `|| exit 1` to `|| true` in `validate-plugins.yml` to unblock CI while 177-agent pre-existing frontmatter debt is worked off over a multi-PR campaign. Reversal tracked in #604; hard gate returns once debt is cleared

### Fixed

- **Frontmatter cleanup campaign — Phase 1** (#604, #605) — 5 pre-existing errors: 4 shipwright command categories (`ai-agency` → `deployment`) and 1 over-length `backup-strategy` description (158 → 80 chars). 182 → 177 `ccpi validate --strict` errors
- **Frontmatter cleanup campaign — Phase 2A batch 1** (#604, #606) — 12 files in `fullstack-starter-pack` (6 top-level + 6 byte-identical nested mirrors) brought to production-grade frontmatter. 177 → 170
- **Frontmatter cleanup campaign — Phase 2A batch 2** (#604, #607) — 11 agents in `testing/code-cleanup` backfilled with capabilities + model + expertise_level. 170 → 159
- **Skills `allowed-tools` errors** (#603) — 3 pre-existing errors: `freshie-inventory-manager` used unknown `Agent` tool (→ `Task`); `sentry-pack` and `supabase-pack` had malformed wildcards missing colons (`Bash(python*)` → `Bash(python:*)`, `Bash(npx supabase *)` → `Bash(npx supabase:*)`)
- **Freshie compliance populator** (#593) — Stamps `run_id` and normalizes paths for correct run-versioning
- **Agent frontmatter quoting** (#579) — `phase_*.md` descriptions now properly quoted to avoid YAML mapping errors
- **`quick-test.sh`** (#538) — Replaced silent global `pnpm install` with a clear prerequisite error
- **Schema-optimization phase agents** (#536) — Added missing YAML frontmatter
- **fairdb-setup-backup webhook guard** (#539) — `curl` now guarded by env-var presence check
- **`backup-strategy.md`** (#537) — Replaced shell-substitution expressions in frontmatter
- **skill-auditor agent** (#535) — Added missing YAML frontmatter
- **Plane sync jq injection** (#529) — `$SEQ` now passed as jq `--arg` variable instead of shell-interpolated (defensive security fix per Gemini review)
- **Cloud Functions Slack webhook logging** — Webhook failures now surface in logs instead of silently swallowing

### Security

- **Secret scanning hardened** — Replaced the previous regex-based secret scan in `validate-plugins.yml` with a dedicated workflow (`secret-scan.yml`) that runs `gitleaks` on every PR and push, plus a weekly `trufflehog` verified-credentials scan with Slack alerting. `.gitleaks.toml` adds rules for Anthropic, Groq, and Firebase/GCP credential shapes on top of the upstream defaults
- **Gemini reviewer WIF binding narrowed** (#602) — Service account IAM binding tightened from `attribute.repository_owner/jeremylongshore` (org-wide) to `attribute.repository/jeremylongshore/claude-code-plugins-plus-skills` (this repo only). Fully standalone GCP isolation across every layer
- **Branch protection hardened** (#602) — `require_code_owner_reviews: true`, `dismiss_stale_reviews: true`, 1 approval required. Combined with CODEOWNERS, no PR merges without Jeremy's approval

### Known issues

- **171 pre-existing agent frontmatter errors** tracked in #604 as a multi-PR cleanup campaign. `ccpi validate --strict` is currently reporting-only (`|| true`) until the campaign completes; strict enforcement returns when the final campaign PR restores `|| exit 1`

## [4.27.0] - 2026-04-21

### Added

- **LangChain Python Skill Pack v1.0** - Complete 33-skill pack for LangChain/LangGraph Python development:
  - Core skills (8): model-inference, embeddings-search, sdk-patterns, reference-architecture, multi-env-setup, debug-bundle, deep-agents, langgraph-basics
  - LangGraph advanced (10): agents, checkpointing, human-in-loop, streaming, subgraphs, middleware-patterns, content-blocks, otel-observability
  - Production patterns (8): performance-tuning, cost-tuning, rate-limits, security-basics, enterprise-rbac
  - DevOps (7): ci-integration, deploy-integration, observability, incident-runbook, local-dev-loop, webhooks-events, upgrade-migration
  - Support skills: common-errors, core-workflow, data-handling, prompt-engineering, eval-harness
  - Average enterprise score: 92.4/100 (A-grade)
  - Reference architecture with pain-catalog documenting 25+ real-world failure modes

### Fixed

- **Gemini PR Review workflow** - Added `workflow_dispatch` trigger for manual review runs on any PR (#546+)
- **npm Publish** - Fixed repository.url for npm provenance compliance (#545)
- **npm Publish** - Fixed SIGPIPE abort in mass-publish enumerate step (#544)

### Changed

- **VERSION file sync** - Corrected VERSION file to match package.json (4.25.0 → 4.26.0)

### Metrics

- Commits since v4.26.0: 4 (1 feature, 3 fixes)
- New skills added: 33 (langchain-py-pack)
- Total skills: 2,882 (+33)
- Enterprise score maintained: 92.4/100 average for new pack

---

## [4.26.0] - 2026-04-20

### Added

- **npm Download Tracking Infrastructure** - Daily stats aggregation (`fetch-npm-stats.mjs`), hero marquee showing top 8 packages with 30-day counts, Slack digest at 1pm Central via #operation-hired webhook (#543)
- **npm Publish Workflows** - Mass publish (`publish-all-packages.yml` with confirmation gate) and incremental publish (`publish-changed-packages.yml` on push to main) for all @intentsolutionsio/\* packages (#542)
- **Plugin Package.json Scaffolding** - Generated package.json for 305+ catalog plugins under @intentsolutionsio scope, enabling npm download tracking (#541)
- **README Awesome-List TOC** - Auto-generated table of contents with category counts, enforced by CI via `generate-readme-toc.mjs --check` (#531)
- **agent37.com Partner Integration** - Added to hero partner marquee alongside Nixtla (#532, #533)
- **Ultimate Code Cleanup Plugin** - 11-dimension, 11-agent comprehensive code analysis tool scoring 98/100 A+ enterprise grade
- **Bubble Invest Plugins** - local-tts (voice synthesis), boycott-filter (ethical filtering) from community PR #520
- **Killer Skill of the Week** - web-analytics skill with Umami MCP integration

### Fixed

- **Marquee Symmetry** - Restored translateX(-50%) pattern duplication so agent37 actually renders in seamless loop (#533)
- **Catalog Validation** - Removed phantom entries (tonone, claudebase), normalized 33 plugin author fields to object format
- **SKILL.md Compliance** - Split 13 files exceeding 500-line limit into references/, removed XML tags from frontmatter
- **Cowork Downloads** - Replaced non-existent stripe-pack with clerk-pack
- **CodeQL Finding** - Removed unused tableHeaderDone variable

### Changed

- **Micro-Category Consolidation** - Merged analytics→business-tools, code-quality→testing, finance→business-tools, automation→devops with CLI aliases for backwards compatibility (#530)
- **FS=Catalog Invariant** - Enforced filesystem path matching catalog category via `validate-catalog-invariants.py`
- **SaaS Pack Display** - Individual cards on /cowork page for better discoverability
- **Comprehensive Codebase Cleanup** - 8-parallel-agent refactor addressing code quality across repository

### Metrics

- Commits since v4.25.0: 34 (10 features, 8 fixes, 3 chore)
- Plugins with npm tracking: 305+ (newly scaffolded package.json files)
- Categories consolidated: 4 (analytics, code-quality, finance, automation)
- SaaS packs corrected: 106 → 105 (removed windsurf duplicate)

---

## [4.25.0] - 2026-04-14

### Added

- **Shopify Skill Pack v2.0** - Complete overhaul: 30 → 38 skills, 116 reference files extracted. Added 8 new skills (metafields-metaobjects, functions, storefront-headless, checkout-extensions, theme-performance, graphql-cost-optimizer, b2b-wholesale, ai-toolkit-wrapper). Enterprise score: 81.9 → 93.1/100.
- **Deep Evaluation Engine v1.0** - Intent Solutions 10-dimension skill quality assessment with coaching system and professional tier.
- **CLI Power Skills** - External plugin sync for enhanced CLI automation workflows.
- **CCHub plugin** - Desktop control panel for Claude Code / Codex / Gemini CLI management.
- **Work Diary blog** - Added Apr 6-13 posts to tonsofskills.com/blog.

### Changed

- **Shopify sdk-patterns rewrite** - Removed generic Zod/retry patterns, added codegen-typed operations, bulk operation helpers, and webhook registry.
- **Marketplace data sync** - Updated plugin counts to 430 plugins, 2,838 skills.

### Metrics

- Commits since v4.24.0: 10 (6 features, 2 chores, 2 merges)
- Shopify skills upgraded: 30 → 38 (+8 new)
- Reference files created: 116
- Lines added: +9,950 / -4,893

---

## [4.24.0] - 2026-04-06

### Added

- **SaaS pack skill upgrades** - Upgraded 232 D/F-grade skills to 70+ compliance (C+ or better). Expanded from ~30 lines to 90-150 lines each with Overview, Instructions, Error Handling tables, and product-specific TypeScript examples. Affected packs: appfolio, apple-notes, coreweave, fathom, glean, linktree, lucidchart, mindtickle, openevidence, together.
- **Legal & Compliance collection** - Added to homepage and /collections page with curated legal toolkit plugins.
- **General Legal Assistant plugin** - 12-skill, 5-agent legal toolkit (plugin #417) with contract analysis, compliance checking, and document drafting capabilities.
- **Agent Creator skill** - Added agent-creator skill and agent template to skill-creator plugin.
- **Work Diary blog** - Added Apr 3-5 posts to tonsofskills.com/blog.

### Changed

- **Legal plugin rename** - Renamed legal-assistant → general-legal-assistant for clarity.
- **Freshie inventory cleanup** - Removed 530 stale DB rows (500 legacy skills/, 30 ghost paths). Accurate skill count now 2,834.

### Fixed

- **CI deploy trigger** - Added pnpm-lock.yaml to deploy-firebase workflow trigger paths.
- **Lockfile sync** - Added x-bug-triage to pnpm-lock.yaml, unblocking Firebase deploys.
- **Homepage sponsor** - Restored scrolling marquee for sponsor section under byline.

### Metrics

- Commits since v4.23.0: 11 (5 features, 4 fixes, 1 refactor, 1 chore)
- Skills upgraded: 232 (D/F → C+)
- SaaS packs improved: 10
- Lines added: +21,464 / -5,440

---

## [4.23.0] - 2026-04-04

### Added

- **Skill-creator Anthropic alignment** - Updated to 2026 AgentSkills.io spec and Anthropic best practices
- **Work Diary blog** - Added intentcad-viewer-dwg-fastview-parity post to tonsofskills.com/blog

### Changed

- **Homepage partner banner** - Moved strategic partners section above fold, replaced Agent37 with Nixtla sponsor
- **CLAUDE.md accuracy** - Updated plugin/skill counts to 416/2,574, fixed build pipeline (6 steps), added verify CI job, corrected test file listing

### Fixed

- **YAML frontmatter repairs** - Fixed 1,252 SKILL.md files across the plugin ecosystem:
  - 9 Wondelai skills: double-escaped quotes (`''` → `'`) in block scalars
  - 3 Grammarly pack skills: duplicate frontmatter keys dropping `Bash(curl:*)` access
  - 1,219 skills: removed blank lines before closing `---` delimiters
- **README sponsor badge** - Added Nixtla sponsor badge, updated counts

---

## [4.22.0] - 2026-03-27

### Added

- **Hooks `if` conditional upgrade** - 4 plugins upgraded to use Claude Code v2.1.85 native `if` field for in-process tool filtering, eliminating unnecessary subprocess spawns. (#496)
  - `jeremy-github-actions-gcp` - Replace non-standard `filePattern` with native `if` glob
  - `claude-reflect` - Add `if: "Bash(git commit*)"` to PostToolUse
  - `pm-ai-partner` - Add `if: "Bash(git commit*)|Bash(git push*)"` to PreToolUse
  - `formatter` - Add `if` matching 15 file extensions for Write|Edit
- **x-bug-triage plugin** - External plugin sync with auto-dispatch workflow for all external repos. (#493)
- **OneNote pack rewrite** - All 18 skills rewritten from stubs (61.7) to production quality (91.4/100). (#489)
- **Work Diary blog** - /blog with 100 posts backfilled from startaitools.com, plus March 24-25 daily posts.

### Changed

- **Navigation** - Renamed Blog to Work Diary, replaced Pro nav link with Work Diary link.

### Fixed

- **Hooks schema normalization** - 2 plugins fixed to standard event-keyed format:
  - `prettier-markdown-hook` - Convert non-standard root-level array to standard schema
  - `travel-assistant` - Convert content-based matchers to standard `matcher: ".*"` (scripts handle detection)
- **x-bug-triage catalog** - Convert author field from string to object format.
- **/pro page** - Deactivated with 301 redirect to homepage.

### Metrics

- Commits since v4.21.0: 16 (7 features, 5 fixes, 2 chore)
- Hook plugins upgraded: 6 (4 with `if` conditionals, 2 schema normalizations)
- OneNote skills rewritten: 18
- Contributors: Jeremy Longshore, intentsolutions.io

---

## [4.21.0] - 2026-03-23

### Added

- **oraclecloud-pack rewrite** - All 26 OCI skills rewritten from stubs (61.3) to production quality (92.8/100). Pain-point-driven content covering auth config, capacity errors, IAM policies, SDK memory leaks, Terraform bugs. (#488)
- **navan-pack rewrite** - All 25 Navan skills rewritten to 93.0/100 with Airbyte connector research, real API patterns. (#485, #486, #487)
- **claude-pack hand-written** - Claude API skills at 95.3/100 with real SDK code. (#482)
- **Killer Skill nomination form** - Firebase form for community skill nominations. (#483)
- **105 SaaS packs total** - Notion, Supabase, Sentry packs fully built out (30 skills each). (#391-#480)
- **Universal validator v5.0** - Anthropic schema alignment, 100-point rubric, `--populate-db` for freshie inventory. (#378)
- **Pro tier + benchmarks** - CLI performance benchmark suite, Pro tier landing page. (#381)
- **63 SaaS pack directories** - Generated from marketplace extended metadata. (#380)
- **Infrastructure compliance** - Tags + compatible-with mass migration to 1,412 skills. (#379)
- **Severity1 marketplace plugin** - Severity levels and prompt-improver. (#382)
- **Slack channel plugin** - Added to ecosystem. (#375)

### Changed

- **Performance budget** - Bumped to 40MB gzipped, 1MB largest file, 2800-4000 routes for 414 plugins + 63 SaaS packs.
- **Freshie inventory system** - SQLite CMDB with 50 tables, versioned discovery runs, batch remediation.
- **Gold standard docs** - PRD/ARD/references pattern established for 13 Jeremy plugins.

### Fixed

- **Firebase forms** - Broken killer skill signup fixed. (#374)
- **CI validation** - Python + pyyaml setup for validation-scripts job.
- **Enterprise compliance** - 0 D/F grades after remediation rounds. (#384, #385)
- **Bare except clauses** - Replaced with `except Exception`. (#387)

### Metrics

- Commits since v4.20.0: 124 features, 25 fixes
- Files changed: 5,161 (+large delta)
- SaaS packs: 105 total (42 newly populated)
- Skills: 2,788+ across 414 plugins
- Contributors: Jeremy Longshore, intentsolutions.io

---

## [4.20.0] - 2026-03-20

### Added

- **pr-to-spec MCP plugin** - Convert PRs and local diffs into structured, agent-consumable specs with intent drift detection. 6 MCP tools for agentic coding workflows.
- **claude-memory-kit plugin** - Persistent agent memory system (#370, @seankim-android)
- **prism-scanner plugin** - Added to ecosystem section (#369, @aidongise-cell)
- **Content consistency validator improvements** - Enhanced skill structure validation with skill-review CI (#347, @fernandezbaptiste)

### Changed

- **8 SaaS packs rewritten with production content** - 150+ skills upgraded:
  - MaintainX pack (24 skills) - CMMS API integration
  - Evernote pack (24 skills) - Note management workflows
  - Apollo pack (22 skills) - Sales engagement APIs
  - Clerk pack (22 skills) - Auth/user management
  - Speak pack (9 skills) - Language learning APIs
  - Obsidian pack (10 skills) - Vault plugin development
  - Lokalise pack (23 skills) - Localization workflows
  - Juicebox pack (18 skills) - Community platform APIs
- **Agent spec updated for v2.1.78** - New `effort`, `maxTurns`, `disallowedTools` fields; corrected agent vs skill tool patterns
- **Performance budget** - Bumped to 19.5MB for 346+ plugins

### Fixed

- **Homepage badges** - Removed redundant badges above Killer Skill and Jeremy's Stash headings
- **Skill-review CI** - Removed insecure workflow dispatch, restored Overview + Examples sections
- **HTML attribute sanitization** - Complete quote escaping in discover-skills.mjs
- **Repository URL consistency** - Fixed pr-to-spec → pr-to-prompt mapping
- **Validation script** - Fixed duplicate tuple entry, added anchor skip

### Metrics

- Commits since v4.19.0: 13
- Files changed: 432 (+56,454 lines)
- Contributors: Jeremy Longshore, fernandezbaptiste, aidongise-cell, seankim-android, intentsolutions.io

---

## [4.19.0] - 2026-03-17

### Added

- **box-cloud-filesystem plugin** - Box cloud storage integration with file operations (#368)
- **geepers plugin** - Added to catalog (#367)
- **lumera-agent-memory plugin** - MCP server for persistent agent memory (#367)

### Fixed

- **Content quality audit sweep** - Comprehensive remediation of stub files and boilerplate:
  - Final 3 audit findings resolved (2 stubs + 1 false positive) (#365)
  - Wondelai implementation.md stubs filled with methodology guides (#363)
  - Remaining reference stubs for lokalise, documenso, speak (#364)
  - SaaS packs prose expanded to meet body-substance threshold (#362)
  - 12 misc reference stubs across community/crypto/productivity (#361)
  - 22 devops/saas reference stubs filled (#360)
  - 13 API development reference stubs with real examples (#359)
  - OpenRouter pack: 30 skills replaced boilerplate with unique content (#358)
  - 7 AI/ML reference stubs with real code examples (#357)
  - 24 performance skills: replaced generic boilerplate openings (#356)
  - 21 AI/ML skills: replaced generic boilerplate openings (#355)
  - 4 empty shell skill-enhancers built out with real content (#354)
  - 13 security/packages skills: replaced generic boilerplate (#353)
  - Audit content quality false positives addressed (#352)

### Metrics

- Commits since v4.18.0: 46
- Files changed: 376 (+37,973 / -2,436 lines)
- Contributors: Jeremy Longshore, intentsolutions.io, Ahmed Khaled Mohamed

---

## [4.18.0] - 2026-03-16

### Added

- **navigating-github plugin** - Interactive GitHub setup and learning companion with 6 modes (setup, learn, save, share, understand, fix), adaptive skill assessment, and 9 progressive hands-on lessons
- **mgonto EA skills** - 5 executive assistant skills: action-items-todoist, email-drafting, executive-digest, meeting-prep, todoist-due-drafts
- **Enhanced plugin & skill detail pages** - README section extraction, markdown-to-HTML rendering, FAQ accordions, and improved CTAs
- **Killer Skills spotlight** - Featured hero section on homepage with email signup
- **/github-learn slash command** - User-invocable entry point for navigating-github plugin

### Changed

- **Full facelift Phase 2** - Terminal-Bold redesign across all pages with OKLCH color system
- **Contributor cards redesigned** - Cross-page consistency with new card layout
- **Performance budget bumped** - 16MB for 343+ plugins

### Fixed

- **Mobile UX on /explore** - Card overlap, 480px breakpoint, filter bar improvements
- **Firebase deploy** - Split targets to avoid serviceusage permission error
- **run_eval.py** - Fixed 0% recall for already-installed plugin skills

### Metrics

- Commits since v4.17.0: 27
- Files changed: 41 (+7,331 / -1,665 lines)
- Contributors: Jeremy Longshore, intentsolutions.io

---

## [4.17.0] - 2026-03-11

### Added

- **Intent Solutions skill standard** - Updated all 5 tutorial notebooks to current standard
- **Verified Plugins Program** - Badges, rubric, and /verification page (#326)
- **Blog with changelog posts** - Astro content collections at /blog (#324)
- **Compare Marketplaces page** - SEO landing page at /compare (#323)
- **Light/dark theme toggle** - Across entire marketplace (#329)
- **Doctor --fix flag** - Safe auto-remediation for ccpi doctor (#333)
- **Cross-platform skill headers** - compatible-with field, YAML parser fix (#332)
- **Automated weekly metrics** - GitHub Actions workflow (#330)
- **Wondelai skills pack** - 25 agent skills for business, design & marketing (#303)
- **CONTRIBUTING.md** - Contributor guide with SEO meta tags (#320)

### Fixed

- **4300+ validator warnings reduced to 258** - 94% reduction (#337)
- **130 stub SKILL.md files replaced** - Substantive domain-specific content (#335)
- **Skill counts corrected** - Add windsurf pack, fix cowork claims (#334)
- **Gemini model ID updated** - gemini-2.0-flash-exp → gemini-2.5-flash (#316)
- **Wondelai skills frontmatter** - Added required fields to all 25 skills (#317)
- **SECURITY.md added** - Security policy (#315)

### Changed

- **Validator compliance** - Community page, PDA skill quality upgrade (#336)
- **Playbooks converted** - 11 playbooks to Astro content collections (#325)
- **18 jeremy-owned plugins** - Version bump 1.0.0 → 2.0.0 (#331)
- **Performance budgets** - Bumped for 340+ plugins and dark mode CSS

### Metrics

- Commits since v4.16.0: 33
- Files changed: 2,956 (+272,838 / -215,356 lines)
- Contributors: intentsolutions.io, Jeremy Longshore, Michal Jaskolski, Eugene Aseev

---

## [4.16.0] - 2026-03-07

### Added

- **Domain migration to tonsofskills.com** - Primary domain with Firebase hosting and 301 redirects
- **Homepage dark theme redesign** - Braves Booth-inspired dark theme with modern UI
- **Production E2E tests** - Playwright tests for tonsofskills.com deployment validation
- **Research page** - `/research` with 6 data-driven analysis documents
- **Trading strategy backtester fixes** - 8 quality gaps fixed (#314):
  - Stop-loss and take-profit enforcement
  - Short position support for RSI, MACD, Bollinger, MeanReversion strategies
  - Settings.yaml loading with CLI override support
  - Full test suite with 31 pytest tests

### Fixed

- **Axiom submodule issue** - Converted broken submodule to regular directory, fixing CI on forks
- Mobile horizontal overflow on `/explore` page
- Badge text size and cowork plugin overflow on mobile
- Hidden nav links handling in Playwright tests
- Skills link to cowork page, updated skills page title

### Changed

- CI cron schedules disabled to reduce Actions minutes usage
- Workflow dispatch trigger added to Validate Plugins workflow
- Cowork zip integrity check now works without unzip (Node.js fallback)
- Production E2E job now independent of marketplace-validation

### Reverted

- Chainstack and deAPI plugins temporarily reverted pending review

### Metrics

- Commits since v4.15.0: 50
- Files changed: 183 (+25,792 / -1,584 lines)
- Contributors: Jeremy Longshore, intentsolutions.io, clowreed, Eugene Aseev

---

## [4.15.0] - 2026-02-13

### Added

- Products & Services section on homepage with Agent37 partner integration
- Penetration testing plugin v2.0.0 with 3 real Python security scanners (~4,500 lines):
  - `security_scanner.py` - HTTP headers, SSL/TLS, endpoint probing, CORS analysis
  - `dependency_auditor.py` - npm audit & pip-audit wrapper with unified reporting
  - `code_security_scanner.py` - bandit + 16 regex patterns for static analysis
- Security reference documentation: OWASP Top 10, Security Headers, Remediation Playbook

### Fixed

- Windows Defender false positive in penetration-tester plugin (#300) - removed literal PHP payloads
- Sponsor page pricing tiers replaced with email-for-details contact form
- stored-procedure-generator test functions renamed to avoid pytest collection conflicts
- Homepage product listing prices updated to $10
- Explore page style preservation when filtering search results

### Changed

- Copyrights updated to 2026 across all documentation
- Opus model ID now allowed in skills schema validation
- Schema references synced to 2026 spec

### Metrics

- Commits since v4.14.0: 8
- Files changed: 50+
- New Python code: ~4,500 lines (security scanners)
- New reference docs: 3 (~1,100 lines)

---

## [4.14.0] - 2026-01-31

### Added

- 17 additional SaaS skill packs (408 skills), completing the 42-pack SaaS collection:
  - **apollo-pack**: Sales engagement, sequences, analytics, CRM integration
  - **clerk-pack**: User authentication, session management, organization features
  - **coderabbit-pack**: AI code review, PR automation, code quality analysis
  - **customerio-pack**: Email marketing, customer messaging, campaigns, segments
  - **deepgram-pack**: Speech-to-text, audio transcription, real-time ASR
  - **fireflies-pack**: Meeting transcription, note-taking, conversation intelligence
  - **gamma-pack**: AI presentations, document generation, visual content
  - **granola-pack**: Meeting notes, AI summaries, productivity automation
  - **groq-pack**: LPU inference, ultra-fast AI, Groq Cloud deployment
  - **ideogram-pack**: AI image generation, text rendering, creative design
  - **instantly-pack**: Cold email, outreach automation, lead generation
  - **juicebox-pack**: People search, lead enrichment, contact data
  - **langchain-pack**: LLM orchestration, chains, agents, RAG patterns
  - **linear-pack**: Issue tracking, project management, engineering workflows
  - **lindy-pack**: AI assistants, workflow automation, business processes
  - **posthog-pack**: Product analytics, feature flags, session replay
  - **vastai-pack**: GPU marketplace, cloud compute, ML infrastructure

### Changed

- Updated all skill counts in README.md (739 → 1,537 total skills)
- SaaS pack summary: 42 packs with 1,086 skills total
- Standalone skills: 1,298 (was 500)

### Metrics

- New SaaS skill packs: 17 (408 skills)
- Total SaaS packs: 42 (1,086 skills)
- Total skills: 1,537 (previously 1,027)
- 13 packs with 30 skills, 29 packs with 24 skills

---

## [4.13.0] - 2026-01-26

### Added

- 12 complete SaaS skill packs with real, production-ready content (288 skills total):
  - **databricks-pack**: Delta Lake, MLflow, notebooks, clusters, data engineering workflows
  - **mistral-pack**: Mistral AI inference, embeddings, fine-tuning, production deployment
  - **langfuse-pack**: LLM observability, tracing, prompt management, evaluation metrics
  - **obsidian-pack**: Vault management, plugins, sync, templates, personal knowledge management
  - **documenso-pack**: Document signing, templates, e-signature workflows, compliance
  - **evernote-pack**: Note management, notebooks, tags, search, productivity workflows
  - **guidewire-pack**: InsuranceSuite, PolicyCenter, ClaimCenter, insurance platform integration
  - **lokalise-pack**: Translation management system, localization, i18n automation
  - **maintainx-pack**: Work orders, preventive maintenance, CMMS workflows, asset tracking
  - **openevidence-pack**: Medical AI, clinical decision support, healthcare evidence platform
  - **speak-pack**: AI language learning, speech recognition, pronunciation training, education tech
  - **twinmind-pack**: AI meeting assistant, transcription, summaries, productivity automation
- Each pack follows standard template: S01-S12 (Standard), P13-P18 (Pro), F19-F24 (Flagship)
- All skills include 2026 schema frontmatter with proper tool permissions
- Brand strategy framework plugin integration (#292)

### Changed

- Updated all 2025 schema/spec references to 2026 across documentation
- Improved contributor ordering convention (newest first)
- Marketplace catalog extended with 12 new SaaS packs

### Metrics

- New SaaS skill packs: 12 (288 skills)
- Total skills: 1,027 (previously 739)
- Commits since v4.12.0: 15
- Contributors: Jeremy Longshore (10), Rowan Brooks (4)
- Files changed: 301
- Days since last release: 14

## [4.12.0] - 2026-01-12

### Added

- 5 crypto trading plugins to public repository
- Validator content quality validation checks (#299)

### Fixed

- creating-kubernetes-deployments skill quality (#298)
- automating-database-backups skill quality (#297)
- generating-stored-procedures skill quality (#296)
- All 3 skills improved based on Richard Hightower's quality feedback

### Changed

- Added Richard Hightower as contributor
- Banner text and mobile spacing improvements

## [4.11.0] - 2026-01-18

### Added

- 8 new crypto plugin skills with full PRD/ARD documentation and Python implementations:
  - **Blockchain & On-Chain**: blockchain-explorer-cli, on-chain-analytics, mempool-analyzer, whale-alert-monitor, gas-fee-optimizer
  - **NFT & Tokens**: nft-rarity-analyzer, token-launch-tracker
  - **Infrastructure**: cross-chain-bridge-monitor, wallet-security-auditor
- Firebase Hosting deployment workflow for [retired legacy public domain]
- Firebase Analytics integration with measurement ID tracking
- Google Secret Manager integration for secure Firebase config

### Fixed

- Gemini code review feedback for all new crypto skills:
  - Timezone-naive datetime operations (now UTC)
  - Empty except clauses with explanatory comments
  - Unused import cleanup
  - Config loading from settings.yaml
  - Mock data fallback with explicit --demo flag

### Infrastructure

- GitHub Actions workflow for Firebase Hosting deployment
- Workload Identity Federation for keyless GCP authentication
- All crypto skills follow nixtla enterprise PRD/ARD standard

### Metrics

- New crypto skills: 8 (completing Batch 5 & 6)
- Commits since v4.10.0: 29
- PRs merged: 10
- Total files changed: 221
- Lines changed: +23,839 / -19,891

## [4.10.0] - 2026-01-15

### Added

- 13 new crypto plugin skills with full PRD/ARD documentation and Python implementations:
  - **Market Data & Pricing**: market-price-tracker, market-movers-scanner, crypto-news-aggregator, market-sentiment-analyzer
  - **Portfolio & Tax**: crypto-portfolio-tracker, crypto-tax-calculator
  - **DeFi**: defi-yield-optimizer, liquidity-pool-analyzer, staking-rewards-optimizer, dex-aggregator-router, flash-loan-simulator
  - **Trading & Derivatives**: arbitrage-opportunity-finder, crypto-derivatives-tracker
- Firebase Hosting integration for marketplace website
- Firebase Analytics for download tracking

### Changed

- Updated skill validator compliance for backtester and signal generator skills
- Unified theme colors across all marketplace pages (CSS consolidation)
- Updated .gitignore for firebase cache and skill data files

### Infrastructure

- All crypto skills follow nixtla enterprise PRD/ARD standard
- Each skill includes: SKILL.md, PRD.md, ARD.md, Python scripts, references, config
- Skills use DeFiLlama, CoinGecko, CryptoCompare APIs (free tiers)

### Metrics

- New crypto skills: 13 (with full documentation)
- Commits since v4.9.0: 50
- PRs merged: 8 (crypto skill branches)
- Total files changed: ~200
- Lines added: ~25,000

## [4.9.0] - 2026-01-08

### Added

- 10 new SaaS vendor skill packs (Batch 3): Apollo, Deepgram, Juicebox, Customer.io, LangChain, Lindy, Granola, Gamma, Clerk, Linear
- 240 new skills across Batch 3 vendors (24 skills per pack)
- npm packages for all 30 SaaS packs with download tracking
- Learn pages for all Batch 3 vendors on [retired legacy public domain]

### Changed

- Updated marketplace.extended.json with 10 new pack entries
- Updated vendor-packs.json with Batch 3 vendor metadata
- Updated TRACKER.csv with Batch 3 completion status

### Infrastructure

- All 30 SaaS packs now published to npm (@intentsolutionsio/{vendor}-pack)
- Consistent naming across marketplace and npm registries
- Website deployed with 642 pages including all vendor learn pages

### Metrics

- Total SaaS skill packs: 30 (720 skills)
- Batch 3 packs: 10 (240 skills)
- npm packages published: 30
- Files changed: 305
- Lines added: +72,405

## [4.8.0] - 2026-01-06

### Added

- Marketplace redirects for deleted learning pages
- 14 new vendor skill packs with website pages

### Changed

- Updated learn hub with all vendor icons
- Synced marketplace catalogs

## [4.7.0] - 2026-01-06

### Added

- Progressive Disclosure Architecture (PDA) pattern for all skills
- Intent Solutions 100-point grading system integrated into validator
- 348 reference files for detailed skill content extraction
- `scripts/refactor-skills-pda.py` automation script for skill restructuring

### Changed

- Refactored 98 skills to PDA pattern (SKILL.md files now <150 lines)
- Merged `validate-frontmatter.py` into unified `validate-skills-schema.py` (v3.0)
- Improved average skill score from 88.0/100 (B) to 92.5/100 (A)
- All 957 skills now 100% production ready

### Fixed

- Excel skills quality issues (GitHub Issues #250, #251, #252, #253)
- OpenRouter pack skills grading (8 skills improved from 80 to 95+ points)
- All C/D grade skills elevated to A/B grade
- Kling AI common-errors skill malformed code fences

### Metrics

- Skills validated: 957
- A grade: 897 (93.7%)
- B grade: 60 (6.3%)
- C/D/F grade: 0 (0%)
- Files changed: 2,173
- Lines added: +77,698
- Lines removed: -70,011

## [4.6.0] - 2026-01-05

### Added

- Batch 2 vendor skill databases (217 files)
- Skill databases for 6 published SaaS packs
- Kling AI flagship+ skill pack (30 skills)

### Fixed

- OpenRouter pack skill quality improvements

## [4.5.0] - 2026-01-04

### Added

- External plugin sync infrastructure
- ZCF integration
- 50-vendor SaaS skill packs initiative

### Changed

- Skill quality improvements to 99.9% compliance

### Fixed

- **Cowork manifest contract** — require generated manifest totals, use the producer's `skills`/`commands` fields, and verify emitted `checksum` values deterministically instead of inventing fallback totals or silently skipping checksum checks.
