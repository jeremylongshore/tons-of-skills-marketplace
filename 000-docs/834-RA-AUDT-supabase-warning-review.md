<!-- doc-class: record -->

# Supabase warning review

Date: 2026-11-22. Owner: Jeremy Longshore. Bead: `claude-v68g.34`.
Reviewer: Codex; independent acceptance review remains pending.

## Evidence and boundary

This snapshot evaluates all 30 Supabase skills at commit `29e66d05d9dd42e15c72ec54d6cc69627df9d8bb`.
Each skill passed marketplace validation with zero errors; 167 warnings remain.
The [per-finding record](834a-RA-DATA-supabase-warning-review.json) retains each
path, source SHA-256, rule, original message, owner, rationale and security
assessment. It is a review artifact, not a scanner allowlist or runtime approval.
Recompute findings after source changes; do not reuse these dispositions against
changed bytes without review.

| Disposition            | Findings |
| ---------------------- | -------: |
| nonblocking-editorial  |       76 |
| review-required        |       69 |
| reviewed-numeric-value |       20 |
| reviewed-tool-use      |        1 |
| reviewed-metavariables |        1 |

Editorial dispositions cover wording, length and optional invocation hints only.
They do not endorse API claims or security behavior. The naming-table findings
are reviewed metavariables with adjacent concrete examples. The known-pitfalls
tool findings retain Read/Grep for its source-review workflow. Other tool grants, the remaining numeric constants and stale-content findings
remain open for contextual review.

## Implemented corrections under review

PR [1872](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1872)
contains authentication boundaries, complete handoffs, ordinary-user RLS checks,
a forged-owner insert fix, safer secret inputs, and corrected command scopes.
These changes do not establish complete pack acceptance.

The upgrade workflow also preserves the prior types file when generation fails or
returns empty output, refuses symlink/non-file destinations, and publishes only a
successful nonempty candidate. Six temporary-file tests execute the documented
Bash with an inert CLI fixture; all pass. The previous direct-redirection command
reproduced partial overwrite despite a failing CLI exit. This tests local file
handling, not a live CLI/database or TypeScript compatibility. Broad shell grants
were replaced with inventory scopes, package versions require explicit review,
and an unsupported SDK/API compatibility table was removed. Six previously
review-required findings in that skill are resolved; its two remaining warnings
are editorial. Reference/API review across the rest of the pack remains open.

The diagnostic collector now creates a unique owner-only directory and archive,
keeps failed observations explicit, and labels the candidate unreviewed. It no
longer captures raw CLI status or claims regex masking makes arbitrary output safe.
Ordinary probes use the anonymous client even when an admin key exists; only the
separately approved count comparison creates an admin client. Five offline tests
exercise file modes, archive contents, uniqueness and the actual documented client
selection with injected fixtures. All pass. The old collector reproduced 0777/0666
modes under a permissive umask; the old client selection failed all three approval
boundary cases. No real SDK/server request or support upload is covered by these
fixtures. Four more review-required findings were resolved by that source change.

The six type-generation tests also actually passed in hosted
job [137121248658](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/44994019265/job/137121248658)
at `601fe3b1e`, alongside the repaired generated-content drift check. Those receipts
precede the diagnostic collector changes and do not prove their hosted acceptance.

The two PostgreSQL regression tests passed locally and actually ran in hosted
job [137109661985](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/44990279811/job/137109661985)
at the preceding `8d54204ed` head. The old template failed the forged-owner test.
This is bounded SQL evidence, not a live Supabase deployment or a complete RLS audit.

## Numeric-value review

Twenty findings identify documented ports or protocol identifiers rather than
unexplained tuning constants. Each JSON finding now records the inspected source
lines and a primary reference: [local API/Studio ports](https://supabase.com/docs/guides/local-development/cli/getting-started),
[database connection ports](https://supabase.com/docs/guides/database/connecting-to-postgres),
[SQLSTATE identifiers](https://www.postgresql.org/docs/current/errcodes-appendix.html),
and [PostgREST singular-response errors](https://docs.postgrest.org/en/stable/references/errors.html).
The exact source hashes and original warnings are retained. No validator rule,
score, skill source or permission was changed by these dispositions.

This review clears the numeric-value finding only. In particular, it does not
endorse the production checklist's blanket transaction-pooling requirement or
its claim that direct connections are only for administrative work. Those claims
need correction against the connection-mode guidance. The schema-from-requirements
error table also recommends adding `security definer` on an insufficient-privilege
error; that escalation advice needs a separate safety repair. The 730-day retention
example and the remaining 443 finding have not been cleared in this pass. There
are 69 remaining warning dispositions plus the broader content review.

## Remaining acceptance

Resolve every `review-required` finding with a content fix or a documented,
evidence-backed disposition. Review linked references for contradictions and
unsafe examples; schema success alone cannot clear those defects. Then verify
pack/catalog/curated projections at the exact merged main commit and obtain the
independent review required by the bead. Required CI gates remain mandatory.
No live provider calls, paid evaluations, production credentials or gate waivers
were used for this review.
