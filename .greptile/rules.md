# claude-code-plugins ("Tons of Skills") — review context for Greptile

This repo is the **Tons of Skills** marketplace for Claude Code plugins and skills (live at https://tonsofskills.com). It is three things at once:

1. A **catalog** of AI-instruction plugins, MCP-server plugins, skills, agents, and SaaS skill-packs under `plugins/` (~450 entries).
2. A **validator + CI gate system** (`scripts/validate-skills-schema.py` and friends) that grades every authored artifact against the IS marketplace standard.
3. An **Astro website** (`marketplace/`) that renders the catalog.

## Architecture you must respect

- **Two-catalog system.** `.claude-plugin/marketplace.extended.json` is the **source of truth** (edit this). `.claude-plugin/marketplace.json` is **auto-generated** by `pnpm run sync-marketplace` — never hand-edit it; CI's drift gate rejects divergence. The same step generates plugin `package.json`s and the README AUTO-TOC block.
- **The prose-spec validator is authoritative.** `scripts/validate-skills-schema.py` is the canonical gate. The `@intentsolutions/core` kernel is the SSoT being migrated to, currently in an **advisory soak**. Keep its pin exact and current, but do not treat a pin bump as an authority flip or promote the kernel CI lanes from advisory to blocking before the documented cutover gates pass.
- **External-sync pipeline.** `sources.yaml` + `scripts/sync-external.mjs` mirror external plugin repos into `plugins/`; synced plugins carry a `.source.json` marker.
- **Package managers:** pnpm everywhere **except `marketplace/` (npm)**, CI-enforced. Node >= 22 (Node 20 is end-of-life and `better-sqlite3`, pulled in by the root `@intentsolutions/jrig-cli` dev dependency, ships no Node 20 binary; Node 18 breaks workspace resolution).

## Prioritize (in order)

- **Correctness** — especially in the validator, the sync engine (`scripts/sync-external.mjs`), the marketplace build pipeline, and the CLI (`packages/cli`).
- **Security** — secrets (gitleaks/trufflehog), Unicode trapdoors (Trojan Source / bidi overrides), supply-chain, and prompt/tool safety in agent & skill definitions.
- **Gate integrity** — never weaken a CI threshold, test, or assertion (see the `no-gate-weakening` rule).
- **Catalog & data integrity** — generated-vs-source drift, required-fields / tier semantics, kernel-soak discipline.
- **Regression risk** across the ~450 catalog entries when a change touches shared scripts or config.

## Deprioritize

- Style-only or subjective-naming comments — eslint, prettier, ruff, markdownlint, and the Python validators already cover these.
- Churn on generated files: `.claude-plugin/marketplace.json`, generated `package.json`s, the README TOC, `marketplace/dist/`, `marketplace/public/downloads/`.
- Comments that merely duplicate an existing linter or typechecker.

## Related repos (multi-repo context)

The root config attaches the six-repository Intent Eval Platform cluster as read-only context:

- `intent-eval-core` owns shared authoring contracts, schemas, validators, and Evidence Bundle shapes.
- `intent-eval-lab` owns methodology, Blueprints, binding Decision Records, and governance rationale.
- `intent-audit-harness` owns deterministic gates and their Evidence Bundle emission.
- `j-rig-skill-binary-eval` owns behavioral evaluation, judge independence, and rollout decision logic.
- `intent-rollout-gate` is the thin GitHub Action shell consuming the published decision package.
- `intent-eval-dashboard` verifies and renders signed evidence.

Use those repos when a CCPI change crosses one of those contracts. Do not demand cross-repo changes for ordinary catalog or marketplace work, and do not copy a kernel-owned schema or predicate into CCPI merely because the related repo is available as context.

## Reviewing a `sources.yaml` entry

A `sources.yaml` entry is a **pointer** to an external repo, not the plugin, and it is validated at **sync time, not PR time**: the weekly `sync-external.mjs --strict` clones the upstream and runs it through `scripts/validate-skills-schema.py` before mirroring into `plugins/community/`.

- **Review the entry's schema** (`name`, `description`, `repo`, `source_path`, `target_path`, `include`/`exclude`, `license`, `category`) against the established format.
- **Do NOT assert whether the upstream repo exists, is reachable, or has valid frontmatter from a web search.** Repo existence is time-sensitive (a repo can be created minutes after review) and non-deterministic; the `--strict` clone and `validate-skills-schema.py` are the real gates. If you flag upstream risk, say "the sync will verify this at clone time," not "the repo does not exist."
