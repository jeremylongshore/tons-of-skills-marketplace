# COPIED-FROM

- **Source:** `skills/sentry-issue-triage/agents/noise-classifier/skills/inbound-filter-matrix/CHECKLIST.md`
- **Owner agent:** `noise-classifier`
- **Caller:** `sentry-quota-leak-hunter` → `volume-cutter`
- **Why:** Absorb rule — reference-copy fallback is mandatory until a spike proves
  this runtime can invoke another skill's subagent. Quota pilot must not wait on triage.
- **Delete when:** Cross-skill agent calls are proven (new ADR / spike note).
