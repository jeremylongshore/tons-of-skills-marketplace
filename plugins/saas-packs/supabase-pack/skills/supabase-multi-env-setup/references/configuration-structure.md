# Configuration Structure

Use a distinct reviewed project (or explicitly configured local stack) for each
environment. There are no generic `api-sandbox.supabase.com` or
`api-staging.supabase.com` Data API endpoints. Copy each project's actual URL and
publishable key from its dashboard into that environment's managed configuration;
never derive credentials or project selection from an untrusted request parameter.

```text
config/supabase/base.json       # non-secret application settings
.env.local                     # ignored local values
```

```json
{
  "readPageSize": 100,
  "publicCacheTtlSeconds": 60
}
```

Those JSON keys are application-owned settings, not `createClient` options. JSON
itself does not expand `${VARIABLE}` placeholders. Validate required environment
variables explicitly before constructing a client:

```typescript
import { createClient } from '@supabase/supabase-js';

export function createStatelessPublicClient(env: Record<string, string | undefined>) {
  const url = env.SUPABASE_URL;
  const key = env.SUPABASE_PUBLISHABLE_KEY;
  if (!url || !key) throw new Error('Missing project configuration');
  const parsed = new URL(url);
  if (
    parsed.protocol !== 'https:' &&
    !(parsed.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(parsed.hostname))
  ) {
    throw new Error('Expected HTTPS project URL or explicit local stack');
  }
  return createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
}
```

This public client is not a cookie-authenticated SSR adapter. Create the latter per
request using `@supabase/ssr`. Keep secret/service-role credentials in a separate
server-only configuration with explicit caller and operation authorization. Do not
log keys, Authorization headers, or raw environment objects during selection.

[Initialization](https://supabase.com/docs/reference/javascript/initializing)
[SSR](https://supabase.com/docs/guides/auth/server-side/creating-a-client)
