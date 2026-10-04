# sampler-and-filters

**Owner:** `sentry-quota-leak-hunter` → `volume-cutter`
**Not a marketplace skill.**

The inbound-filter matrix is **not** this file. Read the labeled copy next to
this directory. Owner: triage `noise-classifier`.

## Decision order for traces (CQ03, CQ06)

1. If `tracesSampler` is set, its return value is used **even when a parent decision exists**. That is the trap.
2. Else honor the parent sampling decision.
3. Else `tracesSampleRate`.

Refuse any sampler that returns 0 or false when `parentSampled === true`.
A broken trace is not a savings strategy.

Drop a health-check transaction by **name** only when there is no parent
decision. Do not drop `/health` by setting `tracesSampleRate` to a flat 0.1.

```javascript
tracesSampler(samplingContext) {
  if (samplingContext.parentSampled !== undefined) {
    return samplingContext.parentSampled;
  }
  const name = samplingContext.transactionContext?.name ?? "";
  if (name === "/health" || name === "GET /health") return 0;
  return 0.2; // state what the other 80% of traces will hide
}
```

If you ship a number below 1, the answer must say what visibility is lost
(deploys that only fail in the unsampled slice, broken cross-service traces).
`sampleRate: 0` on errors is forbidden. Keep error `sampleRate` at 1 unless
volume is extreme, and even then say which issues disappear. A key minute
ceiling is the better error lever.

## Rate limits vs sampling

- SDK `sampleRate` needs a deploy and blinds you continuously.
- A server key rate limit is Business/Enterprise, per DSN, not per environment.
  Prefer a **minute** window so one spike cannot eat the day. It is a ceiling,
  not a monthly target. On 429, the SDK must **drop** until `Retry-After`, not
  queue and retry.
- There is no environment rate limit. Do not write `environment: production`
  into a rate-limit recommendation. Send the user to `key-boundary-mapper`.

## Spike protection

Plan placement: **unknown**. Leave it blank. Behavior you may state: above a
baseline, events are dropped so the excess is not charged. The drop is not a
sample you can reconstruct. The issue you needed may be partial. Do not raise
reserved volume for a temporary spike (see `references/subscription-clocks.md`).

## beforeSend

A `beforeSend` that returns null for one **named** error is a quota lever and
needs a deploy. A `beforeSend` that returns null for everything is an outage
(forensics `drop-tracer`). `beforeSend` does not see Replay, spans' names, logs,
or metrics.

## What you do not do

- Click the filter, the discard, or the key limit.
- Sum filtered and dropped to justify the lever.
- Promise that a fingerprint rule or a source map will shrink history. Both are
  prospective.

## Health-check transactions vs the inbound filter

The filter matrix (labeled copy next to this file; owner `noise-classifier`)
has a transaction glob list (`*/health`, `*healthcheck*`, `*/ping`, and the
rest on that checklist). `ping_health` does not match. Error events from a
health URL are not dropped by that transaction filter. A `tracesSampler` that
returns 0 for `GET /health` is only for the no-parent case. It is not a
substitute for the matrix, and it does not drop error events.
