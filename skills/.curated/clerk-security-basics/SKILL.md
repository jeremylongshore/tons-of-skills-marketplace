---
name: clerk-security-basics
description: 'Implement security best practices with Clerk authentication.

  Use when securing your application, reviewing auth implementation,

  or hardening Clerk configuration.

  Trigger with phrases like "clerk security", "secure clerk",

  "clerk best practices", "clerk hardening".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- security
- authentication
compatibility: Designed for Claude Code
---
# Clerk Security Basics

## Overview

Implement security best practices for Clerk authentication: environment variable protection, middleware hardening, API route defense, webhook verification, and session security.

## Prerequisites

- Clerk SDK installed and configured
- Understanding of OWASP authentication best practices
- Production deployment planned or active

## Instructions

### Step 1: Secure Environment Variables

```bash
# .env.local — never commit this file
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...  # Safe to expose (public)
CLERK_SECRET_KEY=sk_live_...                    # NEVER expose client-side
CLERK_WEBHOOK_SECRET=whsec_...                  # Server-only
```

```gitignore
# .gitignore — ensure secrets stay out of git
.env.local
.env.*.local
.env.production
```

Validate at startup that secret keys are not leaked:

```typescript
// lib/security-check.ts
export function assertServerOnly() {
  if (typeof window !== 'undefined') {
    throw new Error('This module must only be used server-side')
  }
  if (!process.env.CLERK_SECRET_KEY) {
    throw new Error('CLERK_SECRET_KEY is not configured')
  }
}
```

### Step 2: Hardened Middleware Configuration

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // Protect all non-public routes
  if (!isPublicRoute(req)) {
    await auth.protect()
  }

  // Add security headers
  const response = NextResponse.next()
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set(
    'Content-Security-Policy',
    "frame-ancestors 'none'; form-action 'self' https://clerk.com https://*.clerk.accounts.dev"
  )
  return response
})
```

### Step 3: Secure API Routes

```typescript
// app/api/admin/route.ts
import { auth } from '@clerk/nextjs/server'
import { NextRequest } from 'next/server'

export async function POST(req: NextRequest) {
  const { userId, has } = await auth()

  // 1. Verify authentication
  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // 2. Verify authorization (permission-based, not role-based)
  if (!has({ permission: 'org:admin:access' })) {
    return Response.json({ error: 'Forbidden' }, { status: 403 })
  }

  // 3. Validate and sanitize input
  const body = await req.json()
  if (typeof body.name !== 'string' || body.name.length > 200) {
    return Response.json({ error: 'Invalid input' }, { status: 400 })
  }

  // 4. Rate limit sensitive operations
  // (Use a rate limiter like @upstash/ratelimit)

  return Response.json({ success: true })
}
```

### Step 4: Secure Webhook Verification

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix'
import { headers } from 'next/headers'

export async function POST(req: Request) {
  const secret = process.env.CLERK_WEBHOOK_SECRET
  if (!secret) {
    // Log but don't expose internal state
    console.error('Missing CLERK_WEBHOOK_SECRET')
    return new Response('Internal error', { status: 500 })
  }

  const headerPayload = await headers()
  const svixHeaders = {
    'svix-id': headerPayload.get('svix-id') || '',
    'svix-timestamp': headerPayload.get('svix-timestamp') || '',
    'svix-signature': headerPayload.get('svix-signature') || '',
  }

  // Reject requests missing required headers
  if (!svixHeaders['svix-id'] || !svixHeaders['svix-signature']) {
    return new Response('Missing verification headers', { status: 400 })
  }

  const body = await req.text()
  const wh = new Webhook(secret)

  try {
    const event = wh.verify(body, svixHeaders)
    // Process verified event...
    return new Response('OK', { status: 200 })
  } catch {
    // Don't leak verification details
    return new Response('Verification failed', { status: 400 })
  }
}
```

### Step 5: Session Security Best Practices

```typescript
// Enforce session checks in sensitive operations
import { auth } from '@clerk/nextjs/server'

export async function dangerousAction() {
  const { userId, sessionId } = await auth()

  if (!userId || !sessionId) {
    throw new Error('Valid session required')
  }

  // For extra-sensitive operations, verify the session is fresh
  // by checking session claims or requiring re-authentication
  const { sessionClaims } = await auth()
  const sessionAge = Date.now() / 1000 - (sessionClaims?.iat || 0)

  if (sessionAge > 300) { // 5 minutes
    throw new Error('Session too old for this operation. Please re-authenticate.')
  }
}
```

Configure session settings in Clerk Dashboard:

- **Session lifetime**: 7 days (default) — reduce for sensitive apps
- **Inactivity timeout**: Enable for compliance requirements
- **Multi-session mode**: Disable unless explicitly needed

## Output

- Environment variables secured with leak prevention
- Middleware with security headers (CSP, X-Frame-Options, etc.)
- API routes with auth + authz + input validation
- Webhook endpoint with Svix signature verification
- Session freshness checks for sensitive operations

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Secret key exposed client-side | Imported in client component | Move to server-only module, add `assertServerOnly()` |
| CSP blocks Clerk UI | Missing Clerk domain in CSP | Add `*.clerk.accounts.dev` to frame-src |
| Webhook verification fails | Clock skew on server | Ensure server time is NTP-synced |
| Session too old error | User idle too long | Prompt re-authentication for sensitive actions |

## Examples

### Rate Limiting Sensitive Endpoints

```typescript
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'
import { auth } from '@clerk/nextjs/server'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, '60 s'),
})

export async function POST() {
  const { userId } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })

  const { success } = await ratelimit.limit(userId)
  if (!success) return Response.json({ error: 'Rate limited' }, { status: 429 })

  // Proceed with operation
}
```

## Resources

- [Clerk Security Overview](https://clerk.com/docs/security/overview)
- [OWASP Authentication Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Webhook Verification](https://clerk.com/docs/integrations/webhooks/overview)

## Next Steps

Proceed to `clerk-prod-checklist` for production readiness review.
