---
name: clerk-enterprise-rbac
description: 'Configure enterprise SSO, role-based access control, and organization
  management.

  Use when implementing SSO integration, configuring role-based permissions,

  or setting up organization-level controls.

  Trigger with phrases like "clerk SSO", "clerk RBAC",

  "clerk enterprise", "clerk roles", "clerk permissions", "clerk organizations".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- rbac
- enterprise
- organizations
compatibility: Designed for Claude Code
---
# Clerk Enterprise RBAC

## Overview

Implement enterprise-grade role-based access control, organization management, and SSO with Clerk. Covers custom roles and permissions, organization lifecycle, multi-tenant access patterns, SAML/OIDC SSO, and the Backend API for programmatic role management (released Nov 2025).

## Prerequisites

- Clerk Pro or Enterprise plan (Organizations + SSO require paid plan)
- Organizations feature enabled in Clerk Dashboard > Organizations > Settings
- Next.js 14+ with App Router (examples use `@clerk/nextjs`)

## Instructions

### Step 1: Enable Organizations and Add UI Components

```typescript
// app/org-selector/page.tsx
import { OrganizationSwitcher, OrganizationProfile } from '@clerk/nextjs'

export default function OrgPage() {
  return (
    <div className="p-8">
      <h1>Select Organization</h1>
      <OrganizationSwitcher
        hidePersonal={false}
        afterSelectOrganizationUrl="/dashboard"
        afterCreateOrganizationUrl="/dashboard"
      />
      <div className="mt-8">
        <OrganizationProfile />
      </div>
    </div>
  )
}
```

### Step 2: Define Custom Roles and Permissions

Configure in **Clerk Dashboard > Organizations > Roles** and **Permissions**.

**Default roles (built-in):**

| Role | Key | Built-in Permissions |
|------|-----|---------------------|
| Admin | `org:admin` | Full org management (members, settings, billing) |
| Member | `org:member` | View org, read-only access |

**Custom permissions (create in Dashboard > Organizations > Permissions):**

| Permission | Key | Description |
|------------|-----|-------------|
| Read data | `org:data:read` | View organization resources |
| Write data | `org:data:write` | Create/update resources |
| Delete data | `org:data:delete` | Delete resources |
| Manage billing | `org:billing:manage` | Access billing settings |
| View analytics | `org:analytics:read` | Access analytics dashboard |

**Custom roles (create in Dashboard > Organizations > Roles):**

| Role | Permissions | Use Case |
|------|-------------|----------|
| `org:manager` | `data:read`, `data:write`, `analytics:read` | Content managers |
| `org:viewer` | `data:read` | Read-only stakeholders |
| `org:billing_admin` | `data:read`, `billing:manage` | Finance team |

### Step 3: RBAC Middleware — Route Protection by Role

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
])
const isAdminRoute = createRouteMatcher(['/admin(.*)'])
const isManagerRoute = createRouteMatcher(['/manage(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (isPublicRoute(req)) return

  if (isAdminRoute(req)) {
    // Only org:admin can access /admin/*
    await auth.protect({ role: 'org:admin' })
  } else if (isManagerRoute(req)) {
    // org:admin OR org:manager can access /manage/*
    await auth.protect((has) =>
      has({ role: 'org:admin' }) || has({ role: 'org:manager' })
    )
  } else {
    // All other routes just require authentication
    await auth.protect()
  }
})
```

### Step 4: Permission Checks in Server Components

```typescript
// app/admin/page.tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function AdminPage() {
  const { userId, orgId, orgRole, has } = await auth()

  if (!userId) redirect('/sign-in')
  if (!orgId) redirect('/org-selector')

  // Permission-based checks (preferred over role-based)
  const canManageMembers = has({ permission: 'org:sys_memberships:manage' })
  const canWriteData = has({ permission: 'org:data:write' })
  const canDeleteData = has({ permission: 'org:data:delete' })
  const canViewAnalytics = has({ permission: 'org:analytics:read' })

  return (
    <div>
      <h1>Admin Panel</h1>
      <p>Current role: {orgRole}</p>

      <nav>
        {canManageMembers && <a href="/admin/members">Manage Members</a>}
        {canWriteData && <a href="/admin/content">Content Management</a>}
        {canDeleteData && <a href="/admin/danger-zone">Danger Zone</a>}
        {canViewAnalytics && <a href="/admin/analytics">Analytics</a>}
      </nav>
    </div>
  )
}
```

### Step 5: Permission Checks in Client Components

```typescript
'use client'
import { Protect, useOrganization, useAuth } from '@clerk/nextjs'

export function AdminSection() {
  const { organization } = useOrganization()
  const { has } = useAuth()

  return (
    <div>
      <h2>{organization?.name}</h2>

      {/* Declarative: Protect component with fallback */}
      <Protect
        role="org:admin"
        fallback={<p>You need admin access to view this section.</p>}
      >
        <DangerZone />
      </Protect>

      {/* Permission-based rendering */}
      <Protect permission="org:data:write">
        <EditForm />
      </Protect>

      {/* Imperative: has() for conditional logic */}
      {has?.({ permission: 'org:analytics:read' }) && (
        <AnalyticsDashboard />
      )}
    </div>
  )
}
```

### Step 6: Organization Member Management via Backend API

```typescript
// app/api/org/members/route.ts
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function GET() {
  const { orgId, has } = await auth()
  if (!orgId) return Response.json({ error: 'No org selected' }, { status: 400 })
  if (!has({ permission: 'org:sys_memberships:read' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  const client = await clerkClient()
  const members = await client.organizations.getOrganizationMembershipList({
    organizationId: orgId,
  })

  return Response.json({
    members: members.data.map(m => ({
      userId: m.publicUserData?.userId,
      name: `${m.publicUserData?.firstName} ${m.publicUserData?.lastName}`,
      email: m.publicUserData?.identifier,
      role: m.role,
      joinedAt: m.createdAt,
    })),
  })
}

export async function POST(req: Request) {
  const { orgId, userId, has } = await auth()
  if (!orgId || !has({ permission: 'org:sys_memberships:manage' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  const { emailAddress, role } = await req.json()
  const client = await clerkClient()

  const invitation = await client.organizations.createOrganizationInvitation({
    organizationId: orgId,
    emailAddress,
    role: role || 'org:member',
    inviterUserId: userId!,
  })

  return Response.json({ invitation: { id: invitation.id, emailAddress, role } })
}
```

### Step 7: Programmatic Role/Permission Management (Backend API)

```typescript
// lib/org-roles.ts — manage roles and permissions via API (released Nov 2025)
import { clerkClient } from '@clerk/nextjs/server'

export async function createCustomRole(orgId: string) {
  const client = await clerkClient()

  // Create a custom permission
  await client.organizations.createOrganizationPermission({
    organizationId: orgId,
    name: 'Manage reports',
    key: 'org:reports:manage',
    description: 'Create, edit, and delete reports',
  })

  // Create a custom role with that permission
  await client.organizations.createOrganizationRole({
    organizationId: orgId,
    name: 'Report Manager',
    key: 'org:report_manager',
    description: 'Can manage all reports',
    permissions: ['org:reports:manage', 'org:data:read'],
  })
}

// Update a member's role
export async function updateMemberRole(
  orgId: string,
  userId: string,
  newRole: string
) {
  const client = await clerkClient()
  const memberships = await client.organizations.getOrganizationMembershipList({
    organizationId: orgId,
  })

  const membership = memberships.data.find(
    m => m.publicUserData?.userId === userId
  )
  if (!membership) throw new Error('User is not a member of this organization')

  await client.organizations.updateOrganizationMembership({
    organizationId: orgId,
    userId,
    role: newRole,
  })
}
```

### Step 8: SAML SSO Configuration

Configure in **Clerk Dashboard > SSO Connections > Add SAML Connection**:

1. **ACS URL:** `https://<your-clerk-frontend-api>.clerk.accounts.dev/v1/saml/acs`
2. **Entity ID:** `https://<your-clerk-frontend-api>.clerk.accounts.dev/v1/saml/metadata`
3. Upload IdP metadata XML from your provider (Okta, Azure AD, Google Workspace)
4. Map SAML attributes: `email`, `firstName`, `lastName`

```typescript
// Enforce SSO for specific email domains
// Clerk Dashboard > Organizations > Settings > "Verified domains"
// Add your company domain (e.g., acme.com)
// Users with @acme.com emails will be forced through SSO
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `orgId` is null | No active organization | Redirect to org selector, show `<OrganizationSwitcher />` |
| `has()` returns false | Role/permission not assigned | Check assignment in Dashboard > Organizations > Members |
| Permission denied on middleware | User lacks required role | Verify route matcher maps to correct role |
| SSO login fails | Misconfigured IdP metadata | Verify ACS URL and Entity ID in IdP settings |
| Invitation fails | Email already a member | Check membership before inviting |
| Custom role not visible | Created via API, not Dashboard | Roles created via API are org-scoped, not instance-wide |

## Enterprise Considerations

- Roles and permissions are embedded in the session JWT -- no extra network requests needed for authorization checks
- Custom roles created in the Dashboard are instance-wide; roles created via Backend API are organization-scoped
- For multi-tenant SaaS, combine Organizations with tenant-scoped database queries (`WHERE org_id = :orgId`)
- Session claims include `org_id`, `org_role`, and `org_permissions` -- available in middleware without API calls
- Verified domains + SAML SSO enable "just-in-time provisioning" -- users auto-join the org on first SSO sign-in
- Consider the `org:sys_*` system permissions (`sys_memberships:manage`, `sys_memberships:read`, `sys_domains:manage`) for built-in org management actions

## Resources

- [Organizations Overview](https://clerk.com/docs/guides/organizations/overview)
- [Roles & Permissions](https://clerk.com/docs/guides/organizations/control-access/roles-and-permissions)
- [Check Access](https://clerk.com/docs/guides/organizations/control-access/check-access)
- [Roles/Permissions Backend API](https://clerk.com/changelog/2025-11-24-organization-roles-and-permission-bapi-management)

## Next Steps

Proceed to `clerk-migration-deep-dive` for auth provider migration.

## Output

- RBAC model mapping Clerk orgs/roles/permissions to app authorization checks
- Code or config for role gates (middleware, server actions, or API guards)
- Escalation notes for SSO/SAML enterprise setups when in scope

## Examples

### Map org roles to feature access

```
User: Only org:billing can open the invoices page.
Skill: implements role check on the server and fails closed when claims missing.
```

### Audit permission matrix

```
User: Produce a role × capability matrix for our Clerk org roles.
Skill: enumerates Clerk roles/permissions and maps them to app routes/actions.
```
