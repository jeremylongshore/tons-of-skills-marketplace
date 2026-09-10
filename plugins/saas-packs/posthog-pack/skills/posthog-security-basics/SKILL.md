---
name: posthog-security-basics
description: |
  Secure PostHog tokens, hosts, proxy routes, captured properties, and private-API scopes across browser and server boundaries. Use when reviewing secrets or hardening an integration. Trigger with "PostHog security", "PostHog secret scan", or "PostHog API key review".
argument-hint: "[project-path] [security-scope]"
allowed-tools: Read, Write, Grep
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- api
- security
- audit
compatibility: Designed for Claude Code
---
# PostHog Security Basics

## Overview

Secure PostHog API key management, least-privilege access, and secret rotation. PostHog has two key types with very different security profiles: the Project API Key (`phc_...`) is intentionally public and safe to include in frontend bundles, while the Personal API Key (`phx_...`) grants admin access and must never be exposed.

## Prerequisites

- PostHog account with admin access
- Understanding of environment variable management
- `.gitignore` configured

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries. Use `Write` only for a new, explicitly requested artifact inside the target project.

### Step 1: Understand Key Security Profiles

| Key Type | Prefix | Exposure Risk | Capabilities |
|----------|--------|--------------|-------------|
| Project API Key | `phc_` | **Low** (designed to be public) | Capture events, evaluate flags, identify users |
| Personal API Key | `phx_` | **Critical** (full admin access) | CRUD flags, read persons, query insights, delete data |

```bash
# .env (NEVER commit)
NEXT_PUBLIC_POSTHOG_KEY=phc_abc123   # Safe for frontend (NEXT_PUBLIC_ prefix)
POSTHOG_PERSONAL_API_KEY=phx_xyz789  # Server-only — NEVER in frontend code
POSTHOG_PROJECT_ID=12345

# .gitignore
.env
.env.local
.env.*.local
```

### Step 2: Create Scoped Personal API Keys

```bash
set -euo pipefail
# Create a read-only key for BI dashboards
curl -X POST "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "bi-dashboard-readonly",
    "scopes": ["insight:read", "dashboard:read", "query:read"]
  }'

# Create a key scoped to feature flags only
curl -X POST "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "feature-flag-service",
    "scopes": ["feature_flag:read", "feature_flag:write"]
  }'
```

### Step 3: Rotate Personal API Keys

```bash
set -euo pipefail
# 1. Create new key in PostHog Settings > Personal API Keys
# 2. Update secret in your deployment platform
# Vercel:
vercel env rm POSTHOG_PERSONAL_API_KEY production
vercel env add POSTHOG_PERSONAL_API_KEY production

# GitHub Actions:
gh secret set POSTHOG_PERSONAL_API_KEY --body "phx_new_key_here"

# 3. Verify new key works
curl -s "https://us.posthog.com/api/projects/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | jq '.[0].name'

# 4. Delete old key in PostHog dashboard
```

### Step 4: Prevent Key Leaks

```bash
# Git pre-commit hook to catch PostHog personal keys
# .git/hooks/pre-commit (or use husky)
#!/bin/bash
if git diff --cached --diff-filter=ACM | grep -qE 'phx_[a-zA-Z0-9]{20,}'; then
  echo "ERROR: PostHog personal API key (phx_) detected in staged files!"
  echo "Remove it and use environment variables instead."
  exit 1
fi
```

```yaml
# .github/secret-scanning.yml (or use GitHub's built-in secret scanning)
patterns:
  - name: PostHog Personal API Key
    regex: 'phx_[a-zA-Z0-9]{20,}'
    severity: critical
```

### Step 5: Server-Side Key Isolation

```typescript
// lib/posthog-server.ts — Personal key never leaves the server
import { PostHog } from 'posthog-node';

const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  host: 'https://us.i.posthog.com',
  // The SDK option keeps its historical name; provide the server-only secure flag key.
  personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
});

// API routes that proxy admin operations
// Never expose the personal key to the client
export async function getFeatureFlagsForUser(userId: string) {
  return posthog.getAllFlags(userId);
}
```

### Step 6: Audit API Key Usage

```bash
set -euo pipefail
# Check activity log for API key operations
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/activity_log/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '[.results[] | select(.scope == "PersonalAPIKey") | {
    user: .user.email,
    activity: .activity,
    created_at
  }]'
```

## Security Checklist

- [ ] Project key (`phc_`) used for all frontend/capture code
- [ ] Personal key (`phx_`) only on server, never in frontend bundles
- [ ] `.env` files in `.gitignore`
- [ ] Separate keys per environment (dev/staging/prod)
- [ ] Scoped personal keys (not full admin for every service)
- [ ] Git pre-commit hook scanning for `phx_` keys
- [ ] Key rotation documented and scheduled (quarterly)

## Error Handling

| Issue | Detection | Fix |
|-------|-----------|-----|
| Personal key in git history | GitHub secret scanning alert | Rotate key immediately, revoke old one |
| Wrong key type | 401 on admin API | Use `phx_` for admin, `phc_` for capture |
| Overprivileged key | Audit log shows unexpected operations | Create scoped key, revoke broad one |
| Key exposed in logs | Log scrubbing finds `phx_` | Redact logs, rotate key |

## Output

- Environment-specific API key configuration
- Scoped personal API keys for least privilege
- Key rotation procedure
- Git pre-commit hook for leak prevention
- Audit log queries for key usage monitoring

## Examples

For a leaked personal API key, revoke it in PostHog, search history and deployment logs for exposure, issue a least-privilege replacement, rotate affected integrations, and verify audit evidence. Do not treat the public project token as a secret, but still constrain where it can send data.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog API Overview](https://posthog.com/docs/api)
- [PostHog Privacy & Security](https://posthog.com/docs/privacy)

## Next Steps

For production deployment, see `posthog-prod-checklist`.
