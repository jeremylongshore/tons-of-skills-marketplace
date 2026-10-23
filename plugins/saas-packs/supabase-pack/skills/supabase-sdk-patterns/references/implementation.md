# Client Initialization and Returned Errors

## Scope the Client to the Identity

Use `createClient(url, key, options)` for an HTTP client. Reuse an appropriate
browser client, but do not reuse mutable user sessions across unrelated server
requests. Cookie-authenticated SSR needs a request-scoped `@supabase/ssr` client;
see [the SSR example](https://supabase.com/docs/guides/auth/server-side/creating-a-client).
This qualification is essential when applying the parent skill's singleton advice.

The following stateless client is for an existing public/authorized table, not
privileged admin operations or cookie-session authentication.

```typescript
import { createClient } from '@supabase/supabase-js';

export function createPublicReadClient(url: string, publishableKey: string) {
  return createClient(url, publishableKey, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
}

export async function readProducts(url: string, publishableKey: string) {
  const client = createPublicReadClient(url, publishableKey);
  const { data, error } = await client.from('products').select('id, name').limit(10);
  if (error) throw error;
  return data;
}
```

## Respect Each API's Error Contract

Database queries normally return `{ data, error }`; check `error` before consuming
data. Catch transport/application exceptions at the caller boundary as needed.
There is no generic exported `SupabaseError` covering every SDK service, and not
every SDK operation has the database-query return shape. Python has its own response
and exception contracts. Do not wrap an unchecked `{ error }` result as successful
`data`, and do not assume a catch block alone detects a failed query.

## Retry Only Explicitly Safe Operations

Do not apply a catch-all retry wrapper to every operation. Authentication/RLS and
validation failures need correction, not repetition. For a transient failure of an
idempotent read, use a bounded retry budget with backoff and preserve the final
returned error. Writes require a deliberate idempotency/transaction design before
retrying; a timed-out write may already have committed. Do not retry a mutation
merely because the client returned an error or threw.

[JavaScript initialization](https://supabase.com/docs/reference/javascript/initializing)
[JavaScript error handling](https://supabase.com/docs/reference/javascript/select)

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
