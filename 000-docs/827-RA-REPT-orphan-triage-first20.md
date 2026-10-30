<!-- doc-class: record -->

# Orphan triage: first 20 candidate dispositions

Tracking: `claude-xx4k.3.3`; parent `claude-rx0s`. This is a bounded classification
pass, not a publication, quality remediation or upstream synchronization.

## Frozen inventory and denominator

The inventory is frozen at reviewed main
`2ee558af51cc66ae3a7613053c6c77915371bf38`. The canonical resolver reports 3,493
graded skills, 2,902 marketplace-visible skills and 500 curriculum skills.
The 591 graded-but-not-visible paths include all 500 curriculum entries; removing
those leaves **91 plugin candidates**, not 591 orphans. Even those 91 are only
candidates: catalog ownership and publication policy must be examined separately.
The historical audit-266 aggregate is not a current count or an enumerated cohort.

Selection: sort `graded − marketplace-visible − curriculum` lexically. Freeze the
first 20 as E1 and the next 30 distinct paths as E2. The
[frozen receipt](828-RA-DATA-orphan-triage-frozen-cohorts.json) records all 50 exact
paths and blob identities; E2 remains a separate, uncompleted task
`claude-xx4k.4.2`, blocked by E1. Reserving its paths does not triage them.

## Shared E1 evidence and disposition

All 20 E1 paths already have catalog parent `hyperflow`, with source
`plugins/ai-agency/hyperflow`, manifest name `hyperflow`, and explicit membership
in that root's `.source.json.files`. The source record credits
`Mohammed-Abdelhady/hyperflow`. The catalog's `publication: quarantined` excludes
them from the visible discovery cohort. Their absence is explained by publication
policy, not missing parent linkage.

Disposition for each row: **obsolete orphan label**. Preserve the existing parent,
source attribution and quarantine. No skill body, source record, manifest,
catalog publication field or source lock is changed. This classification does not
resolve the separate held Hyperflow upgrade/relock task `claude-juoz.14`, certify
its content, or authorize publication. The expected post-state is identical
ownership and visibility, with a resolved classification record.

## The 20 reviewed items

Paths below are relative to `plugins/ai-agency/hyperflow/`. Each row is independently
bound to its full path, declared skill name and source blob in the JSON receipt.

| #   | Exact relative path                                     | Disposition           | Expected post-state          |
| --- | ------------------------------------------------------- | --------------------- | ---------------------------- |
| 1   | `skills/audit/SKILL.md`                                 | Obsolete orphan label | Existing parent; quarantined |
| 2   | `skills/background/SKILL.md`                            | Obsolete orphan label | Existing parent; quarantined |
| 3   | `skills/bridge/SKILL.md`                                | Obsolete orphan label | Existing parent; quarantined |
| 4   | `skills/cache/SKILL.md`                                 | Obsolete orphan label | Existing parent; quarantined |
| 5   | `skills/deploy/SKILL.md`                                | Obsolete orphan label | Existing parent; quarantined |
| 6   | `skills/design/SKILL.md`                                | Obsolete orphan label | Existing parent; quarantined |
| 7   | `skills/dispatch/SKILL.md`                              | Obsolete orphan label | Existing parent; quarantined |
| 8   | `skills/flush/SKILL.md`                                 | Obsolete orphan label | Existing parent; quarantined |
| 9   | `skills/handoff/SKILL.md`                               | Obsolete orphan label | Existing parent; quarantined |
| 10  | `skills/hyperflow/SKILL.md`                             | Obsolete orphan label | Existing parent; quarantined |
| 11  | `skills/issue/SKILL.md`                                 | Obsolete orphan label | Existing parent; quarantined |
| 12  | `skills/plan/SKILL.md`                                  | Obsolete orphan label | Existing parent; quarantined |
| 13  | `skills/pr/SKILL.md`                                    | Obsolete orphan label | Existing parent; quarantined |
| 14  | `skills/scaffold/SKILL.md`                              | Obsolete orphan label | Existing parent; quarantined |
| 15  | `skills/status/SKILL.md`                                | Obsolete orphan label | Existing parent; quarantined |
| 16  | `skills/sticky/SKILL.md`                                | Obsolete orphan label | Existing parent; quarantined |
| 17  | `skills/trace/SKILL.md`                                 | Obsolete orphan label | Existing parent; quarantined |
| 18  | `skills/workflow/SKILL.md`                              | Obsolete orphan label | Existing parent; quarantined |
| 19  | `templates/antigravity/skills/hyperflow-audit/SKILL.md` | Obsolete orphan label | Existing parent; quarantined |
| 20  | `templates/antigravity/skills/hyperflow-cache/SKILL.md` | Obsolete orphan label | Existing parent; quarantined |

## Validation and limits

Read the canonical catalog, plugin manifest, source membership record and exact
Git blobs at the frozen SHA; compare each path with resolver cohort membership.
All 20 have a parent and explicit source ownership records, all remain excluded
from marketplace visibility, and the E1/E2 path sets are disjoint. The receipt
records these checks per E1 item. Source membership is provenance evidence, not
a new legal ownership attestation or runtime safety guarantee.

No orphan detector or mirror content is rewritten. The 91-candidate inventory
still contains the quarantined paths after classification; the expected change
is their triage state, not a smaller corpus or a manufactured discovery count.
A follow-up comparison must preserve the 20 blob identities, parent and quarantine
and show no unresolved classification among E1. New candidates belong to later
cohorts. E2's 30 reserved candidates still need their own assessment and validation.

Focused regression checks at the frozen source SHA:

- `node --test scripts/corpus-resolver.test.mjs scripts/plugin-provenance.test.mjs`:
  24 passed, zero failed or skipped.
- Repository virtualenv Python: `-m pytest tests/test_validate_skills_schema_frontmatter.py -q`:
  72 passed. These are schema regression tests, not a claim that the quarantined
  mirror skills pass content grading.
- Unicode scan of this worklog: zero blocker, major or minor findings.

The follow-up classification check confirmed all 20 source blobs and explicit
membership records unchanged and zero E1/E2 overlap. Publishing this worklog still
requires the normal documentation, generated-index and merged-artifact checks.
