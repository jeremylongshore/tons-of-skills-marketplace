# Subscription clocks (CQ04)

Parent reference. No agent.

- Raising reserved volume is immediate. Lowering it waits until the next billing period (annual plans: next billing year). Unused reserved volume is not refunded.
- Pay-as-you-go changes are documented as immediate (within about 24 hours) and cannot drop below what the period already consumed.
- A temporary spike: raise pay-as-you-go, not reserved. Steady growth: reserved, because it is cheaper than pay-as-you-go. Do not "temporarily" raise reserved.
- Team → Business mid-period can change pay-as-you-go rates retroactively. First overage on a paid plan may enter a one-time grace period. Confirm on the customer's screen.
- Quota edits are Owner/Billing. The on-call engineer often cannot click them.
- Change plans before the last day of the period; the docs warn about timezone edges.

This file does not contain a price. The subscription screen is the price.

Citation: https://docs.sentry.io/pricing/quotas/manage-event-stream-guide/
