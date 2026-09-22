# PostHog Skill Pack

> Verified PostHog operator workflows for event capture, flags, privacy, cost control, incident response, migrations, and safe releases (24 skills)

## What This Covers

This pack provides evidence-driven workflows for `posthog-js`, `posthog-node`, and PostHog's public and private APIs. Each skill identifies credential and region boundaries, links to official documentation checked on 2026-09-09, and requires live verification for changing facts such as pricing, entitlements, SDK defaults, and availability.

**Key PostHog concepts covered:** event capture (`posthog.capture`), user identification (`posthog.identify`), group analytics (`posthog.group`), feature flags (`getFeatureFlag`, `isFeatureEnabled`, `getAllFlags`), experiments, cohorts, session recordings, autocapture, HogQL, CDP destinations, and the current `/i/v0/e`, `/batch`, and `/flags` public endpoints.

## Installation

```bash
/plugin install posthog-pack@claude-code-plugins-plus
```

## Skills

### Getting Started (S01-S04)

| Skill | What It Does |
|-------|-------------|
| `posthog-install-auth` | Install SDKs and separate public project, private API, and secure flag credentials |
| `posthog-hello-world` | First event capture, identify, and feature flag check (Node + browser + Python + curl) |
| `posthog-local-dev-loop` | Debug mode, mocked PostHog for vitest, integration tests against dev project |
| `posthog-sdk-patterns` | Singleton client, typed events, React hooks, Next.js App Router provider, reverse proxy |

### Core Workflows (S05-S08)

| Skill | What It Does |
|-------|-------------|
| `posthog-core-workflow-a` | Event taxonomy design, `posthog.capture`, `identify`, `group`, server-side capture, annotations API |
| `posthog-core-workflow-b` | Feature flags (boolean + multivariate), `getAllFlags`, experiments, cohorts API |
| `posthog-common-errors` | Fix events not appearing, flags returning undefined, 401/429 errors, identity fragmentation |
| `posthog-debug-bundle` | Redacted diagnostics with read-only defaults and an approval-gated synthetic write probe |

### Operations (S09-S12)

| Skill | What It Does |
|-------|-------------|
| `posthog-rate-limits` | Current team-wide private endpoint budgets, backoff, queues, and export alternatives |
| `posthog-security-basics` | `phc_` vs `phx_` key security, scoped API keys, rotation procedure, git leak prevention |
| `posthog-prod-checklist` | Production SDK config, graceful degradation wrappers, health check endpoint, serverless pattern |
| `posthog-upgrade-migration` | Exact-version release-note delta, focused tests, canary, and rollback evidence |

### Pro Skills (P13-P18)

| Skill | What It Does |
|-------|-------------|
| `posthog-ci-integration` | GitHub Actions with mocked unit tests, integration tests, deployment annotations |
| `posthog-deploy-integration` | Deploy the application integration through Vercel, Fly, or Cloud Run with proxy and rollback checks |
| `posthog-webhooks-events` | CDP webhook destinations, event handler routing, Events API, HogQL queries |
| `posthog-performance-tuning` | Measured local flag evaluation, batching, sampling, and query tuning |
| `posthog-cost-tuning` | Autocapture tuning, `before_send` sampling, bot filtering, session recording sampling, billing monitoring |
| `posthog-reference-architecture` | File structure, event taxonomy, flag constants, analytics module, data pipeline integration |

### Flagship Skills (F19-F24)

| Skill | What It Does |
|-------|-------------|
| `posthog-multi-env-setup` | Separate projects per env, environment-aware SDK config, flag rollout per env |
| `posthog-observability` | Application-owned delivery signals, ingestion warnings, live limits, and status evidence |
| `posthog-incident-runbook` | Triage decision tree, immediate actions for 401/429/500, graceful degradation, evidence collection |
| `posthog-data-handling` | GDPR `sanitize_properties`, consent opt-in/opt-out, data deletion API, PII-safe exports |
| `posthog-enterprise-rbac` | Org/project hierarchy, member roles, scoped API keys, SSO/SAML, activity audit log |
| `posthog-migration-deep-dive` | Migrate from GA/Mixpanel/Amplitude, dual-write adapter, historical import, flag-controlled cutover |

## Quick Reference

| Operation | SDK Method |
|-----------|-----------|
| Capture event | `posthog.capture({ distinctId, event, properties })` |
| Identify user | `posthog.identify({ distinctId, properties })` |
| Group analytics | `posthog.group('company', 'id', { name: '...' })` |
| Check boolean flag | `posthog.isFeatureEnabled('flag-key', userId)` |
| Get multivariate flag | `posthog.getFeatureFlag('flag-key', userId)` |
| Get all flags | `posthog.getAllFlags(userId)` |
| Flush events | `await posthog.flush()` or `await posthog.shutdown()` |

## API Key Types

| Key | Prefix | Purpose | Client-safe? |
|-----|--------|---------|-------------|
| Project API Key | `phc_` | Event capture, flag evaluation | Yes |
| Personal API Key | `phx_` | Scoped private API and HogQL access | Never |
| Feature Flags Secure API Key | project-specific secret | Server-side local flag evaluation through the SDK's historical key option | Never |

## License

MIT
