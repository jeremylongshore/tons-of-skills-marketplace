# Severity rubric

`scripts/issue-context.py` is the implementation. Do not assign a severity the script did not return. Do not invent timestamps.

Inputs, payload only:

- `status` (`unresolved`, `resolved`, `ignored`, …)
- `level` (`fatal`, `error`, `warning`, `info`, `debug`)
- `userCount` (or `user_count`)
- `count` (events on the issue)
- `environment` (tag or field), used only as a prod gate
- `release` (field or tag) — if absent, suspect release is unknown
- `firstSeen` / `lastSeen` / event `timestamp` — the only postmortem times

First match:

| Result | Rule |
|---|---|
| SEV-4 | `status` is `resolved` or `ignored` |
| SEV-1 | `level` is `fatal`, or `error` with `userCount >= 100`, or `error` in `production`/`prod` with `count >= 1000` |
| SEV-2 | `level` is `error`, or `userCount >= 10`, or `count >= 100` |
| SEV-3 | `level` is `warning` |
| SEV-4 | anything else |

These thresholds are a pack convention so evals are stable. They are not a Sentry SLO and not a dollar figure.

Postmortem skeleton:

- Timeline: the timestamp strings the script returned, labeled as first/last seen. No other times.
- Impact: `userCount` and `count` from the script.
- Suspect release: the script value or "unknown".
- Five whys: leave blank unless the payload or the repo states a cause.
- Actions: the next check from the agent that actually ran (fingerprint, noise, span, log, or symbolication handoff).

Do not sum `accepted + filtered + dropped`. This rubric does not read stats.
