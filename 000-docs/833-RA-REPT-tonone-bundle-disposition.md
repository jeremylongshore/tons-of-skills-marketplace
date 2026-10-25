<!-- doc-class: record -->

# Tonone bundle discovery disposition

Review date: 2026-10-25. Issue: `claude-rx0s.1`; parent: `claude-rx0s`.

## Decision

Retain the twelve frozen Tonone bundle instructions and exclude separate
`marketing-team` and `revenue-team` discovery listings. This selects the existing
issue's retention/exclusion lane. It does not retire these capabilities or change
the existing outer Tonone listing. Preserve `curated: true`, `verified: false`,
source provenance, and every frozen instruction blob.

The instruction bodies cover recognizable marketing, sales, and customer-success
workflows. Retention reflects that content review, not a behavioral quality grade. A new listing
would expose incomplete mirrored packages: all twelve instructions reference
`docs/output-kit.md`, which is absent from the tracked Tonone mirror. Neither
bundle identity is registered in our catalog, the vendored upstream catalog, or
the inspected current upstream catalog. Existing source selection excludes
`docs/**`; repairing that packaging requires a separate governed source transition.

## Immutable evidence

The [evidence receipt](833a-RA-DATA-tonone-bundle-evidence.json) records every local
path, Git blob, SHA-256, nearest manifest, ancestor provenance, discovery state,
upstream candidate, disposition, and expected post-state. Analysis uses marketplace
commit `3f15d981b8b6d0c869df0106741d192448dcc51d` and preserves the original
[frozen cohort](828-RA-DATA-orphan-triage-frozen-cohorts.json) from
`2ee558af51cc66ae3a7613053c6c77915371bf38`.

Upstream inspection pins [tonone-ai/tonone](https://github.com/tonone-ai/tonone/tree/1ceec80367a4e846e2f209cc87eea9d7544bd978)
at `1ceec80367a4e846e2f209cc87eea9d7544bd978`: a complete, nontruncated
4,437-entry tree and 112-entry catalog. Twenty-one unique blobs cover 45 inspected
paths; retrieved bytes were checked against their Git blob identities. The receipt
records their hashes without copying vendor instruction content into this report.

Upstream has root, bundle, and team variants of every named instruction; the three
variants are byte-identical within that revision. Catalog entries expose the
`buzz`, `ink`, `deal`, and `keep` teams at version 1.18.0. The local bundle manifests
remain version 1.9.1. No complete frozen instruction equals its current upstream
candidate. Seven bodies match after frontmatter removal and line-end whitespace
normalization; five changed: `buzz-hn`, `buzz-outreach`, `ink-brief`, `ink-cluster`,
and `deal-outreach`. These observations establish candidates for future review,
not adopted replacements or runtime equivalence.

The upstream output-kit resource exists; its blob is recorded in the receipt.
The local `atlas-report` skill also exists and is visible. The missing resource
finding concerns `docs/output-kit.md`, not `atlas-report`. Ancestor `.source.json`
identifies the repository but has no enumerated `files` array; it is not explicit
per-file source-membership evidence.

## Twelve terminal classifications

| Skill            | Bundle           | Capability                | Disposition                             |
| ---------------- | ---------------- | ------------------------- | --------------------------------------- |
| `buzz-devrel`    | `marketing-team` | DevRel program            | Retain frozen; exclude separate listing |
| `buzz-hn`        | `marketing-team` | Hacker News draft         | Retain frozen; exclude separate listing |
| `buzz-outreach`  | `marketing-team` | Media and podcast pitch   | Retain frozen; exclude separate listing |
| `ink-brief`      | `marketing-team` | Content brief             | Retain frozen; exclude separate listing |
| `ink-cluster`    | `marketing-team` | Topic cluster             | Retain frozen; exclude separate listing |
| `ink-distribute` | `marketing-team` | Distribution copy         | Retain frozen; exclude separate listing |
| `deal-outreach`  | `revenue-team`   | Outbound sequence         | Retain frozen; exclude separate listing |
| `deal-proposal`  | `revenue-team`   | Sales proposal            | Retain frozen; exclude separate listing |
| `deal-qualify`   | `revenue-team`   | MEDDPICC qualification    | Retain frozen; exclude separate listing |
| `keep-churn`     | `revenue-team`   | Churn intervention        | Retain frozen; exclude separate listing |
| `keep-qbr`       | `revenue-team`   | Quarterly business review | Retain frozen; exclude separate listing |
| `keep-segment`   | `revenue-team`   | Customer segmentation     | Retain frozen; exclude separate listing |

## Cohort reconciliation and acceptance boundary

The original E1 twenty and E2 thirty stay frozen and disjoint. Historical E1/E2
review objects remain intact. Only the twelve deferred records gain a
`final_review`; the receipt defines how that overlay supplies their effective
classification. The other 28 obsolete orphan labels and ten byte-identical
visible-root copies retain their previous dispositions. Together these account
for all fifty frozen paths; no newly arriving candidate enters either cohort.

At the pinned marketplace analysis commit, the resolver snapshot contains 3,376 graded instructions, 2,785 visible
instructions, 500 curriculum exclusions, and 91 graded plugin candidates outside
discovery. This report does not authorize publication of those 91 candidates. This decision resolves the
twelve frozen classifications without claiming to resolve every later candidate,
Hyperflow quarantine, or Kobiton source hold.

No plugin payload, source lock, catalog registration, curation flag, grade, or
visibility changes. No provider/native evaluation, outreach, installation, or
hosted runtime verification occurred. This report makes no safety certification
or adoption claim. Local checks and normal PR acceptance must still be recorded
before issue closure; the evidence receipt alone is not merge proof.

## Local validation

All 24 resolver/provenance tests and all 72 schema-frontmatter regression tests
passed. The frozen-record comparison verified all fifty source SHA-256 values
and preserved original item fields and the historical E2 review. Document class,
authority, index, filing-policy (29 assertions), Markdown, and whitespace checks
passed. Canonical marketplace synchronization wrote no package or catalog changes.
Canonical scorecard measurement passed; its only delta is the document count
from 274 to 276. Hosted PR acceptance remains pending.

## Reproduction and canonical inputs

All observations are dated snapshots at the analysis commit above, not competing
catalog authority. `marketplace_visible` means membership of the exact instruction
path in `resolveCorpus('marketplace-visible')`; an outer plugin listing does not
imply membership for every instruction beneath a different nested manifest.

Canonical inputs at the pinned marketplace commit:

- [Catalog](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/3f15d981b8b6d0c869df0106741d192448dcc51d/.claude-plugin/marketplace.extended.json): the outer `tonone` entry, without separate `marketing-team` or `revenue-team` entries.
- [Source registry](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/3f15d981b8b6d0c869df0106741d192448dcc51d/sources.yaml#L425): Tonone verification/curation flags and selection/exclusion rules. These rules live in `sources.yaml`, not `.source.json`.
- [Ancestor provenance](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/3f15d981b8b6d0c869df0106741d192448dcc51d/plugins/ai-agency/tonone/.source.json): repository identity without an enumerated files array.
- [Corpus resolver](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/3f15d981b8b6d0c869df0106741d192448dcc51d/scripts/corpus-resolver.mjs): the cohort predicates, including manifest-based discovery. Cohort counts are source inventory, not new Freshie grades.

For the pinned tracked tree, `git ls-tree -r --name-only <analysis-commit> --
plugins/ai-agency/tonone` enumerates the package. Filtering those paths for
`output-kit.md` returns no matches. Reading the twelve receipt paths with
`git show <analysis-commit>:<path>` shows their output-kit references. The receipt
provides each blob and SHA-256; recompute SHA-256 over those exact Git bytes.
The fifty historical item objects compare equal after removing only the new
`final_review` property; the historical `E2_review` object also compares equal.

The upstream receipt's `inputs` map records all 45 paths and blob/hash identities.
Retrieve the pinned tree with `gh api
repos/tonone-ai/tonone/git/trees/1ceec80367a4e846e2f209cc87eea9d7544bd978?recursive=1`;
check `truncated` is false before interpreting an absence. Fetch blob bytes at the
recorded IDs and verify Git's SHA-1 over `blob <byte-length>\0<bytes>` plus SHA-256
over the raw bytes. Compare each root/bundle/team triple before comparing to its
frozen local instruction. The checked LICENSE input is evidence of the inspected
artifact; this report makes no additional legal determination.

Local regression commands were `node --test scripts/corpus-resolver.test.mjs
scripts/plugin-provenance.test.mjs` (24 passed) and `python -m pytest
tests/test_validate_skills_schema_frontmatter.py -q` in the existing repository
Python environment (72 passed). Generator/check commands were `pnpm run
sync-marketplace`, `node scripts/measure-epic-1.mjs`, `node
scripts/generate-docs-index.mjs --check`, `node scripts/check-doc-classes.mjs`,
`node scripts/check-doc-authority.mjs`, `node scripts/check-docs-ignore-policy.mjs`,
and `git diff --cached --check`. Hosted results are attached to
[PR 1784](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1784);
local pass counts do not imply hosted acceptance or independent review of the
JSON receipt. The first automated reviews explicitly excluded that JSON file.
