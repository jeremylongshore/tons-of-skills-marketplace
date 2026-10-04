# ADR: sentry-issue-triage

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Accepted for the local v2 draft (not pushed)

## Context

Pack ADR `008` locks five parents. This one is the on-call loop over an issue
that exists. Absorb `010` adds `fingerprint-auditor`, `noise-classifier`, and
`perf-span-auditor` because phase 0's tree had dropped OP02–OP08 into a single
runbook. Nested procedures are `CHECKLIST.md` so `isGradedSkill` does not grade
them as marketplace peers. Cross-skill agent calls are unverified, so the
filter matrix is owned here and copied, labeled, by quota. Cardinality stays
one file under quota; this skill lists it.

Research `002` is the procedure source. v1 `SKILL.md` bodies are not.

## Decision

1. Parent routes. It does not classify severity in prose when `issue-context.py` can.
2. `issue-investigator` / `issue-triage-loop` is severity, suspect release, and the postmortem skeleton. It does not own filters.
3. `fingerprint-auditor` owns OP02–OP04, including prospective-only and the AI-grouping opt-out when `{{ default }}` is omitted.
4. `noise-classifier` owns OP05–OP07 (the matrix). Ignore still bills. Delete & Discard is Business/Enterprise, prospective, and per project.
5. `perf-span-auditor` owns OP08 and spawns only for a performance issue. Thresholds are in the checklist, not improvised.
6. `trace-bottleneck` does not fork `transaction-cardinality` and does not pretend it covers N+1.
7. `log-correlator` returns a query or "never writes it." No Datadog install skill.
8. Read-only. Communication template is a reference, not a send.
9. Minified stacks hand off. This ADR does not pick a `resolved_with` winner.

## Alternatives

| Alternative | Why not |
|---|---|
| One checklist that is both postmortem and filter matrix | That is the doc skill the cut rejected (`009` §2). |
| Sixth parent for fingerprints or noise | `008` Decision 1. Five slugs stay. |
| Fork `transaction-cardinality` under triage | Drift. Listing is not forking (`010` A3). |
| Nested `SKILL.md` | Catalog peers (`010` A1). |
| API writes (merge, ignore, discard) | `008` Decision 4. Recommend only. |
| Interpret `resolved_with` here | Forensics owns it. A second essay will drift. |

## Consequences

- Quota's volume path depends on a labeled copy of this matrix until a spike proves cross-skill calls. The copy is not edited by this batch; the canonical body is `agents/noise-classifier/skills/inbound-filter-matrix/CHECKLIST.md`.
- Operators who bookmarked `sentry-incident-runbook` need the v1 stub redirect (pack A5), which this skill does not delete.
- Severity numbers in the rubric are a pack convention so the script and the judge agree. They are not a Sentry product SLO.

## Confirmation

Eval blockers in `eval-spec.yaml` match the decision: payload severity, no invented times, no fingerprint backfill, matrix not merged into the loop, span fingerprint ≠ cardinality, no migrator/volume/gdpr spawn, no writes, no filtered+dropped sum, no environment rate limit, no map backfill.
