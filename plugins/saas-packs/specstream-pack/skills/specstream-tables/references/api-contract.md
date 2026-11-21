# SpecStream Deep Search Tables Reference

## Account Workflow (MCP and REST)

1. `compile` (or `POST /v1/parse` with `{"q": ...}`): parses a plain-language request into columns and conditions.
2. `quote_capacity_work`: returns the quote ID, hash, and maximum spend ceiling (valid for 30 minutes).
3. User approval: confirm the maximum before spending.
4. `authorize_capacity_work`: pass `quote_id`, hash, `confirm_max_cents`, and a stable request key for idempotent retries.
5. `get_find_decisions` / `replay_find_decisions`: inspect each condition's value, reason, `source_url`, and read time (`replay_find_decisions` costs nothing).

## Keyless Per-Request Flow (`POST https://api.specstream.ai/v1/agent/lists`)

- Body: `{"request": "<plain language list>", "count": 25}` (`count` optional, 1 to 500).
- Returns `402` with column read-back, ceiling price, MPP challenge (`WWW-Authenticate: Payment`), and x402 `upto` challenge (`PAYMENT-REQUIRED`).
- Re-sending with payment returns `202` with `purchase_id`, `token`, and `status_url`.
- Unused balance is returned when the run completes; runs returning no rows cost nothing.

## Pricing and Billing Rules

- Delivered rows carry `billable: true` at 5c, 15c, or $1 per row depending on work required, plus 5c per person email and 15c per phone when requested.
- Duplicates, rows already owned, and contradicted rows are not charged.
- Existing lists catalog (`https://specstream.ai/data/lists.json`): 5c/row for the first 2,000 rows, 1c/row after, $5 minimum.
