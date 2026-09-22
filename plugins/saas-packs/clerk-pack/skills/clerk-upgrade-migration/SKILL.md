---
name: clerk-upgrade-migration
description: 'Manage Clerk SDK version upgrades and handle breaking changes.

  Use when upgrading Clerk packages, migrating to new SDK versions,

  or handling deprecation warnings.

  Trigger with phrases like "upgrade clerk", "clerk migration",

  "update clerk SDK", "clerk breaking changes".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- migration
compatibility: Designed for Claude Code
---
# Clerk Upgrade & Migration

## Current State

!`npm list @clerk/nextjs @clerk/clerk-react @clerk/express 2>/dev/null | grep clerk || echo 'No Clerk packages found'`

## Overview

Safely upgrade Clerk SDK versions and handle breaking changes. Covers version checking, upgrade procedures, common migration patterns, and rollback planning.

## Prerequisites

- Current Clerk integration working
- Git repository with clean working state
- Test environment available for validation

## Instructions

### Step 1: Check Current Version and Available Updates

```bash
# Check installed version
npm list @clerk/nextjs

# Check latest available
npm view @clerk/nextjs version

# Check all Clerk packages and their versions
npm outdated | grep clerk
```

### Step 2: Review Breaking Changes

```bash
# View changelog for the target version
npx open-cli https://clerk.com/changelog

# Check GitHub releases for migration notes
npx open-cli https://github.com/clerk/javascript/releases
```

Key version milestones to watch for:

- **v5 to v6**: `auth()` became async (must `await auth()`)
- **v5 to v6**: `authMiddleware` renamed to `clerkMiddleware`
- **v5 to v6**: Import paths changed to `@clerk/nextjs/server`

### Step 3: Upgrade Process

```bash
# Create upgrade branch
git checkout -b chore/upgrade-clerk

# Upgrade all Clerk packages together (they must version-match)
npm install @clerk/nextjs@latest @clerk/themes@latest

# If using other Clerk packages:
# npm install @clerk/clerk-react@latest @clerk/express@latest @clerk/backend@latest

# Verify no version mismatches
npm list | grep clerk
```

### Step 4: Handle Common Migration Patterns

**v5 to v6: `auth()` is now async**

```typescript
// BEFORE (v5): auth() was synchronous
// const { userId } = auth()

// AFTER (v6): auth() returns a Promise
const { userId } = await auth()
```

Find all affected files:

```bash
# Search for synchronous auth() calls that need await
grep -rn "const.*= auth()" --include="*.ts" --include="*.tsx" | grep -v "await"
```

**v5 to v6: Middleware migration**

```typescript
// BEFORE (v5):
// import { authMiddleware } from '@clerk/nextjs'
// export default authMiddleware({ publicRoutes: ['/'] })

// AFTER (v6):
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher(['/'])

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})
```

**v5 to v6: Import path changes**

```typescript
// BEFORE:
// import { auth, currentUser } from '@clerk/nextjs'

// AFTER:
import { auth, currentUser } from '@clerk/nextjs/server'
```

Fix import paths across codebase:

```bash
# Find files using old import path
grep -rn "from '@clerk/nextjs'" --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v "/server"
```

### Step 5: Update Type Definitions

```typescript
// If using custom type extensions, update them
// BEFORE:
// declare module '@clerk/nextjs' { ... }

// AFTER:
declare module '@clerk/nextjs/server' {
  interface AuthObject {
    // Custom session claims type
    sessionClaims?: {
      metadata?: {
        role?: string
      }
    }
  }
}
```

### Step 6: Test Upgrade

```bash
# Build to catch type errors
npm run build

# Run tests
npm test

# Start dev server and test manually
npm run dev

# Test critical flows:
# 1. Sign in with email/password
# 2. Sign in with OAuth
# 3. Protected route access
# 4. API route authentication
# 5. Webhook endpoint
# 6. Sign out
```

### Step 7: Rollback Plan

```bash
# If upgrade fails, rollback to previous version
git stash  # Save any manual changes

# Install previous version
npm install @clerk/nextjs@5.x.x  # Replace with your previous version

# Or restore from git
git checkout main -- package.json package-lock.json
npm install

# Verify rollback works
npm run build && npm test
```

## Output

- Clerk SDK upgraded to latest version
- Breaking changes migrated (async auth, new middleware, import paths)
- Type definitions updated
- All tests passing
- Rollback procedure documented

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Type errors after upgrade | API signature changes | Add `await` to `auth()`, update imports |
| `authMiddleware is not exported` | Renamed in v6 | Use `clerkMiddleware` from `@clerk/nextjs/server` |
| `auth() returns Promise` | Now async in v6 | Add `await` to all `auth()` calls |
| Import not found | Path changed | Use `@clerk/nextjs/server` for server-side imports |
| Version mismatch | Clerk packages on different versions | Update all `@clerk/*` packages together |

## Examples

### Automated Migration Script

```bash
#!/bin/bash
# scripts/migrate-clerk-v6.sh
set -euo pipefail

echo "=== Clerk v5 to v6 Migration ==="

# 1. Fix auth() calls (add await)
echo "Adding await to auth() calls..."
find . -name "*.ts" -o -name "*.tsx" | xargs grep -l "const.*= auth()" 2>/dev/null | while read file; do
  sed -i 's/const \(.*\) = auth()/const \1 = await auth()/g' "$file"
  echo "  Fixed: $file"
done

# 2. Fix import paths
echo "Updating import paths..."
find . -name "*.ts" -o -name "*.tsx" | xargs grep -l "from '@clerk/nextjs'" 2>/dev/null | while read file; do
  if grep -q "auth\|currentUser\|clerkClient" "$file"; then
    sed -i "s/from '@clerk\/nextjs'/from '@clerk\/nextjs\/server'/g" "$file"
    echo "  Fixed: $file"
  fi
done

echo "Done. Run 'npm run build' to check for remaining issues."
```

## Resources

- [Clerk Changelog](https://clerk.com/changelog)
- Clerk Upgrade Guides
- [GitHub Releases](https://github.com/clerk/javascript/releases)

## Next Steps

After upgrade, review `clerk-ci-integration` for CI/CD updates.
