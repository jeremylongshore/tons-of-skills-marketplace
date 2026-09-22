---
name: clerk-data-handling
description: 'Handle user data, privacy, and GDPR compliance with Clerk.

  Use when implementing data export, user deletion,

  or privacy compliance features.

  Trigger with phrases like "clerk user data", "clerk GDPR",

  "clerk privacy", "clerk data export", "clerk delete user".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- compliance
compatibility: Designed for Claude Code
---
# Clerk Data Handling

## Overview

Manage user data, implement privacy features, and ensure GDPR/CCPA compliance using the Clerk Backend API. Covers data export, right to be forgotten, consent management, and audit logging.

## Prerequisites

- Clerk integration working
- Understanding of GDPR/CCPA requirements
- Database with user-related data linked by Clerk user IDs

## Instructions

### Step 1: User Data Export

```typescript
// app/api/privacy/export/route.ts
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function GET() {
  const { userId } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })

  const client = await clerkClient()
  const clerkUser = await client.users.getUser(userId)

  // Gather data from Clerk
  const clerkData = {
    id: clerkUser.id,
    emails: clerkUser.emailAddresses.map((e) => e.emailAddress),
    firstName: clerkUser.firstName,
    lastName: clerkUser.lastName,
    createdAt: clerkUser.createdAt,
    lastSignInAt: clerkUser.lastSignInAt,
    publicMetadata: clerkUser.publicMetadata,
  }

  // Gather data from your database
  const appData = await db.user.findUnique({
    where: { clerkId: userId },
    include: { posts: true, comments: true, preferences: true },
  })

  return Response.json({
    exportDate: new Date().toISOString(),
    clerkProfile: clerkData,
    applicationData: appData,
  })
}
```

### Step 2: User Deletion (Right to be Forgotten)

```typescript
// app/api/privacy/delete/route.ts
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function DELETE() {
  const { userId } = await auth()
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 })

  const deletionLog: { step: string; status: string }[] = []

  try {
    // 1. Delete application data first
    await db.comment.deleteMany({ where: { authorId: userId } })
    deletionLog.push({ step: 'comments', status: 'deleted' })

    await db.post.deleteMany({ where: { authorId: userId } })
    deletionLog.push({ step: 'posts', status: 'deleted' })

    await db.user.delete({ where: { clerkId: userId } })
    deletionLog.push({ step: 'app_user', status: 'deleted' })

    // 2. Delete from Clerk (this ends the session)
    const client = await clerkClient()
    await client.users.deleteUser(userId)
    deletionLog.push({ step: 'clerk_user', status: 'deleted' })

    // 3. Log deletion for compliance audit trail
    await db.auditLog.create({
      data: {
        action: 'USER_DELETED',
        subjectId: userId,
        details: JSON.stringify(deletionLog),
        timestamp: new Date(),
      },
    })

    return Response.json({ deleted: true, log: deletionLog })
  } catch (error) {
    return Response.json({ error: 'Partial deletion', log: deletionLog }, { status: 500 })
  }
}
```

### Step 3: Consent Management with Metadata

```typescript
// lib/consent.ts
import { clerkClient } from '@clerk/nextjs/server'

interface ConsentRecord {
  marketing: boolean
  analytics: boolean
  thirdParty: boolean
  updatedAt: string
}

export async function updateConsent(userId: string, consent: Partial<ConsentRecord>) {
  const client = await clerkClient()
  const user = await client.users.getUser(userId)
  const existing = (user.publicMetadata.consent as ConsentRecord) || {}

  const updated: ConsentRecord = {
    ...existing,
    ...consent,
    updatedAt: new Date().toISOString(),
  }

  await client.users.updateUser(userId, {
    publicMetadata: { ...user.publicMetadata, consent: updated },
  })

  return updated
}

export async function getConsent(userId: string): Promise<ConsentRecord | null> {
  const client = await clerkClient()
  const user = await client.users.getUser(userId)
  return (user.publicMetadata.consent as ConsentRecord) || null
}
```

### Step 4: Consent UI Component

```typescript
'use client'
import { useUser } from '@clerk/nextjs'
import { useState } from 'react'

export function ConsentManager() {
  const { user } = useUser()
  const consent = (user?.publicMetadata as any)?.consent || {}
  const [marketing, setMarketing] = useState(consent.marketing ?? false)
  const [analytics, setAnalytics] = useState(consent.analytics ?? true)

  const saveConsent = async () => {
    await fetch('/api/privacy/consent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ marketing, analytics }),
    })
  }

  return (
    <div>
      <h3>Privacy Preferences</h3>
      <label>
        <input type="checkbox" checked={marketing} onChange={(e) => setMarketing(e.target.checked)} />
        Marketing communications
      </label>
      <label>
        <input type="checkbox" checked={analytics} onChange={(e) => setAnalytics(e.target.checked)} />
        Analytics tracking
      </label>
      <button onClick={saveConsent}>Save Preferences</button>
    </div>
  )
}
```

### Step 5: Audit Logging via Webhooks

```typescript
// app/api/webhooks/clerk/route.ts (audit section)
async function logAuditEvent(evt: WebhookEvent) {
  const auditEntry = {
    eventType: evt.type,
    userId: 'user_id' in evt.data ? evt.data.user_id : evt.data.id,
    timestamp: new Date().toISOString(),
    metadata: JSON.stringify(evt.data),
  }

  await db.auditLog.create({ data: auditEntry })

  // Track compliance-relevant events
  if (['user.deleted', 'user.updated'].includes(evt.type)) {
    console.log(`[COMPLIANCE] ${evt.type} for user ${auditEntry.userId}`)
  }
}
```

## Output

- Data export API returning Clerk profile + application data
- User deletion cascade (app data, then Clerk, then audit log)
- Consent management stored in Clerk publicMetadata
- Privacy preferences UI component
- Audit logging for compliance events

## Error Handling

| Scenario | Action |
|----------|--------|
| Partial deletion failure | Log completed steps, retry failed services, alert ops team |
| Export timeout on large data | Queue export job, email user download link when ready |
| Consent sync failure | Retry with exponential backoff, fall back to local storage |
| Clerk API rate limit on bulk delete | Batch deletions with delays between requests |

## Examples

### Bulk User Data Cleanup Script

```typescript
// scripts/cleanup-orphaned-users.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function cleanupOrphanedDbUsers() {
  const dbUsers = await db.user.findMany({ select: { clerkId: true } })

  for (const dbUser of dbUsers) {
    try {
      await clerk.users.getUser(dbUser.clerkId)
    } catch (err: any) {
      if (err.status === 404) {
        console.log(`Orphaned user: ${dbUser.clerkId} — removing from DB`)
        await db.user.delete({ where: { clerkId: dbUser.clerkId } })
      }
    }
  }
}
```

## Resources

- [Clerk User API](https://clerk.com/docs/references/backend/user/get-user)
- [Clerk Metadata](https://clerk.com/docs/users/metadata)
- [GDPR Compliance Guide](https://gdpr.eu/checklist/)

## Next Steps

Proceed to `clerk-enterprise-rbac` for enterprise SSO and RBAC.
