# Examples — Multi-Tenant Setup and Job Queue Consumer

## Complete Multi-Tenant Setup (TypeScript)

```typescript
// Use the current request's authenticated, non-admin client.
import { getSupabaseServer } from './supabase-server'

export async function readTenantProjects(tenantId: string) {
  const supabase = await getSupabaseServer()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) throw new Error('Authentication required')

  const { data, error } = await supabase.from('projects')
    .select('id, name, created_at')
    .eq('org_id', tenantId) // Query scope only; membership RLS authorizes access.
    .order('created_at', { ascending: false })
  if (error) throw new Error('Project query failed')
  return data
}
```

## Job Queue Consumer (TypeScript)

```typescript
import { getSupabaseAdmin } from './admin'

async function processJobs() {
  const supabase = getSupabaseAdmin()

  while (true) {
    // Atomically claim the next job
    const { data: job, error } = await supabase
      .rpc('claim_next_job', { p_job_type: 'send-email' })

    if (error || !job) {
      // No jobs available — wait before polling again
      await new Promise(r => setTimeout(r, 5000))
      continue
    }

    try {
      // Process the job
      console.log(`Processing job ${job.id}:`, job.payload)
      await sendEmail(job.payload)

      // Mark complete
      await supabase
        .from('job_queue')
        .update({ status: 'completed', completed_at: new Date().toISOString() })
        .eq('id', job.id)
    } catch (err) {
      // Mark failed — pg_cron will retry if attempts < max_attempts
      await supabase
        .from('job_queue')
        .update({
          status: 'failed',
          error_message: err instanceof Error ? err.message : String(err)
        })
        .eq('id', job.id)
    }
  }
}

async function sendEmail(payload: Record<string, unknown>) {
  console.log('Sending email to:', payload.to)
}

processJobs().catch(console.error)
```

## SvelteKit Integration

Use a request-scoped cookie adapter, not a raw `Cookie` header. Keep privileged clients in a separate server-only module, never in ordinary request locals.

```typescript
// src/hooks.server.ts — application supplies its Database and App.Locals types.
import { createServerClient } from '@supabase/ssr'
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_PUBLISHABLE_KEY } from '$env/static/public'
import type { Handle } from '@sveltejs/kit'
import type { Database } from '@my-platform/supabase'

export const handle: Handle = async ({ event, resolve }) => {
  event.locals.supabase = createServerClient<Database>(
    PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_PUBLISHABLE_KEY, {
      cookies: {
        getAll: () => event.cookies.getAll(),
        setAll: (updates) => {
          for (const { name, value, options } of updates) {
            event.cookies.set(name, value, { ...options, path: '/' })
          }
        }
      }
    }
  )
  const response = await resolve(event)
  // Manual cache protection also covers resolved error/redirect responses.
  const headers = new Headers(response.headers)
  headers.set('Cache-Control', 'private, no-store')
  return new Response(response.body, {
    status: response.status, statusText: response.statusText, headers
  })
}
```

Each protected server load/action must call `event.locals.supabase.auth.getUser()` and reject errors or an absent user before using user data. This hook alone does not authorize a route. Use the configured legacy anon key if the project has not adopted publishable keys; never use a service-role key for this client. Follow the [current SvelteKit adapter](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=sveltekit) for framework typing and response handling.

The hook applies manual `private, no-store` protection rather than relying on `setAll` cache-header arguments. Disable shared/CDN caching for authenticated routes and verify the deployed cache policy; a CDN configuration can override origin headers.
