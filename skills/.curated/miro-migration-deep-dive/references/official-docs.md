# Official Miro Sources for miro-migration-deep-dive

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API comparison guide](https://developers.miro.com/docs/rest-api-comparison-guide)
- [REST API reference guide](https://developers.miro.com/docs/rest-api-reference-guide)
- [REST API introduction](https://developers.miro.com/reference/overview)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)

## Workflow-specific review notes

- Map each v1 widget and relationship to an explicit v2 item-type contract; do not assume a polymorphic replacement.
- Shadow-read and compare normalized results before enabling v2 writes for a cohort.
- Keep rollback possible until content, relationships, pagination, and error semantics reconcile.
