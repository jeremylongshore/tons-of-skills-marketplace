# transaction-cardinality

**Owner:** `sentry-quota-leak-hunter` → `cardinality-hunter`
**Single file.** Triage `trace-bottleneck` has an `OWNER.md` pointer only.
Do not copy this checklist under triage.

This is not the performance-issue span-fingerprint job (OP08). That is triage
`perf-span-auditor`. Raw URL transaction names and span explosions are this
file. N+1 detection thresholds are not.

## Flag these names

- Path contains a numeric id: `/users/12345/orders`
- Path contains a UUID or long token: `/api/orders/8f3a9c0e-...`
- Name includes a query string: `GET /search?q=secret&page=2`
- Name is the full URL including host, rebuilt per request

## Replacement

Parameterize: `/users/:id/orders`, `/search`. Low-cardinality route templates
are the fix. A flat `tracesSampleRate` hides the bug and the rest of the trace.

If a `tracesSampler` is also required, point at `sampler-and-filters`. Do not
paste a second sampler that overrides `parentSampled`.

## Span explosion

A transaction that starts one span per row, per retry, or per log line burns
the **span** meter even when the transaction name is clean. Recommend a cap
or a coarser span, and say which spans disappear. `profilesSampleRate` is a
separate meter (`profile` / `profile_chunk`). Do not subtract profiles from
spans in your head.

## Not a backfill

Renaming transactions does not rewrite transactions already accepted.
Fingerprint rules do not restack old issues. Source maps do not either.

## Example

Flag: `GET /users/12345/orders?token=abc`
Replacement: `GET /users/:id/orders`
Do not set `sampleRate: 0`.
