# Personas — Tons of Skills / claude-code-plugins-plus-skills

> **Status:** policy-zone (engineer-owned). Update when a real new persona shows
> up in the issue tracker, the analytics funnel, or a user-research call — not
> in response to a hypothetical "what if".
>
> **Sourcing:** every persona below is drawn from existing repo material
> (`CONTRIBUTING.md`, `SECURITY.md`, `marketplace/src/content/docs/`, the
> `ccpi` CLI commands, the SaaS pack folder structure, and the MCP plugin
> shape) plus signals from issues / PRs in this repo's history. None are
> aspirational.

This document codifies the five user types this codebase actually serves. It
exists to keep tests, docs, and product decisions grounded in the real
surface area we ship — not in a generic "developer persona" abstraction.

---

## Persona 1 — Plugin Author ("Pat")

**Role.** External contributor opening a fork-and-PR to add or update a
plugin or skill. Could be a one-time submitter or a recurring contributor.
Maps to the workflow described in [`CONTRIBUTING.md`](../.github/CONTRIBUTING.md).

**Primary goals.**

- Get a plugin or skill merged into `main` with the contribution credited in
  the README contributor block.
- Pass `./scripts/quick-test.sh` locally before pushing so CI doesn't churn.
- Score above the Intent Solutions 100-point rubric threshold in the
  marketplace-tier validator (`scripts/validate-skills-schema.py
--marketplace`).
- Get actionable feedback fast — Gemini PR review within 2–5 minutes,
  maintainer follow-up within 48 hours.
- Have the install command published in the README and `/plugins/<slug>/`
  page work the moment the merge lands.

**Key flows (these become JOURNEYS entries).**

1. Fork → clone → copy from `templates/` → edit plugin → run
   `quick-test.sh` → push → open PR.
2. Address Gemini PR review comments — every `[Critical]` and `[High]`
   finding must be resolved before merge.
3. Land merge → `pnpm run sync-marketplace` runs in CI → catalog updates →
   marketplace site rebuilds → contributor block at top of README gets
   their attribution.
4. Bump version in own plugin's `package.json` → `publish-changed-packages`
   workflow detects the version bump → publishes `@intentsolutionsio/<plugin>`
   to npm.

**What they care about most.**

- The validator's error messages must point at the exact problem (line +
  rule + suggested fix).
- The 100-point rubric is published and stable — they shouldn't get
  surprised by a moving bar.
- Their install command works on day one (no broken `/plugin install`
  string in the merged README).

**What would make them disengage.**

- Validator says "fail" without saying why.
- Quick-test passes locally but CI fails because of a check that's not in
  quick-test.
- The Gemini reviewer is wrong and the maintainer takes a week to weigh in.
- Their plugin lands and the marketplace page 404s for a day.

---

## Persona 2 — Marketplace Consumer ("Maya")

**Role.** End user browsing [tonsofskills.com](https://tonsofskills.com) to
find plugins or skills. Most arrive via search engines, social posts, or
the install command in someone's blog.

**Primary goals.**

- Find a plugin or skill that solves a specific problem.
- Skim what it does before installing — read description, see verification
  badge, see the install command.
- Copy-paste the `/plugin install` command into Claude Code and have it
  work first try.
- Filter the catalog by category, type, or pack without the page reloading
  or losing scroll position.

**Key flows.**

1. Land on `/` (homepage) → enter a query in the hero search → redirect to
   `/explore?q=<query>` → click a card → land on `/plugins/<slug>/`.
2. Land on `/explore/` directly → use the type-toggle (plugin / skill / all)
   → click a result → land on plugin or skill detail page.
3. Land on `/skills/` → use category + tool filters → click a skill → land
   on `/skills/<slug>/`.
4. Visit `/cowork/` → download the mega-zip or a category bundle → unzip and
   install offline.
5. Read `/docs/getting-started/installation` → install `ccpi` globally →
   add the marketplace → install first plugin.

**What they care about most.**

- Search relevance — typing "git commit" should surface `git-commit-smart`
  near the top.
- The plugin detail page must show what the plugin actually does (not just
  its name + description blurb).
- Install commands are copy-paste correct — no broken slugs, no missing
  catalog suffix.
- Page loads fast on mobile (iPhone 13 / Pixel 5 are the canonical mobile
  viewports — see `marketplace/playwright.config.ts`).

**What would make them disengage.**

- A plugin detail page returns 404.
- The install command in the page copies a different slug than the URL.
- Mobile rendering is broken (lines longer than 5000 chars used to crash
  iOS Safari — `compressHTML: false` in `astro.config.mjs` is there to
  prevent regression).
- Search returns nothing for an obvious query.

---

## Persona 3 — MCP Integrator ("Mei")

**Role.** Developer wiring an MCP server plugin (`pr-to-spec`,
`domain-memory-agent`, etc.) into their own Claude Code config. These plugins
ship as published npm packages with a TypeScript runtime, not just markdown
instructions.

**Primary goals.**

- Find the right MCP plugin via the marketplace.
- Install the npm package and have its `dist/index.js` be executable + have
  the correct shebang.
- Have the `.mcp.json` in the plugin describe the server contract clearly
  enough that Claude Code's `/mcp` tooling registers it on first try.
- Pin a known-good version (versioning is manual per
  `CLAUDE.md` — `package.json` `version` is the source of truth).

**Key flows.**

1. Browse `/explore?type=plugin&category=mcp` → click an MCP plugin → see
   the install command + `.mcp.json` in the README.
2. `npm install -g @intentsolutionsio/<mcp-plugin>` → the binary is on
   `$PATH` and `--help` works.
3. Wire the MCP server into Claude Code's settings → restart →
   `/mcp` lists the new tools.
4. Bump pinned version when a new release ships (publish-changed-packages
   workflow makes this safe — only versions not yet on npm get published).

**What they care about most.**

- The published `.tgz` actually contains a working `dist/index.js` with
  `chmod +x` — the `cli-smoke-tests` CI job's "Verify bin entrypoint is
  executable" check catches this on every PR.
- Tool names in the MCP server match the documentation — Claude won't
  invoke a tool that doesn't exist.
- No `workspace:` deps in the published `package.json` — verified by the
  `cli-smoke-tests` job's "Verify no workspace dependencies" step.
- `npm pack --dry-run` shows the right files (no `node_modules`, no test
  files, no `.env`).

**What would make them disengage.**

- Published binary is a TypeScript file, not a compiled JS file.
- Shebang missing — Linux refuses to exec the binary.
- Documented MCP tool name doesn't match what the server registers.
- `.mcp.json` references env vars that aren't documented.

---

## Persona 4 — CLI User ("Casey")

**Role.** Developer using `ccpi` (`@intentsolutionsio/ccpi`) from their
terminal — usually right after running `npm install -g @intentsolutionsio/ccpi`
the first time, then again when adding plugins to a new project. Could be
the same human as Maya at a different point in their journey, but the
needs are different so we treat them as a separate persona.

**Primary goals.**

- `ccpi --version` and `ccpi --help` work and exit 0.
- `ccpi marketplace-add` writes the catalog config files.
- `ccpi install <plugin>` prints the right `/plugin install ...` command.
- `ccpi doctor` flags real problems (missing Claude Code config dir,
  outdated catalog, broken installed plugins).
- `ccpi validate --strict` returns non-zero exit code on failure so it
  composes into shell pipelines.

**Key flows.**

1. `npm install -g @intentsolutionsio/ccpi` → `ccpi --version` → install
   succeeded.
2. `ccpi marketplace-add` → catalog written → `ccpi list --all` shows
   ~420 plugins.
3. `ccpi install <plugin>` → see the `/plugin install` command → paste
   into Claude Code.
4. `ccpi upgrade --check` → see outdated plugins → `ccpi upgrade --all`
   to refresh.
5. `ccpi doctor` to debug a broken setup.

**What they care about most.**

- Exit codes are meaningful — `0` on success, non-zero on failure. Shell
  pipelines depend on this.
- `--help` text covers every command and flag.
- Bundle size is small (< 50 KB gzipped today) — install latency matters.
  Enforced by the size-limit budget on every PR.
- Semver — major bumps mean breaking command interface, minor means
  additive, patch means bug fix. The cli-publish workflow ties npm
  versions to git tags `cli-v*.*.*`.

**What would make them disengage.**

- A flag silently changes behavior between versions.
- `ccpi doctor` says "all good" but the install actually doesn't work.
- Install pulls in 100 MB of transitive deps.

---

## Persona 5 — Pack Subscriber ("Sam")

**Role.** Engineer using one of the SaaS skill packs (`langchain-py-pack`,
`databricks-pack`, `apollo-pack`, etc.) at `plugins/saas-packs/<vendor>-pack/`.
They want a deeply curated set of skills for one vendor, not a single
plugin. Maps to `marketplace/src/content/docs/guides/saas-skill-packs.md`.

**Primary goals.**

- Install the entire pack with one command (`ccpi install --pack <name>`)
  and get every skill activated.
- Each skill in the pack hits the langchain bar — full SKILL.md frontmatter,
  real code examples, accurate `compatibility:` (matches the actual SaaS
  product version).
- External links (vendor docs, API references) work — broken vendor URLs
  are a high-trust failure.
- Pack version pins to a specific vendor SDK version so the skills don't
  fall out of sync with the API.

**Key flows.**

1. Browse `/explore?type=pack` → click a SaaS pack → read the README.
2. `ccpi install --pack <name>` → install command for every plugin in
   the pack prints out → paste each into Claude Code.
3. Use a skill from the pack inside Claude Code → trigger phrases match
   the SKILL.md frontmatter → skill activates.
4. Vendor releases a new SDK version → pack maintainer bumps each skill's
   `compatibility:` → marketplace tier validator passes → publish flow
   ships a new pack version.

**What they care about most.**

- Skill quality. A pack with 30 stub skills is worse than 5 deep ones.
  The marketplace validator's `is_stub` flag (in
  `freshie/inventory.sqlite`) catches the worst offenders.
- Accurate `compatibility:` field — free-text per `agentskills.io/specification`
  (max 500 chars). Migrated from the deprecated `compatible-with:` CSV
  format via `scripts/batch-remediate.py --migrate-compatible-with`.
- No broken vendor URLs in the skill body or references.
- `validate-internal-links.mjs` catches internal link rot at build time;
  external link drift is currently uncovered (see RTM REQ-016).

**What would make them disengage.**

- Pack lists 30 skills, 25 are stubs.
- A SKILL.md `compatibility:` says "Stripe SDK 2024.x" but the skill body
  references endpoints that were removed in 2025.
- Vendor docs link is dead.

---

## When to add a sixth persona

Only add a persona when there's repo-visible evidence of a distinct user
type whose needs aren't covered by these five. Specifically:

- A new `ccpi` subcommand whose primary user isn't Casey (e.g. a
  `ccpi telemetry` command would imply an "operations / observability"
  persona).
- A new directory under `plugins/` or `marketplace/src/pages/` that has
  fundamentally different review/install/use flows.
- An issue cluster where five+ inbound reports describe a workflow none
  of the five existing personas would do.

If you can't point at a specific repo signal, the persona is hypothetical
— file it in JOURNEYS as `(uncovered)` instead.
