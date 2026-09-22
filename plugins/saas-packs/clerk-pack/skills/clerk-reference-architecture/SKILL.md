---
name: clerk-reference-architecture
description: 'Reference architecture patterns for Clerk authentication.

  Use when designing application architecture, planning auth flows,

  or implementing enterprise-grade authentication.

  Trigger with phrases like "clerk architecture", "clerk design",

  "clerk system design", "clerk integration patterns".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- authentication
compatibility: Designed for Claude Code
---
# Clerk Reference Architecture

## Overview

Reference architectures for implementing Clerk in common application patterns: Next.js full-stack, microservices with shared auth, multi-tenant SaaS, and mobile + web with shared backend.

## Prerequisites

- Understanding of web application architecture
- Familiarity with authentication patterns (JWT, sessions, OAuth)
- Knowledge of your tech stack and scaling requirements

## Instructions

### Architecture 1: Next.js Full-Stack Application

```
Browser
  │
  ├─▸ Next.js Middleware (clerkMiddleware)
  │     └─▸ Validates session token on every request
  │
  ├─▸ Server Components (auth(), currentUser())
  │     └─▸ Direct access to user data, no network call
  │
  ├─▸ Client Components (useUser(), useAuth())
  │     └─▸ Real-time auth state via ClerkProvider
  │
  ├─▸ API Routes (auth() for userId, getToken() for JWT)
  │     └─▸ Call external services with Clerk JWT
  │
  └─▸ Webhooks (/api/webhooks/clerk)
        └─▸ Sync user data to database
```

```typescript
// app/layout.tsx — entry point
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html><body>{children}</body></html>
    </ClerkProvider>
  )
}
```

```typescript
// middleware.ts — auth boundary
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublic = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)', '/api/webhooks(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublic(req)) await auth.protect()
})
```

### Architecture 2: Microservices with Shared Auth

```
Browser ─▸ API Gateway / BFF (Next.js + Clerk)
              │
              ├─▸ Service A (Node.js) ──── verifies JWT
              ├─▸ Service B (Python) ──── verifies JWT
              └─▸ Service C (Go) ──────── verifies JWT
```

```typescript
// BFF: Generate service-specific JWT
// app/api/proxy/[service]/route.ts
import { auth } from '@clerk/nextjs/server'

export async function GET(req: Request, { params }: { params: { service: string } }) {
  const { userId, getToken } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })

  // Get JWT with service-specific claims
  const token = await getToken({ template: params.service })

  const serviceUrls: Record<string, string> = {
    billing: process.env.BILLING_SERVICE_URL!,
    analytics: process.env.ANALYTICS_SERVICE_URL!,
    notifications: process.env.NOTIFICATION_SERVICE_URL!,
  }

  const response = await fetch(`${serviceUrls[params.service]}/api/data`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  return Response.json(await response.json())
}
```

```typescript
// Downstream service: Verify Clerk JWT
// services/billing/src/middleware.ts (Express)
import { clerkMiddleware, requireAuth } from '@clerk/express'

app.use(clerkMiddleware())
app.get('/api/data', requireAuth(), (req, res) => {
  // req.auth.userId is available
  res.json({ userId: req.auth.userId })
})
```

### Architecture 3: Multi-Tenant SaaS

```
Tenant A (org_abc) ──┐
Tenant B (org_def) ──┤──▸ Shared App ──▸ Shared DB (tenant-scoped queries)
Tenant C (org_ghi) ──┘
```

```typescript
// lib/tenant.ts — tenant-scoped data access
import { auth } from '@clerk/nextjs/server'

export async function getTenantData<T>(query: (orgId: string) => Promise<T>): Promise<T> {
  const { orgId } = await auth()
  if (!orgId) throw new Error('No organization selected')
  return query(orgId)
}

// Usage:
export async function getProjects() {
  return getTenantData((orgId) =>
    db.project.findMany({ where: { organizationId: orgId } })
  )
}
```

```typescript
// middleware.ts — enforce org context on tenant routes
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isTenantRoute = createRouteMatcher(['/app(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (isTenantRoute(req)) {
    const { orgId } = await auth.protect()
    if (!orgId) {
      // Redirect to org selector if no org is active
      return Response.redirect(new URL('/select-org', req.url))
    }
  }
})
```

```typescript
// app/select-org/page.tsx
import { OrganizationSwitcher } from '@clerk/nextjs'

export default function SelectOrg() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div>
        <h1>Select Your Organization</h1>
        <OrganizationSwitcher
          afterSelectOrganizationUrl="/app/dashboard"
          hidePersonal={true}
        />
      </div>
    </div>
  )
}
```

### Architecture 4: Mobile + Web with Shared Backend

```
Web App (Next.js + @clerk/nextjs)  ──┐
Mobile App (React Native + @clerk/clerk-expo) ──┤──▸ Backend API (Express + @clerk/express)
                                                └──▸ Database
```

```typescript
// Backend API: Express with Clerk
// server.ts
import express from 'express'
import { clerkMiddleware, requireAuth, getAuth } from '@clerk/express'

const app = express()

// Apply Clerk middleware globally
app.use(clerkMiddleware())

// Public endpoint
app.get('/api/public', (req, res) => {
  res.json({ message: 'Public endpoint' })
})

// Protected endpoint (works with both web and mobile clients)
app.get('/api/profile', requireAuth(), async (req, res) => {
  const { userId } = getAuth(req)
  const user = await db.user.findUnique({ where: { clerkId: userId } })
  res.json({ user })
})

app.listen(3001)
```

## Output

- Next.js full-stack architecture with middleware, server/client components, and webhooks
- Microservices architecture with BFF proxy and JWT-based service auth
- Multi-tenant SaaS with organization-scoped data access
- Mobile + web with shared Express backend using `@clerk/express`

## Error Handling

| Pattern | Common Issue | Solution |
|---------|-------------|----------|
| Full-stack | Middleware redirect loop | Add sign-in route to public routes |
| Microservices | JWT template not configured | Create JWT template in Dashboard per service |
| Multi-tenant | No org selected | Redirect to org selector before tenant routes |
| Mobile + Web | Token not sent from mobile | Include `Authorization: Bearer <token>` in mobile fetch |

## Examples

### Database Schema for Clerk Integration

```prisma
// prisma/schema.prisma
model User {
  id        String   @id @default(cuid())
  clerkId   String   @unique
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  posts     Post[]
  orgMemberships OrgMembership[]
}

model OrgMembership {
  id     String @id @default(cuid())
  userId String
  orgId  String  // Clerk organization ID
  role   String  // org:admin, org:member, etc.
  user   User   @relation(fields: [userId], references: [id])
  @@unique([userId, orgId])
}
```

## Resources

- [Clerk Architecture Patterns](https://clerk.com/docs/quickstarts/nextjs)
- [Clerk Organizations (Multi-Tenant)](https://clerk.com/docs/organizations/overview)
- [Clerk Express Integration](https://clerk.com/docs/quickstarts/express)

## Next Steps

Proceed to `clerk-multi-env-setup` for multi-environment configuration.
