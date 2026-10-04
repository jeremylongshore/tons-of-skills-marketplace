# sentry-pack v2 rebuild — decision record

**Status:** accepted with PR #1599. **Reconstructed** 2026-10-04 during review cleanup: the
original decision documents were drafted in an external sandbox and never committed. This record
states only decisions that the PR description and the shipped pack themselves establish.

## Decisions

1. **Five operational skills replace 30 tutorials.** Operators bring Sentry five recurring jobs:
   find quota burn (`sentry-quota-leak-hunter`), explain a missing or wrong event
   (`sentry-event-forensics`), repair a release or sourcemap (`sentry-release-medic`), triage an
   issue (`sentry-issue-triage`), and prove PII scrubbing (`sentry-pii-scrub-enforcer`). SDK tours
   are out of scope.
2. **Advisory, not write-capable.** The skills read pasted configuration and event JSON and
   recommend changes. The shared helper `scripts/lib/sentry_readonly.py` refuses write operations
   (`--apply` / `--send` exit non-zero). Each skill's `allowed-tools` is scoped to its own bundled
   scripts and read-only tooling so the permission boundary matches the claim.
3. **Live API fetch is deferred.** The client's fetch methods currently accept pasted JSON; live,
   read-only Sentry API access is a tracked follow-up, not a shipped feature.
4. **Nested procedures are checklists, not skills.** Agent procedures live at
   `skills/<parent>/agents/<agent>/skills/<child>/CHECKLIST.md`, so the marketplace corpus does
   not count them as separate skills.
5. **No hooks.** sentry-pack 2.0.0 ships no hooks; any hook needs its own later decision.
6. **Redirect stubs until a later release.** Every v1 slug keeps a redirect stub in 2.0.0
   (see `phase0-kill-list.md`).
7. **Organization topology is not a sixth skill.** Key and DSN boundary checks nest under the quota
   skill; project-standard drift checks nest under the PII skill.
