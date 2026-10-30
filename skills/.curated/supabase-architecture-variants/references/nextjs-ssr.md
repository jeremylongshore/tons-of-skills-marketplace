# Next.js SSR (App Router with Server and Client Components)

Next.js App Router requires **two separate clients**: a server-side client using cookies for auth (with `@supabase/ssr`) and a browser client for client components. Use a publishable key (or legacy anon key) for both user clients. Keep privileged credentials in a separate server-only module, without user cookies. Create a server client per request; never share user sessions or cache authenticated responses across users.

## Server-Side Client (for Server Components, Route Handlers, Server Actions)

```typescript
// lib/supabase/server.ts
import 'server-only'
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '../database.types'

export async function createSupabaseServer({ readOnly = false } = {}) {
  const cookieStore = await cookies()
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
    ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  if (!key) throw new Error('Missing Supabase publishable or anon key')

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    key,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          if (readOnly) {
            throw new Error('Session refresh requires a cookie-writable Proxy or route')
          }
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options)
          }
        },
      },
    }
  )
}

```

Use the writable mode only in Route Handlers or Server Actions. Server Components call `createSupabaseServer({ readOnly: true })` after Proxy/session refresh. A refresh attempted in read-only mode fails; it is not silently dropped. Configure the framework's cookie propagation before rendering and do not cache session-bearing responses.

## Separate Privileged Client Boundary

```typescript
// lib/supabase/admin.ts — never re-export through a browser/shared entry point.
import 'server-only'
import { createClient } from '@supabase/supabase-js'
import type { Database } from '../database.types'

export function createSupabaseAdmin() {
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } }
  )
}
```

This client bypasses RLS. It does not establish an end user's identity or authorize an operation. Do not attach cookies or user sessions; keep privileged operations behind their own application-owned authorization.

## Client-Side Client (for Client Components)

```typescript
// lib/supabase/client.ts
'use client'

import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '../database.types'

let client: ReturnType<typeof createBrowserClient<Database>> | null = null

export function createSupabaseBrowser() {
  if (client) return client

  client = createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
      ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)! // Public project key, not privileged
  )

  return client
}
```

## Proxy for Auth Session Refresh

```typescript
// proxy.ts — older Next.js releases call this middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function proxy(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
      ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // Fresh server-confirmed identity; do not trust getSession().user from cookies.
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) {
    const denied = NextResponse.redirect(new URL('/login', request.url))
    for (const cookie of response.cookies.getAll()) denied.cookies.set(cookie)
    denied.headers.set('Cache-Control', 'private, no-store')
    return denied
  }
  response.headers.set('Cache-Control', 'private, no-store')

  return response
}

export const config = {
  matcher: ['/dashboard/:path*'], // Protect only reviewed routes; avoid login redirect loops.
}
```

## Server Component Usage

```typescript
// app/dashboard/page.tsx
import { createSupabaseServer } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const supabase = await createSupabaseServer({ readOnly: true })

  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) redirect('/login')

  const { data: projects, error } = await supabase
    .from('projects')
    .select('id, name, status, created_at')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })

  if (error) throw new Error(`Failed to load projects: ${error.message}`)

  return (
    <div>
      <h1>My Projects</h1>
      {projects.map(p => <ProjectCard key={p.id} project={p} />)}
    </div>
  )
}
```

## Read-Only Account-Deletion Subject Preflight

A Server Action is an externally callable endpoint; its name or module location is not authorization. This preflight accepts no target user ID and performs no deletion or eligibility decision.

```typescript
// app/actions/account.ts
'use server'

import { createSupabaseServer } from '@/lib/supabase/server'

export async function getAccountDeletionSubject() {
  const supabase = await createSupabaseServer({ readOnly: true })
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) throw new Error('Authentication required')
  return { userId: user.id }
}
```

Before implementing any destructive action, separately review:

- Application-owned eligibility and authorization, fresh identity, request protections, and explicit user confirmation; do not accept an arbitrary target ID as authorization.
- Database cascades/retention and Storage ownership. Auth-user removal is not an atomic application-and-Storage cleanup transaction.
- Idempotent retries and recovery after partial failures; do not treat successful data deletion as successful Auth deletion.
- Outstanding access tokens: deleting an Auth user does not immediately invalidate an already-issued JWT. Sensitive operations need a reviewed session/access-revocation strategy.

This example deliberately supplies no executable deletion action. See [Next.js data security](https://nextjs.org/docs/app/guides/data-security) and [Supabase user management](https://supabase.com/docs/guides/auth/managing-user-data).

## Auth Callback Route (OAuth / magic link exchange)

```typescript
// app/auth/callback/route.ts
import { createSupabaseServer } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')

  if (code) {
    const supabase = await createSupabaseServer()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (error) {
      const denied = NextResponse.redirect(new URL('/login?error=auth_failed', request.url))
      denied.headers.set('Cache-Control', 'private, no-store')
      return denied
    }
  }

  const response = NextResponse.redirect(new URL('/dashboard', request.url))
  response.headers.set('Cache-Control', 'private, no-store')
  return response
}
```

## Primary SSR Contract

Follow the [current Supabase Next.js adapter](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=nextjs) for your framework release. The examples use `getUser()` for a fresh Auth-server lookup; current `getClaims()` verifies token identity, while `getSession()` alone does not verify cookie-supplied user data. Preserve refreshed cookies on the response actually returned and exclude session-bearing responses from shared caches.

These examples set manual `private, no-store` response headers on authentication paths. Do not enable ISR for authenticated pages, and verify the deployed CDN policy does not override origin headers. The [advanced SSR guide](https://supabase.com/docs/guides/auth/server-side/advanced-guide) also describes applying the cache headers passed to `setAll` by current SDK versions.
