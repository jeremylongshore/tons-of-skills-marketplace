# Adobe Measured Performance Tuning: first-party evidence

Reviewed: 2026-09-12

Adobe's public documentation establishes the current service contract. The selected organization, project, workspace, credential, entitlement, product profiles, API/model version, SDK lock, storage, account contract, and observed responses remain execution evidence for that environment.

- [Firefly asynchronous APIs](https://developer.adobe.com/firefly-services/docs/firefly-api/guides/how-tos/using-async-apis)
- [Firefly technical usage notes](https://developer.adobe.com/firefly-services/docs/firefly-api/getting-started/usage-notes/)
- [PDF Services limits](https://developer.adobe.com/document-services/docs/overview/limits)
- [App Builder application logging](https://developer.adobe.com/app-builder/docs/guides/app_builder_guides/application_logging/logging)
- [Adobe service status](https://status.adobe.com/)

## Current contract notes

- OAuth Server-to-Server is for application- or organization-owned data. User Authentication is for user-owned data with explicit authorization-code consent. Service Account JWT is deprecated and must not be introduced or retained as fallback.
- Product availability and access depend on license, organization, role, scopes, and product-profile assignment. Token acquisition alone does not prove entitlement.
- Firefly async operations return job, status, and cancellation information. Follow returned URLs with bounded polling; recheck model/API versions and supported storage domains.
- Photoshop v1 reached end of life on 2026-07-31. New work uses current v2 contracts; `/sensei/cutout` is obsolete. The Firefly Services Lightroom API also reached end of life on 2026-07-31 and is not interchangeable with other Lightroom APIs.
- PDF Services supports async asset/job lifecycles and approved signed external storage. Signed URLs are bearer capabilities. Delete Adobe-hosted assets promptly when approved and no longer needed; verify current operation limits and pricing at execution.
- Adobe I/O Events delivery is at least once and can duplicate or arrive out of order. Validate recipient and signature/key origin or use approved mTLS, enqueue idempotently, and operate within current retry/journal windows.
- AIO CLI v11 and later deploy App Builder through Adobe IMS login or OAuth Server-to-Server in CI, not Runtime namespace auth. Workspaces are isolated; `.env` and `.aio` are not source artifacts.
- Skill invocation never grants permission to access secrets or content, request consent, broaden profiles, upload, generate, spend, deploy, alter registrations, replay, cancel, rotate/delete credentials, or delete assets.

## Evidence rules

- Recheck linked first-party pages at execution and record source revision/date plus environment-specific identities and versions.
- Prefer returned headers, URLs, states, request IDs, account contract, and observed behavior over remembered constants.
- When first-party pages conflict or observed behavior differs, fail closed, preserve redacted evidence, and resolve the discrepancy before a side effect.
