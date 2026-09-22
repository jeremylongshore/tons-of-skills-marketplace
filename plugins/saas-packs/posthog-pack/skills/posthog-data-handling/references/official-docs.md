# Official PostHog references

Checked on 2026-09-09. PostHog changes continuously; verify these pages again before making a production change.

## Primary sources

- [Privacy controls](https://posthog.com/docs/privacy)
- [Controlling data collection](https://posthog.com/docs/privacy/data-collection)
- [GDPR guidance](https://posthog.com/docs/privacy/gdpr-compliance)

## Verification boundaries

- Select US, EU, or self-hosted domains from the target project; never infer a region.
- Public ingestion uses the project token. Private API requests require a scoped personal key, project secret key where available, or OAuth.
- Keep every secret out of browser bundles, logs, generated examples, and committed files.
- Treat billing, availability, SDK defaults, and plan entitlements as live facts and recheck them at execution time.
