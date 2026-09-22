---
name: clerk-performance-tuning
description: 'Optimize Clerk authentication performance.

  Use when improving auth response times, reducing latency,

  or optimizing Clerk SDK usage.

  Trigger with phrases like "clerk performance", "clerk optimization",

  "clerk slow", "clerk latency", "optimize clerk".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- performance
- authentication
compatibility: Designed for Claude Code
---
# Clerk Performance Tuning

## Overview

Optimize Clerk authentication for best performance. Covers middleware optimization, user data caching, token handling, lazy loading, and edge runtime configuration.

## Prerequisites

- Clerk integration working
- Performance monitoring in place (Lighthouse, Web Vitals)
- Understanding of Next.js rendering strategies

## Instructions

### Step 1: Optimize Middleware (Skip Static Assets)

```typescript
// middleware.ts — avoid running auth on static files
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)', '/api/webhooks(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})

// Restrict matcher to avoid processing static assets
export const config = {
  matcher: [
    // Skip _next, static files, and images
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)).*)',
    '/(api|trpc)(.*)',
  ],
}
```

### Step 2: Cache User Data

```typescript
// lib/cached-user.ts
import { auth, currentUser } from '@clerk/nextjs/server'
import { cache } from 'react'

// React cache: deduplicates within a single request
export const getAuthUser = cache(async () => {
  const { userId } = await auth()
  if (!userId) return null
  return currentUser()
})

// Usage in multiple server components (only one Clerk API call per request):
// const user = await getAuthUser()
```

For cross-request caching with `unstable_cache`:

```typescript
import { unstable_cache } from 'next/cache'
import { clerkClient } from '@clerk/nextjs/server'

export const getCachedUserProfile = unstable_cache(
  async (userId: string) => {
    const client = await clerkClient()
    const user = await client.users.getUser(userId)
    return {
      id: user.id,
      name: `${user.firstName} ${user.lastName}`,
      email: user.emailAddresses[0]?.emailAddress,
      imageUrl: user.imageUrl,
    }
  },
  ['user-profile'],
  { revalidate: 300 } // Cache for 5 minutes
)
```

### Step 3: Optimize Token Handling

```typescript
// lib/token-cache.ts
let tokenCache: { token: string; expiresAt: number } | null = null

export async function getOptimizedToken(getToken: () => Promise<string | null>) {
  // Reuse token if it has more than 30 seconds remaining
  if (tokenCache && tokenCache.expiresAt > Date.now() + 30_000) {
    return tokenCache.token
  }

  const token = await getToken()
  if (token) {
    const payload = JSON.parse(atob(token.split('.')[1]))
    tokenCache = { token, expiresAt: payload.exp * 1000 }
  }

  return token
}
```

### Step 4: Lazy Load Auth Components

```typescript
// components/lazy-auth.tsx
'use client'
import dynamic from 'next/dynamic'

// Only load UserButton when needed (saves ~15KB)
const UserButton = dynamic(
  () => import('@clerk/nextjs').then((mod) => mod.UserButton),
  { ssr: false, loading: () => <div className="w-8 h-8 rounded-full bg-gray-200 animate-pulse" /> }
)

const SignInButton = dynamic(
  () => import('@clerk/nextjs').then((mod) => mod.SignInButton),
  { ssr: false }
)

export { UserButton, SignInButton }
```

### Step 5: Optimize Server Components

```typescript
// app/dashboard/page.tsx — parallel data fetching
import { auth } from '@clerk/nextjs/server'
import { Suspense } from 'react'

export default async function Dashboard() {
  const { userId } = await auth()
  if (!userId) return null

  return (
    <div>
      {/* Parallel loading with Suspense boundaries */}
      <Suspense fallback={<div>Loading profile...</div>}>
        <UserProfile userId={userId} />
      </Suspense>
      <Suspense fallback={<div>Loading activity...</div>}>
        <RecentActivity userId={userId} />
      </Suspense>
    </div>
  )
}

async function UserProfile({ userId }: { userId: string }) {
  const profile = await getCachedUserProfile(userId)
  return <div>{profile.name}</div>
}

async function RecentActivity({ userId }: { userId: string }) {
  const activity = await db.activity.findMany({ where: { userId }, take: 10 })
  return <ul>{activity.map((a) => <li key={a.id}>{a.description}</li>)}</ul>
}
```

### Step 6: Edge Runtime for Middleware

```typescript
// middleware.ts — runs on Vercel Edge (cold start <50ms vs ~250ms Node)
import { clerkMiddleware } from '@clerk/nextjs/server'

export default clerkMiddleware()

// Clerk middleware is Edge-compatible by default on Vercel
export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
  runtime: 'edge', // Explicitly opt into Edge Runtime
}
```

## Output

- Middleware skipping static assets (fewer auth checks)
- React `cache()` deduplicating user fetches within requests
- Cross-request user profile caching (5-minute TTL)
- Lazy-loaded auth components reducing bundle size
- Parallel Suspense boundaries for dashboard rendering
- Edge Runtime middleware for faster cold starts

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow initial page load | Blocking auth calls | Use Suspense boundaries for parallel loading |
| High Clerk API latency | No caching | Use `cache()` and `unstable_cache()` |
| Large JS bundle | All Clerk components loaded | Use `dynamic()` imports for auth UI components |
| Slow middleware cold start | Node.js runtime | Switch to Edge Runtime on Vercel |
| Stale cached user data | Cache not invalidated | Invalidate on `user.updated` webhook |

## Examples

### Measure Clerk Auth Overhead

```typescript
// lib/perf-measure.ts
export async function measureAuthTime() {
  const start = performance.now()
  const { userId } = await auth()
  const authMs = performance.now() - start
  console.log(`[Perf] auth() took ${authMs.toFixed(1)}ms, userId: ${userId}`)
  return { userId, authMs }
}
```

## Resources

- [Next.js Performance Optimization](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Clerk Quickstart (Next.js)](https://clerk.com/docs/quickstarts/nextjs)
- [Vercel Edge Runtime](https://vercel.com/docs/functions/runtimes/edge-runtime)

## Next Steps

Proceed to `clerk-cost-tuning` for cost optimization strategies.
