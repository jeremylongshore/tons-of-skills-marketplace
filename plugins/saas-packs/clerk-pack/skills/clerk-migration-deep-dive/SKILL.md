---
name: clerk-migration-deep-dive
description: 'Migrate from other authentication providers to Clerk.

  Use when migrating from Auth0, Firebase, Supabase Auth, NextAuth,

  or custom authentication solutions.

  Trigger with phrases like "migrate to clerk", "clerk migration",

  "switch to clerk", "auth0 to clerk", "firebase auth to clerk".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- migration
- authentication
compatibility: Designed for Claude Code
---
# Clerk Migration Deep Dive

## Current State

!`npm list @auth0/nextjs-auth0 next-auth @supabase/auth-helpers-nextjs firebase 2>/dev/null | grep -E "auth0|next-auth|supabase|firebase" || echo 'No auth providers detected'`

## Overview

Comprehensive guide to migrating from Auth0, Firebase Auth, Supabase Auth, or NextAuth to Clerk. Covers user data export, bulk import, parallel running, and phased migration.

## Prerequisites

- Current auth provider access with admin/export permissions
- Clerk account with API keys
- Git repository with clean working state
- Migration timeline planned (recommend 2-4 weeks)

## Instructions

### Step 1: Export Users from Current Provider

**Auth0 Export:**

```bash
# Export users via Auth0 Management API
curl -s -H "Authorization: Bearer $AUTH0_TOKEN" \
  "https://$AUTH0_DOMAIN/api/v2/users?per_page=100&page=0" \
  | jq '[.[] | {email: .email, name: .name, picture: .picture, created_at: .created_at}]' \
  > auth0-users.json
```

**NextAuth (Prisma) Export:**

```typescript
// scripts/export-nextauth-users.ts
const users = await prisma.user.findMany({
  include: { accounts: true },
})
const exported = users.map((u) => ({
  email: u.email,
  name: u.name,
  image: u.image,
  provider: u.accounts[0]?.provider,
  createdAt: u.createdAt,
}))
await fs.writeFile('nextauth-users.json', JSON.stringify(exported, null, 2))
```

### Step 2: Import Users to Clerk

```typescript
// scripts/import-to-clerk.ts
import { createClerkClient } from '@clerk/backend'
import users from './auth0-users.json'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

interface MigrationResult {
  email: string
  status: 'created' | 'exists' | 'error'
  clerkId?: string
  error?: string
}

async function importUsers(): Promise<MigrationResult[]> {
  const results: MigrationResult[] = []

  for (const user of users) {
    try {
      const created = await clerk.users.createUser({
        emailAddress: [user.email],
        firstName: user.name?.split(' ')[0],
        lastName: user.name?.split(' ').slice(1).join(' '),
        skipPasswordRequirement: true, // User will set password on first sign-in
      })
      results.push({ email: user.email, status: 'created', clerkId: created.id })
      console.log(`Created: ${user.email} -> ${created.id}`)
    } catch (err: any) {
      if (err.status === 422) {
        results.push({ email: user.email, status: 'exists' })
      } else {
        results.push({ email: user.email, status: 'error', error: err.message })
      }
    }

    // Respect rate limits
    await new Promise((resolve) => setTimeout(resolve, 100))
  }

  return results
}

importUsers().then((results) => {
  const summary = {
    total: results.length,
    created: results.filter((r) => r.status === 'created').length,
    exists: results.filter((r) => r.status === 'exists').length,
    errors: results.filter((r) => r.status === 'error').length,
  }
  console.log('Migration summary:', summary)
  fs.writeFileSync('migration-results.json', JSON.stringify(results, null, 2))
})
```

### Step 3: Update Database References

```typescript
// scripts/update-db-references.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function updateDatabaseReferences() {
  // Get all users from your database
  const dbUsers = await db.user.findMany()

  for (const dbUser of dbUsers) {
    // Find corresponding Clerk user by email
    const clerkUsers = await clerk.users.getUserList({
      emailAddress: [dbUser.email],
    })

    if (clerkUsers.totalCount > 0) {
      const clerkUser = clerkUsers.data[0]
      await db.user.update({
        where: { id: dbUser.id },
        data: {
          clerkId: clerkUser.id,
          // Keep old auth ID for rollback
          legacyAuthId: dbUser.authProviderId,
        },
      })
      console.log(`Mapped: ${dbUser.email} -> ${clerkUser.id}`)
    }
  }
}
```

### Step 4: Replace Auth Code (NextAuth to Clerk Example)

```typescript
// BEFORE: NextAuth
// import { getServerSession } from 'next-auth'
// import { authOptions } from '@/lib/auth'
// const session = await getServerSession(authOptions)
// const userId = session?.user?.id

// AFTER: Clerk
import { auth } from '@clerk/nextjs/server'
const { userId } = await auth()
```

```typescript
// BEFORE: NextAuth client hook
// import { useSession } from 'next-auth/react'
// const { data: session } = useSession()

// AFTER: Clerk client hook
import { useUser } from '@clerk/nextjs'
const { user, isLoaded } = useUser()
```

```typescript
// BEFORE: NextAuth middleware
// export { default } from 'next-auth/middleware'
// export const config = { matcher: ['/dashboard(.*)'] }

// AFTER: Clerk middleware
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
const isProtected = createRouteMatcher(['/dashboard(.*)'])
export default clerkMiddleware(async (auth, req) => {
  if (isProtected(req)) await auth.protect()
})
```

### Step 5: Parallel Running (Optional Safety Net)

```typescript
// lib/auth-bridge.ts — run both auth systems during transition
import { auth as clerkAuth } from '@clerk/nextjs/server'

export async function getAuthUser() {
  // Try Clerk first (new system)
  const { userId: clerkUserId } = await clerkAuth()
  if (clerkUserId) {
    return { provider: 'clerk', userId: clerkUserId }
  }

  // Fall back to legacy system during migration window
  // const legacySession = await getLegacySession()
  // if (legacySession) return { provider: 'legacy', userId: legacySession.userId }

  return null
}
```

### Step 6: Cleanup After Migration

```bash
# After migration is verified (2+ weeks in production):
npm uninstall next-auth @auth0/nextjs-auth0  # Remove old auth packages
# Delete old auth files: pages/api/auth/[...nextauth].ts, lib/auth.ts
# Remove legacy database columns after confirming all users migrated
```

## Output

- User export from current auth provider (Auth0, NextAuth, Firebase)
- Bulk import script with rate limiting and error handling
- Database reference mapping (old auth IDs to Clerk IDs)
- Code migration examples (NextAuth to Clerk)
- Parallel running bridge for safe transition
- Cleanup checklist for removing old auth code

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Duplicate email on import | User already exists in Clerk | Skip (status: 'exists') or merge |
| Invalid email format | Dirty data from export | Clean/validate before import |
| Rate limited during import | Too many API calls | Add 100ms delay between creates |
| Password can't be migrated | Passwords are hashed | Use `skipPasswordRequirement`, user sets new password |
| OAuth accounts | Social login tokens non-transferable | Users re-link OAuth accounts on first Clerk sign-in |

## Examples

### Migration Verification Script

```typescript
// scripts/verify-migration.ts
async function verifyMigration() {
  const dbUsers = await db.user.findMany({ where: { clerkId: { not: null } } })
  const unmapped = await db.user.findMany({ where: { clerkId: null } })

  console.log(`Mapped: ${dbUsers.length}, Unmapped: ${unmapped.length}`)

  if (unmapped.length > 0) {
    console.log('Unmapped users:', unmapped.map((u) => u.email))
  }
}
```

## Resources

- [Clerk Migration Overview](https://clerk.com/docs/deployments/migrate-overview)
- Migrate from Auth0
- Migrate from NextAuth

## Next Steps

After migration, review `clerk-prod-checklist` for production readiness.
