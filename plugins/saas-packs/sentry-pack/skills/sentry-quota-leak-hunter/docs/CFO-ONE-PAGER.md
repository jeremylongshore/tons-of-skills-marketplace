# CFO-ONE-PAGER: sentry-quota-leak-hunter

**Version:** 2.0.0-draft
**Date:** 2026-10-03
**Read time:** about 90 seconds

## The number you can trust

Counts from your own Usage Stats, split:

- **Accepted** bills.
- **Filtered** is an inbound filter you (or a default) asked for. It does not bill. It is not an outage.
- **Dropped** / **rate_limited** is a ceiling, spike protection, or quota. Those events are gone. They are not a filter.

This skill will not add those into one "events lost" or "waste" figure. If a report does, it is wrong.

## The number you will not get from us

A dollar total we computed from a blog's per-event price. Your subscription screen is the price. If you paste that screen's figure into the stats JSON as `subscription_screen_usd`, we will quote it as yours. We will not annualize a guess.

Reserved volume is not a temporary knob. Turning it up is immediate. Turning it down waits for the next billing period, and unused reserved volume is not refunded. A short spike is pay-as-you-go, if you buy anything. Often you should not buy anything yet.

## The lever, in business words

| If the loud meter is… | The lever that is not "buy more" | What it costs you |
|---|---|---|
| Spans, health checks, or raw URLs like `/users/12345` | Name the route (`/users/:id`) and sample traces only when the parent trace was not already chosen | A flat 10% sample hides 90% of traces, including bugs that are not in the sampled slice |
| Errors from one bad release | Filter that release (Business/Enterprise) or put a per-minute cap on that app's key | The cap drops data when you are over it. It is a ceiling, not a target. Ignore still bills. |
| Replays on every session | Record replays on the checkout or on errors, not on every page | You will not have a replay for the sessions you skipped. A privacy unmask is a separate switch; turning down volume does not turn it off. |
| "Staging is noisy" | A second client key with a tighter cap | You cannot do this by setting environment = staging. Environment is a label, not a bill fence. |

Spike protection can delete the incident you needed. We will not tell you which plan includes it. That line is blank until someone opens your plan screen.

## What we will not click

No filter, no discard, no key change, no contract change. The skill prints the lever. A person applies it.

Template: `references/cfo-output-format.md`.
