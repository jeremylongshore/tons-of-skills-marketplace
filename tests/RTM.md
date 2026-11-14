# Requirements Traceability Matrix (RTM)

> **Status:** policy-zone (engineer-owned). Each row maps a documented
> requirement to its source-of-truth and the test or check that exercises
> it. **No fabricated rows.** Every requirement here is extracted from a
> file already living in this repo — `CONTRIBUTING.md`, `SECURITY.md`,
> `README.md`, `CLAUDE.md`, `marketplace/src/content/docs/**`, or one of
> the workflow YAMLs. Do not invent acceptance criteria the repo has never
> committed to.
>
> **Cross-references.** Personas in [`PERSONAS.md`](./PERSONAS.md), flows
> in [`JOURNEYS.md`](./JOURNEYS.md). ADRs are filed per the Document Filing
> Standard as `000-docs/NNN-AT-ADEC-*.md` — the four declines below are
> ADR-260 through ADR-263.

## Schema

| Column             | Meaning                                                      |
| ------------------ | ------------------------------------------------------------ |
| **ID**             | Stable identifier — never renumber, retire instead           |
| **Requirement**    | One-sentence statement of what we promise                    |
| **MoSCoW**         | MUST / SHOULD / COULD / WON'T (per the spec, not aspiration) |
| **Source**         | The file path where this requirement is documented           |
| **Tests / Checks** | The CI job, script, or test file that gates it               |
| **Status**         | covered / partial / uncovered                                |

## Catalog ingest & marketplace publishing

| ID      | Requirement                                                                                                            | MoSCoW | Source                                                      | Tests / Checks                                                              | Status  |
| ------- | ---------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------- | --------------------------------------------------------------------------- | ------- |
| REQ-001 | `marketplace.json` is auto-generated from `marketplace.extended.json`; never hand-edited                               | MUST   | `CLAUDE.md` § "Two Catalog System (Critical)"               | `validate-plugins.yml` `validate` job — "Sync CLI marketplace catalog" step | covered |
| REQ-002 | `pnpm run sync-marketplace` strips extended-only fields                                                                | MUST   | `CLAUDE.md` § "Two Catalog System (Critical)"               | `scripts/sync-marketplace.cjs` (run in `validate` job)                      | covered |
| REQ-003 | Every entry in `.claude-plugin/marketplace.json` `plugins[*].source` must point at an existing directory               | MUST   | `validate-plugins.yml` "Validate marketplace catalog" step  | `validate` job — `jq -r '.plugins[].source'` loop                           | covered |
| REQ-004 | All JSON files (excluding `tsconfig*.json`) must be valid JSON                                                         | MUST   | `validate-plugins.yml` "Validate JSON files" step           | `validate` job                                                              | covered |
| REQ-005 | `README.md` table of contents must stay in sync with the catalog (between `AUTO-TOC:START` / `AUTO-TOC:END` sentinels) | MUST   | `CLAUDE.md` § "Auto-Generated Data Files (Never Hand-Edit)" | `node scripts/generate-readme-toc.mjs --check` (in `validate` job)          | covered |

## Plugin / skill structural requirements

| ID      | Requirement                                                                                                                                                                                 | MoSCoW | Source                                                                                                            | Tests / Checks                                                                         | Status  |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------- |
| REQ-006 | Every plugin must have a `README.md`                                                                                                                                                        | MUST   | `CONTRIBUTING.md` § "Adding a Plugin", `validate-plugins.yml` "Check plugin structure"                            | `validate` job                                                                         | covered |
| REQ-007 | `plugin.json` may only contain: `name`, `version`, `description`, `author`, `repository`, `homepage`, `license`, `keywords`                                                                 | MUST   | `CONTRIBUTING.md` (final paragraph of "Adding a Plugin"), `CLAUDE.md` § "Plugin Structure"                        | `validate-plugins.yml` `validate` job (rejects unknown fields)                         | covered |
| REQ-008 | Every shell script under a plugin's `scripts/` directory must be executable                                                                                                                 | MUST   | `validate-plugins.yml` "Check plugin structure"                                                                   | `validate` job                                                                         | covered |
| REQ-009 | Skill frontmatter must validate against the IS enterprise 8-field set (`name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, `tags`) at marketplace tier | MUST   | `CLAUDE.md` § "SKILL.md Frontmatter (IS Enterprise Standard)", `000-docs/SCHEMA_CHANGELOG.md` § "NON-NEGOTIABLES" | `python3 scripts/validate-skills-schema.py --marketplace` (run in `test` matrix job)   | covered |
| REQ-010 | Skills must score above the 100-point Intent Solutions rubric threshold at marketplace tier                                                                                                 | MUST   | `CONTRIBUTING.md` § "What this means practically for your PR", `CLAUDE.md` § "Essential Commands"                 | `validate-skills-schema.py --marketplace`                                              | covered |
| REQ-011 | Deprecated `compatible-with:` CSV field must be migrated to free-text `compatibility:`                                                                                                      | SHOULD | `CLAUDE.md` § "compatibility examples"                                                                            | `python3 scripts/batch-remediate.py --migrate-compatible-with` (manual; not yet gated) | partial |

## Security & supply-chain

| ID      | Requirement                                                                                                        | MoSCoW | Source                                                                 | Tests / Checks                                                                                                                     | Status  |
| ------- | ------------------------------------------------------------------------------------------------------------------ | ------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------- |
| REQ-012 | No hardcoded secrets, API keys, or credentials in any plugin                                                       | MUST   | `CONTRIBUTING.md` § "Security", `SECURITY.md` § "How We Protect Users" | `secret-scan.yml` (gitleaks every PR + trufflehog weekly) — authoritative; informational sweep also runs in `validate-plugins.yml` | covered |
| REQ-013 | No dangerous shell patterns (`rm -rf /`, eval, base64-d, IP-curl) in plugin code                                   | MUST   | `validate-plugins.yml` "Security scan - Dangerous patterns"            | `validate` job                                                                                                                     | covered |
| REQ-014 | URLs must be HTTPS (no URL shorteners)                                                                             | SHOULD | `validate-plugins.yml` "Security scan - Suspicious URLs"               | `validate` job (warning only)                                                                                                      | partial |
| REQ-015 | Cowork zip downloads must not contain secrets, `node_modules`, `.git`, or symlinks; must include SHA-256 checksums | MUST   | `SECURITY.md` § "Distribution Security"                                | `marketplace/scripts/validate-cowork-security.mjs` + `validate-cowork-downloads.mjs` (in `marketplace-validation` job)             | covered |

## Marketplace site

| ID      | Requirement                                                                                                                      | MoSCoW | Source                                                     | Tests / Checks                                                                      | Status  |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------- |
| REQ-016 | Internal links across the built marketplace site must resolve                                                                    | MUST   | `CLAUDE.md` § "Marketplace Build Pipeline"                 | `marketplace/scripts/validate-internal-links.mjs` (in `marketplace-validation` job) | covered |
| REQ-017 | Every plugin in the catalog must have a corresponding `/plugins/<slug>/` route                                                   | MUST   | `CLAUDE.md` § "Marketplace Build Pipeline"                 | `marketplace/scripts/validate-routes.mjs`                                           | covered |
| REQ-018 | Production playbook routes must resolve                                                                                          | MUST   | `CLAUDE.md` § "Marketplace Build Pipeline"                 | `marketplace/scripts/validate-playbook-routes.mjs`                                  | covered |
| REQ-019 | Total bundle stays under 40 MB gzipped, largest file under 1 MB gzipped, build under 30s, route count 2,800–4,000                | MUST   | `CLAUDE.md` § "Performance Budgets"                        | `marketplace/scripts/check-performance.mjs` (in `marketplace-validation` job)       | covered |
| REQ-020 | `astro.config.mjs` keeps `compressHTML: false` (iOS Safari fails on lines >5000 chars)                                           | MUST   | `CLAUDE.md` § "Marketplace Build Pipeline" — "Gotcha"      | `marketplace-validation` job smoke test                                             | covered |
| REQ-021 | Marketplace pages do not regress beyond the per-page WCAG 2.0/2.1 A+AA violation baseline                                        | SHOULD | Issue #588, `marketplace/tests/a11y/homepage.a11y.spec.ts` | `playwright-tests` job — "Run a11y baseline tests" step (added in this PR)          | covered |
| REQ-022 | E2E tests cover homepage search, results, mobile viewports, install CTA, playbooks nav, explore flows, cowork page + integration | MUST   | `CLAUDE.md` § "Test Organization" — Dev tests T1–T9        | `marketplace/tests/T*.spec.ts` (in `playwright-tests` job)                          | covered |
| REQ-023 | Production smoke tests cover core pages, search, redirects, navigation, cowork, mobile, performance, SEO meta                    | MUST   | `CLAUDE.md` § "Test Organization" — P1–P8                  | `marketplace/tests/production/P*.spec.ts` (in `production-e2e` job)                 | covered |

## CLI (`@intentsolutionsio/ccpi`)

| ID      | Requirement                                                                                                                         | MoSCoW | Source                                                          | Tests / Checks                                                                        | Status    |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------- |
| REQ-024 | `dist/index.js` must be executable after build                                                                                      | MUST   | `cli-smoke-tests` job                                           | `cli-smoke-tests` "Verify bin entrypoint is executable" step                          | covered   |
| REQ-025 | `ccpi --help` must exit 0                                                                                                           | MUST   | `cli-smoke-tests` "Test CLI --help"                             | `cli-smoke-tests` job                                                                 | covered   |
| REQ-026 | `ccpi --version` must exit 0 and print the version                                                                                  | MUST   | `cli-smoke-tests` "Test CLI --version"                          | `cli-smoke-tests` job                                                                 | covered   |
| REQ-027 | `ccpi doctor`, `validate`, and `install` subcommands must each respond to `--help`                                                  | MUST   | `cli-smoke-tests` job                                           | `cli-smoke-tests` job                                                                 | covered   |
| REQ-028 | Published CLI must not contain `workspace:` deps                                                                                    | MUST   | `CLAUDE.md` § "CI Pipeline" — `cli-smoke-tests` row             | `cli-smoke-tests` "Verify no workspace dependencies" step                             | covered   |
| REQ-029 | `npm pack` of the CLI must succeed                                                                                                  | MUST   | `cli-smoke-tests` job                                           | `cli-smoke-tests` "Test npm pack" step                                                | covered   |
| REQ-030 | CLI gzipped bundle stays under the published size budget                                                                            | SHOULD | Issue #591, `packages/cli/.size-limit.json`                     | `cli-smoke-tests` "Bundle size budget" step (added in this PR)                        | covered   |
| REQ-031 | CLI publish to npm only happens on `cli-v*.*.*` git tag (one-shot) or via `publish-changed-packages` (incremental, on version bump) | MUST   | `CLAUDE.md` § "npm Publish Pipeline"                            | `.github/workflows/cli-publish.yml`, `.github/workflows/publish-changed-packages.yml` | covered   |
| REQ-032 | CLI semver follows public-API contract (`ccpi install`, `validate`, `doctor`, etc.)                                                 | SHOULD | `marketplace/src/content/docs/getting-started/cli-reference.md` | `(uncovered)` — no contract-test enforcing CLI surface stability across versions      | uncovered |

## MCP plugins

| ID      | Requirement                                                                                       | MoSCoW | Source                                                                      | Tests / Checks                                                         | Status  |
| ------- | ------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------- |
| REQ-033 | Each MCP plugin must build, produce a `dist/index.js`, and the binary must be executable          | MUST   | `CLAUDE.md` § "MCP Server Plugins"                                          | `validate-plugins.yml` `test` job (matrix per MCP plugin)              | covered |
| REQ-034 | MCP plugin `package.json` declares the published name in the `@intentsolutionsio/*` scope         | MUST   | `CLAUDE.md` § "npm Publish Pipeline"                                        | `publish-changed-packages.yml` (publishes only `@intentsolutionsio/*`) | covered |
| REQ-035 | `pnpm audit --prod --audit-level=high` runs over the workspace lock (all MCP plugin dependencies) | SHOULD | `validate-plugins.yml` "Audit workspace production dependencies (blocking)" | `validate` job (blocking since 2026-11-14, #1814)                      | covered |

## Validators (universal validator v7.0 / schema 4.x)

| ID      | Requirement                                                                                | MoSCoW | Source                                                             | Tests / Checks                                                                            | Status    |
| ------- | ------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | --------- | ---------------- | ------- |
| REQ-036 | Validator standard tier mirrors Anthropic spec exactly (`name` + `description` required)   | MUST   | `CLAUDE.md` § "Essential Commands", `000-docs/SCHEMA_CHANGELOG.md` | `python3 scripts/validate-skills-schema.py` smoke (in `test` matrix job)                  | covered   |
| REQ-037 | Validator marketplace tier requires the IS enterprise 8-field set as ERRORS (not warnings) | MUST   | `000-docs/SCHEMA_CHANGELOG.md` § "NON-NEGOTIABLES"                 | `python3 scripts/validate-skills-schema.py --marketplace` smoke (in `test` matrix job)    | covered   |
| REQ-038 | Validator can populate `freshie/inventory.sqlite` for ecosystem reporting                  | SHOULD | `CLAUDE.md` § "Freshie — Ecosystem Inventory & Compliance"         | `validate-skills-schema.py --populate-db` (manual; freshie reports in `freshie/reports/`) | covered   |
| REQ-039 | `SCHEMA_VERSION` constant bumps on every observable change to validator output             | MUST   | `CLAUDE.md` § "When working on validator / spec changes"           | `(uncovered)` — no automated check enforces SCHEMA_VERSION bump                           | uncovered |
| REQ-040 | Marketplace tier validator runs in CI in reporting mode (not blocking)                     | MUST   | Project memory — `feedback_validator_standards.md`                 | `test` matrix job (`                                                                      |           | true` semantics) | covered |

## Repository governance / process

| ID      | Requirement                                                                                                 | MoSCoW | Source                                                                                                                      | Tests / Checks                                                                              | Status    |
| ------- | ----------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------- |
| REQ-041 | Branch protection on `main` requires `validate` + `marketplace-validation` checks                           | MUST   | `CLAUDE.md` "Required checks: `validate` + `marketplace-validation` only" (memory file) + GitHub branch protection settings | GitHub branch protection (out-of-repo config)                                               | partial   |
| REQ-042 | All commits and PRs auto-sign via `attribution.commit` / `attribution.pr` in `~/.claude/settings.json`      | MUST   | `~/.claude/CLAUDE.md` § "Git Commit Signature"                                                                              | `(uncovered in this repo)` — enforced at the harness level, not in CI                       | uncovered |
| REQ-043 | Beads (`bd`) is the canonical task tracker — no markdown TODOs                                              | MUST   | `AGENTS.md` § "Important Rules"                                                                                             | `(uncovered)` — convention; not gated                                                       | uncovered |
| REQ-044 | Every Intent Solutions repo installs `@intentsolutions/audit-harness` in-repo (npm dev dep, vendored, etc.) | MUST   | `CLAUDE.md` § "Intent Solutions Testing SOP"                                                                                | `(uncovered in this repo)` — pending Phase 5 PR1 (#621)                                     | uncovered |
| REQ-045 | Package manager: `pnpm` everywhere except `marketplace/` which uses `npm`                                   | MUST   | `CLAUDE.md` § "Package manager policy"                                                                                      | `scripts/check-package-manager.mjs` (in `validate-plugins.yml` `check-package-manager` job) | covered   |
| REQ-046 | New skills installed via `/audit-tests` → `/implement-tests` flow rather than ad-hoc                        | SHOULD | `CLAUDE.md` § "Intent Solutions Testing SOP" — "When starting a new repo"                                                   | `(uncovered)` — process convention, no enforcement                                          | uncovered |

## Out of scope (declined ADRs)

| ID       | Decision                            | Source                                                                                                 |
| -------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------ |
| WONT-001 | Stryker mutation testing — declined | [`260-AT-ADEC-no-stryker-mutation-testing.md`](../000-docs/260-AT-ADEC-no-stryker-mutation-testing.md) |
| WONT-002 | dependency-cruiser — declined       | [`261-AT-ADEC-no-dep-cruiser-yet.md`](../000-docs/261-AT-ADEC-no-dep-cruiser-yet.md)                   |
| WONT-003 | Semgrep static analysis — declined  | [`262-AT-ADEC-no-semgrep-redundant-sast.md`](../000-docs/262-AT-ADEC-no-semgrep-redundant-sast.md)     |
| WONT-004 | BDD / Gherkin scenarios — declined  | [`263-AT-ADEC-no-bdd-no-readership.md`](../000-docs/263-AT-ADEC-no-bdd-no-readership.md)               |

## Notes

- **MoSCoW interpretation:** MUST = repo will not ship without it; SHOULD =
  signal of quality, blocks at marketplace tier; COULD = nice-to-have;
  WON'T = explicitly declined (see WONT- rows).
- **Status interpretation:** "covered" means CI fails on regression.
  "partial" means CI surfaces but does not block (informational warning).
  "uncovered" means no automated check exists today — file an issue if you
  want it gated.
- This RTM does not duplicate ADR rationale. ADRs live under
  `000-docs/NNN-AT-ADEC-*.md` and are linked here by filename.
