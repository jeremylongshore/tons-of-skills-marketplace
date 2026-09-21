# Session & middleware deep dive (full prior SKILL body)

# Clerk Core Workflow B: Session & Middleware

## Overview

Implement session management and route protection with Clerk middleware. Covers `clerkMiddleware()` configuration, `auth()` patterns, custom session claims, JWT templates for external services, organization-scoped sessions, and session token v2.

## Prerequisites

- `@clerk/nextjs` installed with ClerkProvider wrapping the app
- Next.js 14+ with App Router
- Sign-in/sign-up flows working (`clerk-core-workflow-a` completed)

## Instructions

### Step 1: Configure clerkMiddleware with Route Matchers

```typescript
// middleware.ts (project root)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
  '/pricing',
  '/blog(.*)',
])

const isAdminRoute = createRouteMatcher(['/admin(.*)'])
const isApiRoute = createRouteMatcher(['/api(.*)'])

export default clerkMiddleware(async (auth, req) => {
  // Public routes: no auth required
  if (isPublicRoute(req)) return

  // Admin routes: require org:admin role
  if (isAdminRoute(req)) {
    await auth.protect({ role: 'org:admin' })
    return
  }

  // All other routes: require authentication
  await auth.protect()
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
```

**Key behavior:** `clerkMiddleware()` does NOT protect any routes by default. You must explicitly call `auth.protect()` for routes that require authentication. This is a design decision to avoid over-blocking.

### Step 2: Protect API Routes with auth()

```typescript
// app/api/data/route.ts
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { userId, orgId, has } = await auth()

  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Permission-based authorization
  if (!has({ permission: 'org:data:read' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  const data = orgId
    ? await db.items.findMany({ where: { organizationId: orgId } })
    : await db.items.findMany({ where: { ownerId: userId } })

  return Response.json({ data, userId, orgId })
}

export async function POST(req: Request) {
  const { userId, orgId, has } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })
  if (!has({ permission: 'org:data:write' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  const body = await req.json()
  const item = await db.items.create({
    data: { ...body, ownerId: userId, organizationId: orgId },
  })
  return Response.json({ item }, { status: 201 })
}
```

### Step 3: Server Component Auth Patterns

```typescript
// app/dashboard/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const { userId, orgId, orgRole, has, sessionClaims } = await auth()
  if (!userId) redirect('/sign-in')

  // auth() is free (JWT parsing) — use for lightweight checks
  const isAdmin = has({ role: 'org:admin' })

  // currentUser() costs a Backend API call — use only when you need full profile
  const user = await currentUser()

  return (
    <div>
      <h1>Welcome, {user?.firstName}</h1>
      <p>Organization: {orgId || 'Personal account'}</p>
      <p>Role: {orgRole || 'N/A'}</p>
      {isAdmin && <a href="/admin">Admin Panel</a>}
    </div>
  )
}
```

### Step 4: Custom Session Claims

Customize in **Dashboard > Sessions > Customize session token:**

```json
{
  "metadata": "{{user.public_metadata}}",
  "email": "{{user.primary_email_address}}"
}
```

Then declare types and access in code:

```typescript
// types/clerk.d.ts
declare global {
  interface CustomJwtSessionClaims {
    metadata?: {
      role?: string
      plan?: string
    }
    email?: string
  }
}
export {}
```

```typescript
// Access custom claims (no API call needed — embedded in JWT)
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { sessionClaims } = await auth()

  const userPlan = sessionClaims?.metadata?.plan || 'free'
  const userEmail = sessionClaims?.email

  return Response.json({ plan: userPlan, email: userEmail })
}
```

**Warning:** Session token cookie limit is 4KB. Custom claims should be under 1.2KB. Store large data in your database, not in session claims.

### Step 5: JWT Templates for External Services

```typescript
// app/api/supabase-data/route.ts
import { auth } from '@clerk/nextjs/server'
import { createClient } from '@supabase/supabase-js'

export async function GET() {
  const { userId, getToken } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })

  // Get a JWT with Supabase-compatible claims
  // Configure the template in Dashboard > JWT Templates
  const supabaseToken = await getToken({ template: 'supabase' })

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { global: { headers: { Authorization: `Bearer ${supabaseToken}` } } }
  )

  const { data } = await supabase.from('items').select('*')
  return Response.json({ data })
}
```

Configure JWT template in **Dashboard > JWT Templates > New template**:

```json
{
  "sub": "{{user.id}}",
  "email": "{{user.primary_email_address}}",
  "role": "authenticated",
  "aud": "authenticated"
}
```

### Step 6: Organization-Scoped Sessions

```typescript
'use client'
import { useOrganizationList, useOrganization, useAuth } from '@clerk/nextjs'

export function OrgSwitcher() {
  const { organizationList, setActive, isLoaded } = useOrganizationList({
    userMemberships: { infinite: true },
  })
  const { organization } = useOrganization()

  if (!isLoaded) return <div>Loading orgs...</div>

  return (
    <div>
      <p>Active: {organization?.name || 'Personal account'}</p>
      <ul>
        {organizationList?.map(({ organization: org, membership }) => (
          <li key={org.id}>
            <button onClick={() => setActive({ organization: org.id })}>
              {org.name} ({membership.role})
            </button>
          </li>
        ))}
        <li>
          <button onClick={() => setActive({ organization: null })}>
            Personal account
          </button>
        </li>
      </ul>
    </div>
  )
}
```

### Step 7: Server Action Permission Guards

```typescript
'use server'
import { auth } from '@clerk/nextjs/server'

export async function deleteItem(itemId: string) {
  const { userId, orgId, has } = await auth()
  if (!userId) throw new Error('Unauthorized')
  if (!has({ permission: 'org:data:delete' })) {
    throw new Error('You do not have permission to delete items')
  }

  await db.items.delete({ where: { id: itemId, organizationId: orgId } })
  return { success: true }
}

export async function updateOrgSettings(settings: Record<string, any>) {
  const { orgId, has } = await auth()
  if (!orgId) throw new Error('No organization selected')
  if (!has({ role: 'org:admin' })) {
    throw new Error('Only admins can update organization settings')
  }

  await db.orgSettings.upsert({
    where: { orgId },
    update: settings,
    create: { orgId, ...settings },
  })
  return { success: true }
}
```

## Error Handling

The sections above contain the full session, JWT template, and
organization-session patterns.

## Output

- Completed Clerk workflow for the requested advanced flow (orgs, multi-session, or custom session claims)
- Diff-ready code for middleware, webhooks, or session token customization as needed
- Explicit list of residual risks (webhook retries, claim size, org role mapping)

## Examples

### Organization-aware routing

```
User: Gate /admin to org:admin role only.
Skill: maps Clerk org roles into middleware authorization and documents claim paths.
```

### Session claims customization

```
User: Put plan_tier on the session JWT for feature flags.
Skill: configures session token template / backend claims and validates size limits.
```
