---
name: specstream-schedules
description: |
  Configure and validate recurring SpecStream Deep Search schedules, refresh cadences, spending caps, change labeling, and webhook or channel delivery. Use when keeping a saved table up to date or setting up signal monitors. Trigger with "SpecStream schedule", "monitor changes with SpecStream", or "validate SpecStream schedule".
argument-hint: "[schedule-config.json]"
allowed-tools: Read, Bash(python3:*)
version: 1.0.0
author: Tarek Etman <tarek@specstream.ai>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, specstream, schedules, monitoring, webhooks]
---
# SpecStream Schedules and Recurring Monitors

## Overview

Configure and validate saved SpecStream schedules that rerun Deep Search requests on an hourly-to-yearly cadence inside explicit spending limits. Refreshes charge half the row rate for changed or new rows and 1c for unchanged rows, label every change, and route new matches to Slack, email, sheets, CRMs, or signed HTTPS webhooks.

## Prerequisites

- An approved saved Deep Search request or a monthly feed from the SpecStream catalog (`https://specstream.ai/data/lists.json`) or signals catalog (`https://specstream.ai/signals`).
- A scoped key or account spending limit (`spend_cap_cents`) approved by the account owner before creating recurring runs.
- Python 3.10+ to validate schedule configurations offline against [the schedules contract](references/api-contract.md).

## Instructions

1. Use `Read` to inspect the proposed schedule configuration or webhook handler and review [the schedules contract](references/api-contract.md).
2. Verify the refresh cadence (`hourly`, `daily`, `weekly`, `monthly`, or `yearly`), confirm `spend_cap_cents` is a positive integer bounded by the account's monthly and per-key spending limits, and confirm delivery channels (`slack`, `email`, `sheet`, `crm`, or `webhook` with an `https://` target).
3. Run the offline schedule validator before creating or modifying any recurring schedule:

```bash
python3 scripts/validate_specstream_payload.py --kind schedule --file schedule-config.json
```

4. For webhook consumers, verify SpecStream's webhook signature (`https://specstream.ai/docs/webhooks`), deduplicate deliveries by event ID, and read account spend via `GET https://api.specstream.ai/v1/account/usage?group=day|endpoint|key` (`account:read`, zero cost).
5. When monitoring standard record families (for example US funding rounds, layoffs, or new executives), check `https://specstream.ai/signals` and `https://specstream.ai/data/lists.json` before building a custom Deep Search schedule.

## Output

Return the validated schedule configuration, cadence and `spend_cap_cents` summary, delivery channel verification, expected refresh pricing boundary (half-rate changed/new rows, 1c unchanged rows), and offline validator status.

## Error Handling

| Condition | Response |
| --- | --- |
| Missing or non-positive `spend_cap_cents` | Reject the schedule config offline; never create an uncapped recurring schedule. |
| Non-HTTPS webhook URL (`http://`) | Require `https://` for all signed webhook delivery targets. |
| `402` or `403` on scheduled refresh (`spend_cap_cents` or monthly cap) | Inspect `GET /v1/account/usage` and raise `spend_cap_cents` only with owner approval via `PATCH /v1/account/keys/<key_id>`. |
| Pre-built weekly feed covers the need | Prefer the catalog feed ($19/month minimum, weekly added rows) over custom hourly polling. |

## Examples

**Example 1: Validate a daily Deep Search schedule with signed webhook delivery**

```bash
# 2500 cents = $25.00 spend cap on the recurring schedule
python3 scripts/validate_specstream_payload.py --kind schedule --stdin <<'EOF'
{"name": "series-a-robotics-daily", "cadence": "daily", "spend_cap_cents": 2500, "delivery": [{"channel": "webhook", "url": "https://hooks.example.com/specstream"}]}
EOF
```

**Example 2: Catch an unencrypted webhook target offline**

```bash
python3 scripts/validate_specstream_payload.py --kind schedule --stdin <<'EOF'
{"name": "insecure-hook", "cadence": "weekly", "spend_cap_cents": 500, "delivery": [{"channel": "webhook", "url": "http://example.com/hook"}]}
EOF
```

## Resources

- [Schedules and feeds contract](references/api-contract.md)
- [SpecStream Signals](https://specstream.ai/signals)
- [SpecStream Webhooks Docs](https://specstream.ai/docs/webhooks)
