# CFO output format

The CFO line is counts and a lever, not a made-up invoice.

```
Meter: span  accepted=900000  filtered=10  dropped=0  rate_limited=12000
Dollars: not in this payload. Open the subscription screen. Do not use a per-event price from a blog.
Lever: minute ceiling on the noisy DSN (Business/Enterprise), or a tracesSampler that keeps parentSampled.
Visibility lost: a flat 10% trace sample hides 90% of traces, including the slow ones that are not the parent.
Not a lever: environment tag. Ignore still bills.
Wrote to Sentry: no
```

Rules:

- Never add accepted + filtered + dropped under one verb ("lost", "wasted events").
- Never add `rate_limited` into `dropped` unless the script already did, which it will not.
- A `subscription_screen_usd` field may be quoted only as "the payload says the customer screen shows this." It is not an estimate you computed.
- One lever. Say the plan gate or "unknown."
- 90-second skim: meter, lever, what you refuse to sum, what you will not click.
