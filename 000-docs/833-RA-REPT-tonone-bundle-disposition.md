<!-- doc-class: record -->

# Tonone bundle discovery disposition

Review date: 2026-10-25. Issue: `claude-rx0s.1`; parent: `claude-rx0s`.

## Decision

Retain the twelve frozen Tonone bundle instructions and exclude separate
`marketing-team` and `revenue-team` discovery listings. This selects the existing
issue's retention/exclusion lane. It does not retire these capabilities or change
the existing outer Tonone listing. Preserve `curated: true`, `verified: false`,
source provenance, and every frozen instruction blob.

The marketing, sales, and customer-success workflows remain useful. A new listing
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

The current resolver inventory contains 3,376 graded instructions, 2,785 visible
instructions, 500 curriculum exclusions, and 91 graded plugin candidates outside
discovery. The 91 are not 91 new publication requests. This decision resolves the
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
