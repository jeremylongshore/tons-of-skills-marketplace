---
name: clerk-incident-runbook
description: 'Manage incident response for Clerk authentication issues.

  Use when handling auth outages, security incidents,

  or production authentication problems.

  Trigger with phrases like "clerk incident", "clerk outage",

  "clerk down", "auth not working", "clerk emergency".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(curl:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- security
- authentication
- incident-response
compatibility: Designed for Claude Code
---
# Clerk Incident Runbook

## Overview

Procedures for responding to Clerk-related incidents in production. Covers triage, emergency auth bypass, recovery scripts, and post-incident review.

## Prerequisites

- Access to Clerk Dashboard (dashboard.clerk.com)
- Access to application logs and monitoring
- Emergency contact list for on-call team
- Rollback procedures documented

## Instructions

### Step 1: Triage — Identify Incident Category

| Category | Symptoms | Severity |
|----------|----------|----------|
| Clerk outage | status.clerk.com shows incident, all auth fails | Critical |
| Key compromise | Unauthorized access detected | Critical |
| Middleware failure | All routes return 500 | High |
| Session issues | Users randomly logged out | Medium |
| Webhook backlog | User sync falling behind | Low |

Quick diagnostic:

```bash
#!/bin/bash
# scripts/clerk-triage.sh
set -euo pipefail

echo "=== Clerk Incident Triage ==="
echo "Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. Check Clerk status
echo -e "\n--- Clerk Status ---"
curl -s https://status.clerk.com/api/v2/status.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"Status: {d['status']['description']}\")" 2>/dev/null || echo "Cannot reach status API"

# 2. Check API connectivity
echo -e "\n--- API Connectivity ---"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${CLERK_SECRET_KEY}" \
  https://api.clerk.com/v1/users?limit=1 2>/dev/null)
echo "API response: HTTP $HTTP_CODE"

# 3. Check app health
echo -e "\n--- App Health ---"
curl -s http://localhost:3000/api/clerk-health 2>/dev/null | python3 -m json.tool || echo "App not reachable"
```

### Step 2: Emergency Auth Bypass (Clerk Outage Only)

```typescript
// middleware.ts — emergency bypass mode
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const EMERGENCY_BYPASS = process.env.CLERK_EMERGENCY_BYPASS === 'true'

const isPublicRoute = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)'])

export default clerkMiddleware(async (auth, req) => {
  // Emergency bypass: allow all requests when Clerk is down
  if (EMERGENCY_BYPASS) {
    console.warn('[EMERGENCY] Auth bypass active — all requests allowed')
    const response = NextResponse.next()
    response.headers.set('X-Auth-Bypass', 'true')
    return response
  }

  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})
```

Activate bypass:

```bash
# Vercel: set env var and redeploy
vercel env add CLERK_EMERGENCY_BYPASS production  # Set to "true"
vercel deploy --prod

# After Clerk recovers: remove bypass
vercel env rm CLERK_EMERGENCY_BYPASS production
vercel deploy --prod
```

### Step 3: Key Rotation (Compromised Secret Key)

```bash
#!/bin/bash
# scripts/rotate-clerk-keys.sh
set -euo pipefail

echo "=== Clerk Key Rotation ==="
echo "1. Go to dashboard.clerk.com > API Keys"
echo "2. Generate new Secret Key"
echo "3. Update all environments:"

# Update production
echo "Updating production..."
# vercel env rm CLERK_SECRET_KEY production
# vercel env add CLERK_SECRET_KEY production  # Paste new key
# vercel deploy --prod

echo "4. Verify all endpoints still work"
echo "5. Monitor for unauthorized access attempts"
echo "6. File incident report"
```

### Step 4: Session Recovery (Mass Logout Fix)

```typescript
// app/api/admin/refresh-sessions/route.ts
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function POST() {
  const { has } = await auth()
  if (!has({ role: 'org:admin' })) {
    return Response.json({ error: 'Admin only' }, { status: 403 })
  }

  // Force-revoke all sessions (users will need to re-authenticate)
  const client = await clerkClient()
  const users = await client.users.getUserList({ limit: 500 })
  let revoked = 0

  for (const user of users.data) {
    const sessions = await client.sessions.getSessionList({ userId: user.id })
    for (const session of sessions.data) {
      if (session.status === 'active') {
        await client.sessions.revokeSession(session.id)
        revoked++
      }
    }
  }

  return Response.json({ revoked, message: `Revoked ${revoked} sessions` })
}
```

### Step 5: Webhook Replay (Missed Events)

```bash
# Check for missed webhooks in Clerk Dashboard:
# Dashboard > Webhooks > Select endpoint > Message Logs
# Click "Retry" on failed messages

# Or replay from your audit log:
echo "Check database for missing user records:"
echo "SELECT clerk_id FROM users WHERE created_at > NOW() - INTERVAL '1 hour'"
```

### Step 6: Post-Incident Review Template

```markdown
## Incident Report

**Date:** YYYY-MM-DD HH:MM UTC
**Duration:** X hours Y minutes
**Severity:** Critical / High / Medium / Low
**Category:** Clerk Outage / Key Compromise / Config Error / Middleware Failure

### Timeline
- HH:MM — Incident detected (how: monitoring alert / user report / manual)
- HH:MM — Triage started, category identified
- HH:MM — Mitigation applied (emergency bypass / key rotation / rollback)
- HH:MM — Service restored
- HH:MM — Post-incident review completed

### Root Cause
[Description of what caused the incident]

### Impact
- Users affected: X
- Duration of auth downtime: Y minutes
- Data loss: None / Partial / Details

### Action Items
- [ ] Add monitoring for [specific check]
- [ ] Update runbook with [new procedure]
- [ ] Implement [preventive measure]
```

## Output

- Triage script identifying incident category and severity
- Emergency auth bypass middleware (activate via env var)
- Key rotation procedure for compromised credentials
- Session revocation endpoint for mass-logout recovery
- Post-incident review template

## Error Handling

| Scenario | Response |
|----------|----------|
| Clerk API completely down | Activate emergency bypass, monitor status.clerk.com |
| Secret key compromised | Rotate keys immediately, revoke all sessions, audit logs |
| Middleware 500 errors | Check middleware.ts syntax, verify Clerk SDK version |
| Webhook delivery failures | Retry from Dashboard, check endpoint accessibility |
| Users randomly logged out | Check session lifetime settings, verify domain config |

## Examples

### Quick Status Check One-Liner

```bash
curl -s https://status.clerk.com/api/v2/status.json | python3 -c "import json,sys; print(json.load(sys.stdin)['status']['description'])"
```

## Resources

- [Clerk Status Page](https://status.clerk.com)
- [Clerk Support](https://clerk.com/support)
- [Clerk Discord](https://clerk.com/discord)

## Next Steps

After resolving incident, review `clerk-observability` for improved monitoring.
