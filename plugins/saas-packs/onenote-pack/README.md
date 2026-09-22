# OneNote Operator Pack

> 18 evidence-first workflows for the Microsoft Graph OneNote API.

This pack covers delegated authentication, user/group/site content roots, complete hierarchy reads, controlled page creation and updates, throttling, polling reconciliation, security, delivery, and migration. Every workflow defaults to inspection and planning; live Microsoft Graph access, consent, content reads, writes, sharing changes, deployment, file transfer, spend, and deletion require explicit approval.

## Installation

```bash
/plugin install onenote-pack@claude-code-plugins-plus
```

## Skills

| Skill | Operator workflow |
| --- | --- |
| `onenote-ci-integration` | Separate deterministic pull-request checks from trusted delegated sandbox tests |
| `onenote-common-errors` | Classify Graph and OneNote failures from redacted evidence |
| `onenote-core-workflow-a` | Inventory user, group, or site hierarchies with complete pagination |
| `onenote-core-workflow-b` | Create or update constrained HTML with preview and read-back |
| `onenote-cost-tuning` | Measure application waste without inventing OneNote pricing |
| `onenote-debug-bundle` | Produce a content-safe diagnostic and custody package |
| `onenote-deploy-integration` | Deploy with delegated-session lifecycle, canaries, and rollback |
| `onenote-hello-world` | Prove one least-privilege read and one denied boundary |
| `onenote-install-auth` | Establish current delegated authentication and consent controls |
| `onenote-local-dev-loop` | Develop with synthetic fixtures and an isolated delegated sandbox |
| `onenote-performance-tuning` | Tune selected fields, expansion, section reads, paging, and batching |
| `onenote-prod-checklist` | Issue an evidence-backed production readiness decision |
| `onenote-rate-limits` | Bound concurrency and recover from 429 without assuming Retry-After |
| `onenote-reference-architecture` | Design user-bound multi-location access and reconciliation |
| `onenote-sdk-patterns` | Build a versioned, typed, testable OneNote client boundary |
| `onenote-security-basics` | Harden consent, token caches, content, logs, and tenant isolation |
| `onenote-upgrade-migration` | Remove app-only, undocumented delta, search, and webhook assumptions |
| `onenote-webhooks-events` | Replace unsupported events with bounded polling and reconciliation |

Each skill includes `references/official-docs.md`, reviewed on 2026-09-12, with five first-party Microsoft sources and execution-time revalidation rules. The pack preserves all public skill identities while replacing stale tutorial behavior with distinct operator contracts.

## Current contract boundary

- Use Microsoft Graph `v1.0` for stable production OneNote calls.
- The OneNote service-specific documentation says app-only authentication is unsupported; use delegated user context and fail closed when generic permission tables conflict.
- User, Microsoft 365 group, and SharePoint-site notebooks use different roots.
- OneNote is absent from the current supported-resource lists for Graph change notifications and delta query. Change monitoring uses documented page metadata reads plus reconciliation.
- OneNote page lists are paged; broad reads require every opaque `@odata.nextLink`, and section-scoped enumeration is the recommended complete-read pattern.
- OneNote 429 responses do not promise a `Retry-After` header. Bound concurrency and apply capped exponential backoff with jitter when no valid server delay is present.
- Input and output HTML are not byte-identical. Preview intended semantics and verify normalized read-back.

## License

MIT
