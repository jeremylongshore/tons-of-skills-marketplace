# SDK conflicts

- Double `Sentry.init`.
- `@sentry/node` inside a browser bundle.
- OpenTelemetry and Sentry both exporting the same spans. Name it. Do not rewrite the OTel config.
- Logger integration plus a manual `captureException` of the same line.

Not a conflict: two services with two DSNs. That is `key-boundary-mapper` if the question is the ceiling, or release-medic if the question is which project received the maps.

Do not upgrade the SDK because a conflict exists. `sdk-migrator` is a separate ask.
