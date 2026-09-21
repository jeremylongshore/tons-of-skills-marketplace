# Official Miro Sources for miro-upgrade-migration

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [REST API comparison guide](https://developers.miro.com/docs/rest-api-comparison-guide)
- [REST API reference guide](https://developers.miro.com/docs/rest-api-reference-guide)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Experimental webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)

## Workflow-specific review notes

- Inventory endpoint, SDK, schema, scope, error, pagination, and event dependencies before changing versions.
- Use pinned dependencies, contract fixtures, shadow reads, canary cohorts, and explicit rollback criteria.
- Remove dependencies on retired experimental REST webhooks rather than carrying them through an upgrade.
