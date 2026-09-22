# Official Attio References

Checked against the public Attio documentation on 2026-09-10. Recheck these sources before changing production credentials, scopes, limits, subscriptions, or data mappings because hosted service contracts can change.

## REST and data model

- [REST API overview](https://docs.attio.com/rest-api/overview) — base URL, request conventions, and API navigation.
- [Objects and lists](https://docs.attio.com/docs/objects-and-lists) — conceptual model for objects, records, lists, attributes, and entries.
- [List records](https://docs.attio.com/rest-api/endpoint-reference/records/list-records) — record query method, body, and pagination fields.
- [OpenAPI specification](https://docs.attio.com/rest-api/endpoint-reference/openapi) — machine-readable REST contract for diffing and type generation.

## Authentication and applications

- [Authentication](https://docs.attio.com/rest-api/guides/authentication) — Bearer and Basic transport, workspace keys, OAuth, and endpoint scopes.
- [Connect an app through OAuth](https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth) — multi-workspace authorization flow.
- [Creating an app](https://docs.attio.com/sdk/guides/creating-an-app) — Attio app setup and SDK context.
- [App SDK overview](https://docs.attio.com/sdk/deep-dives/overview) — `attio` package boundaries for apps running inside Attio.

## Reliability

- [Pagination](https://docs.attio.com/rest-api/guides/pagination) — endpoint-specific offset and cursor pagination patterns.
- [Rate limiting](https://docs.attio.com/rest-api/guides/rate-limiting) — current global request ceilings, query-score budgets, 429 responses, and `Retry-After` semantics.
- [Webhooks](https://docs.attio.com/rest-api/guides/webhooks) — signature calculation, idempotency key, timeout, retry, and delivery-rate behavior.

## Verification rule

When this reference and a current endpoint page disagree, treat the current official endpoint page as authoritative, record the discrepancy, and stop any affected production mutation until the contract is resolved.
