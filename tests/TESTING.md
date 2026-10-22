# Testing Context — claude-code-plugins-plus-skills

<!-- TESTING.md schema v1 — see @intentsolutions/audit-harness docs -->
<!--
  POLICY sections (above "## Installed gates") are engineer-owned and
  hash-pinned. Editing them via AI without an engineer-initiated
  `pnpm exec audit-harness init` re-pin will trip escape-scan and
  REFUSE the change.

  OBSERVATIONAL sections (below "## Installed gates") may be updated
  by AI via the Edit tool — they reflect what is currently installed,
  not what policy requires.
-->

## Classification (policy)

- Repo type: **monorepo** (pnpm workspaces)
- Primary languages: **TypeScript**, **Python**, **Astro**
- Per-package mixed stacks:
  - `marketplace/` — Astro 5 frontend (uses npm, not pnpm; see CI policy gate)
  - `packages/cli` — TypeScript CLI (`@intentsolutionsio/ccpi` on npm)
  - `packages/analytics-*` — TypeScript analytics tooling
  - `plugins/mcp/*` — TypeScript MCP server plugins
  - `plugins/saas-packs/*-pack` — Markdown SaaS skill packs
  - `plugins/<category>/*` — Markdown AI-instruction plugins (~98% of plugins)
  - `scripts/` — Python validators + Node.js build/sync scripts
  - `freshie/` — Python ecosystem-inventory tooling
- Compliance overlay: **public marketplace publication** (npm) — security
  posture, secret scanning, and dependency auditing are required, not
  optional.

## Thresholds (policy)

These values are the floor. Lowering any of them in a PR will be REFUSED
by `audit-harness escape-scan --staged`.

| Gate                    | Floor                                       | Owner             | Source                                              |
| ----------------------- | ------------------------------------------- | ----------------- | --------------------------------------------------- |
| coverage.lines          | 70                                          | per-vitest-config | `vitest.config.ts` `coverage.thresholds.lines`      |
| coverage.functions      | 70                                          | per-vitest-config | `vitest.config.ts` `coverage.thresholds.functions`  |
| coverage.statements     | 70                                          | per-vitest-config | `vitest.config.ts` `coverage.thresholds.statements` |
| coverage.branches       | 60                                          | per-vitest-config | `vitest.config.ts` `coverage.thresholds.branches`   |
| harness.verify          | exit 0 required at PR-time                  | CI                | `pnpm exec audit-harness verify`                    |
| security.gitleaks       | clean on every PR                           | CI                | `.github/workflows/secret-scan.yml`                 |
| security.trufflehog     | weekly verified-secrets clean               | CI                | `.github/workflows/secret-scan.yml`                 |
| security.codeql         | no `error`-severity alerts                  | CI                | `.github/workflows/codeql.yml`                      |
| validator.marketplace   | per-skill grade ≥ B (80/100) for new skills | per-PR            | `scripts/validate-skills-schema.py --marketplace`   |
| performance.budget.gzip | total dist ≤ 40 MB, largest file ≤ 1 MB     | CI                | `scripts/check-performance.mjs`                     |
| performance.routes      | 2,800–4,000                                 | CI                | `scripts/check-performance.mjs`                     |

## Waived layers (policy)

The 7-layer audit-tests taxonomy includes layers this repo intentionally
does not enforce. Each waiver below has a written ADR or rationale; future
audits should not re-raise these as P1 unless a re-trigger condition fires.

| Layer                     | Status              | ADR / Rationale                                                                                    |
| ------------------------- | ------------------- | -------------------------------------------------------------------------------------------------- |
| L3-mutation (Stryker)     | deferred            | `000-docs/260-AT-ADEC-no-stryker-mutation-testing.md`                                              |
| L3-arch (dep-cruiser)     | deferred            | `000-docs/261-AT-ADEC-no-dep-cruiser-yet.md`                                                       |
| L5-sec (Semgrep / Bandit) | covered-by-existing | `000-docs/262-AT-ADEC-no-semgrep-redundant-sast.md` (CodeQL + gitleaks + trufflehog already cover) |
| L6-bdd (Gherkin)          | deferred            | `000-docs/263-AT-ADEC-no-bdd-no-readership.md` (existing Playwright suite covers same flows)       |
| L5-chaos (chaos eng.)     | not-applicable      | No production-runtime services in this repo; marketplace is a static site.                         |
| L5-perf (load testing)    | not-applicable      | No backend-with-throughput-SLO surface; perf budget is bundle-size only.                           |

## Compliance overlay (policy)

- Plugin authors are third parties. SKILL.md frontmatter and plugin.json
  schemas are public contracts; breaking changes require a major-version
  bump on the validator + a deprecation cycle in `000-docs/SCHEMA_CHANGELOG.md`.
- Security posture is the NON-NEGOTIABLE described in
  `000-docs/SCHEMA_CHANGELOG.md` and the Skills SOP in `~/.claude/CLAUDE.md`.
- Architectural changes to the validator (required-fields set, tier model,
  error vs warning semantics) require explicit pre-approval per the
  governance documented in issue #612.

---

## Installed gates (observational)

CI routing uses the immutable PR-base policy and an exact-result aggregate.
`tests/ci/test_fastlane*.py` exercises real Git diffs, hostile result maps,
and workflow wiring; `tests/ci/test_funding.py` exercises the funding schema.
Executable provisioning probes check exact lightweight selection, full fallback
for missing/unknown lanes, and propagation of build/dependency failures. The
unchanged runtime matrices and coverage remain required alongside validation.
The retained gates and explicit path classes are in
[CI routing](../.github/CI_ROUTING.md).

The required marketplace ratchet also binds R3 corpus counts to committed Git
trees and reconciles actual deletions with catalog withdrawals. Real Git fixtures
exercise the 2% boundary, retained aliases, forged counts, and checkout identity;
`node --test scripts/check-corpus-shrink.test.mjs` covers the catalog edge cases.
Run the full local gate from a clean tracked checkout with
`python3 scripts/check-marketplace-compliance-baseline.py`.

| Layer          | Gate                                                               | Trigger          |
| -------------- | ------------------------------------------------------------------ | ---------------- |
| L1-hooks       | `husky` declared (`package.json` `devDependencies`)                | local pre-commit |
| L1-hooks       | `@intentsolutions/audit-harness` `verify`                          | CI + local       |
| L2-static      | `eslint` + `prettier` (root + per-package)                         | local + CI       |
| L2-static      | `tsc --noEmit` per TS package                                      | CI               |
| L3-unit        | `vitest` per MCP plugin (`pr-to-spec`, `domain-memory-agent`,      | local + CI       |
|                | `project-health-auditor`, `conversational-api-debugger`,           |                  |
|                | `web-to-github-issue`, `tests/e2e`)                                |                  |
| L3-unit        | coverage thresholds (lines/functions/statements 70, branches 60)   | CI               |
| L3-arch        | `scripts/check-package-manager.mjs` (pnpm vs npm boundary)         | CI               |
| L4-integration | `pytest` for `scripts/` + `freshie/scripts/`                       | CI               |
| L5-sec         | `gitleaks` (PR + push) + `trufflehog` (weekly verified)            | CI               |
| L5-sec         | `codeql` (JS/TS + Python)                                          | CI               |
| L5-sec         | `pnpm audit` per MCP plugin                                        | CI (manual cron) |
| L5-sec         | validator `Security scan - Dangerous patterns` / `Suspicious URLs` | CI               |
| L5-system      | route + link + downloads validators (`marketplace/scripts/*`)      | CI               |
| L5-system      | performance budget (`scripts/check-performance.mjs`)               | CI               |
| L6-e2e         | Playwright dev tests T1–T9 (chromium + webkit + mobile)            | CI               |
| L6-e2e         | Playwright production tests P1–P8 (live site)                      | CI               |
| L7-acceptance  | `tests/TESTING.md` (this file) + `tests/RTM.md` /                  | engineer + AI    |
|                | `tests/PERSONAS.md` / `tests/JOURNEYS.md`                          |                  |

## Frameworks (observational)

- vitest 2.x (per-package configs)
- Playwright (chromium + webkit + iPhone 13 + Pixel 5)
- pytest (Python tests in `tests/` and per-plugin `requirements.txt`)
- ESLint 9 + Prettier 3
- TypeScript 5
- gitleaks + trufflehog (gh-actions)
- CodeQL (gh-actions)
- @intentsolutions/audit-harness ^0.1.0

## Last audit (observational)

- Date: 2026-04-21 (`/audit-tests` smoke run)
- Resulting issues: #580–#592
- Resolution PRs: #617 (CI hygiene), #618 (data integrity), #619 (4 ADRs),
  #620 (compatible-with migration PR 1 of N), this PR (testing
  foundation)

## Traceability (observational)

- RTM: `tests/RTM.md`
- Personas: `tests/PERSONAS.md`
- Journeys: `tests/JOURNEYS.md`
