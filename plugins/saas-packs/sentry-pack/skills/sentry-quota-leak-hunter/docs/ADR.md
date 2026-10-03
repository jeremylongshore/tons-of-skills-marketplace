# ADR: sentry-quota-leak-hunter

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Accepted for the v2 draft (`2.0.0-draft`)

## Context

Pack ADR `008` locks this slug as one of five parents (Keep seed `sentry-cost-tuning`). Absorb `010` wins on six points: nested procedures are `CHECKLIST.md`, category fan-out is the usage script plus `usage-auditor` only, cross-skill calls are labeled copies until a spike proves otherwise, evals include the 009 negatives, and scripts use `pack/scripts/lib/sentry_readonly.py`. Org topology is not a parent. `key-boundary-mapper` nests it here, including the SC04 row (team ≠ alert rule ≠ DSN).

Pain in this skill: CQ01–CQ08, SC01, SC02, SC04, SC06, SC07. SC03's diff is owned by PII; this skill holds a pointer copy. SC05's wrong-project upload is release-medic.

## Decision

1. The parent routes. The script prints outcomes. Agents do not re-sum.
2. No per-category spend agents.
3. `volume-cutter` is not on the diagnosis path.
4. `transaction-cardinality` lives once, here. Triage gets an `OWNER.md` pointer, not a fork.
5. Reference copies are mandatory for the filter matrix, replay privacy, and config drift. Each copy has `OWNER.md` and `COPIED-FROM.md`.
6. Read-only. `refuse_write` on `--apply`.
7. No third-party price card. No invented spike-protection plan. No environment rate limit.
8. `sampleRate` below 1 must state visibility lost. `sampleRate: 0` is a failed answer.

## Alternatives

| Alternative | Why not |
|---|---|
| Ship `sentry-quota-guard` beside this slug | `008` forbids the `007` names. |
| Four category agents | `009` / `010`: two trees. Profiles and logs fell out. |
| Copy the filter matrix with no banner | Silent copies are the drift SC03 exists to stop. |
| Call `noise-classifier` directly | No spike has shown this runtime can. `010` makes the copy the rule. |
| Sixth skill `sentry-org-topology` | Rejected. The map is only useful next to a key ceiling. |
| Implement live REST in this skill's script | The shared client still raises on live fetch. Advisory paste is the contract until live fetch in `sentry_readonly.py` is filled for all five parents together. |

## Consequences

- A quota pilot runs without triage or PII being installed, because the copies are in-tree.
- Those copies can drift. `COPIED-FROM.md` is the reminder to delete them after a successful call spike.
- The CFO page cannot show recovered dollars unless the customer pastes `subscription_screen_usd`. That is intentional.
