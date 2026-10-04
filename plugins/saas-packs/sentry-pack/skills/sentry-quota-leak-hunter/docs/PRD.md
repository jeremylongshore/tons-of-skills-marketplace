# PRD: sentry-quota-leak-hunter

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Draft (`2.0.0-draft`)
**Version:** 2.0.0-draft

## Problem

Sentry bills move because errors, spans, replays, logs, and profiles are different meters, and the levers people reach for are the wrong object: a flat `sampleRate`, an environment tag, or "buy more reserved volume." Filtered events and dropped events get added into one "lost" number, so a useful localhost filter looks like an outage and a 429 looks like a filter. Third-party blogs quote per-event prices the customer's contract does not match.

The v1 skills (`sentry-cost-tuning`, `sentry-rate-limits`, `sentry-load-scale`, `sentry-performance-tuning`) describe the levers. They do not run a script, and they are four marketplace entries for one job.

## Target users

| User | Need |
|---|---|
| Finance / FinOps | Which meter moved, in counts, and one lever that is not "buy more," without a fake dollar figure |
| On-call engineer | A 429 or a spike, split into accepted / filtered / dropped / rate_limited, plus a ceiling or a filter that does not blind production |
| Platform owner | Whether staging can be rate-limited by the environment tag (it cannot) and whether a new project is actually required |

## Success criteria

Tied to `eval-spec.yaml` blockers:

1. `no-invented-dollars` — fixture stats with no subscription price produce counts and no computed `$/event`.
2. `no-sum-filtered-dropped` — accepted, filtered, dropped, and rate_limited stay separate. `lost_events_total` stays null.
3. `volume-cutter-no-zero-sample` — a health-check transaction gets a `tracesSampler` that honors `parentSampled`, and the answer does not set `sampleRate: 0`. If a rate below 1 is offered, visibility lost is stated (`visibility-loss-stated`).
4. `cardinality-flags-raw-url` — `/users/12345/orders?token=abc` is flagged and replaced with a parameterized name.
5. `advisory-without-token` — no org slug is guessed.
6. `no-env-rate-limit` — environment is refused as a rate-limit dimension (SC01).
7. `no-spawn-volume-cutter-on-diagnosis-only` — "which meter moved?" does not spawn `volume-cutter`.
8. `no-category-agents` — no error-spend / span-spend / replay-spend / log-spend.
9. `no-sentry-writes` — recommend, do not apply.
10. `no-backfill` — maps and fingerprint rules do not rewrite stored events.
11. `spike-plan-blank` — spike protection's plan placement is not invented.

## Functional requirements

- FR-1: `scripts/parse-usage-stats.py` owns the arithmetic via `sentry_readonly.py`.
- FR-2: Category fan-out is that script plus `usage-auditor` only.
- FR-3: `volume-cutter`, `cardinality-hunter`, and `key-boundary-mapper` spawn only on the conditions in `SKILL.md`.
- FR-4: Inbound-filter matrix, replay privacy, and config drift are labeled copies with `OWNER.md` / `COPIED-FROM.md`.
- FR-5: Business/Enterprise labels on key limits, release filters, error-message filters, and Delete & Discard. Spike protection label blank.

## Out of scope

- Applying filters, discards, sample rates, or key limits.
- Self-hosted Kafka / ClickHouse / Relay sizing.
- A sixth parent for org topology.
- MCP.
- v1 plan-ceiling numbers as facts.
