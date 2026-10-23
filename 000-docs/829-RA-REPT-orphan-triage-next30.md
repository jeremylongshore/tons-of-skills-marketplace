<!-- doc-class: record -->

# Orphan triage: next 30 and Tonone bundle pattern

Tracking: `claude-xx4k.4.2`; program `claude-rx0s`; structural follow-up
`claude-rx0s.1`. E1 landed in PR 1755 at
`43b692cf84d414faa2a2ebb9941cbf57d931dedb` before this pass started.

## Cohort and result

This pass uses exactly the 30 E2 paths frozen in
[receipt 828](828-RA-DATA-orphan-triage-frozen-cohorts.json) at source
`2ee558af51cc66ae3a7613053c6c77915371bf38`. Analysis at the E1 merge found all
30 source blobs unchanged and no overlap with E1's 20 paths. Frozen paths, names,
ordinals and blob identities are unchanged; E1's disposition fields are untouched.
The appended E2 review fields enrich the receipt without recapturing its cohort.

- Eight Hyperflow entries already have a catalog parent, explicit source-record
  membership and quarantined publication. Their orphan labels are obsolete.
- Ten Tonone bundle copies have byte-identical complete `SKILL.md` counterparts
  under the visible root Tonone skill tree. Their instruction files are already
  represented; both copies are retained. This is not a runtime equivalence test.
- Twelve Tonone bundle-only names have no same-named root counterpart or individual
  entry in the vendored upstream catalog. They are deferred to one structural
  parent, `claude-rx0s.1`, rather than treated as twelve unrelated repairs.

Thus 18 classifications are resolved and 12 require deeper distribution review.
All 30 are triaged; the discovery program remains open while the twelve remain
unresolved. No mirror payload, catalog entry, publication state or source lock is
changed by this pass.

## The structural pattern

All 22 Tonone cases sit below two nearest manifests: `marketing-team` (12) and
`revenue-team` (10). Neither identity appears in our catalog or in the vendored
upstream marketplace descriptor. The canonical resolver uses the nearest eligible
plugin manifest identity; an outer source prefix named `tonone` does not register
these nested identities. In receipt 828, `catalog_parent` names that outer source
ancestor; the new `nearest_plugin_name` field records the actual binding.

Ten instruction files also exist byte-for-byte under root Tonone paths already
in `marketplace-visible`. For the other twelve, absence from these frozen
registries does not prove obsolescence, unsafe content, or the state of today's
upstream repository. No automatic catalog aliases or payload copies are justified
by the candidate count alone.

Tonone's ancestor `.source.json` declares `tonone-ai/tonone` but has no enumerated
`files` array. Evidence for these paths is therefore ancestor provenance, not an
explicit per-file source membership receipt. `sources.yaml` records
`verified: false` and `curated: true`: the latter freezes synchronization writes.
The E1/E2 acceptance criteria separately prohibit local mirror rewrites. Those
rules do not imply a blanket ban on all future curated hardening.

The new parent must establish the intended distribution and an evidence-backed
terminal disposition for all twelve. Unresolved decisions keep that parent and
`claude-rx0s` open. The existing Hyperflow relock hold `claude-juoz.14` remains
separate from these classifications.

## Thirty item dispositions

Paths are relative to `plugins/ai-agency/`. Exact source hashes, counterpart paths,
nearest manifests and per-item validation are recorded in receipt 828.

| E2 # | Exact relative path                                                  | Disposition                             |
| ---- | -------------------------------------------------------------------- | --------------------------------------- |
| 1    | `hyperflow/templates/antigravity/skills/hyperflow-deploy/SKILL.md`   | Obsolete orphan label; quarantined      |
| 2    | `hyperflow/templates/antigravity/skills/hyperflow-design/SKILL.md`   | Obsolete orphan label; quarantined      |
| 3    | `hyperflow/templates/antigravity/skills/hyperflow-dispatch/SKILL.md` | Obsolete orphan label; quarantined      |
| 4    | `hyperflow/templates/antigravity/skills/hyperflow-plan/SKILL.md`     | Obsolete orphan label; quarantined      |
| 5    | `hyperflow/templates/antigravity/skills/hyperflow-scaffold/SKILL.md` | Obsolete orphan label; quarantined      |
| 6    | `hyperflow/templates/antigravity/skills/hyperflow-status/SKILL.md`   | Obsolete orphan label; quarantined      |
| 7    | `hyperflow/templates/antigravity/skills/hyperflow-sticky/SKILL.md`   | Obsolete orphan label; quarantined      |
| 8    | `hyperflow/templates/antigravity/skills/hyperflow-trace/SKILL.md`    | Obsolete orphan label; quarantined      |
| 9    | `tonone/bundle/marketing-team/skills/buzz-devrel/SKILL.md`           | Deferred to `claude-rx0s.1`             |
| 10   | `tonone/bundle/marketing-team/skills/buzz-hn/SKILL.md`               | Deferred to `claude-rx0s.1`             |
| 11   | `tonone/bundle/marketing-team/skills/buzz-outreach/SKILL.md`         | Deferred to `claude-rx0s.1`             |
| 12   | `tonone/bundle/marketing-team/skills/ink-brief/SKILL.md`             | Deferred to `claude-rx0s.1`             |
| 13   | `tonone/bundle/marketing-team/skills/ink-cluster/SKILL.md`           | Deferred to `claude-rx0s.1`             |
| 14   | `tonone/bundle/marketing-team/skills/ink-distribute/SKILL.md`        | Deferred to `claude-rx0s.1`             |
| 15   | `tonone/bundle/marketing-team/skills/pitch-copy/SKILL.md`            | Byte-identical visible root instruction |
| 16   | `tonone/bundle/marketing-team/skills/pitch-landing/SKILL.md`         | Byte-identical visible root instruction |
| 17   | `tonone/bundle/marketing-team/skills/pitch-launch/SKILL.md`          | Byte-identical visible root instruction |
| 18   | `tonone/bundle/marketing-team/skills/pitch-message/SKILL.md`         | Byte-identical visible root instruction |
| 19   | `tonone/bundle/marketing-team/skills/pitch-position/SKILL.md`        | Byte-identical visible root instruction |
| 20   | `tonone/bundle/marketing-team/skills/pitch-recon/SKILL.md`           | Byte-identical visible root instruction |
| 21   | `tonone/bundle/revenue-team/skills/deal-outreach/SKILL.md`           | Deferred to `claude-rx0s.1`             |
| 22   | `tonone/bundle/revenue-team/skills/deal-proposal/SKILL.md`           | Deferred to `claude-rx0s.1`             |
| 23   | `tonone/bundle/revenue-team/skills/deal-qualify/SKILL.md`            | Deferred to `claude-rx0s.1`             |
| 24   | `tonone/bundle/revenue-team/skills/keep-churn/SKILL.md`              | Deferred to `claude-rx0s.1`             |
| 25   | `tonone/bundle/revenue-team/skills/keep-qbr/SKILL.md`                | Deferred to `claude-rx0s.1`             |
| 26   | `tonone/bundle/revenue-team/skills/keep-segment/SKILL.md`            | Deferred to `claude-rx0s.1`             |
| 27   | `tonone/bundle/revenue-team/skills/surge-activation/SKILL.md`        | Byte-identical visible root instruction |
| 28   | `tonone/bundle/revenue-team/skills/surge-experiment/SKILL.md`        | Byte-identical visible root instruction |
| 29   | `tonone/bundle/revenue-team/skills/surge-landing/SKILL.md`           | Byte-identical visible root instruction |
| 30   | `tonone/bundle/revenue-team/skills/surge-plg/SKILL.md`               | Byte-identical visible root instruction |

## Validation boundary

Verify every frozen source hash, all eight explicit Hyperflow source memberships
and quarantine states, all ten complete-file byte comparisons and visible root
memberships, and all twelve missing counterpart/registry observations. Preserve
all 50 frozen identities and the complete E1 item records. The receipt carries
per-item evidence; no authenticated runtime, provider evaluation, or upstream
outreach was performed. Schema/provenance regression checks assess repository
logic, not the quality or safety of the mirrored instructions.

E2-specific validation verified all 50 frozen source hashes, unchanged E1 records,
eight explicit source memberships/quarantine states, ten byte-identical visible
counterparts, and twelve deferred cases bound to `claude-rx0s.1`. The canonical
provenance resolver classified all 30 as mirrors with no refused paths.
Validation receipt SHA-256:
`fbf686484bd1478152cd6046b03ea6475b093e1ed61ca54f56abf1562279241b`.

The resolver/provenance/validator code and their regression tests have the same
Git blobs as the frozen E1 source where 24 resolver/provenance tests and 72 schema
tests passed. Those unchanged-code results are reused; the E2-specific evidence
above was checked separately. Unicode scanning found zero findings. This record
makes no claim that the mirrored instructions pass content grading or runtime tests.
