# Official PostHog references

Checked on 2026-09-09. PostHog changes continuously; verify these pages again before making a production change.

## Primary sources

- [Node.js SDK](https://posthog.com/docs/libraries/node)
- [Local flag evaluation](https://posthog.com/docs/feature-flags/local-evaluation)
- [JavaScript configuration](https://posthog.com/docs/libraries/js/config)

## Verification boundaries

- Select US, EU, or self-hosted domains from the target project; never infer a region.
- Public ingestion uses the project token. Private API requests require a scoped personal key, project secret key where available, or OAuth.
- Keep every secret out of browser bundles, logs, generated examples, and committed files.
- Treat billing, availability, SDK defaults, and plan entitlements as live facts and recheck them at execution time.
