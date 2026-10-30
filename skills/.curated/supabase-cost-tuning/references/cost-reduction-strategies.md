# Cost Reduction Strategies

## Batch Reads Through the Data API

Supabase JS has no generic `get()`, `batchGet()`, or `trackEvent()` client methods.
Use the documented table query interface and check its returned error. This example
assumes an application-owned `products(id, name)` table with appropriate RLS.

```typescript
import { createClient } from '@supabase/supabase-js';

export async function readProducts(url: string, publishableKey: string, ids: string[]) {
  if (ids.length === 0) return [];
  const client = createClient(url, publishableKey, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  const { data, error } = await client.from('products').select('id, name').in('id', ids);
  if (error) throw error;
  return data;
}
```

A single query can still encounter row/URL/payload limits. Bound the caller's ID
batch, paginate when needed, and measure actual requests and returned bytes. Do not
promise that every input ID appears: RLS, missing rows, and configured limits apply.
Authenticated applications must use their user-scoped client rather than a public
probe or privileged key. Do not sample required audit records, billing events, or
security controls to reduce costs.

## Cache Only Within the Correct Trust Boundary

Use explicit column selection, query filters, and bounded pagination before adding
caches. If caching authorized results, include the user/tenant authorization context
in cache keys, set TTL/invalidation rules, and avoid sharing private results across
users. Revalidate permissions rather than treating a cache entry as authorization.

## Reduce Payloads Without Invented SDK Options

There is no `compression: true` SupabaseClient option. Optimize image/file bytes
before upload where appropriate, use documented Storage transforms where supported,
and inspect actual HTTP/cache behavior. Verify current project usage and invoices;
these patterns do not establish a fixed saving or change a plan's billing rules.

[Query filters](https://supabase.com/docs/reference/javascript/using-filters)
