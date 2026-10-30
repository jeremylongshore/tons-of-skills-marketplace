# Client Examples by Trust Boundary

## Browser Client and Authenticated Server Requests

A browser client can be reused within one browser session. A tenant ID supplied by
a browser is not permission to select another project's credentials. Do not cache
mutable authenticated clients in a global tenant map on a server.

```typescript
import { createBrowserClient } from '@supabase/ssr';

export function createAppBrowserClient(url: string, publishableKey: string) {
  return createBrowserClient(url, publishableKey);
}
```

For a cookie-authenticated server request, use a request-scoped `createServerClient`
from `@supabase/ssr` with the framework's supported cookie adapter and validated user
identity. See [the SSR reference](https://supabase.com/docs/guides/auth/server-side/creating-a-client).
Privileged admin clients belong in isolated server-only code after authorization;
server execution alone does not authorize an operation.

## Python Public Read

`supabase-py` uses `create_client(url, key)`, not a zero-argument `SupabaseClient()`
constructor. This example assumes an existing public/authorized `products(id, name)`
table and does not establish an authenticated user's session.

```python
import os
from supabase import create_client

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_PUBLISHABLE_KEY'])
response = client.table('products').select('id, name').limit(10).execute()
print({'returned_rows': len(response.data)})
```

Handle the installed Python client's documented exceptions at the application
boundary. Do not assume Python has JavaScript's `{ data, error }` return convention
or an awaitable generic `close()` method. Configure/test resource ownership for the
specific pinned sync/async client rather than inventing a context-manager API.

## Validate Application Data Before Writes

```typescript
import { z } from 'zod';

export const productInput = z.object({
  name: z.string().min(1).max(200),
});
```

Validation does not replace RLS or caller authorization.

[Python initialization](https://supabase.com/docs/reference/python/initializing)

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
