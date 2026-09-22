---
name: clerk-common-errors
description: 'Troubleshoot common Clerk errors and issues.

  Use when encountering authentication errors, SDK issues,

  or configuration problems with Clerk.

  Trigger with phrases like "clerk error", "clerk not working",

  "clerk authentication failed", "clerk issue", "fix clerk".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(npm:*)
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- authentication
compatibility: Designed for Claude Code
---
# Clerk Common Errors

## Overview

Diagnose and resolve common Clerk authentication errors. Organized by error category with root cause analysis and fix code.

## Prerequisites

- Clerk SDK installed
- Access to Clerk Dashboard for configuration verification
- Browser developer tools for client-side debugging

## Instructions

### Error Category 1: Configuration Errors

**`Clerk: Missing publishableKey`**

```typescript
// Cause: ClerkProvider not receiving key
// Fix: Ensure env var is set and accessible
// .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

// Verify in code:
console.log('PK:', process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) // Should not be undefined
```

**`ClerkProvider must wrap your application`**

```typescript
// Cause: Clerk hook used outside provider
// Fix: Wrap root layout with ClerkProvider
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html><body>{children}</body></html>
    </ClerkProvider>
  )
}
```

### Error Category 2: Authentication Errors

**`form_identifier_not_found`**

```typescript
// Cause: Email not registered in Clerk instance
// Fix: Check correct Clerk instance (dev vs prod) and user exists
// Diagnostic:
import { createClerkClient } from '@clerk/backend'
const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })
const users = await clerk.users.getUserList({ emailAddress: ['user@example.com'] })
console.log('User found:', users.totalCount > 0)
```

**`form_password_incorrect`**

```typescript
// Cause: Wrong password or user set up with OAuth only
// Fix: Check auth strategy in Clerk Dashboard
// User may need password reset:
// Dashboard > Users > Select user > Authentication > Reset password
```

**`session_exists` (Error during sign-in)**

```typescript
// Cause: User already has active session
// Fix: Sign out first or redirect
'use client'
import { useAuth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'

export default function SignInPage() {
  const { isSignedIn } = useAuth()
  if (isSignedIn) redirect('/dashboard')
  // ... render sign-in form
}
```

### Error Category 3: Middleware Errors

**Infinite redirect loop**

```typescript
// Cause: Sign-in page not in public routes
// Fix: Add auth pages to public route matcher
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/sign-in(.*)',  // Must include sign-in
  '/sign-up(.*)',  // Must include sign-up
  '/',
  '/api/webhooks(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) await auth.protect()
})
```

**`auth() was called but Clerk middleware was not detected`**

```typescript
// Cause: middleware.ts not in correct location or matcher not matching
// Fix: Ensure middleware.ts is at project root (not inside app/ or src/)

// Verify matcher includes the route:
export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
```

### Error Category 4: Server/Client Component Errors

**`useUser()` in Server Component**

```typescript
// Error: Hooks can only be called inside a Client Component
// Fix: Use auth()/currentUser() server-side, useUser() client-side

// Server Component (no 'use client'):
import { currentUser } from '@clerk/nextjs/server'
export default async function Page() {
  const user = await currentUser()
  return <div>{user?.firstName}</div>
}

// Client Component (with 'use client'):
'use client'
import { useUser } from '@clerk/nextjs'
export function Profile() {
  const { user } = useUser()
  return <div>{user?.firstName}</div>
}
```

**Hydration mismatch with auth state**

```typescript
// Cause: Server renders unauthenticated, client has session
// Fix: Use ClerkLoaded or check isLoaded before rendering auth-dependent UI
'use client'
import { useUser } from '@clerk/nextjs'

export function SafeAuthUI() {
  const { user, isLoaded } = useUser()
  if (!isLoaded) return <div>Loading...</div> // Prevent hydration mismatch
  return <div>{user ? `Hello ${user.firstName}` : 'Not signed in'}</div>
}
```

### Error Category 5: Webhook Errors

**`Invalid signature` on webhook endpoint**

```typescript
// Cause: CLERK_WEBHOOK_SECRET mismatch or body parsing issue
// Fix 1: Verify secret matches Dashboard > Webhooks > Signing Secret
// Fix 2: Read raw body, don't use JSON middleware before verification

// Next.js App Router (correct):
export async function POST(req: Request) {
  const body = await req.text() // Use text(), not json()
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!)
  const evt = wh.verify(body, { /* svix headers */ })
}

// Express (correct):
app.post('/webhooks', express.raw({ type: 'application/json' }), handler)
// NOT: app.post('/webhooks', express.json(), handler) // This breaks signature
```

## Output

- Identified error category and root cause
- Working fix code for each common error
- Diagnostic steps for verification

## Error Handling

| Error | Cause | Quick Fix |
|-------|-------|-----------|
| `Missing publishableKey` | Env var not set | Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `.env.local` |
| `auth() not detected` | Middleware missing/misplaced | Move `middleware.ts` to project root |
| Redirect loop | Auth pages not public | Add sign-in/sign-up to `isPublicRoute` matcher |
| Hydration mismatch | Server/client state differs | Guard with `isLoaded` check |
| Webhook invalid signature | Body parsed before verify | Use `req.text()` not `req.json()` before `wh.verify()` |

## Examples

### Quick Diagnostic Checklist

```bash
# 1. Check Clerk packages are installed
npm list @clerk/nextjs 2>/dev/null

# 2. Verify env vars are set
node -e "console.log('PK:', !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, 'SK:', !!process.env.CLERK_SECRET_KEY)"

# 3. Test API connectivity
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLERK_SECRET_KEY" https://api.clerk.com/v1/users?limit=1

# 4. Check middleware exists at root
ls middleware.ts 2>/dev/null && echo "Found" || echo "Missing - create middleware.ts at project root"
```

## Resources

- [Clerk Error Reference](https://clerk.com/docs/errors/overview)
- [Clerk Debugging Guide](https://clerk.com/docs/troubleshooting/overview)
- [Clerk Discord Community](https://clerk.com/discord)

## Next Steps

Proceed to `clerk-debug-bundle` for comprehensive debugging tools.
