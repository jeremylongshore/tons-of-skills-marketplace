# SQL and log breadcrumbs (PI05)

Backend integrations capture log breadcrumbs and database spans. A breadcrumb or span description can contain `WHERE email = 'person@x'` or a connection string that was logged.

Server scrubbing limitation: Safe Fields do not exempt a breadcrumb by category. Only breadcrumb message and data are scrubbed. Custom JSON is scrubbed by the same rules. Do not tell the user Safe Fields scope scrubbing to "query" vs "ui".

SDK-side fixes, still returning the event:

- Do not log PII.
- `beforeBreadcrumb` drops or redacts `query` breadcrumbs.
- Disable the logging-breadcrumb integration if logs are already a separate pipeline.
- Parameterize SQL so the span description is not the literal.

`beforeSend` on errors does not cover span descriptions. Use `beforeSendSpan` / `beforeSendTransaction` when those surfaces are on.

Over-scrub: do not delete every breadcrumb. Keep a non-PII request id.
