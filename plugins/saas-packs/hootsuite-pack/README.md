# Hootsuite Skill Pack

> Claude Code skill pack for Hootsuite social media management API (18 skills)

## What It Does

Gives Claude Code deep knowledge of Hootsuite's REST API v1 for social media publishing, analytics, and management. Skills cover OAuth 2.0 authentication, message scheduling with media upload, URL shortening with Ow.ly, and cross-platform post management.

## Installation

```bash
/plugin install hootsuite-pack@claude-code-plugins-plus
```

## Skills

### Standard Skills (S01-S12)

| Skill | What It Does |
|-------|-------------|
| `hootsuite-install-auth` | OAuth 2.0 authorization code flow, token exchange, refresh |
| `hootsuite-hello-world` | List profiles, schedule a post, retrieve messages |
| `hootsuite-local-dev-loop` | API client with auto token refresh, mocked tests |
| `hootsuite-sdk-patterns` | Typed client, timezone scheduling, Python client, post formatter |
| `hootsuite-core-workflow-a` | Publish posts with media: upload to S3, wait for READY, schedule |
| `hootsuite-core-workflow-b` | Analytics, Ow.ly URL shortening, message performance |
| `hootsuite-common-errors` | Fix 401/403/422/429 errors, token exchange failures |
| `hootsuite-debug-bundle` | API connectivity test, profile listing, token check |
| `hootsuite-rate-limits` | Retry-After handling, queue-based scheduling |
| `hootsuite-security-basics` | Token rotation, credential storage, OAuth app isolation |
| `hootsuite-prod-checklist` | Auth, publishing, monitoring, compliance checklist |
| `hootsuite-upgrade-migration` | API version migration, social network changes |

### Pro Skills (P13-P18)

| Skill | What It Does |
|-------|-------------|
| `hootsuite-ci-integration` | GitHub Actions with mocked tests and live API verification |
| `hootsuite-deploy-integration` | Deploy with persistent token storage (Upstash Redis or a database) |
| `hootsuite-webhooks-events` | Message status polling, custom scheduling webhooks |
| `hootsuite-performance-tuning` | Profile caching, batch scheduling, connection reuse |
| `hootsuite-cost-tuning` | Plan comparison, API call tracking, profile audit |
| `hootsuite-reference-architecture` | Full social media management architecture |

## Key Concepts

- **OAuth 2.0** — authorization code flow with token refresh (tokens expire ~1 hour)
- **API base** — `https://platform.hootsuite.com/v1/`
- **Media upload** — two-step: create upload URL, PUT to S3, wait for READY state
- **Social profiles** — each connected account (Twitter, Facebook, etc.) has a unique ID

## License

MIT
