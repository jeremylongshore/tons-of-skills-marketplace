---
name: posthog-enterprise-rbac
description: |
  Govern PostHog organization access with verified domains, SSO or SAML, SCIM, project roles, scoped keys, and audit evidence. Use when designing or reviewing enterprise access controls. Trigger with "PostHog SSO", "PostHog RBAC", or "PostHog SCIM".
argument-hint: "[organization] [access-change]"
allowed-tools: Read, Write, Edit
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- rbac
compatibility: Designed for Claude Code
---
# PostHog Enterprise RBAC

## Overview

PostHog access control uses a three-level hierarchy: Organization > Project > Resource. Organizations contain multiple projects (e.g., production, staging), and each project has its own data, feature flags, and dashboards. Members are assigned roles at the organization level and can be restricted to specific projects.

## Prerequisites

- PostHog Cloud organization with the required RBAC, SSO, and audit-log entitlements confirmed from the live plan
- Organization admin role
- Multiple projects configured (one per environment)

## Access Control Model

| Level | Scope | Controls |
|-------|-------|----------|
| Organization | All projects | Member management, billing, SSO enforcement |
| Project | Single project | Feature flags, insights, dashboards, session recordings |
| API Key | Scoped operations | Personal API key with specific scopes |

**Member Roles:**

| Role | Level | Permissions |
|------|-------|------------|
| Owner | 15 | Full admin, billing, delete org |
| Admin | 8 | Manage members, all project settings |
| Member | 1 | View/create insights, flags, recordings |

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.


### Step 1: Set Up Project-Level Access

```bash
set -euo pipefail
# Create a production project with access control
curl -X POST "https://us.posthog.com/api/organizations/$ORG_ID/projects/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production", "access_control": true}'

# Add a member to a specific project (level 1 = Member, 8 = Admin)
curl -X POST "https://us.posthog.com/api/projects/$PROD_PROJECT_ID/members/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_UUID", "level": 1}'

# List current project members
curl "https://us.posthog.com/api/projects/$PROD_PROJECT_ID/members/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.results[] | {email: .user.email, level, joined_at}'
```

### Step 2: Create Scoped API Keys

```bash
set -euo pipefail
# Read-only key for BI dashboard integration
curl -X POST "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "bi-dashboard-readonly",
    "scopes": ["insight:read", "dashboard:read", "query:read"]
  }'

# Feature flag service key (read + write flags only)
curl -X POST "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "flag-service",
    "scopes": ["feature_flag:read", "feature_flag:write"]
  }'

# Event export key (read events only)
curl -X POST "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "data-export-readonly",
    "scopes": ["event:read", "query:read"]
  }'

# List all personal API keys
curl "https://us.posthog.com/api/personal_api_keys/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.[] | {id, label, scopes, created_at}'
```

### Step 3: Configure SSO (Enterprise)

PostHog enterprise supports SAML 2.0 SSO. Configuration is in Organization Settings > Authentication:

1. **Enable SAML**: Add your IdP metadata URL (e.g., Okta, Azure AD, Google Workspace)
2. **Enforce SSO**: Toggle "Enforce SSO" to require all members to authenticate via IdP
3. **Auto-provisioning**: New IdP users are automatically created in PostHog with Member role
4. **Group mapping**: Map IdP groups to PostHog organization roles

```bash
set -euo pipefail
# Check SSO configuration status
curl "https://us.posthog.com/api/organizations/$ORG_ID/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '{
    enforce_sso: .enforce_sso,
    saml_configured: (.saml_enforcement != null),
    member_count: .membership_count
  }'
```

### Step 4: Audit Access and Changes

```bash
set -euo pipefail
# View recent activity log for permission changes
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/activity_log/?scope=Organization" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '[.results[] | select(.activity | contains("member") or contains("role") or contains("api_key")) | {
    user: .user.email,
    activity,
    detail: .detail,
    created_at
  }] | .[:10]'

# View feature flag changes (who changed what)
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/activity_log/?scope=FeatureFlag" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '[.results[:10][] | {
    user: .user.email,
    activity,
    item_id: .item_id,
    created_at
  }]'
```

### Step 5: Access Matrix

```yaml
# Recommended access matrix
access_matrix:
  engineering:
    staging_project:
      role: admin           # Full control in staging
      can_create_flags: true
      can_delete_flags: true
    production_project:
      role: member           # Read + create, no delete in prod
      can_create_flags: true
      can_delete_flags: false  # Require admin approval for flag deletion

  product:
    staging_project:
      role: member
      can_view_recordings: true
      can_create_insights: true
    production_project:
      role: member
      can_view_recordings: true
      can_create_insights: true

  bi_service_account:
    production_project:
      api_key_scopes: [insight:read, dashboard:read, query:read]
      # No write access

  flag_service_account:
    production_project:
      api_key_scopes: [feature_flag:read, feature_flag:write]
      # Only flag operations
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| 403 on feature flag endpoint | Key missing required scope | Create key with `feature_flag:read` scope |
| Member sees prod data | Project access not restricted | Remove from prod project, add to staging only |
| SSO bypass possible | SSO not enforced | Enable "Enforce SSO" in org settings |
| Can't create scoped key | Not org admin | Only admins can create API keys |
| Activity log gaps | Plan entitlement or retention window mismatch | Confirm the live entitlement and export required evidence before it ages out |

## Output

- Project-level member access configured
- Scoped API keys for services (BI, flag service, export)
- SSO/SAML enforcement enabled
- Activity audit log queries
- Access matrix documented

## Examples

For onboarding a production analytics team, verify the authentication domain, map identity-provider groups to least-privilege roles, test join and removal paths, and capture audit evidence. Recheck plan availability before promising JIT, SAML, SCIM, or advanced roles.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog API Overview](https://posthog.com/docs/api)
- [PostHog Projects API](https://posthog.com/docs/api/projects)
- [PostHog Members API](https://posthog.com/docs/api/members)

## Next Steps

For migration strategies, see `posthog-migration-deep-dive`.
