# Official PostHog references

Checked on 2026-09-09. PostHog changes continuously; verify these pages again before making a production change.

## Primary sources

- [API rate limits](https://posthog.com/docs/api)
- [Queries API](https://posthog.com/docs/api/queries)
- [Batch exports](https://posthog.com/docs/cdp/batch-exports)

## Verification boundaries

- Select US, EU, or self-hosted domains from the target project; never infer a region.
- Public ingestion uses the project token. Private API requests require a scoped personal key, project secret key where available, or OAuth.
- Keep every secret out of browser bundles, logs, generated examples, and committed files.
- Treat billing, availability, SDK defaults, and plan entitlements as live facts and recheck them at execution time.
