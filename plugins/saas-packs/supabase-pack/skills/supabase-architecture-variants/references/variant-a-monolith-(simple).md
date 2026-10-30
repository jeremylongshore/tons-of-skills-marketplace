# Variant A: Monolith (Simple)

A single deployment can simplify a small application's operations; a DAU threshold
alone does not prove its capacity. Separate browser client reuse from server request
identity. A cookie-authenticated server route needs a request-scoped client, not a
shared mutable user session or a service-role client with an untrusted user ID.

## Code Pattern: Authenticated Read

This framework-independent handler receives a request-scoped user client supplied
by the application's cookie adapter. The existing `projects` table needs an
`owner_id` column and RLS that enforces the same ownership boundary. A query filter
alone is not authorization. The caller handles the returned response; no generic
`supabaseClient.create()` API exists.

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';

export async function listOwnProjects(client: SupabaseClient) {
  const {
    data: { user },
    error: authError,
  } = await client.auth.getUser();
  if (authError || !user) return new Response('Unauthorized', { status: 401 });
  const { data, error } = await client
    .from('projects')
    .select('id, name')
    .eq('owner_id', user.id)
    .limit(50);
  if (error) return new Response('Query failed', { status: 503 });
  return Response.json({ projects: data });
}
```

Keep migrations, routes, and tests in the same application if appropriate. Cache
only public or correctly user/tenant-scoped results, with bounded lifetimes. Treat
admin operations as separately authorized server-only workflows.

[SSR client setup](https://supabase.com/docs/guides/auth/server-side/creating-a-client)
[Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
