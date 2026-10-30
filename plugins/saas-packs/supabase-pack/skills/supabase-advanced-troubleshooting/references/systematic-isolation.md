# Systematic Isolation

## Layer-by-Layer Testing

Separate transport, authentication, and application authorization failures. Record the
project URL's hostname (not a key), operation, error code, and timestamp. Investigate
DNS/TLS for that project's hostname; `api.supabase.com` is the Management API, not
the project's Data API. Do not print authorization headers, sessions, or full rows.

1. Confirm the configured project URL and runtime/dependency versions locally.
2. Inspect DNS/TLS or proxy failures for that URL using an explicitly approved diagnostic.
3. Check the operation's returned error before interpreting its data.
4. Distinguish a successful empty RLS-filtered result from a failed request. An empty
   result does not establish that a table has no rows.
5. Compare only authorized test identities. Do not substitute a privileged key merely
   to make a user request succeed. Catalog diagnostics require a separately authorized
   administrative connection; see [the diagnostic workflow](../SKILL.md).

## Minimal Read Reproduction

This example assumes your migration defines `public.profiles(id)` and grants this
identity SELECT access. Adapt the table/columns to an existing approved fixture;
this is not a built-in health endpoint or `ping()` method.

```typescript
import { createClient } from '@supabase/supabase-js';

export async function minimalRepro(url: string, publishableKey: string) {
  const client = createClient(url, publishableKey, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  const { data, error } = await client.from('profiles').select('id').limit(1);
  if (error) {
    // Return only an error code; redact any additional diagnostic evidence separately.
    return { ok: false as const, code: error.code };
  }
  return { ok: true as const, returnedRows: data.length };
}
```

Use a separate, request-scoped cookie-aware `@supabase/ssr` client when reproducing
an authenticated SSR operation. This stateless public-key probe does not reproduce
that user's session, validate every service, or prove service availability globally.

[Client initialization](https://supabase.com/docs/reference/javascript/initializing)
