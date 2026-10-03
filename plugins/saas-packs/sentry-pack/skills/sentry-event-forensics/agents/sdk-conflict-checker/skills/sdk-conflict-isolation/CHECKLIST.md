# sdk-conflict-isolation

**Owner:** `sentry-event-forensics` → `sdk-conflict-checker`

## Look for

1. Two `Sentry.init` calls (app entry and a framework plugin, or a test helper that also loads in prod). Name both. The later call can replace `beforeSend` and look like a DSN outage.
2. `@sentry/node` imported from code that webpack/vite ships to the browser. That is a bundle conflict, not a source-map gap.
3. OpenTelemetry SDK **and** Sentry both started, both exporting spans. Name the double-init. Do not rewrite the OTel pipeline, samplers, or collector config. Recommend which exporter should be the one that sends to Sentry.
4. A winston / pino / logging wrapper that also calls `captureException` for the same line the SDK's logging integration already sends. Name the double capture. Do not turn logging off.
5. A custom `transport` that no-ops `send`. That is `drop-tracer` layer transport if events never appear. Say which agent owns it.

## Do not

- Spawn `sdk-migrator` because two packages differ by a minor version.
- Claim "no conflict" for code you were not shown.
- Print `SENTRY_AUTH_TOKEN` or `sntrys_`.
