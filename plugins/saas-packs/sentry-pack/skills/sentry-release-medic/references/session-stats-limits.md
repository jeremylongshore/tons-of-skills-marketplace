# Session stats limits (RL08)

`GET /api/0/organizations/{org}/sessions/`

- At most 10,000 datapoints.
- Documented example: a 90-day window grouped by release returns at most `floor(10000/91) = 109` releases. A noisy release can fall off. Crash-free then looks fine. That is a false pass.
- Fields include `crash_free_rate(session)` and `crash_free_rate(user)`.
- **Session duration stopped being recorded on 2023-01-12.** The API may still list `session.duration` aggregates and warn that data is incomplete. Do not alert on it.
- `groupBy`: `project`, `release`, `environment`, `session.status`.
- Environment and project filters exist. An "org-wide crash-free" number is not one number.

Script: `scripts/assess-session-stats.py`. `health_fine` is the script's boolean, not the model's.

Citation: https://docs.sentry.io/api/releases/retrieve-release-health-session-statistics/
