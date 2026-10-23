---
name: supabase-enterprise-rbac
description: |
  Implement custom role-based access control via JWT claims in Supabase:
  app_metadata.role, RLS policies with auth.jwt() role extraction,
  organization-scoped access, and API key scoping.
  Use when implementing role-based permissions, configuring organization-level
  access, building admin/member/viewer hierarchies, or scoping API keys per role.
  Trigger with "supabase RBAC", "supabase roles", "supabase permissions",
  "supabase JWT claims", "supabase organization access", "supabase custom roles",
  "supabase app_metadata".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(supabase:*), Bash(psql:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- rbac
- security
- enterprise
- roles
- permissions
compatibility: Designed for Claude Code
---
# Supabase Enterprise RBAC

## Overview

Supabase supports custom role-based access control (RBAC) by storing role information in `app_metadata` on the user's JWT, then reading those claims in RLS policies via `auth.jwt() ->> 'role'`. This skill implements a complete RBAC system: roles in `app_metadata`, RLS policies that enforce role hierarchies, organization-scoped access, role management through the Admin API, and API endpoints protected with role checks — all using real `createClient` from `@supabase/supabase-js`.

**When to use:** Building multi-role applications (admin/editor/viewer), implementing organization-scoped access, creating custom permission systems beyond Supabase's built-in `anon`/`authenticated` roles, or scoping API operations by user role.

## Prerequisites

- `@supabase/supabase-js` v2+ with service role key for admin operations
- Understanding of JWT claims and Supabase's `auth.jwt()` SQL function
- Database access via SQL Editor or `psql` for RLS policy creation
- Supabase project with authentication configured

## Instructions

The workflow has three steps: assign roles into the JWT, enforce them in the database with RLS, then enforce them again in application code.

### Step 1: Define Roles via app_metadata and JWT Claims

Store custom roles in the user's `app_metadata` using the Admin API. These claims appear in every JWT the user receives and are readable in RLS policies. Assign roles with the service-role client:

```typescript
// Define the role hierarchy
type AppRole = 'admin' | 'editor' | 'viewer' | 'member';

// Assign a role to a user (admin operation, service role key required)
async function setUserRole(userId: string, role: AppRole, orgId: string) {
  const { data, error } = await supabase.auth.admin.updateUserById(userId, {
    app_metadata: { role, org_id: orgId },
  });
  if (error) throw new Error(`Failed to set role: ${error.message}`);
  return data.user;
}
```

Read the role back in app code with `supabase.auth.getUser()` and compare it against a numeric hierarchy so `hasRole('editor', 'viewer')` is true. See [role assignment and JWT extraction](references/role-assignment.md) for the full service-role client setup, granular permissions, bulk `assignTeamRoles()`, `getCurrentUserRole()`, `getCurrentOrg()`, `hasRole()`, and the `requireRole()` guard.

### Step 2: RLS Policies with JWT Role Claims

Write Row Level Security policies that read `auth.jwt() -> 'app_metadata' ->> 'role'` and `... ->> 'org_id'`. Wrap the JWT extraction in helper functions so every policy stays readable:

```sql
CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS text AS $$
  SELECT coalesce(auth.jwt() -> 'app_metadata' ->> 'role', 'viewer');
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE POLICY "editors_create_projects" ON public.projects
  FOR INSERT WITH CHECK (
    org_id = get_user_org_id()
    AND get_user_role() IN ('admin', 'editor')
  );
```

Policies pair an `org_id = get_user_org_id()` tenant check with a `get_user_role()` role check per operation (SELECT/INSERT/UPDATE/DELETE). See [RLS policies and org-scoped schema](references/rls-policies.md) for both helper functions, the full policy set across projects/documents/team_members, and the `organizations`/`team_members`/`projects` table schema with indexes.

### Step 3: API Key Scoping and Role Enforcement in Application Code

Enforce roles a second time at the application layer so API routes never rely on RLS alone. See [API key scoping and role enforcement](references/api-scoping-and-enforcement.md) for server-side `withRole()` middleware, per-request client creation, admin panel operations (list members, invite users, change roles), and organization management patterns.

## Output

Completing this skill produces:

- **Role assignment via app_metadata** — `admin.updateUserById()` sets role claims on user JWTs
- **JWT claim extraction** — `get_user_role()` and `get_user_org_id()` SQL helper functions
- **Role-based RLS policies** — SELECT/INSERT/UPDATE/DELETE scoped by role hierarchy (admin > editor > member > viewer)
- **Organization-scoped access** — multi-tenant isolation via `org_id` in JWT claims and RLS policies
- **Application-layer enforcement** — `withRole()` middleware for API routes with proper 401/403 responses
- **Admin panel operations** — list members, invite users, change roles with both database and JWT updates
- **Role hierarchy checking** — `hasRole()` function supporting role escalation comparison

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `app_metadata.role` is null in JWT | Role not set or user needs to re-login | Call `admin.updateUserById()` to set role; user must refresh their session |
| RLS policy returns empty results | JWT claims don't match policy conditions | Check `auth.jwt()` output in SQL Editor; verify `app_metadata` was set correctly |
| `permission denied for function` | Helper function not created or wrong schema | Create `get_user_role()` in the `public` schema with `SECURITY DEFINER` |
| User role changes not reflected | JWT cached with old claims | User must sign out and sign in again, or call `supabase.auth.refreshSession()` |
| `duplicate key value violates unique constraint` | User already in organization | Check `team_members` table for existing entry before inserting |
| `foreign key violation` on team_members | User or org doesn't exist | Verify both `user_id` and `org_id` exist before inserting membership |
| Role hierarchy bypass | Direct database access with service role | Service role bypasses RLS by design — restrict its use to server-side admin operations only |

## Examples

**Example 1 — Quick role check in a component:**

```typescript
async function canEditProject(): Promise<boolean> {
  const { data: { user } } = await supabase.auth.getUser();
  const role = user?.app_metadata?.role;
  return role === 'admin' || role === 'editor';
}
```

**Example 2 — Verify RLS policies work correctly:**

```sql
-- Test as an editor in org-123
SET request.jwt.claims = '{"sub": "user-uuid", "role": "authenticated", "app_metadata": {"role": "editor", "org_id": "org-123"}}';

SELECT * FROM projects;                                                    -- returns only org-123 rows
INSERT INTO projects (org_id, name, created_by) VALUES ('org-123', 'Test', 'user-uuid');  -- succeeds
DELETE FROM projects WHERE id = 'some-project-id';                          -- fails (editors cannot delete)

RESET request.jwt.claims;
```

For the full onboarding example (`onboardOrganization()` — create org, assign creator as admin, seed `team_members`), see [role assignment reference](references/role-assignment.md) and [API scoping reference](references/api-scoping-and-enforcement.md).

## Resources

- [Custom Claims and RBAC — Supabase Docs](https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac)
- [Auth Admin updateUserById — Supabase Docs](https://supabase.com/docs/reference/javascript/auth-admin-updateuserbyid)
- [Row Level Security — Supabase Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [auth.jwt() Function — Supabase Docs](https://supabase.com/docs/guides/database/postgres/row-level-security#helper-functions)
- [Multi-tenancy Patterns — Supabase Docs](https://supabase.com/docs/guides/getting-started/architecture#multi-tenancy)
- [inviteUserByEmail — Supabase Docs](https://supabase.com/docs/reference/javascript/auth-admin-inviteuserbyemail)

## Next Steps

- For database migration patterns, see `supabase-migration-deep-dive`
- For security hardening and API key scoping, see `supabase-security-basics`
- For data handling and GDPR compliance, see `supabase-data-handling`
