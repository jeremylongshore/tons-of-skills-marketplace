# BambooHR Official Evidence Register

Evidence reviewed: 2026-09-11.

## Authority boundary

This skill is grounded in BambooHR's public SDK repositories and generated
OpenAPI documentation. Customer-specific permissions, enabled products, and
executed agreements remain authoritative for a particular tenant.

## Reviewed source state

- Python SDK repository: commit `9dfad95472650b7d84c42e444c7d4844e50bafe4`,
  authored on BambooHR's default branch as of the review date.
- PHP SDK repository: commit `ef5bed5a596535fdf8a1090839a2507940fd7339`,
  authored on BambooHR's default branch as of the review date.
- The Python source declares version 1.0.0 and documents `bamboohr-sdk`, but
  public PyPI returned no matching distribution and the repository exposed no
  tag or GitHub release during review. Reverify before installation.
- Packagist exposed `bamboohr/api` 2.0.1. Default-branch changes after that tag
  are not part of 2.0.1 unless their referenced commit is contained in the tag.

## Contract facts used by this pack

- OAuth authorization-code flow is recommended for partner integrations; API
  keys remain available for internal tools and prototypes.
- Tenant requests use `https://{company-subdomain}.bamboohr.com`.
- OAuth tokens refreshed by the SDK must be persisted by the application.
- The Python SDK documents automatic retry for 408, 429, 504, and 598, with
  zero through five retries and default one.
- Dataset v1 data and legacy report operations have deprecation notices; the
  current OpenAPI documents dataset v2 for new data queries.
- Webhook creation returns a `privateKey` only once for HMAC-SHA256. The
  receiver's exact signature carrier and canonical input must come from current
  BambooHR webhook documentation or an authorized observed contract.
- No universal numeric API quota or per-request price is asserted by this pack.

## Primary sources

- [Official Python SDK](https://github.com/BambooHR/bhr-api-python)
- [Python authentication guide](https://github.com/BambooHR/bhr-api-python/blob/main/AUTHENTICATION.md)
- [Python getting started](https://github.com/BambooHR/bhr-api-python/blob/main/GETTING_STARTED.md)
- [Python changelog](https://github.com/BambooHR/bhr-api-python/blob/main/CHANGELOG.md)
- [Official public OpenAPI](https://github.com/BambooHR/bhr-api-python/blob/main/specs/public.yaml)
- [Generated Employees API](https://github.com/BambooHR/bhr-api-python/blob/main/docs/EmployeesApi.md)
- [Generated Datasets API](https://github.com/BambooHR/bhr-api-python/blob/main/docs/DatasetsApi.md)
- [Generated Reports API](https://github.com/BambooHR/bhr-api-python/blob/main/docs/ReportsApi.md)
- [Generated Webhooks API](https://github.com/BambooHR/bhr-api-python/blob/main/docs/WebhooksApi.md)
- [Generated webhook delivery contract](https://github.com/BambooHR/bhr-api-python/blob/main/docs/WebhookEventsApi.md)
- [Official PHP SDK](https://github.com/BambooHR/bhr-api-php)
- [Packagist package](https://packagist.org/packages/bamboohr/api)
- [BambooHR developer documentation](https://documentation.bamboohr.com/)

## Review rule

Re-open the operation-specific OpenAPI section and registry entry before an
implementation or migration. Record the exact source commit, package version,
tenant permission assumptions, and any customer-contract authority used.
