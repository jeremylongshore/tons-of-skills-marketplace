# OneNote Isolated Development Loop: first-party evidence

Reviewed: 2026-09-12

Microsoft's public documentation establishes the current product and API contract. The selected app registration, account type, tenant, signed-in user, delegated scopes, user/group/site root, SDK version, and observed responses remain execution evidence for that environment.

- [Create a Microsoft Graph client](https://learn.microsoft.com/en-us/graph/sdks/create-client)
- [OneNote REST API roots](https://learn.microsoft.com/en-us/graph/api/resources/onenote-api-overview?view=graph-rest-1.0)
- [Create OneNote pages](https://learn.microsoft.com/en-us/graph/api/onenote-post-pages?view=graph-rest-1.0)
- [Update OneNote page content](https://learn.microsoft.com/en-us/graph/onenote-update-page)
- [OneNote API error codes](https://learn.microsoft.com/en-us/graph/onenote-error-codes)

## Current contract notes

- Use Microsoft Graph `v1.0` for stable production OneNote calls; beta behavior is not a production contract.
- The OneNote service overview says app-only authentication is unsupported. General permission and generated method tables can retain conflicting application rows; follow the service-specific support statement and fail closed on documentation drift.
- User, Microsoft 365 group, and SharePoint-site notebooks have distinct roots and access boundaries. Page collections are paged, and opaque `@odata.nextLink` values must be followed unchanged.
- OneNote is absent from the current supported-resource tables for Microsoft Graph change notifications and delta query. Do not invent webhook, subscription, search, or delta support for OneNote resources.
- Current service-specific limits are mutable. OneNote 429 responses do not promise `Retry-After`; bound concurrency and use capped exponential backoff with jitter when no valid server delay is present.
- OneNote accepts constrained input HTML and normalizes output HTML. Binary parts require multipart requests, and update targets must come from `data-id` or server-generated IDs returned by an `includeIDs=true` content read.
- Skill invocation never grants permission to access credentials or notebook data, request consent, broaden roots, transfer files, deploy, write, spend money, change sharing, or delete resources.

## Evidence rules

- Recheck these pages at execution time and record the app, account, tenant, delegated user, scopes, root type, SDK, source revision, and observation date.
- Treat a successful generic Graph token or request as insufficient proof of OneNote access.
- When first-party pages conflict or observed behavior differs, fail closed, preserve redacted request evidence, and resolve the discrepancy before mutation.
