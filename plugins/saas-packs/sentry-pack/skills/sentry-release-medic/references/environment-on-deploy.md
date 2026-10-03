# Environment on the deploy

Salvaged from Cut skill `sentry-multi-env-setup`. Not the DSN-per-env essay. That boundary is quota `org-key-boundaries`.

Record the deploy with the same environment string the SDK sends (`production`, `staging`). Release health can `groupBy=environment`. A missing environment is not production; dashboards filtered to production hide those events (SC06).

This does not create a per-environment rate limit. It does not split quota.
