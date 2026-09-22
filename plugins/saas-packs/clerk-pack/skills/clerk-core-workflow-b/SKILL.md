---
name: clerk-core-workflow-b
description: 'Implement session management and middleware with Clerk.

  Use when managing user sessions, configuring route protection,

  or implementing token refresh and custom JWT templates.

  Trigger with phrases like "clerk session", "clerk middleware",

  "clerk route protection", "clerk token", "clerk JWT".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- clerk-core
- sessions
- middleware
compatibility: Designed for Claude Code
---
# Clerk Core Workflow B: Session & Middleware

## Overview

Implement session management and route protection with Clerk middleware. Covers
`clerkMiddleware()` configuration, `auth()` patterns, custom session claims, JWT
templates for external services, organization-scoped sessions, and session token v2.

Use when managing user sessions, configuring route protection, or implementing
token refresh and custom JWT templates.

## Prerequisites

- `@clerk/nextjs` installed with ClerkProvider wrapping the app
- Next.js 14+ with App Router (or adapt patterns for your stack)
- Working publishable + secret Clerk keys in env

## Instructions

1. Confirm ClerkProvider and env keys are live (see `clerk-install-auth` / `clerk-hello-world`).
2. Configure `clerkMiddleware()` matcher / public routes for the routes you want open.
3. Use `auth()` / `currentUser()` on protected pages and API routes; fail closed when unauthenticated.
4. For custom claims or external JWT consumers, configure session token templates carefully (size limits).
5. For org-scoped apps, bind authorization to org id + role claims, not only user id.
6. Verify: signed-out user cannot hit protected routes; signed-in user can; org role gates hold.

Deep patterns, JWT templates, and edge cases: [session-middleware-deep-dive.md](references/session-middleware-deep-dive.md).

## Output

- Session/middleware configuration enforcing the requested protection rules
- Documented JWT/session claim changes when customized
- Verification steps for protected vs public routes

## Examples

### Protect all routes except marketing

```
User: Protect everything except /, /pricing, and Clerk sign-in routes.
Skill: configures clerkMiddleware publicRoutes / matcher and verifies unauth redirect.
```

### Custom session claim for plan tier

```
User: Put plan_tier on the session JWT for feature flags.
Skill: configures session token template and validates claim size + read path.
```

## Error Handling

| Condition | Response |
|---|---|
| Route is accidentally public | Fail the verification gate and narrow the matcher before release. |
| Session claim is absent or stale | Treat the request as unauthorized for the dependent feature and refresh through the supported path. |
| JWT exceeds consumer limits | Remove nonessential claims; retrieve server-side attributes through an authorized backend. |
| Organization context is missing | Deny the org-scoped operation and require explicit selection/role validation. |

## Resources

- [Clerk middleware reference](https://clerk.com/docs/references/nextjs/clerk-middleware)
- [Session tokens and custom claims](https://clerk.com/docs/guides/sessions/session-tokens)
- [Clerk organization roles](https://clerk.com/docs/guides/organizations/roles-and-permissions)
