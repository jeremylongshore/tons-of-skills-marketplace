<!-- doc-class: canonical -->

# 718-AT-ARCH — Source-of-Truth Map with GENERATED Tiers (Mission 01)

**Captured:** 2026-08-11 @ `4358a65a3` · **Counts refreshed:** 2026-08-18 @ `07eefb5d6` (E2.6)

## Tier A — derived + gated (safe GENERATED label; drift caught by CI)

| Artifact                             | Generator                   | Gate                                       |
| ------------------------------------ | --------------------------- | ------------------------------------------ |
| `.claude-plugin/marketplace.json`    | `pnpm run sync-marketplace` | `validate` job: regenerate-then-diff       |
| README `AUTO-TOC` block              | `generate-readme-toc.mjs`   | gated `--check`                            |
| `skills/.curated/**`                 | `promote-to-curated.py`     | `promote-curated-check` (in `ci-required`) |
| `.github/CODEOWNERS` generated block | generator                   | `codeowners-drift`                         |

## Tier B — derived but UNGATED (~31 M; drift invisible to CI)

| Artifact                                                   | Size   | Note                                                  |
| ---------------------------------------------------------- | ------ | ----------------------------------------------------- |
| `marketplace/src/data/skills-catalog.json`                 | 25.6 M | byte-identical twin in `public/data` (`cmp`-verified) |
| `marketplace/src/data/unified-search-index.json`           | 2.9 M  | byte-identical twin in `public/data` (`cmp`-verified) |
| other `marketplace/src/data/*.json`                        | —      | no drift gate except the cowork manifest              |
| `npm/github/skills-stats.json` + README `NPM-STATS`        | —      | ungated                                               |
| freshie `grades.csv` / `grade-histogram.json` / `reports/` | —      | run-stamp inconsistency recorded in doc 723           |

Duplicated bytes across the two `src`↔`public` twins: **28,460,845 B** — exactly these 2 files;
no other data file has a twin (doc 722).

## Tier C — scaffolded-once then mutated (NOT pure GENERATED)

- `plugins/**/package.json` and `.claude-plugin/plugin.json` corpus: existence-checked only by
  sync-marketplace; content drifts freely. Historical count reconciliation is in doc 722.

## Enforcement gaps (FIX-bead candidates — recorded, not fixed)

1. No drift gate on any `marketplace/src/data/*` except the cowork manifest.
2. `reconstruct-versions.mjs --check` exists but is wired into **no workflow** (doc 723).
3. `sync-lockfile-test` is path-filtered and outside `ci-required`.
4. Freshie run-stamp inconsistency (doc 723).

## Authority pointers per area

- **Catalog:** `marketplace.extended.json` (SoT) → `marketplace.json` (generated).
- **Skill validity:** `scripts/validate-skills-schema.py` authoritative; kernel lanes advisory
  (pin `@intentsolutions/core@0.9.0`, documented staleness — doc 723).
- **External mirrors:** upstream repos via `sources.yaml`; `curated:true` = frozen locally.
- **Freshie:** Dolt = versioned system of record; `inventory.sqlite` untracked local runtime;
  `grades.csv` tracked compact export.
- **Beads:** embedded Dolt, `refs/dolt/data` sync; `.beads/` untracked by design.
- **Docs:** doc-filing v4.4 + `000-INDEX.md` (created by this PR); ignore-rule design is
  register row 9 (doc 719).
