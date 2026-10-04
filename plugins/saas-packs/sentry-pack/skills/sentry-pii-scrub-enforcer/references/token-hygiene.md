# Token hygiene

Salvaged from cut `sentry-enterprise-rbac` as a scope list. Not an SSO/SCIM guide.

- The DSN is a public write credential. A leaked DSN means spam ingest, not a read of your issues. Rotation is a release for mobile binaries.
- `SENTRY_AUTH_TOKEN` is a secret. Never print it, never commit it, never put it in a DSN query string. Output must not contain `sntrys_` or the live token.
- Read-only work in this pack wants `project:read`, `org:read`, `event:read`. It does not use `event:admin`, `project:write`, or `member:admin`.
- An erasure the operator later sends themselves needs `event:admin` on issue delete. This skill still does not send it.
- Org auth tokens and internal integration tokens are different objects from a project DSN key. Do not "fix" a scrub review by minting a new admin token.

Prevent-IP-storage and Advanced Data Scrubbing are recommendations. This skill does not toggle them.
