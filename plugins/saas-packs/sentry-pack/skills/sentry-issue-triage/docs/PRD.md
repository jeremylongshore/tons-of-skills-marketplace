# PRD: sentry-issue-triage

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Draft (`2.0.0-draft`) — local, not pushed

> Filled from pack ADR `008`, absorb `010` (wins on checklists, copies, and eval
> negatives), kill-list §4, and research `002` OP01–OP08. Not a v1 body copy.

## Problem

An on-call page is one Sentry issue that may be lying. Minified frames split one
bug across releases. A message with an id becomes a new issue every time. AI
grouping will not split a fingerprint, and a fully custom fingerprint opts out.
Rules written after the bad release do not restack the 40 issues already stored.
Browser noise and health checks still page. Ignore still bills. Performance
issues group by span evidence that error fingerprint rules do not touch. The
operator also cannot find the log line that carries the event id.

v1 `sentry-incident-runbook` was a severity essay. v1 `sentry-observability` was
an APM tour. Neither ran a script, and neither separated the postmortem from the
inbound-filter matrix.

## Target users

| User | Context | Primary need |
|---|---|---|
| On-call engineer | Paged on one issue | Severity from the payload, the release that is actually on the event, the next check |
| Triage lead | "This project is noisy" or issues keep splitting | Fingerprint verdict that says prospective-only, and the filter matrix (Ignore vs Discard) |
| Someone writing the postmortem | Needs timeline and impact | Timestamps and counts copied from the issue, not invented |

## Success criteria

Tied to `eval-spec.yaml` blocker ids.

1. Severity and suspect release come from the payload; the postmortem does not invent times — `severity-from-payload`.
2. Log correlation returns a query containing the event id, or says the codebase never writes it — `log-query-or-absent`.
3. Transaction-name cardinality is not reimplemented; the quota checklist is listed, not forked — `defers-cardinality`.
4. Fingerprint rules are not described as rewriting stored events — `no-fingerprint-backfill`.
5. The inbound-filter matrix stays on `noise-classifier`; `issue-triage-loop` is severity and postmortem only — `noise-not-merged-into-triage-loop`.
6. A performance issue uses `perf-span-auditor` / `span-fingerprint`, not `transaction-cardinality` — `span-fingerprint-not-cardinality`.
7. A diagnosis does not spawn `sdk-migrator`, `volume-cutter`, or `gdpr-deletion` — `no-spawn-migrator-on-diagnosis`.
8. No Sentry write API — `no-sentry-writes`.
9. Does not sum filtered and dropped, does not put a rate limit on `environment`, and does not claim source maps backfill — `no-sum-filtered-dropped`, `no-env-rate-limit`, `no-sourcemap-backfill`.

## Functional requirements

- **FR-1:** `scripts/issue-context.py` assigns SEV-1..SEV-4 from the rubric in `references/severity-rubric.md` using only payload fields.
- **FR-2:** `scripts/fingerprint-from-event.py` reports fingerprint, `{{ default }}`, AI opt-out, stack presence, and id-like message tokens. `backfill` is false.
- **FR-3:** Parent routes to the six agents in `SKILL.md`. Agents `skills: []` and Read `CHECKLIST.md`. No nested `SKILL.md`.
- **FR-4:** `noise-classifier` owns `inbound-filter-matrix`. Callers use a labeled copy. This parent does not paste the matrix into the postmortem.
- **FR-5:** `trace-bottleneck` has an `OWNER.md` pointer only for `transaction-cardinality`.
- **FR-6:** OP01 minified frames hand off to `sentry-event-forensics` / `sourcemap-debugger` without restating `resolved_with`.
- **FR-7:** Shared reads go through `scripts/lib/sentry_readonly.py`. No token in output. No MCP.

## Out of scope

- Events that never arrived, SDK upgrades, debug bundles (forensics).
- Uploading source maps or release health (release-medic).
- Quota arithmetic and applying a sampler (quota-leak-hunter).
- Applying Ignore, Discard, merge, or resolve. Recommend only.
- Self-hosted Sentry. Generic SRE essays. Sending the communication template.
