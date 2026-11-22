<!-- doc-class: record -->

# Supabase warning review

Date: 2026-11-22. Owner: Jeremy Longshore. Bead: `claude-v68g.34`.
Reviewer: Codex; independent acceptance review remains pending.

## Evidence and boundary

This snapshot evaluates all 30 Supabase skills at commit `169aef6776b461f9582e989caa16deed6f83321c`.
Each skill passed marketplace validation with zero errors; 175 warnings remain.
The [per-finding record](834a-RA-DATA-supabase-warning-review.json) retains each
path, source SHA-256, rule, original message, owner, rationale and security
assessment. It is a review artifact, not a scanner allowlist or runtime approval.
Recompute findings after source changes; do not reuse these dispositions against
changed bytes without review.

| Disposition            | Findings |
| ---------------------- | -------: |
| nonblocking-editorial  |       74 |
| review-required        |       99 |
| reviewed-tool-use      |        1 |
| reviewed-metavariables |        1 |

Editorial dispositions cover wording, length and optional invocation hints only.
They do not endorse API claims or security behavior. The naming-table findings
are reviewed metavariables with adjacent concrete examples. The known-pitfalls
tool findings retain Read/Grep for its source-review workflow. Other tool grants,
numeric constants and stale-content findings remain open for contextual review.

## Implemented corrections under review

PR [1872](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1872)
contains authentication boundaries, complete handoffs, ordinary-user RLS checks,
a forged-owner insert fix, safer secret inputs, and corrected command scopes.
These changes do not establish complete pack acceptance.

The two PostgreSQL regression tests passed locally and actually ran in hosted
job [137109661985](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/44990279811/job/137109661985)
at the preceding `8d54204ed` head. The old template failed the forged-owner test.
This is bounded SQL evidence, not a live Supabase deployment or a complete RLS audit.

## Remaining acceptance

Resolve every `review-required` finding with a content fix or a documented,
evidence-backed disposition. Review linked references for contradictions and
unsafe examples; schema success alone cannot clear those defects. Then verify
pack/catalog/curated projections at the exact merged main commit and obtain the
independent review required by the bead. Required CI gates remain mandatory.
No live provider calls, paid evaluations, production credentials or gate waivers
were used for this review.
