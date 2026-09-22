---
name: clerk-hello-world
description: 'Create your first authenticated request with Clerk.

  Use when making initial API calls, testing authentication,

  or verifying Clerk integration works correctly.

  Trigger with phrases like "clerk hello world", "first clerk request",

  "test clerk auth", "verify clerk setup".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- api
- testing
- authentication
compatibility: Designed for Claude Code
---
# Clerk Hello World

## Overview

Make your first authenticated requests using Clerk across server components, client components, API routes, and server actions. Validates your Clerk integration end-to-end.

## Prerequisites

- Clerk SDK installed (`clerk-install-auth` completed)
- Environment variables configured (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`)
- ClerkProvider wrapping application root
- Middleware configured at project root

## Instructions

### Step 1: Server Component — auth() and currentUser()

```typescript
// app/dashboard/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  // auth() is lightweight — reads JWT from the session cookie, no API call
  const { userId } = await auth()

  if (!userId) redirect('/sign-in')

  // currentUser() makes a Backend API call — use sparingly, counts toward rate limit
  const user = await currentUser()

  return (
    <div>
      <h1>Hello, {user?.firstName || 'User'}!</h1>
      <p>User ID: {userId}</p>
      <p>Email: {user?.emailAddresses[0]?.emailAddress}</p>
      <p>Created: {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}</p>
    </div>
  )
}
```

**Key distinction:** `auth()` is cheap (JWT parsing, no network). `currentUser()` is expensive (Backend API call, rate-limited). Prefer `auth()` when you only need `userId`, `orgId`, or `sessionClaims`.

### Step 2: Protected API Route

```typescript
// app/api/hello/route.ts
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { userId, orgId, sessionClaims } = await auth()

  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  return Response.json({
    message: 'Hello from Clerk!',
    userId,
    orgId: orgId || null,
    sessionId: sessionClaims?.sid,
    timestamp: new Date().toISOString(),
  })
}
```

### Step 3: Client Component with Hooks

```typescript
'use client'
import { useUser, useAuth, useClerk } from '@clerk/nextjs'

export function AuthTest() {
  const { user, isLoaded, isSignedIn } = useUser()
  const { getToken, signOut } = useAuth()
  const { openUserProfile } = useClerk()

  if (!isLoaded) return <div>Loading...</div>
  if (!isSignedIn) return <div>Not signed in</div>

  const testAPI = async () => {
    // getToken() returns the session JWT — use for calling your own API routes
    // or external services with Bearer token auth
    const token = await getToken()
    const res = await fetch('/api/hello', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    console.log('API response:', data)
  }

  return (
    <div>
      <p>Signed in as: {user.primaryEmailAddress?.emailAddress}</p>
      <img src={user.imageUrl} alt="Avatar" width={48} height={48} />
      <div className="flex gap-2 mt-4">
        <button onClick={testAPI}>Test API</button>
        <button onClick={() => openUserProfile()}>Profile</button>
        <button onClick={() => signOut()}>Sign Out</button>
      </div>
    </div>
  )
}
```

### Step 4: Server Action with Auth

```typescript
// app/actions.ts
'use server'
import { auth } from '@clerk/nextjs/server'

export async function greetUser() {
  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  // Perform server-side work here (DB queries, external API calls, etc.)
  return { greeting: `Hello user ${userId}!`, timestamp: new Date().toISOString() }
}
```

```typescript
// app/dashboard/greeting.tsx
'use client'
import { greetUser } from '@/app/actions'
import { useState } from 'react'

export function GreetingButton() {
  const [msg, setMsg] = useState<string | null>(null)

  return (
    <div>
      <button onClick={async () => {
        const result = await greetUser()
        setMsg(result.greeting)
      }}>
        Get Server Greeting
      </button>
      {msg && <p>{msg}</p>}
    </div>
  )
}
```

### Step 5: Express.js Hello World

```typescript
import express from 'express'
import { clerkMiddleware, requireAuth, getAuth } from '@clerk/express'

const app = express()
app.use(clerkMiddleware())

// Public endpoint
app.get('/api/hello', (req, res) => {
  const { userId } = getAuth(req)
  res.json({
    message: userId ? `Hello user ${userId}!` : 'Hello anonymous!',
    authenticated: !!userId,
  })
})

// Protected endpoint — returns 403 if no valid session
app.get('/api/me', requireAuth(), (req, res) => {
  const { userId, orgId } = getAuth(req)
  res.json({ userId, orgId })
})

app.listen(3001)
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `userId` is null | User not authenticated | Redirect to `/sign-in` or check middleware covers route |
| `currentUser()` returns null | Session expired or invalid | Refresh page; ensure middleware is running |
| 401 from API route | Token missing or expired | Include `Authorization: Bearer <token>` header |
| Hydration mismatch | Server/client state differs | Guard client components with `isLoaded` check |
| `auth() was called but Clerk can't detect clerkMiddleware()` | Middleware not in project root | Move `middleware.ts` out of `app/` to project root |

## Enterprise Considerations

- Use `auth()` over `currentUser()` in hot paths to avoid Backend API rate limits
- Deduplicate `currentUser()` calls with React's `cache()` function across server components in the same request
- For microservices, pass Clerk JWTs between services and verify with `@clerk/backend` or `@clerk/express`
- Session token v2 (default since April 2025) uses a more compact format -- ensure downstream JWT consumers are updated
- Custom session claims can be set in Dashboard > Sessions > Customize session token (limit: 1.2KB)

## Resources

- [auth() Reference](https://clerk.com/docs/reference/nextjs/app-router/auth)
- [currentUser() Reference](https://clerk.com/docs/reference/nextjs/app-router/current-user)
- [useUser() Hook](https://clerk.com/docs/references/react/use-user)
- [Express getAuth()](https://clerk.com/docs/reference/express/get-auth)

## Next Steps

Proceed to `clerk-local-dev-loop` for local development workflow setup.

## Output

- Minimal Clerk "hello world" that signs in a user and shows identity on a protected page
- Exact install + env steps for the chosen framework
- Next-step links into deeper clerk-pack skills (webhooks, RBAC, production checklist)

## Examples

### Next.js hello world

```
User: Smallest possible Clerk + Next.js demo with a protected /me page.
Skill: scaffolds packages, middleware, sign-in UI, and /me reading user id.
```

### Verify keys are live

```
User: Confirm publishable + secret keys work against Clerk API.
Skill: runs a minimal session/user fetch and reports success or key-mismatch errors.
```
