---
name: clerk-install-auth
description: 'Install and configure Clerk SDK/CLI authentication.

  Use when setting up a new Clerk integration, configuring API keys,

  or initializing Clerk in your project.

  Trigger with phrases like "install clerk", "setup clerk",

  "clerk auth", "configure clerk API key", "add clerk to project".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
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
# Clerk Install & Auth

## Overview

Set up Clerk SDK and configure authentication for Next.js, React, or Express. This skill covers SDK installation, environment variables, ClerkProvider, middleware, and initial auth verification.

## Prerequisites

- Node.js 18+
- Package manager (npm, pnpm, or yarn)
- Clerk account at dashboard.clerk.com
- Publishable Key (`pk_test_*`) and Secret Key (`sk_test_*`) from Clerk Dashboard > API Keys

## Instructions

### Step 1: Install SDK for Your Framework

```bash
set -euo pipefail
# Next.js (App Router or Pages Router)
npm install @clerk/nextjs

# React SPA (Vite, CRA, etc.)
npm install @clerk/clerk-react

# Express / Node.js backend
npm install @clerk/express

# Backend-only (Cloudflare Workers, serverless, etc.)
npm install @clerk/backend
```

### Step 2: Configure Environment Variables

```bash
# .env.local — never commit this file
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Optional: routing URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

Ensure `.env.local` is in `.gitignore`:

```bash
echo ".env.local" >> .gitignore
```

### Step 3: Add ClerkProvider (Next.js App Router)

```typescript
// app/layout.tsx
import { ClerkProvider, SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>
          <header className="flex justify-between p-4">
            <SignedOut>
              <SignInButton />
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
```

### Step 4: Add Middleware

```typescript
// middleware.ts (project root, NOT inside app/ or src/app/)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define which routes should be publicly accessible
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    // Skip Next.js internals and static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
```

### Step 5: Create Sign-In and Sign-Up Pages

```typescript
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  )
}
```

```typescript
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp />
    </div>
  )
}
```

### Step 6: Verify Connection

```typescript
// app/api/health/route.ts
import { auth } from '@clerk/nextjs/server'

export async function GET() {
  const { userId } = await auth()
  return Response.json({
    clerkConnected: true,
    authenticated: !!userId,
    userId: userId || null,
  })
}
```

### React SPA Setup (Vite)

```typescript
// src/main.tsx
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY in .env')
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
    <App />
  </ClerkProvider>
)
```

### Express Setup

```typescript
// server.ts
import express from 'express'
import { clerkMiddleware, requireAuth, getAuth } from '@clerk/express'

const app = express()

// Apply Clerk middleware globally — attaches auth to all requests
app.use(clerkMiddleware())

// Public route
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' })
})

// Protected route — redirects unauthenticated requests
app.get('/api/profile', requireAuth(), (req, res) => {
  const { userId } = getAuth(req)
  res.json({ userId })
})

app.listen(3001, () => console.log('Server running on :3001'))
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing publishableKey` | Env var not set | Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `.env.local` |
| `ClerkProvider must wrap your application` | Hook used outside provider | Ensure `ClerkProvider` wraps root layout |
| `auth() was called but Clerk can't detect clerkMiddleware()` | Middleware not running | Place `middleware.ts` at project root, check matcher |
| `Module not found: @clerk/nextjs` | Package not installed | Run `npm install @clerk/nextjs` |
| 500 error on all pages | `CLERK_SECRET_KEY` missing or wrong | Verify key prefix matches environment (`sk_test_` for dev) |

## Enterprise Considerations

- Use separate Clerk instances per environment (dev/staging/prod)
- Store keys in platform secrets (Vercel, AWS Secrets Manager), never in `.env` files committed to git
- The `CLERK_SECRET_KEY` must never be exposed client-side; only `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is safe for browsers
- For monorepos, install `@clerk/nextjs` only in the app that needs it; use `@clerk/backend` for shared server packages
- Enable Clerk's "Enhanced email deliverability" in production for reliable transactional emails

## Resources

- [Next.js Quickstart](https://clerk.com/docs/nextjs/getting-started/quickstart)
- [React Quickstart](https://clerk.com/docs/quickstarts/react)
- [Express Quickstart](https://clerk.com/docs/quickstarts/express)
- Clerk Dashboard

## Next Steps

Proceed to `clerk-hello-world` for your first authenticated request.

## Output

- Installed Clerk SDK/packages for the target stack
- Auth routes/middleware wired and smoke-tested sign-in/sign-out
- Documented env vars and local-dev secrets posture (never commit real keys)

## Examples

### Fresh install on Next.js

```
User: Install Clerk auth from zero on this Next.js repo.
Skill: adds dependencies, env template, middleware, and a protected smoke route.
```

### Repair a half-finished install

```
User: Clerk packages are present but middleware never runs.
Skill: fixes matcher config, provider placement, and env loading order.
```
