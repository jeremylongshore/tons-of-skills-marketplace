# quota-usage-audit

**Owner:** `sentry-quota-leak-hunter` → `usage-auditor`
**Not a marketplace skill.** `CHECKLIST.md` on purpose.

## When to run

Every quota audit, after `scripts/parse-usage-stats.py`. Not before.

## Steps

1. Confirm the script exited 0 and `ok: true`. If it exited 2, stop. Advisory mode needs a pasted file. Do not guess the org.
2. Copy `categories` into the answer. For each category print `accepted`, `filtered`, `dropped`, and any other outcome (`rate_limited`, `invalid`, `client_discard`) as its own number.
3. Leave `lost_events_total` null. If you feel the urge to add the three series, you are wrong (CQ08). Filtered means an inbound filter. Dropped or `rate_limited` means a ceiling, spike protection, or quota. Only accepted bills.
4. Name `highest_accepted_category`. If `meter_that_moved.accepted_delta` is present, that category is the one that moved. A large baseline is not automatically a leak.
5. Dollars: print `dollars` only when `dollar_source` is `customer_subscription_screen_field`. If `ignored_unofficial_price_keys` is non-empty, say you ignored them. Never multiply events by a per-event price from a blog.
6. Do not compare the counts to v1's Developer 5K / Team 50K / Business 100K ceilings. Those were claims to re-verify, not facts.
7. Fan-out check: `category_agents` must be `[]`. You are the only auditor. Profiles and `log_item` stay in this list.
8. Replay `accepted == 0`: do not open replay privacy. Replay `accepted > 0` and the user is talking about cost: the parent may spawn `volume-cutter`, which may Read the replay-privacy copy. You do not.

## Output

The parent output block, filled only from the script JSON. `Wrote to Sentry: no`.

## Fail

- A single "lost events" KPI.
- A dollar figure you computed.
- Four category agents.
