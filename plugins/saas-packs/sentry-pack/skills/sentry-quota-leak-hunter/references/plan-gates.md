# Plan gates

Label these Business/Enterprise when you recommend them:

- Client key (DSN) rate limits
- Inbound release filter
- Error-message filter
- Delete & Discard (prospective; does not erase accepted events)

Free-toggle class (confirm on the customer's plan screen; do not invent a SKU): browser extensions, localhost, legacy browsers, web crawlers. Those are filtered, not dropped.

Spike protection: the page fetched for this pack did **not** state a plan placement. Leave the label blank (008 follow-up 5). Do not write "Team includes spike protection" or the opposite.

v1 ceilings (Developer 5K errors, Team 50K, Business 100K) are not shipped as facts.

If the plan is unknown, say unknown and do not tell the user to click a missing control. Fallback on lower plans: free filter toggles, a named `beforeSend` on the next deploy, an Owner quota change.
