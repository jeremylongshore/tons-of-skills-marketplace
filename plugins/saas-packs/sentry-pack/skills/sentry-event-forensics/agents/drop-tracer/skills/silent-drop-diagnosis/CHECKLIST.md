# silent-drop-diagnosis

**Owner:** `sentry-event-forensics` → `drop-tracer`
**Not a marketplace skill.**

One layer. Do not spawn `sdk-migrator` or `debug-bundler` from this list.

## Layers, in order

1. **init** — `Sentry.init` missing, `enabled: false`, DSN host typo, init after the error already threw, second init that replaces a working one. A public DSN key in the browser is normal. A `beforeSend` that returns null is not an init failure.
2. **sample** — `sampleRate` / `tracesSampleRate` / sampler returns 0. State the fraction that will never arrive. Do not recommend `sampleRate: 0` as the repair. Parent sampling: do not override `parentSampled === true` (that is quota's sampler checklist if the user also asked to cut volume — do not spawn `volume-cutter` yourself).
3. **beforeSend** — function returns `null` (or `beforeSendTransaction` does). Cause is `beforeSend`, not the DSN. Fixture: `references/fixtures/event-beforesend-null.json`.
   - `beforeSend` does not cover Session Replay unmask (PI06).
   - `beforeSend` does not scrub span names, log lines, or metric names (PI02).
   - If the user wanted a scrub that still sends the event, that is PII `pii-scrubber`, and returning null fails that job.
4. **transport** — blocked by the client, CORS, ad-block on the ingest host, custom transport that drops, missing `flush()` / `close(timeout)` on Lambda or a CLI that exits. Serverless without flush looks like a DSN bug. It is not.
5. **inbound filter** — only if the event left the SDK. Outcome is filtered, not dropped. You do not own the matrix. Name triage `noise-classifier` if they need the row. Ignore still bills; that means the event **was** accepted, so this is not why it vanished.
6. **release mismatch** — the event **exists** and is minified. Hand to `sourcemap-debugger`. Not a silent drop.

## Ruled out

Write the layers you checked. "Turn on `debug: true` and look" is not the cause field.

## Self-hosted

Stop. SaaS ingest behavior may not match.
