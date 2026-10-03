# Known pitfalls (salvaged from the Cut skill, one list)

Not a skill. The ten-style list, kept short:

1. Hardcoded DSN in a public repo is a write credential leak (rotate the key). It is not the same as an auth token leak.
2. `sampleRate: 1` on traces in production blows the span meter. State what you lose if you lower it.
3. Missing `flush()` on serverless. Transport layer.
4. `beforeSend` returns null. Outage, not a scrub.
5. Release id in the SDK ≠ release id on the uploaded maps.
6. `beforeSend` that fails to strip email is PII, not this list's fix. Hand off.
7. `@sentry/node` in a browser bundle.
8. CORS / ad-block on the ingest host. Transport.
9. Environment tag missing, then a production dashboard that hides untagged events.
10. Source maps uploaded after the first error. No backfill.

DSN typo (wrong org host) is init. Do not use it to explain a null `beforeSend`.
