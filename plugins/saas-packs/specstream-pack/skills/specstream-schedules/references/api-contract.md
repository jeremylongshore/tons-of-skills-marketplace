# SpecStream Schedules and Feeds Reference

## Saved Request Schedules

- Cadence: hourly to yearly inside account and key spending limits.
- Refresh billing: half the row rate for rows that changed and new rows; 1c per row that returns unchanged.
- Output: every change is labeled; new matches deliver to Slack, email, a sheet, a CRM, or a signed webhook (`https://specstream.ai/docs/webhooks`).
- Spend caps: enforce key limits (`spend_cap_cents`) via `POST /v1/account/keys` or `PATCH /v1/account/keys/{id}`, and monitor spend via `GET /v1/account/usage?group=day|endpoint|key` (free with `account:read`).

## Pre-Built Signals and Weekly Feeds

- Signals directory: `https://specstream.ai/signals` (US funding rounds, layoffs, new executives, and related events).
- Lists and feeds catalog: `https://specstream.ai/data/lists.json` (1,695 monthly feeds across 38,142 lists as of Nov 10, 2026).
- Feed pricing: delivers rows added by the source each week at 5c/row for the first 2,000 rows and 1c/row after in a month, $19/month minimum.
