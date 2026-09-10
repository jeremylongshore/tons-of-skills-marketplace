# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Tons of Skills — Claude Code plugins marketplace. Live at https://tonsofskills.com

**Runtime:** Node `>=20.0.0`, pnpm `>=9.15.9`. Node 18 causes silent workspace-resolution failures.

**Package manager:** `pnpm` everywhere **except** `marketplace/` which uses `npm` (CI-enforced).

**Contributor guidelines live in `AGENTS.md`** — project structure, build/test/dev commands, style and naming, test conventions, commit/PR expectations, and the merge gates. Read it before starting work. (Session protocol lives in this file: the beads workflow in § Beads Issue Tracker — where `bd prime` is also the post-compaction context-recovery step — and the end-of-session push checklist in § Session Completion.)

## Cross-session coordination — another Claude session may be in this repo

This repo is frequently worked in **parallel** with the `intent-eval-platform` umbrella session (that platform's CCPI validator + jrig-cli + kernel reach into this repo). Sessions are separate processes that share only the filesystem, so stay in sync via the shared surfaces:

- **Read + append the shared journal** on cross-repo work: `~/000-projects/CROSS-SESSION-LOG.md` (append a dated line: what / branch or PR# / status).
- **Durable cross-cutting tasks:** umbrella beads `~/000-projects/.beads/`, label `cross-session` (`bd list --label cross-session`).
- **Guard the working tree:** this repo has ONE checkout; a concurrent session can `git checkout`/`reset` it out from under you and **wipe UNCOMMITTED work** (happened 2026-07-01). Commit early, or do multi-step file work in a `git worktree`.

Full protocol (loaded by every session under `/home/jeremy`): `/home/jeremy/CLAUDE.md` § "Cross-session coordination".

## Essential Commands

```bash
# Before ANY commit — regenerates marketplace.json, plugin package.jsons, README TOC
pnpm run sync-marketplace

# Quick sanity check (~30s)
./scripts/quick-test.sh

# Build & test
pnpm install && pnpm build
pnpm test && pnpm typecheck
pnpm lint
pnpm run verify                   # Full pipeline — what CI's `verify` job runs

# Validator (schema 4.1.0 — see 000-docs/SCHEMA_CHANGELOG.md)
python3 scripts/validate-skills-schema.py --verbose
python3 scripts/validate-skills-schema.py --marketplace --verbose
python3 scripts/validate-skills-schema.py --marketplace --populate-db freshie/inventory.sqlite
python3 scripts/validate-skills-schema.py --agents-only --verbose   # agents only (kernel-strict gate)

# Unicode hygiene gate — Trapdoor / Trojan Source defense for SKILL.md /
# plugin.json / agent / command files. Default mode blocks on tag chars
# (U+E0000-E007F) + bidi overrides (CVE-2021-42574). --strict also blocks
# on zero-width / format chars outside the BOM position.
python3 scripts/validate-unicode-hygiene.py
python3 scripts/validate-unicode-hygiene.py --strict           # tighter
python3 scripts/validate-unicode-hygiene.py path/to/file.md    # one file
python3 -m unittest tests.test_validate_unicode_hygiene -v     # regression suite

# Marketplace website
cd marketplace/ && npm run dev    # localhost:4321
cd marketplace/ && npm run build
cd marketplace/ && npx playwright test

# Single test
cd packages/cli && pnpm test -- --grep "pattern"

# JRig behavioral eval — the published @intentsolutions/jrig-cli (bin `j-rig`),
# pinned as a root devDep. Invoke via `pnpm exec j-rig` so it resolves the
# repo's pinned version (node_modules/.bin/j-rig), NOT a global shim.
pnpm exec j-rig --version         # → 0.1.2 (the real 7-layer CLI)
pnpm exec j-rig check <skill-dir> # Tier 3A: deterministic (~seconds, free, no API key, no DB)

# Real behavioral eval (opt-in, ~$2-5/skill) — needs the native better-sqlite3
# build (run `pnpm rebuild better-sqlite3` once; the build script is not
# auto-run on install). ALWAYS route through the wrapper — it runs j-rig
# against a /dev/shm scratch DB and records the verdict into forge_proofs via
# scripts/record-jrig-proofs.mjs. NEVER pass freshie/inventory.sqlite to
# `j-rig eval --db` directly: j-rig writes its own run tables into whatever
# --db it is given, which contaminates the tracked CMDB (and, pre-allowlist,
# leaked those tables to the public DoltHub record).
scripts/run-jrig-eval.sh --skill-dir <skill-dir> --plugin <catalog-name> \
  --inventory-db freshie/inventory.sqlite
# DEEPSEEK_API_KEY is SOPS-decrypted in-process by the wrapper
# (intent-eval-lab/.env.sops; see the IEP umbrella CLAUDE.md credential
# table). Defaults: --provider deepseek --models deepseek-v4-flash — a real
# behavioral provider, this is ground truth; other providers (haiku/sonnet/
# opus via Anthropic, etc.) remain available via --provider/--models.
```

## Two Catalog System — Critical

| File                                       | Purpose                        | Edit?     |
| ------------------------------------------ | ------------------------------ | --------- |
| `.claude-plugin/marketplace.extended.json` | Source of truth                | **Yes**   |
| `.claude-plugin/marketplace.json`          | CLI-compatible, auto-generated | **Never** |

`pnpm run sync-marketplace` regenerates all three derived artifacts: `marketplace.json`, any missing `plugins/**/package.json` files, and the `README.md` AUTO-TOC block. The pre-commit hook runs this automatically when `marketplace.extended.json` is staged.

CI fails if any derived file is out of sync. Never hand-edit auto-generated files.

## Marketplace Build Pipeline

`npm run build` in `marketplace/` runs 8 sequential steps via `scripts/build.mjs`: discover-skills → extract-readme-sections → sync-catalog → generate-unified-search → build-cowork-zips → validate-cowork-manifest → copy-public-data → astro build. `readme-sections.json` is an untracked build projection; `npm run dev` regenerates the README projection before Astro starts. Marketplace pages do not publish a JRig verification badge: behavioral-eval results remain governed evidence in Freshie until a retained-evidence class and a separately reviewed public projection exist.

`discover-skills.mjs` emits two artifacts (schema 3.4.0+): `skills-index.json` (L0, ~97 KB gzipped, metadata only — for trigger-match / browse) and `skills-catalog.json` (L1, ~5.5 MB gzipped, full body HTML). Both carry top-level `schemaVersion` + `level` fields. CLI flag `--level=metadata|full|file` (default `full`).

`pnpm run validate:generated-content` regenerates the L0 index, L1 full catalog, and plugin catalog
in memory and byte-compares all three with the Git index. The check is non-mutating and
network-free. The plugin catalog renderer reads only the canonical extended catalog and L1 skill
projection; its tracked output is never an input. The unified search projection remains tracked
but is not yet covered by this command; blueprint E1.8 owns its separately reviewed determinism
repair and gate expansion. External statistics are E1.10 snapshots, and `spotlights.json` is
canonical editorial data, not deterministic build output.

**Gotcha:** `compressHTML` is disabled in `astro.config.mjs` — iOS Safari fails on lines > 5000 chars. CI enforces this.

Performance budgets (CI-enforced; authority is `scripts/check-performance.mjs` `BUDGETS`): 48 MB total gzipped, 1 MB largest file, < 30s build, 2,800–4,500 routes.

## Auto-cowork contract

**Author flow.** Add a plugin to `.claude-plugin/marketplace.extended.json` and run `pnpm run sync-marketplace`. That is the entire authoring step. The pre-commit hook regenerates `marketplace.json`, plugin `package.json`s, and the README AUTO-TOC. There is no separate "update the cowork page" step.

**Pipeline (deterministic from the catalog).** `cd marketplace && npm run build` runs `scripts/build.mjs`, which on every invocation:

1. `cowork:zips` (`scripts/build-cowork-zips.mjs`) — wipes `marketplace/public/downloads/{plugins,bundles}` and rebuilds them from `marketplace.extended.json`. Produces individual plugin zips, category bundle zips, the mega-zip, `downloads/manifest.json`, and the Astro-consumed `marketplace/src/data/cowork-manifest.json`. Skips `category: mcp` entries (MCP plugins do not appear in cowork).
2. `cowork:validate` (`scripts/validate-cowork-manifest.mjs`) — drift gate. Fails the build if catalog ↔ manifest ↔ disk fall out of alignment (orphan zips, missing entries, or stale manifest rows). Runs again in CI as a discrete step in `.github/workflows/validate-plugins.yml` so the failure signal is clearly named.
3. `astro build` — copies `marketplace/public/` → `marketplace/dist/`. The `/cowork/` page reads `cowork-manifest.json` at build time and renders the download grid.

**Deployment authority.** Intent OS owns the deployment runbook, host state, and operational behavior. Consult `intent-os/ops/deploy/` for the current deployment record; this repository must not restate host commands or paths.

**Don't commit downloads/.** `marketplace/public/downloads/` is gitignored (see `.gitignore:146`). CI checks out fresh and rebuilds from scratch — local state cannot leak to prod. Never commit or hand-edit anything under that directory.

**Don't wire cowork build into `sync-marketplace`.** `sync-marketplace` is the fast (<2s) per-commit hook; `cowork:zips` is the slow (~30s) per-build step. They run on different cadences by design.

## External Plugin Sync (mirror-by-default)

Adopted model: **mirror by default · upstream improvements · never clobber.** Decision record: `000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md`; pipeline audit + hardening: `000-docs/691-AT-AUDT-sync-external-pipeline-audit-and-hardening.md`.

**Scale first — external is a minority augment, not the core.** 443 entries in `marketplace.extended.json` (the `measure:e1` catalog-entry cohort is measured separately — regenerate with `pnpm run measure:e1` rather than quoting a number from here), but only 36 are externally synced (30 third-party sources + 6 of Jeremy's own repos, per `sources.yaml`; the mirror plugins are the 36 dirs carrying a `.source.json`). The overwhelming majority is in-repo Intent Solutions work. The sync is a curated side-channel, not the marketplace — treat external contributors as a respected minority augment, never the center of gravity.

**How sync works.** `sources.yaml` registers each external source. `.github/workflows/sync-external.yml` runs weekly (Mondays 06:00 UTC) and on demand (`workflow_dispatch` / `repository_dispatch`), invoking `scripts/sync-external.mjs` to mirror a source's files into `plugins/` and open an automated PR. A human reviews every auto-PR — historically ~1 in 10 sync PRs merges. The contributor's own repo is the source of truth; we do NOT locally edit a pure-mirror plugin.

**Mirror vs curate.** Default is a pure mirror — the upstream repo governs, and improvements flow by upstreaming (see below), so the mirror becomes A-grade naturally with nothing to revert. Only when we deliberately harden a plugin past its upstream do we mark it `curated:` and freeze it.

**Never-clobber guard (`curated:` freeze).** A source with `curated: true` in `sources.yaml` is FROZEN: `sync-external.mjs` logs `Curated — mirror frozen`, writes no files (no clone, no overwrite, no orphan-prune), and only keeps the catalog entry current — so even a `--force` sync can never revert our edits. `tonone`, `servicegraph`, and `schedule-after-usage-reset` carry `curated: true` today; `hyperflow` does NOT — it is the completed off-ramp example (its frontmatter hardening merged upstream, so the flag was dropped in #1008). This guard exists because a prior `--force` run reverted ~100 A-graded agents back to 3-field upstream stubs — the ~18.9k-line deletion that motivated the whole model. Note `curated:` (we hardened it locally) and `verified:` (a maintainer vetted quality/trust) are orthogonal: all three curated sources are `curated: true` but `verified: false`, an honest state and exactly why the two flags are separate.

**Pileup auto-close (≤1 open sync PR).** `sync-external.yml` runs a "Close superseded sync PRs" step before Create-PR: it closes older open `automation/sync-external-*` PRs (with `--delete-branch`), keeping at most one open sync PR. The safe unique-per-run-branch model (from the 691 audit, which fixed an earlier shared-branch clobber) is preserved — this only prunes the pileup that model produced.

**How we upstream respectfully.** Want a plugin at our A-grade bar? We bring THEIR plugin to standard on THEIR repo: a friendly issue first ("we featured your plugin and hardened its frontmatter to our A-grade bar — would you be open to a PR upstreaming it?"), then a PR the contributor owns and merges. No surprise PRs; credit preserved; they decide. Once merged upstream, the mirror is A-grade naturally and `curated:` can be dropped. **Any contributor-facing post (issue or PR body) gets Jeremy's wording sign-off BEFORE posting.**

## Plugin Structure

**AI instruction plugins** (`plugins/[category]/[name]/`): `.claude-plugin/plugin.json` + `README.md` + optional `commands/*.md`, `agents/*.md`, `skills/[name]/SKILL.md`.

**MCP server plugins** (`plugins/mcp/[name]/`): TypeScript source in `src/`, built to `dist/index.js` (must be executable: shebang + `chmod +x`).

**Forge-generated plugins** include a `.forge/` audit trail dir (`research.md`, `ecosystem.md`, `proofs.md`) — build-time only, not used at runtime. Canonical example: `plugins/productivity/plane/`.

### SKILL.md Required Frontmatter (marketplace tier — all 8 fields)

```yaml
---
name: skill-name
description: |
  Capability summary. Use when ... Trigger with "...".
allowed-tools: Read, Write, Edit, Bash(npm:*), Glob
version: 1.0.0
author: Name <email>
license: MIT
compatibility: Designed for Claude Code
tags: [devops, ci]
---
```

Beyond the 8 required fields, schema 3.5.0+ adds optional visibility-gating fields, 3.6.0+ adds self-declared config fields, and 3.7.0+ adds `disallowed-tools` — see the Optional frontmatter section below.

`compatible-with` is deprecated. Migrate with: `python3 scripts/batch-remediate.py --migrate-compatible-with`

**Agents use `disallowedTools` (camelCase denylist).** Skills use `allowed-tools` (allowlist) AND optionally `disallowed-tools` (kebab-case denylist, schema 3.7.0+). The two field names are intentionally different — do NOT use camelCase on skills or kebab-case on agents; the validator rejects either mismatch. Agent-only fields: `effort`, `maxTurns`.

**Agent gate is kernel-strict (schema 3.10.0, NOT tier-gated).** Every authored agent must carry the kernel-floor 8 (`name, description, tools, model, color, version, author, tags`) plus the enterprise live set (`disallowedTools`, `skills`, `background`; + `hooks`, `mcpServers`, `permissionMode` on standalone agents) — all **errors** at every tier. Banned fields (`capabilities`, `expertise_level`, `activation_priority`, `type`, `category`, `compatible-with`, `when_to_use`) are errors; `fable` is an accepted model. **Corpus status (measured 2026-08-11, doc 721):** the advisory `--agents-only` lane recorded a baseline of **253 errors** across the agent corpus — the earlier "all agents A-grade" claim is retired until the lane is re-baselined clean; treat A-grade as the bar, not the current state. **Schema 3.11.0** added a body-vs-allowlist check: an agent whose body invokes `mcp__server__tool` not in its `tools` allowlist is an error (it would runtime-block). Validate with `--agents-only`.

### Optional frontmatter (schema 3.5.0 / 3.6.0 / 3.7.0 — all default to off)

- **Visibility gating (3.5.0):** `requires_env` / `requires_tools` / `fallback_for_env` / `fallback_for_tools` — list-of-strings. Skill hidden unless deps met; fallback form is the inverse. Cross-field overlap (`requires_X` + `fallback_for_X` of same value) is an ERROR.
- **Self-declared config (3.6.0):** `required_environment_variables` (top-level list, each entry needs `name` + `prompt`) and `metadata.intent-solutions.config` (nested list, each entry needs `key` + `description` + `default`). Full reference: `000-docs/264-DR-GUID-skill-config-pattern.md`.
- **Defense-in-depth disallow list (3.7.0):** `disallowed-tools` — kebab-case string or YAML list of tool patterns. Removes those tools from the model while the skill is active. Parallel to (not a replacement for) `allowed-tools`. Cross-field overlap with `allowed-tools` is an ERROR (mirrors the 3.5.0 visibility-gating overlap rule). Defense-in-depth for skills that legitimately need broad `allowed-tools` but should never reach for specific high-risk operations (`rm`, `curl`, `wget`, `.env` writes). Full reference: `000-docs/681-AT-ADEC-claude-code-platform-changelog-impact.md` § Change 1.
- **NON-NEGOTIABLE:** these are optional. `ALWAYS_REQUIRED` is still the 8-field set above. See issue #612 + `000-docs/681-AT-ADEC-claude-code-platform-changelog-impact.md` § Implementation directives before proposing any change to required fields — the 8-field set is preserved; `disallowed-tools` is additive, not required.

## CI gate architecture — three required checks (rebuilt 2026-07; skill-conform added 2026-07-23)

**Branch protection on `main` requires THREE always-reporting contexts: `ci-required` + `gitleaks` + `skill-conform`** (GitHub Actions app; `strict:false`, `enforce_admins:false`, 0 required approving reviews, code-owner reviews not required). CODEOWNERS routes ownership and optional review; it is not a merge gate. Authorization for any permissive baseline policy-envelope mutation is the narrower machine gate defined by blueprint 727 § 10.2/E6.6.

- **`ci-required`** is the final job in `.github/workflows/validate-plugins.yml` — `if: always()`, `needs:` all 23 gate jobs (validate, marketplace-compliance-ratchet, verify, test, check-package-manager, marketplace-validation, cli-smoke-tests, shellcheck-skills, skill-codeblock-syntax, typescript-coverage-audit, eslint-check, format-check, ruff-check, ruff-format-check, markdownlint, scan-synced-content, promote-curated-check, check-submission-docs, commit-scope-check, codeowners-drift, generated-content-drift, doc-governance, secret-diff-scan). It fails if any needed job ended `failure`/`cancelled`; a `skipped` result counts as PASS — legitimate **only** for a designed job-level `if:`.
- **`gitleaks`** comes from `secret-scan.yml` (also unfiltered).
- **`skill-conform`** is its **own** workflow (`.github/workflows/skill-conform.yml`) — `pnpm exec audit-harness conform --strict` over the full marketplace corpus. Always-reports (no path filter). **Never** folded into `ci-required`'s `needs:` (doc 110 § 5: a skippable/path-scoped job must not green the aggregate). Baseline after #1108/#1118: thousands PASS / 0 FAIL; remaining ADVISORY is the harness-side missing marketplace schema only.
- **Advisory (never required):** `.github/workflows/skill-eval-advisory.yml` — j-rig behavioral eval on changed skills that already carry `eval-spec.yaml`. Kill-switch `vars.ENABLE_SKILL_EVAL=true` + same-repo guard + `MINIMAX_API_KEY`. Graduation to required needs Jeremy + ≥4-week clean flap window (doc 110).
- **Ruff pin:** `validate-plugins.yml` installs **`ruff==0.15.22`** for both ruff-check and ruff-format-check. Unpinned install pulled 0.16.0 mid-2026-07-23 and treated SKILL.md fenced Python as format targets (~1132 files). Do not unpin without a deliberate corpus reformat.

**Why, and the rules that keep it fixed (do not regress):** the previous 10-context required set sourced checks from path-filtered workflows, so a PR without matching files left them "Expected" forever and could never merge (the #778/#964 stuck-PR class).

1. `validate-plugins.yml` runs on **every** `pull_request` — never add a `paths:` filter to it.
2. **Never add a path-filtered workflow's context to the required-status set.** To make a new check blocking: add it as a job in `validate-plugins.yml` and list it in `ci-required`'s `needs:`.
3. A job in the aggregate's `needs:` may only skip via a _designed_ `if:` — an undesigned skip silently passes the gate.
4. The five split lint workflows (`lint-markdown/python/shell/typescript/skill-codeblocks.yml`) were retired 2026-07; their identically-named jobs live in `validate-plugins.yml`. Do not re-split them. `tests/ci/test_path_routing.py` pins this invariant.

**Supply-chain gate:** `scan-synced-content` (the REFUSE/CHALLENGE/FLAG scanner over `plugins/**`, `scripts/scan-synced-content.mjs`) blocks via the aggregate. A `sources.yaml`-only PR scans zero files and deliberately fails with a **waivable** `sources-change-unscanned` CHALLENGE — a reviewer clears it with a `sources.yaml:sources-change-unscanned  <reason>` line in `scripts/scan-allowlist.txt` after confirming the source is vetted and pinned in `sources.lock.json`. REFUSE is never waivable.

**Submission-docs intake gate:** `check-submission-docs` (`scripts/check-submission-docs.mjs`) blocks via the aggregate. A PR that adds a NEW plugin directory (its `.claude-plugin/plugin.json` is an added file in the diff) must ship the tiered submission documents per the matrix in `templates/skill-docs/README.md` (micro → `docs/PRD.md`; standard → + `docs/ADR.md`; pack, 2+ skills → + `docs/ONE-PAGER.md`; `CFO-ONE-PAGER.md` stays review-enforced — "money is the pitch" isn't deterministic). External mirror plugins (dir contains `.source.json`) are exempt — their docs live upstream. A PR adding no new plugin passes clean INSIDE the script (the designed skip), so the job always reports. Standard: `000-docs/700-DR-GUID-skill-submission-standard.md`.

**Advisory lanes (report, never block — never promote into the required set from a side PR):** the two kernel lanes (next section); agent frontmatter (`validate-skills-schema.py --agents-only`, report-only with a tracked `REPORT-ONLY-UNTIL:` marker — corpus unbaselined); `.mcp.json` (`scripts/validate-mcp-config.mjs`, never `--strict` — that promotion belongs to the DR-049 soak checklist); CodeQL (PR trigger scoped to `packages/**` + `marketplace/src/**` so it adds no fan-out to plugin PRs); and the PR pre-screen (below).

### AI review — Greptile is active and advisory; CI is the only merge gate

**As of 2026-07-23 Greptile is active through the GitHub App and has reviewed recent CCPI PRs.** Its version-controlled policy lives under `.greptile/`; treat its findings as advisory semantic-review input, not a merge signal. Gemini Code Assist consumer product is **sunset** (bot posts a sunset notice only; `.gemini/config.yaml` has `code_review.disable: true`). Fully removing Apps is a UI/admin action. Optional future path: SHA-pinned MiniMax review (`MINIMAX_API_KEY` + `ENABLE_MINIMAX_REVIEW`) as already patterned in `minimax-review.yml`.

**Operationally: never block a merge waiting for an AI review.** Required contexts are **`ci-required` + `gitleaks` + `skill-conform`**.

### PR pre-screen (advisory respond leg)

`pr-prescreen.yml` (`pull_request_target`; kill switch `vars.ENABLE_PR_PRESCREEN`) grades changed plugins with the pinned validator and responds in two low-noise ways: a **`prescreen-grade` commit status** on every run (advisory forever — never a required context) and **one upserted marker comment** only on `CHANGES_REQUESTED`/`HARD_BLOCK` (silent on PASS; re-runs edit the same comment). Two hard-won invariants:

- **The validator anchors its scan root to its own script location** (`Path(__file__).resolve().parents[1]`), not the cwd. Prescreen therefore copies the BASE-authored validator into the PR tree and runs the copy — invoking `../base/scripts/…` directly grades **main's** tree and false-PASSes every frontmatter change (the 2026-07 bug, fixed in #980). Do not "simplify" this back.
- **Never checkout or execute PR-authored code in a `pull_request_target` workflow.** Applies equally to `plane-sync.yml` (which runs on `pull_request_target` so fork-PR close-outs get secrets — it reads event context only).

## Validation & the kernel SSoT — CI/CD posture

> **Authority map:** which document owns which fact class is assigned in blueprint
> `000-docs/727` § 11 (indexed by `STANDARDS.md § Canonical documents`). The sections below are
> operational guidance that NAMES its authorities — where this file and an owner disagree, the
> owner wins, and the doc-governance assertions (`validate:doc-fact-assertions`) pin the facts
> most prone to drift.

Two things grade frontmatter in this repo today, and the relationship between them is the load-bearing context to preserve.

### The two validators

- **Prose-spec validator (authoritative):** `scripts/validate-skills-schema.py`. This is the canonical gate. It runs at standard and marketplace tiers, it grades both frontmatter AND markdown body sections, and at marketplace tier a missing required field is an **ERROR** (not a warning). Its CI jobs block merges through the `ci-required` aggregate (see "CI gate architecture" above). `ALWAYS_REQUIRED` (the IS 8-field set) is hand-authored here and stays **AUTHORITATIVE** — read `000-docs/SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES before touching it. The IS rubric sits on top of Anthropic's permissive spec; the marketplace tier is intentionally strict. Do not reduce the 8-field set, do not demote marketplace errors to warnings, and do not "realign" to Anthropic's floor — any change to required-fields / tier model / error-vs-warning semantics is approval-gated per that doc.

- **Kernel machine-spec (the SSoT being migrated to):** `@intentsolutions/core` — its `schemas/authoring/v1` family (byte-frozen) plus the strict fork `authoring/v2` — is the single internal source of truth for "what is a valid agent-native artifact." The kernel's `skill-frontmatter` schema encodes the **same** IS 8-field required set as a pure `allOf` of upstream-base + universal folds + the IS overlay. The plan of record is for `validate-skills-schema.py` to **consume the kernel folds** instead of its hand-rolled rule sets. That migration is in progress; the root kernel pin is **exactly `0.10.0`** in `package.json` (no `^`/`~`). The `authoring/v1` schema family is byte-frozen across kernel package versions, so a pin bump tracks the latest published kernel without changing the `authoring/v1` contract the shadow lane reads. Contract semantics for `authoring/v1` fields are canonical in the kernel's own changelog — cite it, do not duplicate it (see `000-docs/SCHEMA_CHANGELOG.md` § "Kernel changelog citation").

### Two advisory lanes (never block) running the soak

Both are `continue-on-error: true`, neither is in the required-status set, and neither mutates anything:

- **kernel-shadow soak** — `.github/workflows/kernel-shadow-validation.yml` + `scripts/kernel-shadow-validation.mjs`. Runs the kernel-pinned `skill-frontmatter` schemas (from `@intentsolutions/core@0.10.0`) over the same SKILL.md corpus the prose-spec validator grades and logs per-file AGREE / DISAGREE deviation to `scripts/.kernel-shadow/report.json`. This is the DR-049 shadow soak (the "zero-on-corpus shadow signal"). The cutover-relevant number is strict `authoring/v2` **existing-PASS / kernel-FAIL**; the frontmatter-scoped `authoring/v1` deviation remains supporting evidence. A file that fails the prose-spec on missing `[body]` sections but has valid frontmatter is a scope difference, not a kernel gap, and is excluded.
- **kernel-vendor-hash gate** — `.github/workflows/kernel-vendor-hash.yml` + `scripts/kernel-vendor-hash.mjs`. Enforces the version-coupling invariant **V ≤ C ≤ K** (vendored ≤ CCPI-declared ≤ kernel-latest) plus a ≤7-day staleness bound. Soak-aware: it reads the exact `0.10.0` pin, polices ordering/staleness only, and must never pressure a pin bump or change validator authority.

The validator itself does a kernel-loaded **shadow read** of `ALWAYS_REQUIRED` (`load_kernel_required()` / `--kernel-shadow`) — it compares the kernel's effective required set against the hand-authored one and reports drift. The hand-authored `ALWAYS_REQUIRED` stays authoritative; the shadow read is observational only.

### Do-not-flip soak discipline (do not lose this)

**The kernel pin and the authority flip are two SEPARATE axes — do not conflate them.** The pin is _intended_ to track the latest published kernel; bumping it keeps the shadow lane reading a current, byte-frozen `authoring/v1` contract and is a routine governance/coupling update, not an authority change.

> **Current coupling receipt (2026-08-30).** The root pins are exactly `@intentsolutions/core@0.10.0` and `@intentsolutions/jrig-cli@0.2.0`; a narrow root override keeps the CLI's published `core@0.9.0` dependency on the governed `0.10.0` root copy, and the lockfile resolves one kernel version. `@intentsolutions/audit-harness` is exactly `1.4.0` (verify against `package.json`, not this line — it has drifted before). The pin bump is complete, but it is **not** an authority flip: both kernel lanes remain advisory and `validate-skills-schema.py` remains authoritative.

What stays frozen is the **authority**: do **NOT** flip the kernel-shadow lane from advisory to authoritative (blocking) until ALL of these hold:

1. ≥99.5% corpus agreement (deterministic folds must be 100%; the 0.5% band is reserved for non-deterministic surfaces only);
2. ≥30 days of advisory soak;
3. zero open P0 blockers;
4. the Rekor superseding-event rollback protocol implemented and tested;
5. governance sign-off from the CTO + CISO + VP-DevRel triple; and
6. a ≥14-day public deprecation-window notice to affected skill authors.

As of 2026-08-30 the soak has **not** met the bar. The current 3,630-file report has strict `authoring/v2` `existing-PASS / kernel-FAIL = 0` and `authoring/v1` frontmatter agreement of 3,624/3,630 (99.83%), but six real frontmatter disagreements remain and the deterministic-fold 100% condition is not proven. The new-pin soak is under 30 days, open P0s remain, and the rollback, sign-off, and public-notice conditions are not complete. Until every condition above is satisfied, validator authority stays with `validate-skills-schema.py` and both kernel lanes stay advisory. Promotion to blocking is a separate, later cutover step gated by these conditions — never a side effect of an unrelated PR.

**Alignment note (`@intentsolutions/jrig-cli`).** The `j-rig` behavioral-eval CLI is a root devDep pinned to **exactly `@intentsolutions/jrig-cli@0.2.0`**. Its published manifest still depends on **`@intentsolutions/core@0.9.0` (exact)**, so the root `pnpm.overrides` entry deliberately forces the single governed `@intentsolutions/core@0.10.0` copy across the graph; `pnpm list --depth 20` and the lockfile must continue to prove that single-version result. The pin bump is a coupling update only; the authority flip to `authoring/v2` remains the separate, six-condition cutover above.

### Validator consolidation (already landed)

A recent cleanup removed 74 dead duplicate `validation.sh` stubs, collapsed previously-diverged secondary validators into delegating wrappers around the canonical `validate-skills-schema.py`, and added the kernel-loaded shadow read described above. There is now one canonical validator; secondary entry points delegate to it.

### auto-bump posture for contributors

`.github/workflows/auto-bump-on-pr.yml` auto-bumps changed plugins' patch versions on PRs (only on `plugins/**` / `packages/**` changes). For a docs-only or otherwise non-release PR, put **`[skip auto-bump]`** in the PR title or body so the auto-bumper steps aside. Minor/major bumps stay a deliberate human choice — hand-edit the version in the same PR. It stays on `pull_request` (not `pull_request_target`) by design — the bump needs a write token, which must never be handed to fork code; fork PRs are skipped cleanly, and a first-time fork contributor's queued "Approve and run" entry just no-ops when approved.

## Adding a New Plugin

**Hand-authored:** copy from `templates/`, add catalog entry to `marketplace.extended.json`, run `pnpm run sync-marketplace`, validate with `--marketplace`.

**Forge-generated:** `/skill-creator --forge <api-name>` — runs 8-gate workflow, requires a NOI (Name of Identity), produces Grade-A skill + `.forge/` audit trail + catalog entry.

To regenerate against a current API: `/skill-creator --reforge <plugin-name>`.

## Design System

Constitution: `marketplace/DESIGN.md` (Data-Dense Pro family, locked 2026-05-06). If a component disagrees with it, the component is wrong.

Key tokens (`marketplace/src/styles/tokens.css`): `--bg`, `--panel`, `--rule`, `--ink`, `--signal`. Old aliases (`--primary`, `--surface`, `--text`, `--border`) remain mapped for back-compat. CSS colors: **OKLCH only, never hex/rgb**.

Reject: gradients on cards, glassmorphism, drop-shadow stacks, `hover:scale-105` on whole cards.

## Killer Skill of the Week

Editorial — Jeremy picks manually for the marketplace website.

```bash
# Promote a new spotlight
node scripts/promote-spotlight.mjs path/to/new-spotlight.json
```

Source of truth: `marketplace/src/data/spotlights.json`. The root README deliberately
does not carry a spotlight copy.

## Key Identifiers — Do Not "Normalize"

- **GitHub repo (canonical):** `jeremylongshore/tons-of-skills-marketplace`
- **Marketplace catalog id:** `claude-code-plugins-plus`
- **Public install slug:** `jeremylongshore/claude-code-plugins` (legacy, GitHub 301s to canonical — hardcoded in CLI, Hero snippet, hundreds of READMEs — renaming is a breaking API change)

## Freshie Inventory

CMDB with a hybrid storage model: `freshie/inventory.sqlite` is the **local
runtime format** every tool reads/writes (UNTRACKED — the blob is out of git);
the **versioned system of record is Dolt**, exported by
`freshie/scripts/dolt-sync.py` into `freshie/dolt/` (gitignored) and pushed to
public DoltHub `jeremylongshore/freshie-inventory` with a `run-N` tag per
inventory run. The tracked compact export (`freshie/grades.csv` +
`freshie/grade-histogram.json`) is regenerated by every sync — its git diff is
the "skill X went B→A" story.

The full cycle:

```bash
python3 freshie/scripts/rebuild-inventory.py                         # 1. New discovery run
python3 scripts/validate-skills-schema.py --marketplace --populate-db freshie/inventory.sqlite  # 2. Compliance
python3 freshie/scripts/dolt-sync.py                                 # 3. Dolt commit + tag + DoltHub push
python3 freshie/scripts/promote-to-curated.py                        # 4. Refresh skills/.curated/ (skills.sh mirror)
sqlite3 freshie/inventory.sqlite "SELECT grade, COUNT(*) FROM skill_compliance GROUP BY grade;"  # runtime queries
python3 freshie/scripts/batch-remediate.py --dry-run && python3 freshie/scripts/batch-remediate.py --all --execute
```

**skills.sh curated mirror** (`freshie/scripts/promote-to-curated.py`): rebuilds
`skills/.curated/` as a generated mirror of the repo's best **A+B** plugin skills (our own;
external `.source.json` mirrors excluded — 2,392 promoted dirs at this writing; the promote gate message
is the live count) so skills.sh can index them — it only
crawls root `skills/` / `.curated/`, never `plugins/**/skills/`. The plugin skill stays the
source of truth; the mirror is wipe-and-rebuilt from the tracked `grades.csv` (not the
git-ignored `inventory.sqlite`, so the CI drift gate is reproducible), copies only
git-tracked files, and re-grades each candidate in-process (promote iff fresh grade still
A/B). Audit trail: `skills/.curated/MANIFEST.json`. It is excluded from the README count
(`generate-readme-toc.mjs`) and the inventory scan (`validate-skills-schema.py`
`find_skill_files`) so a mirror copy is never double-counted. Self-maintaining:
`promote-curated.yml` refreshes it weekly (PR on change, Slack-on-fail); the
`promote-curated-check` gate in `ci-required` fails a PR that edits a promoted source
without regenerating. Repo-page branding: root `skills.sh.json`.

History queries go to Dolt (`cd freshie/dolt/freshie`): `WHERE run_id = N`,
`AS OF 'run-N'`, `dolt diff run-7 run-8 --stat` — the run_id model is
append-only, so diffs between run tags show added rows, not cell changes.
Clone-free check: `curl "https://www.dolthub.com/api/v1alpha1/jeremylongshore/freshie-inventory/main?q=SELECT+COUNT(*)+FROM+skill_compliance"`.

**Interactive/MCP history — the in-repo `dolt-mcp-vcs` plugin** (`plugins/mcp/dolt-mcp-vcs/`,
registered as this project's MCP server → freshie Dolt on `127.0.0.1:3308`). Use it to query the
run-over-run history conversationally instead of hand-writing `dolt sql`:

- **Start the sql-server first** — the MCP client connects to a _running_ server; it is NOT
  auto-started. From `freshie/dolt/freshie`: `dolt sql-server -H 127.0.0.1 -P 3308` (run
  detached; log to a scratch path). Do NOT pass `-u`/`-p` — dolt ≥2 removed them from
  `sql-server`; the default `root` is passwordless, matching the MCP config's `DOLT_PASSWORD=""`.
  Then load tools with `ToolSearch
query="select:mcp__dolt-mcp-vcs__query,mcp__dolt-mcp-vcs__list_dolt_commits,mcp__dolt-mcp-vcs__list_dolt_diff_changes_by_table_name"`
  — `query` for `AS OF 'run-N'` reads, the diff tools for per-run deltas; expert agents
  `dolt-sync-advisor` / `bead-epic-auditor` / `dolt-mcp-vcs:beads-guru` are also available.
- **⚠️ Stop the sql-server before `freshie/scripts/dolt-sync.py`** — both write
  `freshie/dolt/freshie`; a live server holds the lock and the sync will clobber/deadlock. `kill
<server-pid>`, sync, then restart if you still need it.
- **Mutation gate**: destructive verbs (`push`/`merge`/`reset`/`branch-delete`) are
  **recommend-only, enforced at the wire** — since E4.9 the registered entrypoint is
  `plugins/mcp/dolt-mcp-vcs/scripts/dolt-mcp-guard.py`, which refuses those verbs before the
  server sees them and hides them from `tools/list` — so DoltHub pushes still go
  through the one-way `dolt-sync.py` exporter, never the MCP.

**Rules:** local is the sole writer — never merge DoltHub PRs or web-edit the
public database (the exporter is one-way and will clobber them). A failed
DoltHub push exits non-zero on purpose: until pushed, Dolt history is
single-copy on this box. Exporter unit tests: `python3 -m unittest
tests.test_dolt_sync`. Full details + restore path: `freshie/README.md`.

Key tables: `skill_compliance` (scores, grades, JRig columns) and `forge_proofs` (durable JRig behavioral-evaluation evidence). No marketplace projection or badge is generated from `forge_proofs`; publishing one requires retained, hash-matched evidence and a separately reviewed public-evidence boundary.

## npm Publish Pipeline

Patch version bumps happen automatically on PR (via `auto-bump-on-pr.yml`). For minor/major bumps, hand-edit the version in the same PR. Merge to main triggers publish + tag + GitHub Release via `publish-changed-packages.yml`. See `RELEASING.md` for the full operator flow.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->

## Internal governance agents — use them, don't re-derive their checks

This repo ships ~352 agents as **product** under `plugins/**/agents/`. Separately,
`.claude/agents/` holds 6 internal agents that exist to work **on this
repo** — 3 governance agents (below) plus 3 Omarchy-lane agents
(`omarchy-plugin-architect` to build, `omarchy-submission-auditor` to block a bad
submission, `omarchy-coverage-reporter` to prove what a PASS actually covered). The governance agents are advisory (read-only, no Write/Edit) — a deterministic
check belongs in a script wired to `ci-required`, not in a prompt.

| Agent            | Reach for it when                                                                                 | Catches                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `claim-verifier` | before merging anything that asserts counts, consumers, enforcement, provenance, or certification | false statements in PR bodies, commits, bead notes and governing docs — the class that shipped six times in one day              |
| `beads-warden`   | after a batch of `bd` writes, before closing an epic, when a bead premise smells stale            | dropped writes from the bd rapid-write race, closures whose _title_ overstates delivery, undispositioned beads, projection drift |
| `skill-auditor`  | repairing SKILL.md compliance                                                                     | frontmatter + body-section defects                                                                                               |

**Do NOT duplicate the bead specialists.** `plugins/mcp/dolt-mcp-vcs/agents/` already owns
the graph: `bead-dependency-mapper` (cycles, bottlenecks, critical path),
`bead-epic-auditor` (epic closure drift), `bead-recovery-specialist`, `beads-guru` (the
routing generalist), `dolt-sync-advisor`. `beads-warden` deliberately delegates to them and
keeps only record-integrity — a second owner of one fact is the anti-pattern.

`claim-verifier` delegates documentation-drift classes to the `/validate-consistency`
skill; take its **deterministic** findings as evidence and its advisory findings as leads.

**Verification traps these encode** (they have each produced a wrong verdict here):
`cmd | head; echo $?` reports _head's_ exit code — capture it directly; `git grep` searches
**tracked files only**, so use `git grep --untracked` (never stage a probe — that mutates
the caller's index) before concluding a pattern is absent; `grep`→`rg`,
`find`→`fd`, `cp`→`cp -i` (hangs) — use `/usr/bin/grep`, `command find`, `\cp -f`.

## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:

   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```

5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**

- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- END BEADS INTEGRATION -->
