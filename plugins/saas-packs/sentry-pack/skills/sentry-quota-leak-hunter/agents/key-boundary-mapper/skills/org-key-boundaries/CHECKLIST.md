# org-key-boundaries

**Owner:** `sentry-quota-leak-hunter` → `key-boundary-mapper`
Spawn **once per question**, not once per environment.

## Table

| Object | Isolates | Does not isolate |
|---|---|---|
| Org | Quota, plan gates, billing owners | Project filters, one team's alerts |
| Project | Issue stream, inbound filters, grouping, alerts, allowed domains | A private quota silo. Filters do not inherit to the next project (SC03). |
| Key / DSN | Rate limit and rotation. A write credential. | Environment. Who is paged. A read of your issues. |
| Environment | Query filter and sessions `groupBy` | Quota. Rate limit. There is **no** per-environment rate limit (Help Center 2026-07-28, SC01). |
| Team | Membership: who can own the project | An alert rule. A DSN. (SC04) |
| Alert rule | When to page | Team membership. A DSN. (SC04) |

## Refusals

- "Set environment = production on the rate limit screen." Refuse. Second DSN (or a second project if settings and alerts must differ). Extra **keys** beat extra **projects** when the only need is a ceiling.
- New org, because mobile needs a DSN. Almost never. A new org splits quota and duplicates SSO, scrubbing, and the GitHub integration.
- One project per preview environment, if each copy needs the same filters. One non-prod project plus the environment tag, unless you needed a separate key ceiling.

## Plan gates (SC07)

Label Business/Enterprise: key rate limits, release filters, error-message filters, Delete & Discard.
Spike protection: plan label **blank**.
If the customer's plan is unknown, say unknown. Do not tell a Team plan to click a Business-only control. On lower plans the immediate tools are the free filter toggles, a named `beforeSend` on the next deploy, and a quota change an Owner actually has permission to make.

## Drift

If the pain is "twenty projects do not match the template," Read the labeled
`references/config-drift/` copy. Owner: PII `config-drift-auditor`. Do not
re-implement `settings-diff.py`. Do not restate `tracesSampler` order in that copy.

## Wrong-project maps

SC05 is `sentry-release-medic` / `sourcemap-uploader`, not this table.
