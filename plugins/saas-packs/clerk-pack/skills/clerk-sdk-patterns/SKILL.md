---
name: clerk-sdk-patterns
description: 'Common Clerk SDK patterns and best practices.

  Use when implementing authentication flows, accessing user data,

  or integrating Clerk SDK methods in your application.

  Trigger with phrases like "clerk SDK", "clerk patterns",

  "clerk best practices", "clerk API usage".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- api
- authentication
compatibility: Designed for Claude Code
---
# Clerk SDK Patterns

## Overview

Common patterns and best practices for using the Clerk SDK effectively across server components, client components, API routes, and middleware.

## Prerequisites

- Clerk SDK installed and configured
- Basic understanding of React/Next.js
- ClerkProvider wrapping application

## Instructions

### Pattern 1: Server-Side Authentication

```typescript
// Server Component — use auth() for lightweight checks
import { auth } from '@clerk/nextjs/server'

export default async function ServerPage() {
  const { userId, orgId, has } = await auth()

  if (!userId) return <div>Not authenticated</div>
  if (!has({ permission: 'org:posts:create' })) return <div>No permission</div>

  return <div>Authorized content for {userId}</div>
}
```

```typescript
// Use currentUser() when you need full user profile data
import { currentUser } from '@clerk/nextjs/server'

export default async function ProfilePage() {
  const user = await currentUser()
  if (!user) return null

  return (
    <div>
      <h1>{user.firstName} {user.lastName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
      <img src={user.imageUrl} alt="Avatar" />
    </div>
  )
}
```

### Pattern 2: Client-Side Hooks

```typescript
'use client'
import { useUser, useAuth, useClerk, useSignIn } from '@clerk/nextjs'

export function ClientAuthExample() {
  const { user, isLoaded, isSignedIn } = useUser()       // Full user object
  const { userId, getToken, signOut } = useAuth()          // Auth state + token access
  const { openSignIn, openUserProfile } = useClerk()       // UI controls

  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <button onClick={() => openSignIn()}>Sign In</button>

  const fetchWithAuth = async (url: string) => {
    const token = await getToken()
    return fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  return (
    <div>
      <p>Hello, {user.firstName}</p>
      <button onClick={() => openUserProfile()}>Profile</button>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
```

### Pattern 3: Protected Routes with Middleware

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/pricing',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})
```

### Pattern 4: Organization-Aware Queries

```typescript
// lib/db-helpers.ts
import { auth } from '@clerk/nextjs/server'

export async function getOrgData() {
  const { userId, orgId } = await auth()

  if (orgId) {
    // Org-scoped query: return data for the active organization
    return db.items.findMany({ where: { organizationId: orgId } })
  }

  // Personal account: return user's own data
  return db.items.findMany({ where: { ownerId: userId } })
}
```

### Pattern 5: Custom JWT Templates for External Services

```typescript
// Generate a Supabase-compatible JWT
import { auth } from '@clerk/nextjs/server'
import { createClient } from '@supabase/supabase-js'

export async function getSupabaseClient() {
  const { getToken } = await auth()
  const supabaseToken = await getToken({ template: 'supabase' })

  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: {
        headers: { Authorization: `Bearer ${supabaseToken}` },
      },
    }
  )
}
```

Configure the JWT template in Clerk Dashboard > JWT Templates with claims:

```json
{
  "sub": "{{user.id}}",
  "email": "{{user.primary_email_address}}",
  "role": "authenticated"
}
```

## Output

- Server and client authentication patterns ready to use
- Protected route middleware with public route exceptions
- Organization-aware data queries
- Custom JWT tokens for third-party integrations (Supabase, Hasura, etc.)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `auth()` returns null userId | Not in server context | Use only in Server Components or API routes |
| `useUser()` not updating | Stale component | Check ClerkProvider wraps the component tree |
| `getToken()` fails | JWT template not configured | Create template in Dashboard > JWT Templates |
| `orgId` is null | No organization selected | Prompt user with `<OrganizationSwitcher />` |

## Examples

### Server Action with Auth Check

```typescript
'use server'
import { auth } from '@clerk/nextjs/server'

export async function createPost(title: string, content: string) {
  const { userId, orgId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  return db.post.create({
    data: { title, content, authorId: userId, orgId },
  })
}
```

## Resources

- [Clerk SDK Reference](https://clerk.com/docs/references/nextjs/overview)
- [Auth Helper](https://clerk.com/docs/references/nextjs/auth)
- [JWT Templates](https://clerk.com/docs/backend-requests/making/jwt-templates)

## Next Steps

Proceed to `clerk-core-workflow-a` for user sign-up and sign-in flows.
