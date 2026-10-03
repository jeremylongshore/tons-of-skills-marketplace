# Relay boundary (PI07)

Parent reference. Not an agent. Not a nested checklist. Do not invent `sentry-relay-ops`.

Three layers, in the order that matters:

1. SDK hooks so data is not sent. Requires a redeploy. This is the boundary Sentry's SDK docs recommend.
2. Server-side scrubbing in the UI. Immediate for **new** events. The data was already transmitted. Default-on. Only a documented subset of fields unless Advanced Data Scrubbing rules are added. Backstop, not the boundary.
3. A Relay you run. Rules can change without an app deploy, and the client sends to your Relay instead of straight to Sentry. This is the layer that matches "no redeploy" plus "raw PII should not transit to the processor."

Relay is another component. A misconfigured Relay is a silent drop (operators think Sentry is down). That diagnosis belongs to `sentry-event-forensics`, not a new agent here.

Recommend Relay only when policy forbids unscrubbed transit or a hotfix deploy is weeks away (mobile store). Keep SDK hooks anyway so a DSN pointed "temporarily" at Sentry is still scrubbed.

Self-hosted Sentry (Kafka, ClickHouse, Symbolicator) is out of scope. If the user says self-hosted, stop.

Do not claim Relay rewrites events already stored.
