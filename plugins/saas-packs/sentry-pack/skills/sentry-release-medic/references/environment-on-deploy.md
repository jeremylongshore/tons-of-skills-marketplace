# Environment on the deploy

Salvaged from Cut skill `sentry-multi-env-setup`. Not the DSN-per-env essay.
That boundary is quota `org-key-boundaries`.

## Two places the environment string is set

1. **SDK init.** Pass `environment` when the SDK initializes, for example
   `Sentry.init({ dsn: DSN, release: RELEASE, environment: "production" })`.
   Every event the SDK sends carries this string. If `environment` is left
   unset, Sentry defaults it to `production` server-side — a silent default,
   not an explicit decision, so name it even when the value happens to match.
2. **The deploy record.** A human runs
   `sentry-cli releases deploys RELEASE new -e ENVIRONMENT` after the release
   is created and finalized, to record that this release went out to this
   environment. This is a write command; this skill recommends it and does
   not run it.

## Why the two strings must match

Record the deploy with the same environment string the SDK sends
(`production`, `staging`). Release health can `groupBy=environment`. A
missing or mismatched environment is not production; dashboards filtered to
production hide those events (SC06). A typo — `prod` on the deploy record
versus `production` in the SDK — splits one environment into two in every
grouped query, and neither half looks complete on its own.

## Naming consistency

Pick one string per environment and use it everywhere: SDK init, CI
environment variables, and the `-e` flag on `sentry-cli releases deploys new`.
Treat the string as case-sensitive and exact-match; `Production` and
`production` are two different environments to the API.

## What this does not do

This does not create a per-environment rate limit. It does not split quota.
Environment is a tag on events and deploys, not a resource boundary.
