---
name: sentry-enterprise-rbac
description: 'Configure enterprise role-based access control, SSO/SAML2, and SCIM

  provisioning in Sentry. Use when setting up organization hierarchy,

  team permissions, identity provider integration, API token governance,

  or audit logging for compliance.

  Trigger: "sentry rbac", "sentry permissions", "sentry team access",

  "sentry sso setup", "sentry scim", "sentry audit log".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(curl:*), Bash(python3:*), Bash(jq:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- rbac
- sso
- saml
- scim
- teams
- permissions
- audit
- enterprise
compatibility: Designed for Claude Code
---
# Sentry Enterprise RBAC

## Overview

Configure Sentry's Organization-Team-Project hierarchy, role assignments, SSO/SAML2 federation, SCIM automated provisioning, API token governance, and audit logging. Covers the full enterprise access control lifecycle from initial setup through ongoing compliance monitoring.

## Prerequisites

- **Sentry Business or Enterprise plan** — team-level roles, SSO, SCIM, and audit logs require Business tier or higher
- **Organization Owner or Manager role** — only these roles can configure auth, teams, and member roles
- **Identity Provider access** — admin credentials for Okta, Azure AD, or Google Workspace if configuring SSO/SCIM
- **Environment variables set:**

  ```bash
  export SENTRY_AUTH_TOKEN="sntrys_..."   # Auth token with org:admin, member:admin, team:admin scopes
  export SENTRY_ORG="your-org-slug"       # Organization slug from sentry.io/settings/
  ```

## Instructions

### Step 1 — Establish the Organization-Team-Project Hierarchy

Sentry's access model flows top-down: **Organization > Teams > Projects**. Members inherit permissions from their org-level role, then gain project access through team membership.

**Organization-level roles** define the ceiling of what a member can do:

| Role | Capabilities | Typical Use |
|------|-------------|-------------|
| **Owner** | Full control: billing, auth, members, all settings. Irremovable. | Founding eng, CTO |
| **Manager** | Manage all teams, projects, and members. No billing access. | Engineering managers |
| **Admin** | Manage integrations, projects, teams. No member management. | Tech leads, DevOps |
| **Member** | View data, act on issues, join/leave teams. Default for new users. | Individual contributors |
| **Billing** | Payment and subscription management only. No technical access. | Finance team |

**Team-level roles** (Business/Enterprise only) add granularity within teams:

| Team Role | Additional Capabilities |
|-----------|------------------------|
| **Team Admin** | Manage team membership, add/remove projects from the team |
| **Contributor** | View and act on issues in the team's projects |

A member's effective permissions are the **union** of their org-level role and all team-level roles they hold. A Member with Team Admin on "payments-team" can manage that team but cannot touch org-wide settings.

**Create the team structure:**

```bash
# Create a team
curl -s -X POST \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slug": "backend-eng", "name": "Backend Engineering"}' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/teams/" | jq '{slug, name, dateCreated}'

# List all teams with member counts
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/teams/" \
  | jq '.[] | {slug, memberCount, hasAccess}'

# Assign a project to a team (grants team members access to that project)
curl -s -X POST \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/payment-api/teams/backend-eng/"

# Remove a team's access to a project
curl -s -X DELETE \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/payment-api/teams/backend-eng/"

# List which teams have access to a project
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/payment-api/teams/" \
  | jq '.[].slug'
```

**Manage team membership:**

```bash
# List organization members (get MEMBER_ID values)
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/members/" \
  | jq '.[] | {id, email, role, expired}'

# Add a member to a team
curl -s -X POST \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/members/$MEMBER_ID/teams/backend-eng/"

# Remove a member from a team
curl -s -X DELETE \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/members/$MEMBER_ID/teams/backend-eng/"

# Update a member's organization role
curl -s -X PUT \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/members/$MEMBER_ID/"
```

### Step 2 — Configure SSO/SAML2 and SCIM Provisioning

SSO centralizes authentication; SCIM automates the user lifecycle. Configure SSO first, then layer SCIM on top.

**SSO/SAML2 setup — Okta example:**

1. In Okta Admin Console, create a new SAML 2.0 application
2. Set the Single Sign-On URL to: `https://sentry.io/saml/acs/{org_slug}/`
3. Set the Audience URI (SP Entity ID) to: `https://sentry.io/saml/metadata/{org_slug}/`
4. Configure attribute statements:

   | Name | Value |
   |------|-------|
   | `email` | `user.email` |
   | `firstName` | `user.firstName` |
   | `lastName` | `user.lastName` |

5. Download the IdP metadata XML or copy the metadata URL

**SSO/SAML2 setup — Azure AD:**

1. In Azure Portal > Enterprise Applications, add Sentry from the gallery
2. Configure SAML SSO with Reply URL: `https://sentry.io/saml/acs/{org_slug}/`
3. Set Identifier (Entity ID): `https://sentry.io/saml/metadata/{org_slug}/`
4. Map claims: `emailaddress`, `givenname`, `surname`
5. Download the Federation Metadata XML

**SSO/SAML2 setup — Google Workspace:**

1. In Google Admin > Apps > SAML Apps, add a custom SAML app for Sentry
2. Set ACS URL: `https://sentry.io/saml/acs/{org_slug}/`
3. Set Entity ID: `https://sentry.io/saml/metadata/{org_slug}/`
4. Map `email`, `firstName`, `lastName` attributes
5. Download the IdP metadata

**Activate in Sentry:**

1. Navigate to **Organization Settings > Auth**
2. Click **Configure** next to SAML2
3. Enter the IdP metadata URL or upload the metadata XML
4. Click **Save** then **Test SSO Login** — verify it redirects and authenticates correctly
5. Enable **Require SSO** to enforce SSO for all organization members
6. Optionally set a **Default Role** for SSO-provisioned users (typically Member)

**SCIM provisioning** automates user creation, deactivation, and group sync:

```
SCIM Base URL:  https://sentry.io/api/0/organizations/{org_slug}/scim/v2/
Authentication: Bearer token (generated in Sentry's SCIM settings page)
```

```bash
# Provision a new user via SCIM
curl -s -X POST \
  -H "Authorization: Bearer $SCIM_TOKEN" \
  -H "Content-Type: application/scim+json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "engineer@company.com",
    "name": {"givenName": "Jane", "familyName": "Doe"},
    "emails": [{"primary": true, "value": "engineer@company.com", "type": "work"}],
    "active": true
  }' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/scim/v2/Users"

# List SCIM-provisioned users
curl -s -H "Authorization: Bearer $SCIM_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/scim/v2/Users?count=100" \
  | jq '.Resources[] | {id, userName, active}'

# Deactivate a user via SCIM (sets active to false)
curl -s -X PATCH \
  -H "Authorization: Bearer $SCIM_TOKEN" \
  -H "Content-Type: application/scim+json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
    "Operations": [{"op": "replace", "value": {"active": false}}]
  }' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/scim/v2/Users/$SCIM_USER_ID"

# Sync IdP groups to Sentry teams via SCIM Groups
curl -s -X POST \
  -H "Authorization: Bearer $SCIM_TOKEN" \
  -H "Content-Type: application/scim+json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
    "displayName": "backend-eng",
    "members": []
  }' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/scim/v2/Groups"
```

SCIM capabilities once connected:

- **Auto-create** users when assigned in the IdP
- **Auto-deactivate** users when removed from the IdP group
- **Sync team membership** from IdP groups to Sentry teams
- **No manual user management** — the IdP becomes the single source of truth

### Step 3 — API Token Governance and Audit Logging

**API token scopes** — always apply the principle of least privilege:

| Scope | Access Level | Typical Use Case |
|-------|-------------|------------------|
| `project:read` | Read project settings and stats | Monitoring dashboards |
| `project:write` | Update project settings | Automation scripts |
| `project:releases` | Create releases, upload source maps | CI/CD pipelines |
| `event:read` | Read error/transaction events | Alerting integrations |
| `event:write` | Update/resolve events | Automated triage bots |
| `org:read` | Read organization data | Reporting tools |
| `org:write` | Update organization settings | Admin automation |
| `member:read` | List organization members | Directory sync |
| `member:write` | Manage members and invites | Onboarding automation |
| `team:read` | List teams | Discovery scripts |
| `team:write` | Create/update/delete teams | Team provisioning |

**Create and manage API tokens:**

```bash
# Create a new auth token via API
curl -s -X POST \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": ["project:read", "project:releases", "org:read"],
    "name": "ci-cd-pipeline-prod"
  }' \
  "https://sentry.io/api/0/api-tokens/"

# List all active auth tokens
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/api-tokens/" \
  | jq '.[] | {id, name, scopes, dateCreated}'

# Delete a token by ID
curl -s -X DELETE \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/api-tokens/$TOKEN_ID/"
```

**Token hygiene best practices:**

- **CI/CD tokens:** `project:releases` + `org:read` only — the minimum for deploys
- **Monitoring tokens:** `event:read` + `project:read` — read-only for dashboards
- **Admin tokens:** Use sparingly, rotate quarterly, limit to one or two Owners
- **Naming convention:** `{purpose}-{environment}` (e.g., `ci-cd-pipeline-prod`, `grafana-monitoring-read`)

**Audit log** — track all access control changes (Business/Enterprise):

```bash
# Query the audit log
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/audit-logs/" \
  | jq '.rows[] | {dateCreated, event, actor: .actor.name, targetObject, ipAddress}'

# Filter audit logs by event type
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/audit-logs/?event=member.invite" \
  | jq '.rows[] | {dateCreated, actor: .actor.name, data}'
```

Tracked audit events include:

- `member.invite` / `member.accept` / `member.remove` / `member.edit` — membership changes
- `team.create` / `team.edit` / `team.remove` — team lifecycle
- `project.create` / `project.remove` / `project.edit` — project changes
- `org.edit` — organization setting modifications
- `sso.enable` / `sso.disable` / `sso-identity.link` — SSO configuration
- `api-token.create` / `api-token.remove` — token lifecycle
- `integration.add` / `integration.edit` / `integration.remove` — third-party integrations

**IP allowlisting** (Enterprise only):

Navigate to **Organization Settings > Security > Allowed IP Ranges** to restrict API access and dashboard logins to corporate network CIDR blocks. This is enforced at the organization level and applies to all auth tokens and browser sessions.

## Output

After completing all three steps, your Sentry organization will have:

- **Team hierarchy** established with projects assigned to specific teams
- **Organization roles** configured with least-privilege access per member
- **SSO/SAML2** federated with your identity provider, with required authentication enforced
- **SCIM provisioning** automating user creation, deactivation, and team sync from the IdP
- **API tokens** created with minimal scopes, named by purpose, with a rotation schedule
- **Audit logging** enabled and queryable for compliance reporting
- **IP allowlisting** (if Enterprise) restricting access to approved networks

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` on team/member endpoints | Auth token missing `team:admin` or `member:admin` scope | Create a new token at `sentry.io/settings/auth-tokens/` with the required scopes |
| User cannot see a project | User is not on any team that has access to that project | Add the user to a team via the Members API, then assign that team to the project |
| SSO login redirects but fails | SAML ACS URL or Audience URI mismatch between IdP and Sentry | Verify the URLs match exactly: `https://sentry.io/saml/acs/{org_slug}/` and `https://sentry.io/saml/metadata/{org_slug}/` |
| SCIM sync creates users but does not assign teams | IdP groups not mapped to SCIM Groups in Sentry | Create SCIM Groups matching your IdP group names, then push group membership from the IdP |
| `401 Unauthorized` on SCIM endpoints | Using an org auth token instead of the SCIM-specific bearer token | Use the dedicated SCIM token generated in **Organization Settings > Auth > SCIM** |
| Audit log returns empty results | Organization is on Team or Developer plan | Upgrade to Business or Enterprise plan for audit log access |
| `429 Too Many Requests` on API calls | Rate limit exceeded (org-level: 100 req/s for Business) | Implement exponential backoff; batch operations where possible |

## Examples

**Example 1 — Microservices team isolation:**

```bash
# Create teams for each domain
for team in "payments" "identity" "notifications" "platform"; do
  curl -s -X POST \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"slug\": \"$team\", \"name\": \"$(echo $team | sed 's/.*/\u&/') Team\"}" \
    "https://sentry.io/api/0/organizations/$SENTRY_ORG/teams/" | jq '.slug'
done

# Assign projects to their owning team
curl -s -X POST -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/payment-api/teams/payments/"
curl -s -X POST -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/billing-worker/teams/payments/"
curl -s -X POST -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/auth-service/teams/identity/"
```

**Example 2 — Contractor access with limited blast radius:**

```bash
# Create a contractor team with restricted access
curl -s -X POST \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slug": "contractors-q1", "name": "Q1 Contractors"}' \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/teams/"

# Give contractors access to only their assigned project
curl -s -X POST -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/mobile-redesign/teams/contractors-q1/"

# Contractor members get org-level "Member" role (minimum privilege)
# + SSO required (enforced by "Require SSO" org setting)
# + Auto-deactivation via SCIM when removed from IdP group at contract end
```

**Example 3 — Quarterly audit log review:**

```bash
# Export last 90 days of audit events for compliance review
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/audit-logs/" \
  | jq '[.rows[] | {
      date: .dateCreated,
      event: .event,
      actor: .actor.name,
      target: .targetObject,
      ip: .ipAddress
    }]' > sentry-audit-q1-2026.json

echo "Exported $(jq length sentry-audit-q1-2026.json) audit entries"
```

## Resources

- [Organization Roles & Membership](https://docs.sentry.io/organization/membership/) — role definitions and permission matrix
- [SSO & SAML2 Configuration](https://docs.sentry.io/organization/authentication/sso/) — identity provider setup guides
- SCIM Provisioning — automated user lifecycle management
- [Teams API Reference](https://docs.sentry.io/api/teams/) — create, list, update, delete teams
- [Organization Members API](https://docs.sentry.io/api/organizations/list-an-organizations-members/) — member management endpoints
- Audit Log API — query audit trail programmatically
- [Auth Tokens API](https://docs.sentry.io/api/auth/) — token creation and management
- IP Allowlisting — network-level access restriction

## Next Steps

- Set up **Sentry alerting rules** per team so each team owns their project's alerts
- Configure **integration-level permissions** (Slack, Jira, PagerDuty) scoped to specific projects
- Implement **token rotation automation** using the Auth Tokens API on a quarterly schedule
- Review the **audit log** monthly and export to your SIEM for long-term retention
- Consider **custom roles** (Enterprise only) for more granular permission sets beyond the five built-in roles
