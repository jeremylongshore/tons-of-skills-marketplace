---
name: clade-enterprise-rbac
description: 'Manage Anthropic workspaces, API keys, team access, and spending limits

  Use when working with enterprise-rbac patterns.

  for enterprise Claude deployments.

  Trigger with "anthropic workspace", "anthropic team management",

  "claude enterprise", "anthropic api key management".

  '
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- enterprise
- rbac
compatibility: Designed for Claude Code
---
# Anthropic Enterprise & Access Management

## Overview

Anthropic uses **Organizations** and **Workspaces** for access control. API keys are scoped to workspaces.

## Organization Structure

```
Organization (your-company)
├── Workspace: Production
│   ├── API Key: prod-backend (Tier 4)
│   └── API Key: prod-frontend-proxy (Tier 2)
├── Workspace: Staging
│   └── API Key: staging-all (Tier 2)
└── Workspace: Development
    └── API Key: dev-team (Tier 1)
```

## API Key Best Practices

| Practice | Why |
|----------|-----|
| One key per service/environment | Isolate blast radius |
| Name keys descriptively | `prod-recommendation-service` not `key-1` |
| Set spending limits per key | Prevent runaway costs from bugs |
| Rotate quarterly | Reduce exposure window |
| Never share dev and prod keys | Different rate limit tiers |

## Spending Limits

Set in Anthropic Console → Settings → Limits:

- **Monthly spend limit**: Hard cap on total spend
- **Per-key limits**: Not yet available — use separate workspaces

## Access Control Checklist

- [ ] Separate workspaces for dev/staging/prod
- [ ] Separate API keys per service
- [ ] Spending alerts configured
- [ ] Key rotation schedule (90 days)
- [ ] Offboarding process: revoke keys when team members leave
- [ ] Audit log review (Console → Logs)

## Output

- Separate workspaces for production, staging, and development
- Dedicated API keys per service/environment with descriptive names
- Spending limits and alerts configured
- Key rotation schedule established (90-day cycle)
- Access control checklist completed

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See Organization Structure diagram, API Key Best Practices table, and Access Control Checklist above.

## Resources

- [Console Dashboard](https://console.anthropic.com)
- [Organization Settings](https://console.anthropic.com/settings)
- [Enterprise Plans](https://www.anthropic.com/enterprise)

## Next Steps

See `clade-migration-deep-dive` for migrating from other LLM providers.

## Prerequisites

- Anthropic Organization account at [console.anthropic.com](https://console.anthropic.com)
- Admin access to create workspaces and API keys
- Understanding of environment isolation requirements

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
