# release-health

**Owner:** `sentry-release-medic` → `release-finalizer`

Recommend finalize, commits, and a deploy record. Do not mark health fine
unless `scripts/assess-session-stats.py` prints `health_fine: true`.

## Commits vs maps

Debug ID symbolication does not attach commits. If the release has events and
an empty commit list, check `fetch-depth: 0` and that the SDK release string
is the release the action created. Do not spawn a new agent for that.

## Deploy record

Recommend a deploy with an **environment** (`production`, `staging`, the string
the SDK already sends). See parent `references/environment-on-deploy.md`.
Environment is not a quota silo and not a rate limit. Untagged events are
their own bucket; a dashboard filtered to `environment:production` will not
show them. Do not call them production.

You do not POST the deploy. Print the fields: release, environment, name if
they have one.

## Session stats (RL08)

```bash
python3 scripts/assess-session-stats.py --json query.json
```

Hard rules the script enforces:

- Cap: 10,000 datapoints. A 90-day window grouped by release is at most `floor(10000/91) = 109` releases. `groups_returned: 109` on that query is truncation, not "we only have 109 releases."
- `session.duration` stopped 2023-01-12. Do not alert on it. The API may still list the field and warn that data is incomplete.
- `health_fine` requires `api_read: true`, one `project`, one `environment`, one `release`, no duration field, and a query shape that is not the 90-day group-by-release cap.
- No API read → not fine. Do not say "looks healthy" from a screenshot of crash-free without the query.

Gate a deploy on one project + one environment + the release you just shipped, over a short window. Not on 90 days of every release in the org.

Fields you may mention: `crash_free_rate(session)`, `crash_free_rate(user)`. `groupBy` can be `project`, `release`, `environment`, `session.status`. An org-wide number is not one number.

## Bad release still ingesting

Recommend an inbound release filter only as a label: Business/Enterprise, full release string, glob not SemVer, no match when `release` is missing. Copy the string from event JSON. Do not click it. Ignore still bills. This filter is not Delete & Discard.

## Do not

- Create the release, finalize, or record the deploy via the API.
- Use session duration as a rollback signal.
