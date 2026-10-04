# Quota categories

Meters are not one bucket (CQ01). SDK transport categories include `error`,
`transaction`, `span`, `log_item`, `log_byte`, `replay`, `monitor`, `session`,
`profile`, `profile_chunk`, `profile_chunk_ui`, `feedback`, `trace_metric`.
Spike protection and reserved volume are also not one bucket.

Usage Stats: accepted vs filtered vs dropped. Only accepted counts toward quota.
The project table is the breakdown. Do not add the series (CQ08). `rate_limited`
is its own outcome in the stats API; this pack does not fold it into `dropped`.

Script: `scripts/parse-usage-stats.py`. Fan-out is that script plus `usage-auditor`.
No per-category agents.

Citations:

- https://docs.sentry.io/pricing/quotas/manage-event-stream-guide/
- https://develop.sentry.dev/sdk/foundations/transport/rate-limiting/
- https://blog.sentry.io/sampling-strategy-sentry/
